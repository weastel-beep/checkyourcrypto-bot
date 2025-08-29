"""
Главный файл Telegram бота Check Your Crypto
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json

from common.database import init_db, close_db
from common.config import settings
from bot.handlers import handle_all_messages, cmd_start
from bot.health import router as health_router
from bot.monitoring_endpoints import router as monitoring_router
from common.api.unified import router as unified_router
from bot.middleware import MetricsMiddleware, LoggingMiddleware, SecurityMiddleware, ErrorHandlingMiddleware

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск
    logger.info("🚀 Запуск приложения...")

    # Инициализация базы данных
    await init_db()
    logger.info("✅ База данных инициализирована")

    # Создание приложения бота
    application = Application.builder().token(settings.bot_token).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

    logger.info("✅ Обработчики зарегистрированы")

    # Инициализация приложения
    await application.initialize()
    logger.info("✅ Приложение инициализировано")

    # Настройка webhook
    webhook_url = f"https://{settings.heroku_app_name}.herokuapp.com/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook настроен: {webhook_url}")

    # Сохраняем приложение в состоянии
    app.state.application = application

    yield

    # Завершение
    logger.info("🛑 Завершение приложения...")

    # Удаление webhook
    await application.bot.delete_webhook()
    logger.info("✅ Webhook удален")

    # Закрытие базы данных
    await close_db()
    logger.info("✅ База данных закрыта")


# Создание FastAPI приложения
app = FastAPI(
    title="Check Your Crypto Bot",
    description="Telegram бот для проверки криптовалютных адресов",
    version="2.0.0",
    lifespan=lifespan,
)

# Подключаем health check router
app.include_router(health_router)

# Подключаем monitoring router
app.include_router(monitoring_router)

# Подключаем единый API router (для внутренних нужд бота)
app.include_router(unified_router)

# Добавляем middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)


@app.post("/webhook")
async def webhook_handler(request: Request) -> dict:
    """Обработчик webhook от Telegram"""
    try:
        # Получаем JSON данные
        data = await request.json()
        
        # Создаем Update объект из JSON с ботом
        application = app.state.application
        update = Update.de_json(data, bot=application.bot)
        
        application = app.state.application

        # Обрабатываем обновление
        await application.process_update(update)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Ошибка в webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "Check Your Crypto Bot API", "version": "2.0.0", "status": "running"}


# Health check endpoint теперь обрабатывается через health_router


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Запуск бота на порту {port}...")
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port, log_level="info")
