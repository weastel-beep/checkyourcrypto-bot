#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Telegram API
"""
import asyncio
import logging
from aiogram import Bot
from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_telegram():
    """Тестировать подключение к Telegram API"""
    bot = Bot(token=settings.bot_token)
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"✅ Подключение к Telegram API успешно")
        logger.info(f"🤖 Бот: @{bot_info.username} (ID: {bot_info.id})")
        logger.info(f"📝 Имя: {bot_info.first_name}")
        logger.info(f"🔗 Может присоединяться к группам: {bot_info.can_join_groups}")
        logger.info(f"📢 Может читать сообщения: {bot_info.can_read_all_group_messages}")
        
        # Получаем информацию о webhook
        webhook_info = await bot.get_webhook_info()
        logger.info(f"📋 Webhook URL: {webhook_info.url or 'Не установлен'}")
        logger.info(f"📋 Pending updates: {webhook_info.pending_update_count}")
        
        # Пробуем получить обновления
        try:
            updates = await bot.get_updates(limit=1, timeout=1)
            logger.info(f"✅ Получение обновлений работает, получено: {len(updates)}")
        except Exception as e:
            logger.error(f"❌ Ошибка при получении обновлений: {e}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Telegram API: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_telegram())
