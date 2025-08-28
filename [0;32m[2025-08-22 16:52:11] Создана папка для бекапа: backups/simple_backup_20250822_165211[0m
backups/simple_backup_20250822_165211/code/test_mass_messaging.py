#!/usr/bin/env python3
"""
Тест системы массовых сообщений
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Добавляем путь к модулям
sys.path.insert(0, '.')

from common.database import async_session_maker, init_db
from common.models import User, MassMessage, MassMessageRecipient, MassMessageStatus, OutboxStatus
from common.mass_messaging_service import MassMessagingService
from aiogram import Bot
from common.config import settings
from sqlalchemy import text, select, func

async def test_mass_messaging():
    """Тестирование системы массовых сообщений"""
    print("🧪 Начинаем тестирование системы массовых сообщений...")
    
    # Инициализируем базу данных
    await init_db()
    
    # Создаем тестовых пользователей
    async with async_session_maker() as session:
        # Проверяем, есть ли уже пользователи
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        if user_count == 0:
            print("👥 Создаем тестовых пользователей...")
            test_users = [
                User(
                    tg_id=123456789,
                    username="test_user_1",
                    language="ru",
                    balance=Decimal("100.00"),
                    is_blocked=False,
                    created_at=datetime.utcnow() - timedelta(days=10),
                    updated_at=datetime.utcnow(),
                    last_free_check=datetime.utcnow() - timedelta(hours=2)
                ),
                User(
                    tg_id=987654321,
                    username="test_user_2",
                    language="en",
                    balance=Decimal("50.00"),
                    is_blocked=False,
                    created_at=datetime.utcnow() - timedelta(days=5),
                    updated_at=datetime.utcnow(),
                    last_free_check=datetime.utcnow() - timedelta(hours=1)
                ),
                User(
                    tg_id=555666777,
                    username="test_user_3",
                    language="ru",
                    balance=Decimal("200.00"),
                    is_blocked=False,
                    created_at=datetime.utcnow() - timedelta(days=15),
                    updated_at=datetime.utcnow(),
                    last_free_check=datetime.utcnow() - timedelta(days=1)
                )
            ]
            
            for user in test_users:
                session.add(user)
            
            await session.commit()
            print(f"✅ Создано {len(test_users)} тестовых пользователей")
        else:
            print(f"✅ Найдено {user_count} пользователей в базе данных")
    
    # Создаем тестовое массовое сообщение
    print("📝 Создаем тестовое массовое сообщение...")
    async with async_session_maker() as session:
        mass_message = MassMessage(
            title="Тестовое сообщение",
            content="Это тестовое массовое сообщение для проверки системы рассылки.",
            language="ru",
            status=MassMessageStatus.DRAFT,
            user_language="ru",
            is_active_only=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(mass_message)
        await session.commit()
        await session.refresh(mass_message)
        
        print(f"✅ Создано массовое сообщение ID: {mass_message.id}")
    
    # Тестируем сервис массовых сообщений
    print("🔧 Тестируем сервис массовых сообщений...")
    
    # Создаем мок-бота для тестирования
    class MockBot:
        async def send_message(self, chat_id, text, parse_mode=None):
            print(f"📤 МОК: Отправка сообщения пользователю {chat_id}: {text[:50]}...")
            return True
    
    bot = MockBot()
    service = MassMessagingService(bot)
    
    # Подготавливаем сообщение
    print(f"🔄 Подготавливаем сообщение {mass_message.id}...")
    prepared = await service.prepare_mass_message(mass_message.id)
    
    if prepared:
        print("✅ Сообщение успешно подготовлено")
        
        # Проверяем получателей
        async with async_session_maker() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM mass_message_recipients WHERE mass_message_id = :message_id"),
                {"message_id": mass_message.id}
            )
            recipient_count = result.scalar()
            print(f"📊 Создано {recipient_count} получателей")
            
            # Показываем детали получателей
            result = await session.execute(
                text("SELECT user_id, status FROM mass_message_recipients WHERE mass_message_id = :message_id"),
                {"message_id": mass_message.id}
            )
            recipients = result.fetchall()
            for user_id, status in recipients:
                print(f"   - Пользователь {user_id}: {status}")
        
        # Отправляем сообщение
        print(f"📤 Отправляем сообщение {mass_message.id}...")
        result = await service.send_mass_message(mass_message.id)
        
        print(f"✅ Отправка завершена!")
        print(f"📊 Статистика:")
        print(f"   📨 Всего получателей: {result['total']}")
        print(f"   ✅ Успешно отправлено: {result['success']}")
        print(f"   ❌ Ошибок: {result['failed']}")
        
    else:
        print("❌ Не удалось подготовить сообщение")
    
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_mass_messaging())
