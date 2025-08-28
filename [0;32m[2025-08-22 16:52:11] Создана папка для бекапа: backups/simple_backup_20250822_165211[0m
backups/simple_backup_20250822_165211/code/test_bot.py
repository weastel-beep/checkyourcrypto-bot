#!/usr/bin/env python3
"""
Простой тест бота Check Your Crypto
"""
import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.main import main

if __name__ == "__main__":
    print("🚀 Запуск тестового бота...")
    print("Убедитесь, что в .env файле настроены:")
    print("- BOT_TOKEN")
    print("- METASLEUTH_WALLET_SCREENING_KEY") 
    print("- METASLEUTH_ADDRESS_LABEL_KEY")
    print("- DATABASE_URL=sqlite+aiosqlite:///./checkyourcrypto.db")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
