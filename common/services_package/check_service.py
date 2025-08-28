"""
Универсальный сервис проверок - новая архитектура
"""

import logging
from typing import Dict, Any, Optional
from common.integrations.free_check_service import free_check_service
from common.integrations.paid_check_service import paid_check_service
from common.integrations.cache_service import cache_service

logger = logging.getLogger(__name__)


class CheckService:
    """Универсальный сервис проверок"""

    def __init__(self):
        self.free_service = free_check_service
        self.paid_service = paid_check_service

    async def check_address(self, address: str, chain: str, check_type: str = "free") -> Dict[str, Any]:
        """Универсальная проверка адреса"""
        try:
            logger.info(f"🔍 Выполняем {check_type} проверку: {address[:10]}...")

            if check_type == "free":
                # Бесплатная проверка
                result = await self.free_service.execute(address, chain)

            elif check_type == "paid":
                # Платная проверка - сначала получаем базовые данные
                free_result = await self.free_service.execute(address, chain)
                wallet_data = free_result.get("screening", {})
                label_data = free_result.get("label", {})

                # Выполняем платную проверку
                paid_result = await self.paid_service.execute(address, chain, wallet_data, label_data)

                # Объединяем результаты
                result = {**free_result, **paid_result, "check_type": "paid"}

            else:
                raise ValueError(f"Неизвестный тип проверки: {check_type}")

            logger.info(f"✅ {check_type} проверка завершена: {address[:10]}...")
            return result

        except Exception as e:
            logger.error(f"Ошибка {check_type} проверки: {e}")
            raise

    async def get_provider_info(self) -> Dict[str, Any]:
        """Получить информацию о всех провайдерах"""
        try:
            free_info = await self.free_service.get_provider_info()
            paid_info = await self.paid_service.get_provider_info()

            return {"free_check": free_info, "paid_check": paid_info}

        except Exception as e:
            logger.error(f"Ошибка получения информации о провайдерах: {e}")
            return {"error": str(e)}

    async def switch_provider(self, check_type: str, provider_name: str) -> bool:
        """Переключить провайдера"""
        try:
            if check_type == "free":
                return await self.free_service.switch_provider(provider_name)
            elif check_type == "paid":
                return await self.paid_service.switch_provider(provider_name)
            else:
                logger.error(f"Неизвестный тип проверки: {check_type}")
                return False

        except Exception as e:
            logger.error(f"Ошибка переключения провайдера: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Получить статистику кеша"""
        try:
            return await cache_service.get_cache_stats()
        except Exception as e:
            logger.error(f"Ошибка получения статистики кеша: {e}")
            return {"error": str(e)}

    async def clear_cache(self, cache_type: str = None) -> bool:
        """Очистить кеш"""
        try:
            return await cache_service.clear_cache(cache_type)
        except Exception as e:
            logger.error(f"Ошибка очистки кеша: {e}")
            return False


# Глобальный экземпляр сервиса
check_service = CheckService()
