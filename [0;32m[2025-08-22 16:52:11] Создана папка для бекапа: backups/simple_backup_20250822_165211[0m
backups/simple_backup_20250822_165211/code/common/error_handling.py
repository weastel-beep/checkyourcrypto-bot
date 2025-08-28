"""
Система обработки ошибок для Check Your Crypto
"""
import asyncio
import logging
import time
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from dataclasses import dataclass
from enum import Enum
import traceback

from .logging_config import log_error_with_context


class ErrorType(Enum):
    """Типы ошибок"""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Уровни критичности ошибок"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Контекст ошибки"""
    error_type: ErrorType
    severity: ErrorSeverity
    user_id: Optional[int] = None
    operation: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    additional_data: Optional[Dict] = None


class RetryConfig:
    """Конфигурация retry логики"""
    
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_backoff: bool = True,
                 retry_on_exceptions: tuple = (Exception,)):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.retry_on_exceptions = retry_on_exceptions
    
    def get_delay(self, attempt: int) -> float:
        """Получить задержку для попытки"""
        if self.exponential_backoff:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay * (attempt + 1)
        
        return min(delay, self.max_delay)


class ErrorHandler:
    """Обработчик ошибок"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_stats = {
            error_type: {"count": 0, "last_occurrence": None}
            for error_type in ErrorType
        }
    
    def handle_error(self, 
                    error: Exception, 
                    context: ErrorContext,
                    reraise: bool = True) -> None:
        """Обработка ошибки"""
        
        # Логируем ошибку
        self._log_error(error, context)
        
        # Обновляем статистику
        self._update_stats(context.error_type)
        
        # Применяем стратегии обработки
        self._apply_error_strategy(error, context)
        
        # Повторно вызываем исключение если нужно
        if reraise:
            raise error
    
    def _log_error(self, error: Exception, context: ErrorContext) -> None:
        """Логирование ошибки"""
        error_data = {
            "error_type": context.error_type.value,
            "severity": context.severity.value,
            "user_id": context.user_id,
            "operation": context.operation,
            "retry_count": context.retry_count,
            "additional_data": context.additional_data
        }
        
        log_error_with_context(error, error_data)
    
    def _update_stats(self, error_type: ErrorType) -> None:
        """Обновление статистики ошибок"""
        self.error_stats[error_type]["count"] += 1
        self.error_stats[error_type]["last_occurrence"] = time.time()
    
    def _apply_error_strategy(self, error: Exception, context: ErrorContext) -> None:
        """Применение стратегии обработки ошибки"""
        
        if context.severity == ErrorSeverity.CRITICAL:
            self._handle_critical_error(error, context)
        elif context.severity == ErrorSeverity.HIGH:
            self._handle_high_severity_error(error, context)
        elif context.severity == ErrorSeverity.MEDIUM:
            self._handle_medium_severity_error(error, context)
        else:
            self._handle_low_severity_error(error, context)
    
    def _handle_critical_error(self, error: Exception, context: ErrorContext) -> None:
        """Обработка критических ошибок"""
        # Отправляем уведомление администратору
        self._send_admin_alert(f"Critical error: {error}", context)
        
        # Останавливаем операцию
        self.logger.critical(f"Critical error occurred: {error}")
    
    def _handle_high_severity_error(self, error: Exception, context: ErrorContext) -> None:
        """Обработка ошибок высокой критичности"""
        # Логируем детально
        self.logger.error(f"High severity error: {error}")
        
        # Отправляем уведомление если много ошибок
        if self.error_stats[context.error_type]["count"] > 10:
            self._send_admin_alert(f"Multiple high severity errors: {error}", context)
    
    def _handle_medium_severity_error(self, error: Exception, context: ErrorContext) -> None:
        """Обработка ошибок средней критичности"""
        self.logger.warning(f"Medium severity error: {error}")
    
    def _handle_low_severity_error(self, error: Exception, context: ErrorContext) -> None:
        """Обработка ошибок низкой критичности"""
        self.logger.info(f"Low severity error: {error}")
    
    def _send_admin_alert(self, message: str, context: ErrorContext) -> None:
        """Отправка уведомления администратору"""
        # TODO: Реализовать отправку уведомлений
        self.logger.warning(f"Admin alert: {message}")
    
    def get_error_stats(self) -> Dict:
        """Получение статистики ошибок"""
        return self.error_stats


# Глобальный обработчик ошибок
error_handler = ErrorHandler()


def retry_on_error(retry_config: Optional[RetryConfig] = None,
                   error_context: Optional[ErrorContext] = None):
    """Декоратор для retry логики"""
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_config.retry_on_exceptions as e:
                    last_error = e
                    
                    if attempt < retry_config.max_retries:
                        delay = retry_config.get_delay(attempt)
                        
                        # Создаем контекст ошибки
                        context = error_context or ErrorContext(
                            error_type=ErrorType.UNKNOWN,
                            severity=ErrorSeverity.MEDIUM,
                            retry_count=attempt
                        )
                        context.retry_count = attempt
                        
                        # Логируем попытку retry
                        error_handler.logger.warning(
                            f"Retry attempt {attempt + 1}/{retry_config.max_retries} "
                            f"for {func.__name__} after {delay}s: {e}"
                        )
                        
                        await asyncio.sleep(delay)
                    else:
                        # Последняя попытка не удалась
                        if error_context:
                            error_handler.handle_error(e, error_context)
                        raise e
            
            raise last_error
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_config.retry_on_exceptions as e:
                    last_error = e
                    
                    if attempt < retry_config.max_retries:
                        delay = retry_config.get_delay(attempt)
                        
                        # Создаем контекст ошибки
                        context = error_context or ErrorContext(
                            error_type=ErrorType.UNKNOWN,
                            severity=ErrorSeverity.MEDIUM,
                            retry_count=attempt
                        )
                        context.retry_count = attempt
                        
                        # Логируем попытку retry
                        error_handler.logger.warning(
                            f"Retry attempt {attempt + 1}/{retry_config.max_retries} "
                            f"for {func.__name__} after {delay}s: {e}"
                        )
                        
                        time.sleep(delay)
                    else:
                        # Последняя попытка не удалась
                        if error_context:
                            error_handler.handle_error(e, error_context)
                        raise e
            
            raise last_error
        
        # Возвращаем асинхронную или синхронную обертку
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def handle_network_errors(func: Callable) -> Callable:
    """Декоратор для обработки сетевых ошибок"""
    network_retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_backoff=True,
        retry_on_exceptions=(ConnectionError, TimeoutError, OSError)
    )
    
    return retry_on_error(network_retry_config)(func)


def handle_api_errors(func: Callable) -> Callable:
    """Декоратор для обработки API ошибок"""
    api_retry_config = RetryConfig(
        max_retries=2,
        base_delay=2.0,
        max_delay=60.0,
        exponential_backoff=True,
        retry_on_exceptions=(Exception,)
    )
    
    return retry_on_error(api_retry_config)(func)


def graceful_degradation(fallback_value: Any = None, 
                        fallback_func: Optional[Callable] = None):
    """Декоратор для graceful degradation"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler.logger.warning(
                    f"Graceful degradation for {func.__name__}: {e}"
                )
                
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                return fallback_value
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.logger.warning(
                    f"Graceful degradation for {func.__name__}: {e}"
                )
                
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                return fallback_value
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit Breaker паттерн"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Вызов функции с circuit breaker"""
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Обработка успешного вызова"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Обработка неудачного вызова"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        elif self.state == "HALF_OPEN":
            # Если в HALF_OPEN состоянии произошла ошибка, возвращаемся в OPEN
            self.state = "OPEN"


def create_user_friendly_error_message(error: Exception, 
                                     operation: str) -> str:
    """Создание пользовательского сообщения об ошибке"""
    
    error_messages = {
        "ConnectionError": "Проблема с подключением к серверу. Попробуйте позже.",
        "TimeoutError": "Превышено время ожидания. Попробуйте еще раз.",
        "ValueError": "Некорректные данные. Проверьте введенную информацию.",
        "KeyError": "Отсутствуют необходимые данные. Обратитесь к администратору.",
        "PermissionError": "Недостаточно прав для выполнения операции.",
        "FileNotFoundError": "Файл не найден. Проверьте настройки.",
        "json.JSONDecodeError": "Ошибка обработки данных. Попробуйте позже.",
    }
    
    error_type = type(error).__name__
    
    if error_type in error_messages:
        return error_messages[error_type]
    
    # Общее сообщение для неизвестных ошибок
    return f"Произошла ошибка при выполнении операции '{operation}'. Попробуйте позже."


def log_and_continue(func: Callable) -> Callable:
    """Декоратор для логирования ошибок без прерывания выполнения"""
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_handler.logger.error(f"Error in {func.__name__}: {e}")
            return None
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_handler.logger.error(f"Error in {func.__name__}: {e}")
            return None
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
