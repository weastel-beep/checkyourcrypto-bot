#!/usr/bin/env python3
"""
Тест админ-панели массовых сообщений
"""
import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, '.')

import django
from django.conf import settings as django_settings

# Конфигурируем Django
if not django_settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
    django.setup()

from admin_app.core.admin_models import MassMessage
from common.models import User as SQLAlchemyUser
from common.database import async_session_maker
from sqlalchemy import text

async def test_admin_mass_messaging():
    """Тестирование админ-панели массовых сообщений"""
    print("🧪 Тестируем админ-панель массовых сообщений...")
    
    # Проверяем, что пользователи есть в базе данных
    async with async_session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"✅ Найдено {user_count} пользователей в SQLAlchemy базе")
    
    # Создаем сообщение через Django
    try:
        django_message = MassMessage.objects.create(
            title="Тест из админ-панели",
            content="Это тестовое сообщение, созданное через Django админ-панель.",
            language="ru",
            status="draft",
            user_language="ru",
            is_active_only=True
        )
        print(f"✅ Создано Django сообщение ID: {django_message.id}")
        
        # Проверяем, что сообщение появилось в SQLAlchemy
        async with async_session_maker() as session:
            result = await session.execute(
                text("SELECT id, title, status FROM mass_messages WHERE id = :id"),
                {"id": django_message.id}
            )
            sqlalchemy_message = result.fetchone()
            if sqlalchemy_message:
                print(f"✅ Сообщение найдено в SQLAlchemy: {sqlalchemy_message}")
            else:
                print("❌ Сообщение не найдено в SQLAlchemy")
        
        # Пробуем подготовить и отправить сообщение
        from common.mass_messaging_service import MassMessagingService
        
        # Создаем мок-бота
        class MockBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                print(f"📤 МОК: Отправка админ-сообщения пользователю {chat_id}: {text[:50]}...")
                return True
        
        bot = MockBot()
        service = MassMessagingService(bot)
        
        # Подготавливаем сообщение
        print(f"🔄 Подготавливаем админ-сообщение {django_message.id}...")
        prepared = await service.prepare_mass_message(django_message.id)
        
        if prepared:
            print("✅ Админ-сообщение подготовлено")
            
            # Отправляем сообщение
            print(f"📤 Отправляем админ-сообщение {django_message.id}...")
            result = await service.send_mass_message(django_message.id)
            
            print(f"✅ Отправка админ-сообщения завершена!")
            print(f"📊 Статистика:")
            print(f"   📨 Всего получателей: {result['total']}")
            print(f"   ✅ Успешно отправлено: {result['success']}")
            print(f"   ❌ Ошибок: {result['failed']}")
            
            # Обновляем Django модель
            django_message.refresh_from_db()
            django_message.status = 'completed'
            django_message.sent_at = datetime.now()
            django_message.total_users = result['total']
            django_message.sent_count = result['success']
            django_message.failed_count = result['failed']
            django_message.save()
            
            print("✅ Django модель обновлена")
            
        else:
            print("❌ Не удалось подготовить админ-сообщение")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎉 Тестирование админ-панели завершено!")

if __name__ == "__main__":
    asyncio.run(test_admin_mass_messaging())
