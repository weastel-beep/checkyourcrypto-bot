"""
Обработка ошибок, retry механизмы и circuit breaker паттерн
"""
import asyncio
import logging
import time
from typing import Callable, Any, Optional, TypeVar, Awaitable
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Состояния circuit breaker"""

    CLOSED = "closed"  # Нормальная работа
    OPEN = "open"  # Блокировка запросов
    HALF_OPEN = "half_open"  # Тестовые запросы


class CircuitBreaker:
    """Circuit breaker паттерн для защиты от каскадных сбоев"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0, expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Выполнить функцию с circuit breaker"""

        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("🔄 Circuit breaker переходит в HALF_OPEN состояние")
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker открыт - запрос заблокирован")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Обработка успешного запроса"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.debug("✅ Circuit breaker: успешный запрос")

    def _on_failure(self):
        """Обработка неудачного запроса"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"⚠️ Circuit breaker открыт после {self.failure_count} неудач")
        else:
            logger.warning(f"⚠️ Circuit breaker: неудача {self.failure_count}/{self.failure_threshold}")


def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """Декоратор для retry логики"""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        logger.error(f"❌ Финальная попытка {attempt + 1}/{max_attempts} не удалась: {e}")
                        raise e

                    wait_time = delay * (backoff**attempt)
                    logger.warning(f"⚠️ Попытка {attempt + 1}/{max_attempts} не удалась: {e}. Повтор через {wait_time:.1f}с")

                    await asyncio.sleep(wait_time)

            raise last_exception

        return wrapper

    return decorator


class RetryConfig:
    """Конфигурация для retry механизмов"""

    # HTTP запросы
    HTTP_MAX_ATTEMPTS = 3
    HTTP_DELAY = 1.0
    HTTP_BACKOFF = 2.0
    HTTP_TIMEOUT = 30.0

    # База данных
    DB_MAX_ATTEMPTS = 3
    DB_DELAY = 0.5
    DB_BACKOFF = 1.5

    # Telegram API
    TELEGRAM_MAX_ATTEMPTS = 3
    TELEGRAM_DELAY = 2.0
    TELEGRAM_BACKOFF = 2.0


# Глобальные circuit breakers
http_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0, expected_exception=(Exception,))

db_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0, expected_exception=(Exception,))

telegram_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=120.0, expected_exception=(Exception,))


def get_retry_decorator(service_type: str = "http"):
    """Получить retry декоратор для конкретного типа сервиса"""
    if service_type == "http":
        return async_retry(
            max_attempts=RetryConfig.HTTP_MAX_ATTEMPTS, delay=RetryConfig.HTTP_DELAY, backoff=RetryConfig.HTTP_BACKOFF
        )
    elif service_type == "db":
        return async_retry(
            max_attempts=RetryConfig.DB_MAX_ATTEMPTS, delay=RetryConfig.DB_DELAY, backoff=RetryConfig.DB_BACKOFF
        )
    elif service_type == "telegram":
        return async_retry(
            max_attempts=RetryConfig.TELEGRAM_MAX_ATTEMPTS,
            delay=RetryConfig.TELEGRAM_DELAY,
            backoff=RetryConfig.TELEGRAM_BACKOFF,
        )
    else:
        return async_retry()


class ErrorHandler:
    """Централизованная обработка ошибок"""

    @staticmethod
    def handle_api_error(error: Exception, context: str = "") -> str:
        """Обработать ошибку API и вернуть понятное сообщение"""
        error_msg = str(error).lower()

        if "timeout" in error_msg or "timed out" in error_msg:
            return f"⏰ Таймаут запроса{context}. Попробуйте позже."

        elif "connection" in error_msg or "network" in error_msg:
            return f"🌐 Проблема с сетью{context}. Проверьте подключение."

        elif "rate limit" in error_msg or "too many requests" in error_msg:
            return f"🚫 Слишком много запросов{context}. Подождите немного."

        elif "unauthorized" in error_msg or "forbidden" in error_msg:
            return f"🔒 Ошибка авторизации{context}. Обратитесь к администратору."

        elif "not found" in error_msg or "404" in error_msg:
            return f"🔍 Ресурс не найден{context}."

        else:
            return f"❌ Произошла ошибка{context}: {str(error)[:100]}"

    @staticmethod
    def log_error(error: Exception, context: str = "", user_id: Optional[int] = None):
        """Логировать ошибку с контекстом"""
        user_info = f" (user_id: {user_id})" if user_id else ""
        logger.error(f"❌ {context}{user_info}: {error}")

        # Для критических ошибок можно добавить уведомления
        if "critical" in context.lower():
            logger.critical(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: {context}{user_info}: {error}")


# Утилиты для работы с таймаутами
async def with_timeout(coro: Awaitable[T], timeout: float) -> T:
    """Выполнить корутину с таймаутом"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Операция не завершена за {timeout} секунд")


def create_timeout_decorator(timeout: float):
    """Создать декоратор с таймаутом"""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await with_timeout(func(*args, **kwargs), timeout)

        return wrapper

    return decorator
