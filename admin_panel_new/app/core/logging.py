"""
Улучшенная система логирования для админки
"""
import logging
import time
import uuid
import json
import os
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional
import traceback

# Настройка базового логирования
def setup_logging():
    """Настройка структурированного логирования"""
    
    # Создаем форматтер для структурированных логов
    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Добавляем дополнительные поля если есть
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'duration'):
                log_entry['duration'] = record.duration
            if hasattr(record, 'extra_data'):
                log_entry['extra_data'] = record.extra_data
            
            # Добавляем exception info если есть
            if record.exc_info:
                log_entry['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': traceback.format_exception(*record.exc_info)
                }
            
            return json.dumps(log_entry, ensure_ascii=False)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Очищаем существующие handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler для ошибок
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    error_handler = logging.FileHandler('logs/errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(error_handler)
    
    # File handler для всех логов
    all_handler = logging.FileHandler('logs/admin_panel.log')
    all_handler.setLevel(logging.INFO)
    all_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(all_handler)
    
    return root_logger

# Создаем логгер для приложения
logger = logging.getLogger(__name__)

class RequestLogger:
    """Логгер для HTTP запросов"""
    
    def __init__(self, request_id: str = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.logger = logging.getLogger(f"{__name__}.request")
    
    def log_request_start(self, method: str, url: str, user_id: str = None):
        """Логирование начала запроса"""
        extra = {
            'request_id': self.request_id,
            'method': method,
            'url': url,
            'user_id': user_id
        }
        self.logger.info(f"Request started: {method} {url}", extra=extra)
    
    def log_request_end(self, status_code: int, duration: float = None):
        """Логирование завершения запроса"""
        if duration is None:
            duration = time.time() - self.start_time
        
        extra = {
            'request_id': self.request_id,
            'status_code': status_code,
            'duration': f"{duration:.3f}s"
        }
        
        if status_code >= 400:
            self.logger.error(f"Request failed: {status_code}", extra=extra)
        else:
            self.logger.info(f"Request completed: {status_code}", extra=extra)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Логирование ошибки"""
        extra = {
            'request_id': self.request_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        self.logger.error(f"Request error: {error}", extra=extra, exc_info=True)

def log_performance(func):
    """Декоратор для логирования производительности функций"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Получаем логгер для функции
        func_logger = logging.getLogger(f"{__name__}.{func.__name__}")
        
        try:
            # Логируем начало выполнения
            func_logger.info(f"Function {func.__name__} started", extra={
                'request_id': request_id,
                'function': func.__name__
            })
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Вычисляем время выполнения
            execution_time = time.time() - start_time
            
            # Логируем успешное завершение
            func_logger.info(f"Function {func.__name__} completed", extra={
                'request_id': request_id,
                'function': func.__name__,
                'duration': f"{execution_time:.3f}s"
            })
            
            return result
            
        except Exception as e:
            # Вычисляем время выполнения до ошибки
            execution_time = time.time() - start_time
            
            # Логируем ошибку
            func_logger.error(f"Function {func.__name__} failed", extra={
                'request_id': request_id,
                'function': func.__name__,
                'duration': f"{execution_time:.3f}s",
                'error_type': type(e).__name__,
                'error_message': str(e)
            }, exc_info=True)
            
            raise
    
    return wrapper

def log_database_operation(operation: str, table: str = None, duration: float = None):
    """Логирование операций с базой данных"""
    extra = {
        'operation': operation,
        'table': table,
        'duration': f"{duration:.3f}s" if duration else None
    }
    
    logger.info(f"Database operation: {operation}", extra=extra)

def log_api_call(endpoint: str, method: str, status_code: int, duration: float = None, user_id: str = None):
    """Логирование API вызовов"""
    extra = {
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'duration': f"{duration:.3f}s" if duration else None,
        'user_id': user_id
    }
    
    if status_code >= 400:
        logger.error(f"API call failed: {method} {endpoint} - {status_code}", extra=extra)
    else:
        logger.info(f"API call: {method} {endpoint} - {status_code}", extra=extra)

def log_user_action(action: str, user_id: str, details: Dict[str, Any] = None):
    """Логирование действий пользователя"""
    extra = {
        'action': action,
        'user_id': user_id,
        'details': details or {}
    }
    
    logger.info(f"User action: {action}", extra=extra)

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None):
    """Логирование событий безопасности"""
    extra = {
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        'details': details or {}
    }
    
    logger.warning(f"Security event: {event_type}", extra=extra)

# Инициализируем логирование при импорте модуля
setup_logging()
