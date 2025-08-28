"""
Health check endpoints для мониторинга
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from common.database import async_session_maker
from common.config import settings
from common.error_handling import ErrorHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

# Кеш для результатов health check
_health_cache = {}
_cache_ttl = timedelta(minutes=5)


class HealthChecker:
    """Класс для проверки здоровья системы"""

    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Проверка подключения к базе данных"""
        try:
            async with async_session_maker() as session:
                # Выполняем простой запрос
                result = await session.execute("SELECT 1")
                await result.fetchone()

            return {
                "status": "healthy",
                "response_time_ms": 0,  # TODO: добавить измерение времени
                "last_check": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "last_check": datetime.now().isoformat()}

    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """Проверка подключения к Redis"""
        try:
            # TODO: добавить проверку Redis
            return {"status": "healthy", "response_time_ms": 0, "last_check": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "last_check": datetime.now().isoformat()}

    @staticmethod
    async def check_external_apis() -> Dict[str, Any]:
        """Проверка внешних API"""
        try:
            # Проверяем MetaSleuth API
            metasleuth_status = await HealthChecker._check_metasleuth_api()

            # Проверяем OpenAI API
            openai_status = await HealthChecker._check_openai_api()

            return {
                "status": "healthy"
                if metasleuth_status["status"] == "healthy" and openai_status["status"] == "healthy"
                else "degraded",
                "services": {"metasleuth": metasleuth_status, "openai": openai_status},
                "last_check": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"External APIs health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "last_check": datetime.now().isoformat()}

    @staticmethod
    async def _check_metasleuth_api() -> Dict[str, Any]:
        """Проверка MetaSleuth API"""
        try:
            # TODO: добавить реальную проверку MetaSleuth API
            return {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def _check_openai_api() -> Dict[str, Any]:
        """Проверка OpenAI API"""
        try:
            # TODO: добавить реальную проверку OpenAI API
            return {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_system_resources() -> Dict[str, Any]:
        """Проверка системных ресурсов"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "last_check": datetime.now().isoformat(),
            }
        except ImportError:
            # psutil не установлен
            return {"status": "unknown", "message": "psutil not available", "last_check": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"System resources health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "last_check": datetime.now().isoformat()}


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Основной health check endpoint

    Returns:
        Dict с информацией о состоянии системы
    """
    # Проверяем кеш
    cache_key = "health_check"
    if cache_key in _health_cache:
        cached_data, timestamp = _health_cache[cache_key]
        if datetime.now() - timestamp < _cache_ttl:
            return cached_data

    try:
        # Выполняем все проверки параллельно
        tasks = [
            HealthChecker.check_database(),
            HealthChecker.check_redis(),
            HealthChecker.check_external_apis(),
            HealthChecker.check_system_resources(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        database_status = (
            results[0] if not isinstance(results[0], Exception) else {"status": "unhealthy", "error": str(results[0])}
        )
        redis_status = (
            results[1] if not isinstance(results[1], Exception) else {"status": "unhealthy", "error": str(results[1])}
        )
        external_apis_status = (
            results[2] if not isinstance(results[2], Exception) else {"status": "unhealthy", "error": str(results[2])}
        )
        system_resources_status = (
            results[3] if not isinstance(results[3], Exception) else {"status": "unhealthy", "error": str(results[3])}
        )

        # Определяем общий статус
        all_healthy = all(
            [
                database_status["status"] == "healthy",
                redis_status["status"] == "healthy",
                external_apis_status["status"] in ["healthy", "degraded"],
                system_resources_status["status"] == "healthy",
            ]
        )

        overall_status = "healthy" if all_healthy else "unhealthy"

        health_data = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": settings.environment,
            "checks": {
                "database": database_status,
                "redis": redis_status,
                "external_apis": external_apis_status,
                "system_resources": system_resources_status,
            },
        }

        # Сохраняем в кеш
        _health_cache[cache_key] = (health_data, datetime.now())

        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        ErrorHandler.log_error(e, "health_check", "main")

        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - проверка готовности к обработке запросов

    Returns:
        Dict с информацией о готовности
    """
    try:
        # Проверяем только критические компоненты
        database_status = await HealthChecker.check_database()

        is_ready = database_status["status"] == "healthy"

        return {"ready": is_ready, "timestamp": datetime.now().isoformat(), "checks": {"database": database_status}}

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "error": str(e), "timestamp": datetime.now().isoformat()}


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - проверка что приложение работает

    Returns:
        Dict с информацией о жизнеспособности
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
        "uptime": "TODO: добавить uptime",  # TODO: добавить реальный uptime
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Детальный health check с дополнительной информацией

    Returns:
        Dict с детальной информацией о состоянии системы
    """
    try:
        # Получаем базовый health check
        basic_health = await health_check()

        # Добавляем дополнительную информацию
        detailed_health = {
            **basic_health,
            "additional_info": {
                "app_name": "Check Your Crypto Bot",
                "deployment_environment": settings.environment,
                "database_url": "***hidden***",  # Не показываем реальный URL
                "telegram_webhook_url": f"https://{settings.heroku_app_name}.herokuapp.com/webhook",
                "admin_panel_url": "https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com",
                "last_deployment": "TODO: добавить информацию о последнем деплое",
                "git_commit": "TODO: добавить git commit hash",
            },
        }

        return detailed_health

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
