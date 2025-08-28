"""
API эндпоинты для управления интеграциями - новая архитектура
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# Импортируем сервисы интеграций
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from common.services.check_service import check_service
from common.integrations.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


class ProviderSwitchRequest(BaseModel):
    provider_name: str


class CacheClearRequest(BaseModel):
    cache_type: Optional[str] = None


@router.get("/status")
async def get_integrations_status():
    """Получить статус всех интеграций"""
    try:
        logger.info("Получение статуса интеграций")
        
        # Получаем информацию о провайдерах
        provider_info = await check_service.get_provider_info()
        
        # Получаем статистику кеша
        cache_stats = await check_service.get_cache_stats()
        
        status = {
            "providers": provider_info,
            "cache": cache_stats,
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: использовать реальное время
        }
        
        logger.info("Статус интеграций получен успешно")
        return status
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса интеграций: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")


@router.get("/providers")
async def get_providers():
    """Получить список всех провайдеров"""
    try:
        logger.info("Получение списка провайдеров")
        
        provider_info = await check_service.get_provider_info()
        
        # Форматируем список провайдеров
        providers = {
            "free_check": {
                "type": "free_check",
                "active_provider": provider_info.get("free_check", {}).get("active_provider"),
                "providers": list(provider_info.get("free_check", {}).get("providers", {}).keys())
            },
            "paid_check": {
                "type": "paid_check", 
                "active_provider": provider_info.get("paid_check", {}).get("active_provider"),
                "providers": list(provider_info.get("paid_check", {}).get("providers", {}).keys())
            }
        }
        
        logger.info("Список провайдеров получен успешно")
        return providers
        
    except Exception as e:
        logger.error(f"Ошибка получения списка провайдеров: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения провайдеров: {str(e)}")


@router.put("/free-check")
async def switch_free_check_provider(request: ProviderSwitchRequest):
    """Переключить провайдера для бесплатных проверок"""
    try:
        logger.info(f"Переключение провайдера бесплатных проверок на: {request.provider_name}")
        
        success = await check_service.switch_provider("free", request.provider_name)
        
        if success:
            logger.info(f"Провайдер бесплатных проверок успешно переключен на: {request.provider_name}")
            return {
                "success": True,
                "message": f"Провайдер переключен на {request.provider_name}",
                "active_provider": request.provider_name
            }
        else:
            logger.error(f"Не удалось переключить провайдера на: {request.provider_name}")
            raise HTTPException(status_code=400, detail=f"Не удалось переключить провайдера: {request.provider_name}")
            
    except Exception as e:
        logger.error(f"Ошибка переключения провайдера бесплатных проверок: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка переключения: {str(e)}")


@router.put("/paid-check")
async def switch_paid_check_provider(request: ProviderSwitchRequest):
    """Переключить провайдера для платных проверок"""
    try:
        logger.info(f"Переключение провайдера платных проверок на: {request.provider_name}")
        
        success = await check_service.switch_provider("paid", request.provider_name)
        
        if success:
            logger.info(f"Провайдер платных проверок успешно переключен на: {request.provider_name}")
            return {
                "success": True,
                "message": f"Провайдер переключен на {request.provider_name}",
                "active_provider": request.provider_name
            }
        else:
            logger.error(f"Не удалось переключить провайдера на: {request.provider_name}")
            raise HTTPException(status_code=400, detail=f"Не удалось переключить провайдера: {request.provider_name}")
            
    except Exception as e:
        logger.error(f"Ошибка переключения провайдера платных проверок: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка переключения: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(request: CacheClearRequest):
    """Очистить кеш"""
    try:
        cache_type = request.cache_type
        logger.info(f"Очистка кеша: {cache_type or 'весь кеш'}")
        
        success = await check_service.clear_cache(cache_type)
        
        if success:
            message = f"Кеш {cache_type or 'весь'} очищен успешно"
            logger.info(message)
            return {
                "success": True,
                "message": message,
                "cache_type": cache_type
            }
        else:
            logger.error(f"Не удалось очистить кеш: {cache_type}")
            raise HTTPException(status_code=500, detail="Не удалось очистить кеш")
            
    except Exception as e:
        logger.error(f"Ошибка очистки кеша: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка очистки кеша: {str(e)}")


@router.get("/stats")
async def get_integrations_stats():
    """Получить статистику использования интеграций"""
    try:
        logger.info("Получение статистики интеграций")
        
        # Получаем статистику кеша
        cache_stats = await check_service.get_cache_stats()
        
        # Получаем информацию о провайдерах
        provider_info = await check_service.get_provider_info()
        
        # Формируем статистику
        stats = {
            "cache": cache_stats,
            "providers": {
                "free_check": {
                    "active_provider": provider_info.get("free_check", {}).get("active_provider"),
                    "total_providers": len(provider_info.get("free_check", {}).get("providers", {})),
                    "active_providers": sum(1 for p in provider_info.get("free_check", {}).get("providers", {}).values() if p.get("is_active", False))
                },
                "paid_check": {
                    "active_provider": provider_info.get("paid_check", {}).get("active_provider"),
                    "total_providers": len(provider_info.get("paid_check", {}).get("providers", {})),
                    "active_providers": sum(1 for p in provider_info.get("paid_check", {}).get("providers", {}).values() if p.get("is_active", False))
                }
            },
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: использовать реальное время
        }
        
        logger.info("Статистика интеграций получена успешно")
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики интеграций: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@router.get("/health")
async def check_integrations_health():
    """Проверить здоровье интеграций"""
    try:
        logger.info("Проверка здоровья интеграций")
        
        # Проверяем подключение к Redis
        redis_connected = cache_service.is_connected
        
        # Получаем информацию о провайдерах
        provider_info = await check_service.get_provider_info()
        
        # Проверяем активность провайдеров
        free_providers = provider_info.get("free_check", {}).get("providers", {})
        paid_providers = provider_info.get("paid_check", {}).get("providers", {})
        
        free_active = any(p.get("is_active", False) for p in free_providers.values())
        paid_active = any(p.get("is_active", False) for p in paid_providers.values())
        
        health_status = {
            "overall_status": "healthy" if (redis_connected and free_active and paid_active) else "degraded",
            "redis": {
                "connected": redis_connected,
                "status": "healthy" if redis_connected else "unhealthy"
            },
            "free_check": {
                "active_provider": provider_info.get("free_check", {}).get("active_provider"),
                "has_active_provider": free_active,
                "status": "healthy" if free_active else "unhealthy"
            },
            "paid_check": {
                "active_provider": provider_info.get("paid_check", {}).get("active_provider"),
                "has_active_provider": paid_active,
                "status": "healthy" if paid_active else "unhealthy"
            },
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: использовать реальное время
        }
        
        logger.info("Проверка здоровья интеграций завершена")
        return health_status
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья интеграций: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка проверки здоровья: {str(e)}")
