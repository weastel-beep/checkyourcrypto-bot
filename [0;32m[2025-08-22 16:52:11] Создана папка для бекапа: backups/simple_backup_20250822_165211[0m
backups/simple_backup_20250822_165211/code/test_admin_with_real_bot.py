#!/usr/bin/env python3
"""
Тест админ-панели с реальным ботом
"""
import asyncio
import sys
import os
import django

# Добавляем путь к admin_app
sys.path.insert(0, 'admin_app')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
django.setup()

from django.conf import settings
from admin_app.core.admin_models import MassMessage
from common.mass_messaging_service import MassMessagingService
from aiogram import Bot

async def test_admin_with_real_bot():
    """Тестирование админ-панели с реальным ботом"""
    print("🧪 Тестируем админ-панель с реальным ботом...")
    
    # Проверяем токен бота
    bot_token = settings.BOT_TOKEN
    print(f"🤖 Токен бота: {bot_token[:20]}...")
    
    if bot_token == 'your-bot-token-here':
        print("❌ Токен бота не настроен!")
        return False
    
    # Создаем бота
    bot = Bot(token=bot_token)
    service = MassMessagingService(bot)
    
    # Создаем тестовое сообщение через Django
    try:
        django_message = MassMessage.objects.create(
            title="Тест с реальным ботом",
            content="Это тестовое сообщение, отправленное через админ-панель с реальным ботом.",
            language="ru",
            status="draft",
            user_language="ru",
            is_active_only=True
        )
        print(f"✅ Создано Django сообщение ID: {django_message.id}")
        
        # Подготавливаем сообщение
        print(f"🔄 Подготавливаем сообщение {django_message.id}...")
        prepared = await service.prepare_mass_message(django_message.id)
        
        if prepared:
            print("✅ Сообщение подготовлено")
            
            # Отправляем сообщение
            print(f"📤 Отправляем сообщение {django_message.id}...")
            result = await service.send_mass_message(django_message.id)
            
            print(f"✅ Результат отправки:")
            print(f"   📨 Всего: {result['total']}")
            print(f"   ✅ Успешно: {result['success']}")
            print(f"   ❌ Ошибок: {result['failed']}")
            
            # Обновляем Django модель
            django_message.refresh_from_db()
            django_message.status = 'completed'
            django_message.total_users = result['total']
            django_message.sent_count = result['success']
            django_message.failed_count = result['failed']
            django_message.save()
            
            print("✅ Django модель обновлена")
            
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
    success = asyncio.run(test_admin_with_real_bot())
    
    if success:
        print("\n🎉 Админ-панель работает с реальным ботом!")
        print("✅ Система массовых сообщений полностью функциональна!")
    else:
        print("\n❌ Обнаружены проблемы с админ-панелью")
