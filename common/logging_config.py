# Конфигурация логирования для Check Your Crypto
import logging
import logging.handlers
from pathlib import Path
import os
from datetime import datetime


def setup_logging():
    """Настройка логирования с ротацией"""
    # Создаем директорию для логов
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Основной лог файл с ротацией
    main_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "main.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    main_handler.setLevel(logging.INFO)
    main_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    main_handler.setFormatter(main_formatter)

    # Лог ошибок с ротацией
    error_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "errors.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(main_formatter)

    # Лог аналитики с ротацией
    analytics_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "analytics.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    analytics_handler.setLevel(logging.INFO)
    analytics_formatter = logging.Formatter("%(asctime)s - ANALYTICS - %(message)s")
    analytics_handler.setFormatter(analytics_formatter)

    # Лог производительности
    performance_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "performance.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
    )
    performance_handler.setLevel(logging.INFO)
    performance_formatter = logging.Formatter("%(asctime)s - PERFORMANCE - %(message)s")
    performance_handler.setFormatter(performance_formatter)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(analytics_handler)
    root_logger.addHandler(performance_handler)
    root_logger.setLevel(logging.INFO)

    # Отключаем DEBUG логи для внешних библиотек
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    return root_logger


def setup_structured_logging():
    """Настройка структурированного логирования"""
    import json

    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            # Добавляем дополнительные поля если есть
            if hasattr(record, "user_id"):
                log_entry["user_id"] = record.user_id
            if hasattr(record, "request_id"):
                log_entry["request_id"] = record.request_id
            if hasattr(record, "response_time"):
                log_entry["response_time"] = record.response_time

            return json.dumps(log_entry)

    # Создаем структурированный лог
    logs_dir = Path("logs")
    structured_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "structured.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    structured_handler.setLevel(logging.INFO)
    structured_handler.setFormatter(StructuredFormatter())

    # Добавляем к корневому логгеру
    root_logger = logging.getLogger()
    root_logger.addHandler(structured_handler)

    return structured_handler


def setup_console_logging():
    """Настройка консольного логирования для разработки"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Красивый форматтер для консоли
    console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_formatter)

    # Добавляем только в режиме разработки
    if os.getenv("DEBUG", "False").lower() == "true":
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)

    return console_handler


def log_performance(operation: str, duration: float, **kwargs):
    """Логирование производительности"""
    logger = logging.getLogger("performance")

    log_data = {"operation": operation, "duration": duration, "duration_ms": round(duration * 1000, 2)}
    log_data.update(kwargs)

    logger.info(f"PERFORMANCE: {operation} took {duration:.3f}s", extra=log_data)


def log_user_action(user_id: int, action: str, **kwargs):
    """Логирование действий пользователя"""
    logger = logging.getLogger("user_actions")

    log_data = {"user_id": user_id, "action": action}
    log_data.update(kwargs)

    logger.info(f"USER_ACTION: {action}", extra=log_data)


def log_api_call(api_name: str, endpoint: str, duration: float, status_code: int = None, **kwargs):
    """Логирование API вызовов"""
    logger = logging.getLogger("api_calls")

    log_data = {"api_name": api_name, "endpoint": endpoint, "duration": duration, "status_code": status_code}
    log_data.update(kwargs)

    logger.info(f"API_CALL: {api_name} {endpoint} {duration:.3f}s", extra=log_data)


def log_error_with_context(error: Exception, context: dict = None):
    """Логирование ошибок с контекстом"""
    logger = logging.getLogger("errors")

    error_data = {"error_type": type(error).__name__, "error_message": str(error), "context": context or {}}

    logger.error(f"ERROR: {type(error).__name__}: {error}", extra=error_data)


def get_log_stats():
    """Получение статистики логов"""
    logs_dir = Path("logs")
    stats = {}

    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            if log_file.exists():
                size_mb = log_file.stat().st_size / (1024 * 1024)
                stats[log_file.name] = {"size_mb": round(size_mb, 2), "lines": sum(1 for _ in open(log_file))}

    return stats


def cleanup_old_logs():
    """Очистка старых логов"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return

    import time

    current_time = time.time()
    max_age = 30 * 24 * 60 * 60  # 30 дней

    cleaned_count = 0
    for log_file in logs_dir.glob("*.log.*"):
        if log_file.stat().st_mtime < (current_time - max_age):
            log_file.unlink()
            cleaned_count += 1

    return cleaned_count
