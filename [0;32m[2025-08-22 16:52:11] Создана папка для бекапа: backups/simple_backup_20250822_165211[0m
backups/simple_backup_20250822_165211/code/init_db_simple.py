#!/usr/bin/env python3
"""
Простой скрипт для инициализации базы данных Check Your Crypto
"""
import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.database import init_db, async_session_maker
from common.services import TextService, SettingService

async def init_database():
    """Инициализация базы данных"""
    print("Начинаем инициализацию базы данных...")
    
    # Создаем таблицы
    await init_db()
    print("✅ Таблицы созданы")
    
    async with async_session_maker() as session:
        # Добавляем тексты по умолчанию
        print("Добавляем тексты по умолчанию...")
        default_texts = TextService.get_default_texts()
        
        for key, value in default_texts.items():
            await TextService.set_text(session, key, value, "ru")
            print(f"✅ Добавлен текст: {key}")
        
        # Добавляем настройки по умолчанию
        print("Добавляем настройки по умолчанию...")
        default_settings = SettingService.get_default_settings()
        
        for key, value in default_settings.items():
            await SettingService.set_setting(session, key, value)
            print(f"✅ Добавлена настройка: {key} = {value}")
    
    print("🎉 Инициализация базы данных завершена успешно!")

if __name__ == "__main__":
    asyncio.run(init_database())
