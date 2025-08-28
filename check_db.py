#!/usr/bin/env python3
"""
Временный скрипт для проверки базы данных
"""
import asyncio
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.database import async_session_maker
from sqlalchemy import text

async def check_database():
    """Проверяем содержимое базы данных"""
    print("🔍 Проверяем базу данных...")
    
    async with async_session_maker() as session:
        # Проверяем таблицу scenarios
        print("\n📋 СЦЕНАРИИ:")
        try:
            result = await session.execute(text("SELECT * FROM scenarios"))
            scenarios = result.fetchall()
            if scenarios:
                for row in scenarios:
                    print(f"  {row}")
            else:
                print("  ❌ Сценариев нет!")
        except Exception as e:
            print(f"  ❌ Ошибка при чтении scenarios: {e}")
        
        # Проверяем таблицу scenario_stages
        print("\n📋 СТАДИИ СЦЕНАРИЕВ:")
        try:
            result = await session.execute(text("SELECT * FROM scenario_stages"))
            stages = result.fetchall()
            if stages:
                for row in stages:
                    print(f"  {row}")
            else:
                print("  ❌ Стадий нет!")
        except Exception as e:
            print(f"  ❌ Ошибка при чтении scenario_stages: {e}")
        
        # Проверяем все таблицы
        print("\n📋 ВСЕ ТАБЛИЦЫ:")
        try:
            result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            for table in tables:
                print(f"  {table[0]}")
        except Exception as e:
            print(f"  ❌ Ошибка при чтении списка таблиц: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())
