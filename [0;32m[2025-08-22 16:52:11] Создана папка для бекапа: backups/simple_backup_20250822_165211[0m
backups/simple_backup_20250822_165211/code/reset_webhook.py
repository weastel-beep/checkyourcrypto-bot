#!/usr/bin/env python3
"""
Скрипт для сброса webhook бота
"""
import asyncio
import logging
from aiogram import Bot
from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_webhook():
    """Сбросить webhook бота"""
    bot = Bot(token=settings.bot_token)
    
    try:
        # Удаляем webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook успешно сброшен")
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при сбросе webhook: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(reset_webhook())
