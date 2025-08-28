"""
Система мониторинга и алертов
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from common.config import settings
from common.error_handling import ErrorHandler

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Уровни алертов"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Класс для представления алерта"""

    level: AlertLevel
    message: str
    source: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
        }


class MetricsCollector:
    """Сборщик метрик"""

    def __init__(self):
        self.metrics = {}
        self._lock = asyncio.Lock()

    async def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Увеличение счетчика"""
        async with self._lock:
            key = self._get_metric_key(name, labels)
            if key not in self.metrics:
                self.metrics[key] = {"type": "counter", "value": 0, "labels": labels or {}}
            self.metrics[key]["value"] += value

    async def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Установка значения gauge"""
        async with self._lock:
            key = self._get_metric_key(name, labels)
            self.metrics[key] = {"type": "gauge", "value": value, "labels": labels or {}}

    async def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Запись в гистограмму"""
        async with self._lock:
            key = self._get_metric_key(name, labels)
            if key not in self.metrics:
                self.metrics[key] = {"type": "histogram", "values": [], "labels": labels or {}}
            self.metrics[key]["values"].append(value)

    def _get_metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Получение ключа метрики"""
        if labels:
            label_str = "_".join([f"{k}_{v}" for k, v in sorted(labels.items())])
            return f"{name}_{label_str}"
        return name

    async def get_metrics(self) -> Dict[str, Any]:
        """Получение всех метрик"""
        async with self._lock:
            return self.metrics.copy()

    async def clear_metrics(self):
        """Очистка метрик"""
        async with self._lock:
            self.metrics.clear()


class AlertManager:
    """Менеджер алертов"""

    def __init__(self):
        self.alerts: List[Alert] = []
        self._lock = asyncio.Lock()
        self._max_alerts = 1000  # Максимальное количество алертов в памяти

    async def add_alert(self, level: AlertLevel, message: str, source: str, metadata: Optional[Dict[str, Any]] = None):
        """Добавление алерта"""
        alert = Alert(level=level, message=message, source=source, timestamp=datetime.now(), metadata=metadata)

        async with self._lock:
            self.alerts.append(alert)

            # Ограничиваем количество алертов в памяти
            if len(self.alerts) > self._max_alerts:
                self.alerts = self.alerts[-self._max_alerts :]

        # Логируем алерт
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL,
        }[level]

        logger.log(log_level, f"🚨 ALERT [{level.value.upper()}] {source}: {message}")

        # Отправляем критичные алерты в ErrorHandler
        if level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            ErrorHandler.log_error(Exception(message), f"alert_{source}", "monitoring")

    async def get_alerts(
        self, level: Optional[AlertLevel] = None, source: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Alert]:
        """Получение алертов с фильтрацией"""
        async with self._lock:
            filtered_alerts = self.alerts.copy()

            if level:
                filtered_alerts = [a for a in filtered_alerts if a.level == level]

            if source:
                filtered_alerts = [a for a in filtered_alerts if a.source == source]

            if since:
                filtered_alerts = [a for a in filtered_alerts if a.timestamp >= since]

            return filtered_alerts

    async def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Получение алертов за последние часы"""
        since = datetime.now() - timedelta(hours=hours)
        return await self.get_alerts(since=since)

    async def clear_old_alerts(self, days: int = 7):
        """Очистка старых алертов"""
        cutoff = datetime.now() - timedelta(days=days)

        async with self._lock:
            self.alerts = [a for a in self.alerts if a.timestamp >= cutoff]


class PerformanceMonitor:
    """Монитор производительности"""

    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        self.metrics = metrics_collector
        self.alerts = alert_manager
        self._start_time = datetime.now()

    async def record_request(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Запись метрик запроса"""
        labels = {"endpoint": endpoint, "method": method, "status_code": str(status_code)}

        await self.metrics.increment_counter("http_requests_total", labels=labels)
        await self.metrics.record_histogram("http_request_duration_ms", duration_ms, labels=labels)

        # Алерты для медленных запросов
        if duration_ms > 5000:  # Более 5 секунд
            await self.alerts.add_alert(
                AlertLevel.WARNING,
                f"Медленный запрос: {method} {endpoint} ({duration_ms:.2f}ms)",
                "performance",
                {"endpoint": endpoint, "method": method, "duration_ms": duration_ms},
            )

        # Алерты для ошибок
        if status_code >= 500:
            await self.alerts.add_alert(
                AlertLevel.ERROR,
                f"Ошибка сервера: {method} {endpoint} ({status_code})",
                "performance",
                {"endpoint": endpoint, "method": method, "status_code": status_code},
            )

    async def record_database_operation(self, operation: str, table: str, duration_ms: float):
        """Запись метрик операций с БД"""
        labels = {"operation": operation, "table": table}

        await self.metrics.increment_counter("database_operations_total", labels=labels)
        await self.metrics.record_histogram("database_operation_duration_ms", duration_ms, labels=labels)

        # Алерты для медленных операций с БД
        if duration_ms > 1000:  # Более 1 секунды
            await self.alerts.add_alert(
                AlertLevel.WARNING,
                f"Медленная операция с БД: {operation} {table} ({duration_ms:.2f}ms)",
                "database",
                {"operation": operation, "table": table, "duration_ms": duration_ms},
            )

    async def record_external_api_call(self, service: str, endpoint: str, duration_ms: float, success: bool):
        """Запись метрик внешних API"""
        labels = {"service": service, "endpoint": endpoint, "success": str(success)}

        await self.metrics.increment_counter("external_api_calls_total", labels=labels)
        await self.metrics.record_histogram("external_api_call_duration_ms", duration_ms, labels=labels)

        # Алерты для неудачных вызовов
        if not success:
            await self.alerts.add_alert(
                AlertLevel.ERROR,
                f"Ошибка внешнего API: {service} {endpoint}",
                "external_api",
                {"service": service, "endpoint": endpoint, "duration_ms": duration_ms},
            )

    async def record_bot_interaction(self, user_id: int, action: str, success: bool):
        """Запись метрик взаимодействий с ботом"""
        labels = {"action": action, "success": str(success)}

        await self.metrics.increment_counter("bot_interactions_total", labels=labels)

        # Алерты для неудачных взаимодействий
        if not success:
            await self.alerts.add_alert(
                AlertLevel.WARNING,
                f"Неудачное взаимодействие с ботом: {action} (user_id: {user_id})",
                "bot",
                {"user_id": user_id, "action": action},
            )

    async def get_uptime(self) -> timedelta:
        """Получение времени работы"""
        return datetime.now() - self._start_time


