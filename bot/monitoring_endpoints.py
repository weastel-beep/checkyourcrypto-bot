"""
Endpoints для мониторинга и метрик
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from common.monitoring import (
    metrics_collector,
    alert_manager,
    performance_monitor,
    system_monitor,
    get_monitoring_status,
    AlertLevel,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Получение всех метрик

    Returns:
        Dict с метриками системы
    """
    try:
        metrics = await metrics_collector.get_metrics()
        return {"timestamp": datetime.now().isoformat(), "metrics": metrics}
    except Exception as e:
        logger.error(f"Ошибка получения метрик: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(level: str = None, source: str = None, hours: int = 24) -> Dict[str, Any]:
    """
    Получение алертов с фильтрацией

    Args:
        level: Уровень алерта (info, warning, error, critical)
        source: Источник алерта
        hours: Количество часов для фильтрации

    Returns:
        Dict с алертами
    """
    try:
        # Преобразуем уровень алерта
        alert_level = None
        if level:
            try:
                alert_level = AlertLevel(level.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Неверный уровень алерта: {level}")

        alerts = await alert_manager.get_alerts(level=alert_level, source=source)

        # Фильтруем по времени
        if hours:
            cutoff = datetime.now().replace(hour=datetime.now().hour - hours)
            alerts = [a for a in alerts if a.timestamp >= cutoff]

        return {
            "timestamp": datetime.now().isoformat(),
            "alerts": [alert.to_dict() for alert in alerts],
            "total_count": len(alerts),
        }
    except Exception as e:
        logger.error(f"Ошибка получения алертов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Получение общего статуса мониторинга

    Returns:
        Dict с статусом мониторинга
    """
    try:
        status = await get_monitoring_status()
        return {"timestamp": datetime.now().isoformat(), "status": status}
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts")
async def create_alert(level: str, message: str, source: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Создание нового алерта

    Args:
        level: Уровень алерта
        message: Сообщение алерта
        source: Источник алерта
        metadata: Дополнительные данные

    Returns:
        Dict с результатом создания
    """
    try:
        # Проверяем уровень алерта
        try:
            alert_level = AlertLevel(level.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Неверный уровень алерта: {level}")

        # Создаем алерт
        await alert_manager.add_alert(alert_level, message, source, metadata)

        return {"status": "success", "message": "Алерт создан", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ошибка создания алерта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts")
async def clear_alerts(days: int = 7) -> Dict[str, Any]:
    """
    Очистка старых алертов

    Args:
        days: Количество дней для очистки

    Returns:
        Dict с результатом очистки
    """
    try:
        await alert_manager.clear_old_alerts(days)
        return {"status": "success", "message": f"Алерты старше {days} дней очищены", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ошибка очистки алертов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/metrics")
async def clear_metrics() -> Dict[str, Any]:
    """
    Очистка всех метрик

    Returns:
        Dict с результатом очистки
    """
    try:
        await metrics_collector.clear_metrics()
        return {"status": "success", "message": "Все метрики очищены", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ошибка очистки метрик: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/start")
async def start_monitoring() -> Dict[str, Any]:
    """
    Запуск системного мониторинга

    Returns:
        Dict с результатом запуска
    """
    try:
        await system_monitor.start_monitoring()
        return {"status": "success", "message": "Системный мониторинг запущен", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ошибка запуска мониторинга: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/stop")
async def stop_monitoring() -> Dict[str, Any]:
    """
    Остановка системного мониторинга

    Returns:
        Dict с результатом остановки
    """
    try:
        await system_monitor.stop_monitoring()
        return {"status": "success", "message": "Системный мониторинг остановлен", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Получение метрик производительности

    Returns:
        Dict с метриками производительности
    """
    try:
        metrics = await metrics_collector.get_metrics()

        # Фильтруем метрики производительности
        performance_metrics = {}
        for key, value in metrics.items():
            if any(prefix in key for prefix in ["http_", "database_", "external_api_", "bot_"]):
                performance_metrics[key] = value

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(performance_monitor.get_uptime()),
            "metrics": performance_metrics,
        }
    except Exception as e:
        logger.error(f"Ошибка получения метрик производительности: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Получение системных метрик

    Returns:
        Dict с системными метриками
    """
    try:
        metrics = await metrics_collector.get_metrics()

        # Фильтруем системные метрики
        system_metrics = {}
        for key, value in metrics.items():
            if key.startswith("system_"):
                system_metrics[key] = value

        return {"timestamp": datetime.now().isoformat(), "metrics": system_metrics}
    except Exception as e:
        logger.error(f"Ошибка получения системных метрик: {e}")
        raise HTTPException(status_code=500, detail=str(e))
