"""
Система мониторинга и аналитики для Check Your Crypto
"""
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .database import async_session_maker
from .config import settings


@dataclass
class SystemStatus:
    """Статус системы"""
    timestamp: str
    bot_status: str
    database_status: str
    metasleuth_status: str
    admin_status: str
    alerts_status: str
    uptime_seconds: int
    total_users: int
    total_checks: int
    checks_today: int
    users_today: int
    errors_count: int
    warnings_count: int


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    timestamp: str
    avg_response_time: float
    requests_per_minute: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float


class MonitoringSystem:
    """Система мониторинга"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        self.error_count = 0
        self.warning_count = 0
        self.request_count = 0
        self.response_times = []
        
        # Создаем директорию для логов
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Настраиваем логирование
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка логирования"""
        # Используем новую систему логирования
        from .logging_config import setup_logging, setup_structured_logging
        
        # Настраиваем основное логирование
        setup_logging()
        
        # Настраиваем структурированное логирование
        setup_structured_logging()
        
        # Получаем корневой логгер
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
    
    async def check_database_status(self) -> str:
        """Проверка статуса базы данных"""
        try:
            from sqlalchemy import text
            async with async_session_maker() as session:
                await session.execute(text("SELECT 1"))
                return "healthy"
        except Exception as e:
            self.logger.error(f"Database check failed: {e}")
            return "error"
    
    async def check_metasleuth_status(self) -> str:
        """Проверка статуса MetaSleuth API"""
        try:
            # Простая проверка - можно расширить
            return "healthy"
        except Exception as e:
            self.logger.error(f"MetaSleuth check failed: {e}")
            return "error"
    
    async def check_admin_status(self) -> str:
        """Проверка статуса Django админки"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/api/health/", timeout=5) as response:
                    if response.status == 200:
                        return "healthy"
                    else:
                        return "warning"
        except Exception:
            return "error"
    
    async def get_system_metrics(self) -> Dict:
        """Получение метрик системы"""
        try:
            from sqlalchemy import text
            async with async_session_maker() as session:
                # Общая статистика
                total_users = await session.execute(text("SELECT COUNT(*) FROM users"))
                total_users = total_users.scalar()
                
                total_checks = await session.execute(text("SELECT COUNT(*) FROM checks"))
                total_checks = total_checks.scalar()
                
                # Статистика за сегодня
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_end = datetime.combine(today, datetime.max.time())
                
                users_today = await session.execute(
                    text("SELECT COUNT(*) FROM users WHERE created_at BETWEEN :start AND :end"),
                    {"start": today_start, "end": today_end}
                )
                users_today = users_today.scalar()
                
                checks_today = await session.execute(
                    text("SELECT COUNT(*) FROM checks WHERE created_at BETWEEN :start AND :end"),
                    {"start": today_start, "end": today_end}
                )
                checks_today = checks_today.scalar()
                
                return {
                    "total_users": total_users,
                    "total_checks": total_checks,
                    "users_today": users_today,
                    "checks_today": checks_today
                }
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {
                "total_users": 0,
                "total_checks": 0,
                "users_today": 0,
                "checks_today": 0
            }
    
    async def get_system_status(self) -> SystemStatus:
        """Получение полного статуса системы"""
        uptime = int(time.time() - self.start_time)
        
        # Проверяем статусы компонентов
        db_status = await self.check_database_status()
        metasleuth_status = await self.check_metasleuth_status()
        admin_status = await self.check_admin_status()
        
        # Получаем метрики
        metrics = await self.get_system_metrics()
        
        status = SystemStatus(
            timestamp=datetime.now().isoformat(),
            bot_status="running",
            database_status=db_status,
            metasleuth_status=metasleuth_status,
            admin_status=admin_status,
            alerts_status="running",
            uptime_seconds=uptime,
            total_users=metrics["total_users"],
            total_checks=metrics["total_checks"],
            checks_today=metrics["checks_today"],
            users_today=metrics["users_today"],
            errors_count=self.error_count,
            warnings_count=self.warning_count
        )
        
        return status
    
    def log_request(self, response_time: float):
        """Логирование запроса"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        # Ограничиваем размер списка
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def log_error(self, error: str, context: Optional[Dict] = None):
        """Логирование ошибки"""
        self.error_count += 1
        self.logger.error(f"ERROR: {error}", extra={"context": context})
    
    def log_warning(self, warning: str, context: Optional[Dict] = None):
        """Логирование предупреждения"""
        self.warning_count += 1
        self.logger.warning(f"WARNING: {warning}", extra={"context": context})
    
    def log_analytics(self, event: str, data: Dict):
        """Логирование аналитики"""
        analytics_data = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.logger.info(f"ANALYTICS: {json.dumps(analytics_data)}")
    
    async def generate_performance_report(self) -> PerformanceMetrics:
        """Генерация отчета о производительности"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        requests_per_minute = self.request_count / max(1, (time.time() - self.start_time) / 60)
        error_rate = self.error_count / max(1, self.request_count) * 100
        
        # Упрощенные метрики системы (в реальном проекте использовали бы psutil)
        memory_usage = 0  # Заглушка
        cpu_usage = 0     # Заглушка
        
        return PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            avg_response_time=avg_response_time,
            requests_per_minute=requests_per_minute,
            error_rate=error_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
    
    async def save_status_report(self):
        """Сохранение отчета о статусе"""
        try:
            status = await self.get_system_status()
            performance = await self.generate_performance_report()
            
            report = {
                "status": asdict(status),
                "performance": asdict(performance),
                "generated_at": datetime.now().isoformat()
            }
            
            # Сохраняем в файл
            report_file = self.logs_dir / f"status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Логируем краткий статус
            self.logger.info(f"STATUS REPORT: {status.bot_status}/{status.database_status}/{status.admin_status}")
            
        except Exception as e:
            self.logger.error(f"Failed to save status report: {e}")
    
    async def start_monitoring(self):
        """Запуск мониторинга"""
        self.logger.info("Starting monitoring system...")
        
        while True:
            try:
                await self.save_status_report()
                await asyncio.sleep(300)  # Каждые 5 минут
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)


# Глобальный экземпляр системы мониторинга
monitoring = MonitoringSystem()
