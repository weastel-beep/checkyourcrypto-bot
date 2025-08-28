#!/usr/bin/env python3
"""
Скрипт для добавления тестовых пользователей
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Добавляем путь к модулям
sys.path.insert(0, '.')

from common.database import async_session_maker
from common.models import User

async def add_test_users():
    """Добавить тестовых пользователей"""
    async with async_session_maker() as session:
        # Создаем тестовых пользователей
        test_users = [
            User(
                tg_id=123456789,
                username="test_user_1",
                first_name="Тестовый",
                last_name="Пользователь 1",
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
                first_name="Test",
                last_name="User 2",
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
                first_name="Тестовый",
                last_name="Пользователь 3",
                language="ru",
                balance=Decimal("200.00"),
                is_blocked=False,
                created_at=datetime.utcnow() - timedelta(days=15),
                updated_at=datetime.utcnow(),
                last_free_check=datetime.utcnow() - timedelta(days=1)
            ),
            User(
                tg_id=111222333,
                username="blocked_user",
                first_name="Заблокированный",
                last_name="Пользователь",
                language="ru",
                balance=Decimal("0.00"),
                is_blocked=True,
                created_at=datetime.utcnow() - timedelta(days=20),
                updated_at=datetime.utcnow(),
                last_free_check=datetime.utcnow() - timedelta(days=30)
            )
        ]
        
        # Добавляем пользователей
        for user in test_users:
            session.add(user)
        
        await session.commit()
        
        print(f"✅ Добавлено {len(test_users)} тестовых пользователей:")
        for user in test_users:
            print(f"   - {user.username} (ID: {user.tg_id}, Баланс: {user.balance}, Язык: {user.language}, Заблокирован: {user.is_blocked})")

if __name__ == "__main__":
    asyncio.run(add_test_users())
