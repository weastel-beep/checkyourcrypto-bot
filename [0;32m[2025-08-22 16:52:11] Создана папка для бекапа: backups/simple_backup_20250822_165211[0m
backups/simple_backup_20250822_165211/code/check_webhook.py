#!/usr/bin/env python3
"""
Скрипт для проверки webhook бота
"""
import asyncio
import logging
from aiogram import Bot
from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_webhook():
    """Проверить webhook бота"""
    bot = Bot(token=settings.bot_token)
    
    try:
        # Получаем информацию о webhook
        webhook_info = await bot.get_webhook_info()
        logger.info(f"📋 Webhook информация:")
        logger.info(f"   URL: {webhook_info.url}")
        logger.info(f"   Has custom certificate: {webhook_info.has_custom_certificate}")
        logger.info(f"   Pending update count: {webhook_info.pending_update_count}")
        logger.info(f"   Last error date: {webhook_info.last_error_date}")
        logger.info(f"   Last error message: {webhook_info.last_error_message}")
        logger.info(f"   Max connections: {webhook_info.max_connections}")
        logger.info(f"   Allowed updates: {webhook_info.allowed_updates}")
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке webhook: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_webhook())
