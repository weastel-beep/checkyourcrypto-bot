"""
Исправленная версия main.py с улучшенной логикой polling
"""
import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

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
        
        # 2. Очищаем обновления с принудительным offset
        try:
            # Получаем все обновления
            updates_response = requests.get(f"{base_url}/getUpdates", timeout=10)
            updates_data = updates_response.json()
            
            if updates_data.get('ok') and updates_data['result']:
                logger.info(f"⚠️ Очищаем {len(updates_data['result'])} обновлений")
                last_update_id = updates_data['result'][-1]['update_id']
                
                # Устанавливаем offset на следующий после последнего
                offset = last_update_id + 1
                clear_response = requests.get(f"{base_url}/getUpdates?offset={offset}&limit=1", timeout=10)
                
                if clear_response.json().get('ok'):
                    logger.info(f"✅ Обновления очищены, установлен offset: {offset}")
                else:
                    logger.warning("⚠️ Не удалось очистить обновления")
            else:
                logger.info("✅ Необработанных обновлений нет")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при очистке обновлений: {e}")
        
        # 3. Ждем немного для завершения всех операций
        await asyncio.sleep(3)
        
        logger.info("✅ Очистка Telegram API завершена")
        
    except ImportError:
        logger.warning("⚠️ Модуль requests не установлен, пропускаем очистку")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка очистки Telegram API: {e}")

async def setup_bot_commands(bot: Bot):
    """Настройка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="menu", description="📋 Главное меню"),
        BotCommand(command="help", description="❓ Помощь"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Команды бота настроены")

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск бота Check Your Crypto (исправленная версия)")
    
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
    
    # Запускаем мониторинг в фоне
    monitoring_task = asyncio.create_task(monitoring.start_monitoring())
    
    try:
        logger.info("Бот запущен и готов к работе")
        
        # Настраиваем команды бота
        await setup_bot_commands(bot)
        
        # Логируем запуск
        bot_info = await bot.get_me()
        monitoring.log_analytics("bot_started", {
            "bot_id": bot_info.id,
            "bot_username": bot_info.username,
            "mode": "polling_fixed"
        })
        
        # Запускаем polling с дополнительными параметрами
        await dp.start_polling(
            bot,
            polling_timeout=30,
            skip_updates=True,  # Пропускаем старые обновления
            allowed_updates=["message", "callback_query", "inline_query"]
        )
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
        monitoring.log_error(f"Bot error: {e}")
    finally:
        # Останавливаем мониторинг
        monitoring_task.cancel()
        await close_db()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
