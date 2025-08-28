"""
Middleware для автоматического сбора метрик
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from common.monitoring import performance_monitor

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware для сбора метрик HTTP запросов"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с сбором метрик"""
        start_time = time.time()

        try:
            # Обрабатываем запрос
            response = await call_next(request)

            # Вычисляем время выполнения
            duration_ms = (time.time() - start_time) * 1000

            # Собираем метрики
            await performance_monitor.record_request(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            return response

        except Exception as e:
            # В случае ошибки также записываем метрики
            duration_ms = (time.time() - start_time) * 1000

            await performance_monitor.record_request(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=500,  # Внутренняя ошибка сервера
                duration_ms=duration_ms,
            )

            # Логируем ошибку
            logger.error(f"Ошибка в middleware: {e}")
            raise


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с логированием"""
        start_time = time.time()

        # Логируем входящий запрос
        logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")

        try:
            # Обрабатываем запрос
            response = await call_next(request)

            # Вычисляем время выполнения
            duration_ms = (time.time() - start_time) * 1000

            # Логируем результат
            status_emoji = "✅" if response.status_code < 400 else "❌"
            logger.info(f"{status_emoji} {request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms)")

            return response

        except Exception as e:
            # В случае ошибки логируем её
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"💥 {request.method} {request.url.path} - ERROR ({duration_ms:.2f}ms): {e}")
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware для безопасности"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с проверками безопасности"""

        # Проверяем User-Agent
        user_agent = request.headers.get("user-agent", "")
        
        # Исключение для Telegram webhook
        if request.url.path == "/webhook" and request.client.host in ["91.108.5.133", "91.108.4.0/22"]:
            # Telegram IP диапазон - пропускаем
            pass
        elif not user_agent or user_agent.lower() in ["bot", "crawler", "spider"]:
            logger.warning(f"🚫 Подозрительный User-Agent: {user_agent} от {request.client.host}")
            return Response(content="Access denied", status_code=403, media_type="text/plain")

        # Проверяем количество запросов (простая защита от DDoS)
        # TODO: добавить более сложную логику с Redis

        # Обрабатываем запрос
        response = await call_next(request)

        # Добавляем security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки ошибок"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с обработкой ошибок"""
        try:
            return await call_next(request)

        except Exception as e:
            # Логируем ошибку
            logger.error(f"💥 Необработанная ошибка в {request.method} {request.url.path}: {e}")

            # Возвращаем стандартную ошибку
            return Response(content="Internal Server Error", status_code=500, media_type="text/plain")
