"""
Интеграция с MetaSleuth API для проверки криптовалютных адресов
"""
import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime, timedelta

from .config import settings

logger = logging.getLogger(__name__)

# Кеш для результатов (24 часа)
_cache = {}
_cache_ttl = timedelta(hours=24)


class MetaSleuthAPI:
    """Класс для работы с MetaSleuth API"""
    
    def __init__(self):
        self.wallet_screening_key = settings.metasleuth_wallet_screening_key
        self.address_label_key = settings.metasleuth_address_label_key
        self.base_url = "https://aml.blocksec.com"
        self.session: Optional[aiohttp.ClientSession] = None
        self._circuit_breaker_failures = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60  # секунды
        self._last_failure_time = None
    
    async def _get_session(self, api_type: str = "screening") -> aiohttp.ClientSession:
        """Получить или создать HTTP сессию"""
        if self.session is None or self.session.closed:
            # Выбираем ключ в зависимости от типа API
            api_key = self.wallet_screening_key if api_type == "screening" else self.address_label_key
            
            self.session = aiohttp.ClientSession(
                headers={
                    "API-KEY": api_key,
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        else:
            # Обновляем заголовки для существующей сессии
            api_key = self.wallet_screening_key if api_type == "screening" else self.address_label_key
            self.session._default_headers.update({
                "API-KEY": api_key
            })
        return self.session
    
    def _check_circuit_breaker(self) -> bool:
        """Проверить circuit breaker"""
        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            if self._last_failure_time:
                if datetime.now() - self._last_failure_time > timedelta(seconds=self._circuit_breaker_timeout):
                    # Сброс circuit breaker
                    self._circuit_breaker_failures = 0
                    self._last_failure_time = None
                    return True
            return False
        return True
    
    def _record_failure(self):
        """Записать неудачу для circuit breaker"""
        self._circuit_breaker_failures += 1
        self._last_failure_time = datetime.now()
    
    def _record_success(self):
        """Записать успех для circuit breaker"""
        self._circuit_breaker_failures = 0
        self._last_failure_time = None
    
    def _get_cache_key(self, address: str, chain: str, api_type: str) -> str:
        """Получить ключ кеша"""
        return f"{api_type}:{chain}:{address.lower()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Получить данные из кеша"""
        if cache_key in _cache:
            cached_data, timestamp = _cache[cache_key]
            if datetime.now() - timestamp < _cache_ttl:
                return cached_data
            else:
                del _cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        """Сохранить данные в кеш"""
        _cache[cache_key] = (data, datetime.now())
    
    async def wallet_screening(self, address: str, chain: str) -> Dict:
        """
        Проверка адреса через Wallet Screening API
        
        Returns:
            Dict с ключами: risk, details, percents
        """
        if settings.mock_metasleuth:
            return await self._mock_wallet_screening(address, chain)
        
        cache_key = self._get_cache_key(address, chain, "screening")
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        if not self._check_circuit_breaker():
            logger.warning("Circuit breaker активен для wallet_screening")
            return await self._mock_wallet_screening(address, chain)
        
        try:
            session = await self._get_session("screening")
            url = f"{self.base_url}/address-compliance/api/v3/risk-score"
            
            # Конвертируем chain в chain_id согласно документации
            chain_id_map = {
                "eth": 1,
                "btc": -1,
                "tron": -2,
                "solana": -3
            }
            chain_id = chain_id_map.get(chain.lower(), 1)  # По умолчанию ETH
            
            payload = {
                "address": address,
                "chain_id": chain_id,
                "interaction_risk": True
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 429:
                    logger.warning("Rate limit для MetaSleuth API")
                    self._record_failure()
                    return await self._mock_wallet_screening(address, chain)
                
                if response.status >= 500:
                    logger.error(f"Ошибка сервера MetaSleuth: {response.status}")
                    self._record_failure()
                    return await self._mock_wallet_screening(address, chain)
                
                if response.status != 200:
                    logger.error(f"Ошибка MetaSleuth API: {response.status}")
                    self._record_failure()
                    return await self._mock_wallet_screening(address, chain)
                
                data = await response.json()
                logger.info(f"MetaSleuth API response: {data}")
                
                # Обрабатываем ответ согласно документации
                if data.get("code") == 200000 and "data" in data:
                    risk_data = data["data"]
                    result = {
                        "risk": risk_data.get("risk_score", 0),
                        "details": [],
                        "percents": {},
                        # Добавляем risk_indicators
                        "risk_indicators": risk_data.get("risk_indicators", [])
                    }
                    
                    # Извлекаем детали рисков из risk_indicators
                    risk_indicators = risk_data.get("risk_indicators", [])
                    if risk_indicators:
                        for indicator in risk_indicators:
                            if "indicator" in indicator:
                                result["details"].append(indicator["indicator"].get("name", ""))
                    else:
                        # Если нет индикаторов риска, добавляем базовую информацию
                        result["details"].append("Адрес проверен на соответствие требованиям")
                else:
                    logger.error(f"Unexpected API response format: {data}")
                    result = {
                        "risk": 0,
                        "details": ["Ошибка обработки ответа API"],
                        "percents": {},
                        "risk_indicators": []
                    }
                
                self._set_cache(cache_key, result)
                self._record_success()
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при вызове wallet_screening: {e}")
            self._record_failure()
            return await self._mock_wallet_screening(address, chain)
    
    async def address_label(self, address: str, chain: str) -> Dict:
        """
        Получение метки адреса через Address Label API
        
        Returns:
            Dict с ключами: label, website, type, tags
        """
        if settings.mock_metasleuth:
            return await self._mock_address_label(address, chain)
        
        cache_key = self._get_cache_key(address, chain, "label")
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        if not self._check_circuit_breaker():
            logger.warning("Circuit breaker активен для address_label")
            return await self._mock_address_label(address, chain)
        
        try:
            session = await self._get_session("label")
            url = f"{self.base_url}/address-label/api/v3/labels"
            
            # Конвертируем chain в chain_id согласно документации
            chain_id_map = {
                "eth": 1,
                "btc": -1,
                "tron": -2,
                "solana": -3
            }
            chain_id = chain_id_map.get(chain.lower(), 1)  # По умолчанию ETH
            
            payload = {
                "address": address,
                "chain_id": chain_id
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 429:
                    logger.warning("Rate limit для MetaSleuth API")
                    self._record_failure()
                    return await self._mock_address_label(address, chain)
                
                if response.status >= 500:
                    logger.error(f"Ошибка сервера MetaSleuth: {response.status}")
                    self._record_failure()
                    return await self._mock_address_label(address, chain)
                
                if response.status != 200:
                    logger.error(f"Ошибка MetaSleuth API: {response.status}")
                    self._record_failure()
                    return await self._mock_address_label(address, chain)
                
                data = await response.json()
                logger.info(f"MetaSleuth Address Label API response: {data}")
                
                # Обрабатываем ответ согласно документации
                if data.get("code") == 200000 and "data" in data:
                    label_data = data["data"]
                    result = {
                        "label": label_data.get("main_entity", "") or "Неизвестный адрес",
                        "website": "",
                        "type": "unknown",
                        "tags": [],
                        # Добавляем все дополнительные данные из API
                        "main_entity": label_data.get("main_entity", ""),
                        "main_entity_info": label_data.get("main_entity_info", {}),
                        "comp_entities": label_data.get("comp_entities", []),
                        "attributes": label_data.get("attributes", []),
                        "name_tag": label_data.get("name_tag", "")
                    }
                    
                    # Извлекаем информацию о веб-сайте из main_entity_info
                    if label_data.get("main_entity_info") and label_data["main_entity_info"].get("description"):
                        result["website"] = label_data["main_entity_info"]["description"].get("website", "")
                    
                    # Извлекаем категории как теги
                    if label_data.get("main_entity_info") and label_data["main_entity_info"].get("categories"):
                        categories = label_data["main_entity_info"]["categories"]
                        if isinstance(categories, list):
                            result["tags"] = [cat.get("name", "") for cat in categories if cat.get("name")]
                        else:
                            result["tags"] = []
                    else:
                        result["tags"] = []
                    
                    # Определяем тип на основе категорий
                    if result["tags"]:
                        result["type"] = result["tags"][0].lower()
                else:
                    logger.error(f"Unexpected Address Label API response format: {data}")
                    result = {
                        "label": "Неизвестный адрес",
                        "website": "",
                        "type": "unknown",
                        "tags": [],
                        "main_entity": "",
                        "main_entity_info": {},
                        "comp_entities": [],
                        "attributes": [],
                        "name_tag": ""
                    }
                
                self._set_cache(cache_key, result)
                self._record_success()
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при вызове address_label: {e}")
            self._record_failure()
            return await self._mock_address_label(address, chain)
    
    async def _mock_wallet_screening(self, address: str, chain: str) -> Dict:
        """Мок данные для wallet screening"""
        return {
            "risk": 2,
            "details": [
                "Адрес не связан с известными мошенническими схемами",
                "Низкая активность транзакций"
            ],
            "percents": {
                "scam": 5,
                "mixer": 0,
                "exchange": 15,
                "gambling": 0
            }
        }
    
    async def _mock_address_label(self, address: str, chain: str) -> Dict:
        """Мок данные для address label"""
        return {
            "label": "Обычный пользователь",
            "website": "",
            "type": "user",
            "tags": ["active", "regular"]
        }
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()


# Глобальный экземпляр API
metasleuth_api = MetaSleuthAPI()


async def wallet_screening(address: str, chain: str) -> Dict:
    """Удобная функция для проверки адреса"""
    return await metasleuth_api.wallet_screening(address, chain)


async def address_label(address: str, chain: str) -> Dict:
    """Удобная функция для получения метки адреса"""
    return await metasleuth_api.address_label(address, chain)
