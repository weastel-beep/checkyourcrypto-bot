"""
Сервис платных проверок - новая архитектура
"""

import logging
from typing import Dict, Any, Optional
from .base import BaseIntegration
from .providers import AIAnalysisProvider, DeepScanProvider
from .cache_service import cache_service

logger = logging.getLogger(__name__)


class PaidCheckService(BaseIntegration):
    """Сервис платных проверок"""

    def __init__(self):
        super().__init__("paid_check")
        self._initialize_providers()

    def _initialize_providers(self):
        """Инициализировать провайдеров"""
        # Добавляем провайдеров
        self.add_provider(AIAnalysisProvider())
        self.add_provider(DeepScanProvider())

        logger.info(f"Инициализированы провайдеры платных проверок: {list(self.providers.keys())}")

    async def execute(
        self, address: str, chain: str, wallet_data: Dict[str, Any] = None, label_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Выполнить платную проверку адреса"""
        try:
            # Проверяем кеш
            cache_key = f"{address}_{chain}"
            cached_result = await cache_service.get("paid_checks", cache_key)

            if cached_result:
                logger.info(f"✅ Результат получен из кеша: {address[:10]}...")
                return {**cached_result, "cached": True}

            # Получаем активного провайдера
            active_provider = self.get_active_provider()
            if not active_provider:
                raise Exception("Нет активного провайдера для платных проверок")

            logger.info(f"🔍 Выполняем платную проверку через {active_provider.name}: {address[:10]}...")

            # Выполняем проверку
            if active_provider.name == "ai_analysis":
                # AI Analysis - используем существующую GPT интеграцию
                if not wallet_data or not label_data:
                    raise Exception("Для AI анализа требуются данные скрининга и меток")

                analysis_result = await active_provider.analyze_risk_data(wallet_data, label_data)

                result = {
                    "provider": active_provider.name,
                    "address": address,
                    "chain": chain,
                    "analysis": analysis_result,
                    "screening": wallet_data,
                    "label": label_data,
                    "check_type": "paid",
                    "cached": False,
                    "timestamp": active_provider.last_check.isoformat() if active_provider.last_check else None,
                }

            elif active_provider.name == "deep_scan":
                # Deep Scan
                deep_scan_result = await active_provider.deep_scan(address, chain)

                result = {
                    "provider": active_provider.name,
                    "address": address,
                    "chain": chain,
                    "deep_scan": deep_scan_result,
                    "check_type": "paid",
                    "cached": False,
                    "timestamp": active_provider.last_check.isoformat() if active_provider.last_check else None,
                }

            else:
                raise Exception(f"Неизвестный провайдер: {active_provider.name}")

            # Сохраняем в кеш (TTL: 30 минут)
            await cache_service.set("paid_checks", cache_key, result, ttl=1800)

            logger.info(f"✅ Платная проверка завершена: {address[:10]}...")
            return result

        except Exception as e:
            logger.error(f"Ошибка платной проверки: {e}")

            # Пробуем fallback на другой провайдер
            for provider_name, provider in self.providers.items():
                if provider_name != self.active_provider and provider.is_active:
                    logger.info(f"🔄 Пробуем fallback на провайдер: {provider_name}")
                    try:
                        self.active_provider = provider_name
                        return await self.execute(address, chain, wallet_data, label_data)
                    except Exception as fallback_error:
                        logger.error(f"Fallback на {provider_name} не удался: {fallback_error}")
                        continue

            raise Exception(f"Все провайдеры недоступны: {e}")

    async def get_provider_info(self) -> Dict[str, Any]:
        """Получить информацию о провайдерах"""
        info = {"integration_type": self.integration_type, "active_provider": self.active_provider, "providers": {}}

        for name, provider in self.providers.items():
            info["providers"][name] = {
                "is_active": provider.is_active,
                "error_count": provider.error_count,
                "last_check": provider.last_check.isoformat() if provider.last_check else None,
            }

        return info

    async def switch_provider(self, provider_name: str) -> bool:
        """Переключить провайдера"""
        if provider_name in self.providers:
            self.active_provider = provider_name
            logger.info(f"🔄 Активный провайдер изменен на: {provider_name}")
            return True
        else:
            logger.error(f"Провайдер {provider_name} не найден")
            return False


# Глобальный экземпляр сервиса
paid_check_service = PaidCheckService()
