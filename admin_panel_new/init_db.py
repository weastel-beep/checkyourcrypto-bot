#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных новой админки
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import Base
from app.core.database import DATABASE_URL

def init_database():
    """Инициализация базы данных"""
    print("🔧 Инициализация базы данных...")
    
    # Создаем движок
    engine = create_engine(DATABASE_URL)
    
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы успешно")
        
        # Проверяем подключение
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Простой тест подключения
        result = db.execute("SELECT 1").scalar()
        print(f"✅ Подключение к базе данных: {result}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("🎉 База данных инициализирована успешно!")
    else:
        print("💥 Ошибка инициализации базы данных")
        sys.exit(1)