class SystemMonitor:
    """Монитор системы"""

    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        self.metrics = metrics_collector
        self.alerts = alert_manager
        self._monitoring_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Запуск мониторинга системы"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitor_loop())
            logger.info("🚀 Системный мониторинг запущен")

    async def stop_monitoring(self):
        """Остановка мониторинга системы"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Системный мониторинг остановлен")

    async def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while True:
            try:
                await self._check_system_resources()
                await asyncio.sleep(60)  # Проверяем каждую минуту
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(60)

    async def _check_system_resources(self):
        """Проверка системных ресурсов"""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.metrics.set_gauge("system_cpu_percent", cpu_percent)

            if cpu_percent > 80:
                await self.alerts.add_alert(
                    AlertLevel.WARNING, f"Высокая загрузка CPU: {cpu_percent:.1f}%", "system", {"cpu_percent": cpu_percent}
                )

            # Memory
            memory = psutil.virtual_memory()
            await self.metrics.set_gauge("system_memory_percent", memory.percent)

            if memory.percent > 85:
                await self.alerts.add_alert(
                    AlertLevel.WARNING,
                    f"Высокое потребление памяти: {memory.percent:.1f}%",
                    "system",
                    {"memory_percent": memory.percent},
                )

            # Disk
            disk = psutil.disk_usage("/")
            await self.metrics.set_gauge("system_disk_percent", disk.percent)

            if disk.percent > 90:
                await self.alerts.add_alert(
                    AlertLevel.CRITICAL,
                    f"Критически мало места на диске: {disk.percent:.1f}%",
                    "system",
                    {"disk_percent": disk.percent},
                )

        except ImportError:
            logger.warning("psutil не установлен, системный мониторинг недоступен")
        except Exception as e:
            logger.error(f"Ошибка проверки системных ресурсов: {e}")


# Глобальные экземпляры
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
performance_monitor = PerformanceMonitor(metrics_collector, alert_manager)
system_monitor = SystemMonitor(metrics_collector, alert_manager)


async def get_monitoring_status() -> Dict[str, Any]:
    """Получение статуса мониторинга"""
    metrics = await metrics_collector.get_metrics()
    recent_alerts = await alert_manager.get_recent_alerts(hours=1)

    return {
        "metrics_count": len(metrics),
        "recent_alerts_count": len(recent_alerts),
        "critical_alerts_count": len([a for a in recent_alerts if a.level == AlertLevel.CRITICAL]),
        "error_alerts_count": len([a for a in recent_alerts if a.level == AlertLevel.ERROR]),
        "warning_alerts_count": len([a for a in recent_alerts if a.level == AlertLevel.WARNING]),
        "uptime": str(performance_monitor.get_uptime()),
    }
