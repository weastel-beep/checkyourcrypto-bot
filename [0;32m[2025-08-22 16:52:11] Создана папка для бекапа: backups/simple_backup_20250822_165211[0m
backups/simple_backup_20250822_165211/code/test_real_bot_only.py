#!/usr/bin/env python3
"""
Тест только с реальным ботом (без Django)
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к модулям
sys.path.insert(0, '.')

from common.mass_messaging_service import MassMessagingService
from aiogram import Bot

async def test_real_bot():
    """Тестирование с реальным ботом"""
    print("🧪 Тестируем с реальным ботом...")
    
    # Получаем токен бота
    bot_token = os.getenv('BOT_TOKEN')
    print(f"🤖 Токен бота: {bot_token[:20] if bot_token else 'НЕ НАЙДЕН'}...")
    
    if not bot_token or bot_token == 'your-bot-token-here':
        print("❌ Токен бота не настроен!")
        return False
    
    # Создаем бота
    bot = Bot(token=bot_token)
    service = MassMessagingService(bot)
    
    try:
        # Создаем тестовое сообщение
        print("📝 Создаем тестовое сообщение...")
        message = await service.create_mass_message(
            title="Тест с реальным ботом",
            content="Это тестовое сообщение, отправленное с реальным ботом.",
            language="ru",
            user_language="ru",
            is_active_only=True
        )
        
        print(f"✅ Создано сообщение ID: {message.id}")
        
        # Подготавливаем сообщение
        print(f"🔄 Подготавливаем сообщение {message.id}...")
        prepared = await service.prepare_mass_message(message.id)
        
        if prepared:
            print("✅ Сообщение подготовлено")
            
            # Отправляем сообщение
            print(f"📤 Отправляем сообщение {message.id}...")
            result = await service.send_mass_message(message.id)
            
            print(f"✅ Результат отправки:")
            print(f"   📨 Всего: {result['total']}")
            print(f"   ✅ Успешно: {result['success']}")
            print(f"   ❌ Ошибок: {result['failed']}")
            
            # Закрываем сессию бота
            await bot.session.close()
            
            return True
            
        else:
            print("❌ Не удалось подготовить сообщение")
            await bot.session.close()
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await bot.session.close()
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_bot())
    
    if success:
        print("\n🎉 Реальный бот работает корректно!")
        print("✅ Система массовых сообщений готова к использованию!")
    else:
        print("\n❌ Обнаружены проблемы с ботом")
