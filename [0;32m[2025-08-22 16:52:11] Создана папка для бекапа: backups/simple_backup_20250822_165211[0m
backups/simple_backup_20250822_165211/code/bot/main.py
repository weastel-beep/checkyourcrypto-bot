"""
Основной файл для запуска Telegram-бота Check Your Crypto
"""
import asyncio
import logging
import time
import traceback
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from common.config import settings
from common.database import init_db, close_db
from common.monitoring import monitoring
from .handlers import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Изменено на INFO для продакшена
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')  # Добавляем запись в файл
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
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск бота Check Your Crypto")
    
    try:
        # Создание бота и диспетчера
        logger.info("Создание бота и диспетчера...")
        bot = Bot(token=settings.bot_token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Подключаем роутеры
        logger.info("Подключение роутеров...")
        dp.include_router(router)
        logger.info("Роутеры подключены")
        
        # Получаем информацию о боте
        logger.info("Получение информации о боте...")
        bot_info = await bot.get_me()
        logger.info(f"Бот: @{bot_info.username} (ID: {bot_info.id})")
        
        # Инициализация базы данных (после создания бота)
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных инициализирована")
        
        # Запускаем мониторинг в фоне
        logger.info("Запуск мониторинга...")
        monitoring_task = asyncio.create_task(monitoring.start_monitoring())
        logger.info("Мониторинг запущен")
        
        logger.info("Бот запущен и готов к работе")
        
        # Логируем запуск
        monitoring.log_analytics("bot_started", {
            "bot_id": bot_info.id,
            "bot_username": bot_info.username
        })
        
        logger.info("Начинаем polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            monitoring.log_error(f"Bot error: {e}")
        except:
            pass
    finally:
        # Останавливаем мониторинг
        try:
            monitoring_task.cancel()
            await close_db()
        except:
            pass
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
