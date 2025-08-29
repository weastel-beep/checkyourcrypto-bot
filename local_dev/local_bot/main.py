#!/usr/bin/env python3
"""
Локальная версия бота для быстрого тестирования
Использует общую базу данных с продакшеном
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from common.database import async_session_maker
from common.config import get_settings
from bot.handlers.main_handler import MainHandler
from bot.middleware import LoggingMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalBot:
    def __init__(self):
        self.settings = get_settings()
        self.application = None
        self.main_handler = MainHandler()
        
    async def start_command(self, update: Update, context):
        """Обработчик команды /start"""
        await self.main_handler.handle_start_command(update, context)
    
    async def handle_message(self, update: Update, context):
        """Обработчик всех сообщений"""
        await self.main_handler.handle(update, context)
    
    async def error_handler(self, update: Update, context):
        """Обработчик ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Сообщения
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def run(self):
        """Запуск бота"""
        try:
            # Создаем приложение
            self.application = Application.builder().token(self.settings.BOT_TOKEN).build()
            
            # Добавляем middleware
            self.application.add_handler(LoggingMiddleware())
            
            # Настраиваем обработчики
            self.setup_handlers()
            
            logger.info("🤖 Локальный бот запускается...")
            logger.info(f"🔧 Режим: ЛОКАЛЬНАЯ РАЗРАБОТКА")
            logger.info(f"🌐 API URL: {self.settings.API_BASE_URL}")
            logger.info(f"🗄️ Database: {self.settings.DATABASE_URL}")
            
            # Запускаем бота в режиме polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Локальный бот запущен и готов к работе!")
            logger.info("📝 Отправьте /start боту для тестирования")
            
            # Держим бота запущенным
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска локального бота: {e}")
            raise
        finally:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()

async def main():
    """Главная функция"""
    bot = LocalBot()
    await bot.run()

if __name__ == "__main__":
    # Устанавливаем переменные окружения для локальной разработки
    os.environ.setdefault("ENVIRONMENT", "local")
    os.environ.setdefault("API_BASE_URL", "http://localhost:8001")
    
    # Запускаем бота
    asyncio.run(main())
