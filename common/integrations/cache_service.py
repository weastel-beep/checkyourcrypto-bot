"""
Redis кеширование для интеграций - новая архитектура
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from common.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Сервис Redis кеширования"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False

    async def connect(self):
        """Подключиться к Redis"""
        try:
            if not self.redis_client:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL, decode_responses=True, socket_connect_timeout=5, socket_timeout=5
                )

            # Проверяем подключение
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("✅ Подключение к Redis установлено")

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.is_connected = False
            self.redis_client = None

    async def disconnect(self):
        """Отключиться от Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            self.is_connected = False
            logger.info("Отключение от Redis")

    def _get_cache_key(self, cache_type: str, identifier: str) -> str:
        """Генерировать ключ кеша"""
        return f"{cache_type}:{identifier}"

    async def get(self, cache_type: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Получить данные из кеша"""
        if not self.is_connected or not self.redis_client:
            return None

        try:
            key = self._get_cache_key(cache_type, identifier)
            data = await self.redis_client.get(key)

            if data:
                result = json.loads(data)
                logger.info(f"✅ Данные получены из кеша: {cache_type}:{identifier}")
                return result
            else:
                logger.info(f"❌ Данные не найдены в кеше: {cache_type}:{identifier}")
                return None

        except Exception as e:
            logger.error(f"Ошибка получения из кеша: {e}")
            return None

    async def set(self, cache_type: str, identifier: str, data: Dict[str, Any], ttl: int = 3600):
        """Сохранить данные в кеш"""
        if not self.is_connected or not self.redis_client:
            return False

        try:
            key = self._get_cache_key(cache_type, identifier)
            json_data = json.dumps(data, default=str)

            await self.redis_client.setex(key, ttl, json_data)
            logger.info(f"✅ Данные сохранены в кеш: {cache_type}:{identifier} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Ошибка сохранения в кеш: {e}")
            return False

    async def delete(self, cache_type: str, identifier: str) -> bool:
        """Удалить данные из кеша"""
        if not self.is_connected or not self.redis_client:
            return False

        try:
            key = self._get_cache_key(cache_type, identifier)
            result = await self.redis_client.delete(key)

            if result:
                logger.info(f"✅ Данные удалены из кеша: {cache_type}:{identifier}")
            else:
                logger.info(f"❌ Данные не найдены в кеше для удаления: {cache_type}:{identifier}")

            return bool(result)

        except Exception as e:
            logger.error(f"Ошибка удаления из кеша: {e}")
            return False

    async def clear_cache(self, cache_type: str = None) -> bool:
        """Очистить кеш"""
        if not self.is_connected or not self.redis_client:
            return False

        try:
            if cache_type:
                # Очищаем конкретный тип кеша
                pattern = f"{cache_type}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"✅ Очищен кеш типа: {cache_type} ({len(keys)} записей)")
                else:
                    logger.info(f"❌ Кеш типа {cache_type} пуст")
            else:
                # Очищаем весь кеш
                await self.redis_client.flushdb()
                logger.info("✅ Весь кеш очищен")

            return True

        except Exception as e:
            logger.error(f"Ошибка очистки кеша: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Получить статистику кеша"""
        if not self.is_connected or not self.redis_client:
            return {"error": "Redis не подключен"}

        try:
            stats = {"total_keys": await self.redis_client.dbsize(), "cache_types": {}}

            # Статистика по типам кеша
            cache_types = ["free_checks", "paid_checks", "user_sessions", "integrations"]

            for cache_type in cache_types:
                pattern = f"{cache_type}:*"
                keys = await self.redis_client.keys(pattern)
                stats["cache_types"][cache_type] = len(keys)

            logger.info(f"Статистика кеша получена: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики кеша: {e}")
            return {"error": str(e)}


# Глобальный экземпляр сервиса кеширования
cache_service = CacheService()
