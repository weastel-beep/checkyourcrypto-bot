#!/usr/bin/env python3
"""
Скрипт для начисления тестового баланса пользователю
"""
import asyncio
from decimal import Decimal
from common.database import async_session_maker
from common.services import UserService

async def add_test_balance():
    """Добавить тестовый баланс пользователю"""
    async with async_session_maker() as session:
        # Используем ID пользователя из логов
        user_id = 172156680
        
        user = await UserService.get_or_create_user(session, user_id)
        print(f'Пользователь: {user.tg_id}')
        print(f'Текущий баланс: {user.balance} USDT')
        
        # Добавляем 50 USDT
        user.balance += Decimal('50.00')
        await session.commit()
        
        print(f'✅ Баланс обновлен: {user.balance} USDT')
        print(f'Пользователь готов для тестирования выбора типа проверки!')

if __name__ == "__main__":
    asyncio.run(add_test_balance())
