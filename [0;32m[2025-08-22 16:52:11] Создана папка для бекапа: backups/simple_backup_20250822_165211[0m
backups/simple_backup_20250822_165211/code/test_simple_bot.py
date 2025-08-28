#!/usr/bin/env python3
"""
Простой тестовый бот для проверки логики
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Это тестовый бот. Работает!")

@router.message(Command("test"))
async def cmd_test(message: Message):
    """Обработчик команды /test"""
    await message.answer("Тест работает! Бот функционирует нормально.")

async def main():
    """Основная функция"""
    # Используем тестовый токен (замените на свой)
    bot = Bot(token="YOUR_TEST_BOT_TOKEN")  # Замените на тестовый токен
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем роутер
    dp.include_router(router)
    
    try:
        logger.info("🚀 Запуск тестового бота")
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
        
        # Запускаем polling
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
