#!/usr/bin/env python3
"""
Тест для отладки массовых сообщений
"""
import asyncio
import os
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.database import async_session_maker
from common.models import User, MassMessage
from sqlalchemy import select

async def debug_mass_messaging():
    """Отладка массовых сообщений"""
    
    async with async_session_maker() as session:
        # 1. Проверяем пользователей
        print("=== ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ ===")
        users_query = select(User)
        users_result = await session.execute(users_query)
        users = users_result.scalars().all()
        
        print(f"Всего пользователей: {len(users)}")
        for user in users:
            print(f"- ID: {user.tg_id}, Язык: {user.language}, Активен: {user.is_active}")
        
        # 2. Проверяем массовые сообщения
        print("\n=== ПРОВЕРКА МАССОВЫХ СООБЩЕНИЙ ===")
        messages_query = select(MassMessage)
        messages_result = await session.execute(messages_query)
        messages = messages_result.scalars().all()
        
        print(f"Всего сообщений: {len(messages)}")
        for msg in messages:
            print(f"- ID: {msg.id}, Статус: {msg.status}, Заголовок: {msg.title}")
        
        # 3. Проверяем фильтрацию для конкретного сообщения
        if messages:
            latest_message = messages[-1]
            print(f"\n=== ФИЛЬТРАЦИЯ ДЛЯ СООБЩЕНИЯ {latest_message.id} ===")
            
            # Фильтр по языку
            if latest_message.user_language:
                filtered_users = [u for u in users if u.language == latest_message.user_language]
                print(f"Пользователи с языком '{latest_message.user_language}': {len(filtered_users)}")
            
            # Фильтр по активности
            if latest_message.is_active_only:
                active_users = [u for u in users if u.is_active]
                print(f"Активные пользователи: {len(active_users)}")
            
            # Общий фильтр
            filtered_users = users
            if latest_message.user_language:
                filtered_users = [u for u in filtered_users if u.language == latest_message.user_language]
            if latest_message.is_active_only:
                filtered_users = [u for u in filtered_users if u.is_active]
            
            print(f"Итого получателей после фильтрации: {len(filtered_users)}")
            
            if filtered_users:
                print("Получатели:")
                for user in filtered_users[:5]:  # Показываем первые 5
                    print(f"  - {user.tg_id} ({user.language})")
                if len(filtered_users) > 5:
                    print(f"  ... и еще {len(filtered_users) - 5} пользователей")
            else:
                print("❌ НЕТ ПОЛУЧАТЕЛЕЙ!")

if __name__ == '__main__':
    print("Отладка массовых сообщений...")
    asyncio.run(debug_mass_messaging())
    print("Отладка завершена!")
