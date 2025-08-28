"""
Сервис для работы с OpenAI GPT
"""
from openai import OpenAI
from common.config import settings
from typing import Dict, Any, Optional
import json
import hashlib
import time
from datetime import datetime, timedelta


class GPTService:
    """Сервис для работы с OpenAI GPT"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.cache = {}  # Простое локальное кэширование
        self.request_count = 0
        self.daily_limit = 50  # Лимит запросов в день
        self.last_reset = datetime.now().date()
    
    def _get_cache_key(self, risk_data: Dict[str, Any], address_info: Dict[str, Any]) -> str:
        """Создает ключ кэша на основе данных"""
        data_str = json.dumps({
            'risk_data': risk_data,
            'address_info': address_info
        }, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _check_daily_limit(self) -> bool:
        """Проверяет дневной лимит запросов"""
        today = datetime.now().date()
        if today != self.last_reset:
            self.request_count = 0
            self.last_reset = today
        
        return self.request_count < self.daily_limit
    
    def _increment_request_count(self):
        """Увеличивает счетчик запросов"""
        self.request_count += 1
    
    async def analyze_risk_data(self, risk_data: Dict[str, Any], address_info: Dict[str, Any]) -> str:
        """
        Анализирует данные о рисках через GPT и возвращает рекомендацию
        
        Args:
            risk_data: Данные о рисках от MetaSleuth
            address_info: Информация об адресе
            
        Returns:
            Строка с AI-рекомендацией
        """
        try:
            # Проверяем лимит
            if not self._check_daily_limit():
                return "⚠️ Достигнут дневной лимит AI-запросов. Попробуйте завтра."
            
            # Проверяем кэш
            cache_key = self._get_cache_key(risk_data, address_info)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Формируем промпт для GPT
            prompt = self._create_analysis_prompt(risk_data, address_info)
            
            # Отправляем запрос к GPT (экономичная модель)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Самая экономичная модель
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по криптобезопасности с многолетним опытом. Дай профессиональную, но понятную рекомендацию на русском языке. Будь авторитетным и солидным."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,  # Увеличиваем для более подробных ответов
                temperature=0.3,  # Низкая температура для более предсказуемых ответов
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            
            result = response.choices[0].message.content.strip()
            
            # Кэшируем результат
            self.cache[cache_key] = result
            
            # Увеличиваем счетчик
            self._increment_request_count()
            
            return result
            
        except Exception as e:
            return f"⚠️ AI-анализ временно недоступен: {str(e)}"
    
    def _create_analysis_prompt(self, risk_data: Dict[str, Any], address_info: Dict[str, Any]) -> str:
        """
        Создает промпт для анализа рисков
        
        Args:
            risk_data: Данные о рисках
            address_info: Информация об адресе
            
        Returns:
            Строка с промптом
        """
        # Извлекаем данные о рисках
        minimal_risk = risk_data.get('minimal_risk', 0)
        medium_risk = risk_data.get('medium_risk', 0)
        high_risk = risk_data.get('high_risk', 0)
        
        # Информация об адресе
        address_type = address_info.get('type', 'unknown')
        categories = address_info.get('categories', [])
        main_entity = address_info.get('main_entity', '')
        
        # Определяем общий уровень риска
        if minimal_risk >= 70:
            risk_level = "низкий"
            risk_emoji = "✅"
        elif medium_risk >= 30:
            risk_level = "средний"
            risk_emoji = "⚠️"
        else:
            risk_level = "высокий"
            risk_emoji = "🚨"
        
        prompt = f"""
        Ты эксперт по криптобезопасности с 10-летним опытом анализа блокчейн-транзакций и AML-комплаенса.
        
        ПРОАНАЛИЗИРУЙ криптоадрес на основе следующих данных:
        
        📊 РАСПРЕДЕЛЕНИЕ РИСКОВ:
        • Минимальный риск: {minimal_risk}% (безопасные операции)
        • Средний риск: {medium_risk}% (требует внимания)
        • Высокий риск: {high_risk}% (потенциальные угрозы)
        
        📋 ХАРАКТЕРИСТИКИ АДРЕСА:
        • Тип: {address_type}
        • Основная сущность: {main_entity}
        • Категории: {', '.join(categories) if categories else 'не указаны'}
        • Общий уровень риска: {risk_level} {risk_emoji}
        
        ДАЙ ПРОФЕССИОНАЛЬНУЮ РЕКОМЕНДАЦИЮ (3-4 предложения) на русском языке:
        
        КРИТЕРИИ ОЦЕНКИ:
        ✅ БЕЗОПАСНО (минимальный риск > 70%): "Адрес безопасен для использования"
        ⚠️ ВНИМАНИЕ (средний риск > 30%): "Требует дополнительной осторожности"
        🚨 ОПАСНО (высокий риск > 10%): "Не рекомендуется к использованию"
        
        СТРУКТУРА ОТВЕТА:
        1. Краткая оценка безопасности (1 предложение)
        2. Практические рекомендации по использованию (1-2 предложения)
        3. Меры предосторожности или преимущества (1 предложение)
        
        ТОН: Профессиональный, но понятный. Не пугай клиента без необходимости.
        """
        
        return prompt.strip()
    
    async def get_cached_recommendation(self, risk_data: Dict[str, Any], address_info: Dict[str, Any]) -> str:
        """
        Получает рекомендацию с кэшированием
        
        Args:
            risk_data: Данные о рисках
            address_info: Информация об адресе
            
        Returns:
            Строка с рекомендацией
        """
        return await self.analyze_risk_data(risk_data, address_info)
    
    def get_mock_recommendation(self) -> str:
        """
        Возвращает мок-рекомендацию для примера (без API вызова)
        
        Returns:
            Строка с мок-рекомендацией
        """
        return "Адрес обладает низким уровнем риска, так как минимальный риск составляет 80.2%. Вероятность присутствия высокого риска невелика (1.1%). Следовательно, данный криптоадрес можно считать безопасным для использования."
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику использования
        
        Returns:
            Словарь со статистикой
        """
        return {
            "requests_today": self.request_count,
            "daily_limit": self.daily_limit,
            "cache_size": len(self.cache),
            "remaining_requests": self.daily_limit - self.request_count
        }


# Создаем глобальный экземпляр сервиса
gpt_service = GPTService()
