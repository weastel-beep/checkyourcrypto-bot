"""
Альтернативная версия main.py с использованием webhook
"""
import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from common.config import settings
from common.database import init_db, close_db
from common.monitoring import monitoring
from .handlers import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/main.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Настройка логирования для SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('aiogram').setLevel(logging.INFO)

async def cleanup_telegram_api():
    """Принудительная очистка Telegram API перед запуском"""
    try:
        import requests
        
        # Получаем токен
        token = settings.bot_token
        base_url = f"https://api.telegram.org/bot{token}"
        
        logger.info("🧹 Принудительная очистка Telegram API...")
        
        # 1. Удаляем webhook
        try:
            webhook_response = requests.get(f"{base_url}/getWebhookInfo", timeout=10)
            webhook_data = webhook_response.json()
            
            if webhook_data.get('ok') and webhook_data['result'].get('url'):
                logger.info(f"⚠️ Удаляем webhook: {webhook_data['result']['url']}")
                delete_response = requests.post(f"{base_url}/deleteWebhook", timeout=10)
                if delete_response.json().get('ok'):
                    logger.info("✅ Webhook удален")
                else:
                    logger.warning("⚠️ Не удалось удалить webhook")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при работе с webhook: {e}")
        
        # 2. Очищаем обновления
        try:
            updates_response = requests.get(f"{base_url}/getUpdates", timeout=10)
            updates_data = updates_response.json()
            
            if updates_data.get('ok') and updates_data['result']:
                logger.info(f"⚠️ Очищаем {len(updates_data['result'])} обновлений")
                last_update_id = updates_data['result'][-1]['update_id']
                clear_response = requests.get(f"{base_url}/getUpdates?offset={last_update_id + 1}", timeout=10)
                if clear_response.json().get('ok'):
                    logger.info("✅ Обновления очищены")
                else:
                    logger.warning("⚠️ Не удалось очистить обновления")
            else:
                logger.info("✅ Необработанных обновлений нет")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при очистке обновлений: {e}")
        
        # 3. Ждем немного для завершения всех операций
        await asyncio.sleep(2)
        
        logger.info("✅ Очистка Telegram API завершена")
        
    except ImportError:
        logger.warning("⚠️ Модуль requests не установлен, пропускаем очистку")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка очистки Telegram API: {e}")

async def main():
    """Основная функция запуска бота с webhook"""
    logger.info("🚀 Запуск бота Check Your Crypto (webhook mode)")
    
    # Инициализация базы данных
    await init_db()
    
    # Принудительная очистка Telegram API
    await cleanup_telegram_api()
    
    # Создание бота и диспетчера
    bot = Bot(token=settings.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем роутеры
    dp.include_router(router)
    
    # Настройка webhook
    webhook_path = f"/webhook/{settings.bot_token}"
    webhook_url = f"https://your-domain.com{webhook_path}"  # Замените на ваш домен
    
    # Создаем aiohttp приложение
    app = web.Application()
    
    # Настраиваем webhook
    setup_application(app, dp, path=webhook_path)
    
    # Запускаем мониторинг в фоне
    monitoring_task = asyncio.create_task(monitoring.start_monitoring())
    
    try:
        logger.info("Бот запущен и готов к работе (webhook mode)")
        
        # Логируем запуск
        bot_info = await bot.get_me()
        monitoring.log_analytics("bot_started", {
            "bot_id": bot_info.id,
            "bot_username": bot_info.username,
            "mode": "webhook"
        })
        
        # Устанавливаем webhook
        await bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook установлен: {webhook_url}")
        
        # Запускаем web сервер
        web.run_app(app, host="0.0.0.0", port=8000)
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
        monitoring.log_error(f"Bot error: {e}")
    finally:
        # Удаляем webhook
        try:
            await bot.delete_webhook()
            logger.info("✅ Webhook удален")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при удалении webhook: {e}")
        
        # Останавливаем мониторинг
        monitoring_task.cancel()
        await close_db()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
