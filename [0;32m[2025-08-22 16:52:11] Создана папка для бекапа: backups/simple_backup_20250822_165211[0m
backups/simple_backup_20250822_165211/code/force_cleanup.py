#!/usr/bin/env python3
"""
Скрипт для принудительной очистки Telegram API
"""
import asyncio
import logging
import requests
import time
from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_cleanup():
    """Принудительная очистка Telegram API"""
    token = settings.bot_token
    base_url = f"https://api.telegram.org/bot{token}"
    
    logger.info("🧹 Начинаем принудительную очистку Telegram API...")
    
    # 1. Удаляем webhook
    try:
        logger.info("1️⃣ Удаляем webhook...")
        webhook_response = requests.get(f"{base_url}/getWebhookInfo", timeout=10)
        webhook_data = webhook_response.json()
        
        if webhook_data.get('ok') and webhook_data['result'].get('url'):
            logger.info(f"⚠️ Найден webhook: {webhook_data['result']['url']}")
            delete_response = requests.post(f"{base_url}/deleteWebhook", timeout=10)
            if delete_response.json().get('ok'):
                logger.info("✅ Webhook удален")
            else:
                logger.warning("⚠️ Не удалось удалить webhook")
        else:
            logger.info("✅ Webhook не установлен")
    except Exception as e:
        logger.error(f"❌ Ошибка при работе с webhook: {e}")
    
    # 2. Очищаем все обновления
    try:
        logger.info("2️⃣ Очищаем обновления...")
        
        # Получаем все обновления
        updates_response = requests.get(f"{base_url}/getUpdates", timeout=10)
        updates_data = updates_response.json()
        
        if updates_data.get('ok') and updates_data['result']:
            logger.info(f"⚠️ Найдено {len(updates_data['result'])} обновлений")
            
            # Получаем ID последнего обновления
            last_update_id = updates_data['result'][-1]['update_id']
            logger.info(f"📋 Последний update_id: {last_update_id}")
            
            # Устанавливаем offset на следующий после последнего
            offset = last_update_id + 1
            logger.info(f"📋 Устанавливаем offset: {offset}")
            
            # Очищаем обновления
            clear_response = requests.get(f"{base_url}/getUpdates?offset={offset}&limit=1", timeout=10)
            if clear_response.json().get('ok'):
                logger.info("✅ Обновления очищены")
            else:
                logger.warning("⚠️ Не удалось очистить обновления")
        else:
            logger.info("✅ Необработанных обновлений нет")
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке обновлений: {e}")
    
    # 3. Ждем и проверяем еще раз
    logger.info("3️⃣ Ждем 5 секунд...")
    await asyncio.sleep(5)
    
    try:
        logger.info("4️⃣ Проверяем состояние после очистки...")
        
        # Проверяем webhook
        webhook_response = requests.get(f"{base_url}/getWebhookInfo", timeout=10)
        webhook_data = webhook_response.json()
        if webhook_data.get('ok'):
            logger.info(f"📋 Webhook URL: {webhook_data['result'].get('url', 'Не установлен')}")
            logger.info(f"📋 Pending updates: {webhook_data['result'].get('pending_update_count', 0)}")
        
        # Проверяем обновления
        updates_response = requests.get(f"{base_url}/getUpdates", timeout=10)
        updates_data = updates_response.json()
        if updates_data.get('ok'):
            logger.info(f"📋 Доступных обновлений: {len(updates_data['result'])}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке состояния: {e}")
    
    logger.info("✅ Принудительная очистка завершена")

if __name__ == "__main__":
    asyncio.run(force_cleanup())
