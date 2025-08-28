#!/usr/bin/env python
"""
Скрипт для проверки подключения к базе данных
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from core.models import User, Check, Payment

def check_database():
    """Проверяем подключение к базе данных"""
    try:
        # Проверяем подключение
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Подключение к базе данных успешно")
            print(f"Версия PostgreSQL: {version[0]}")
        
        # Проверяем таблицы
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"\n📋 Таблицы в базе данных:")
            for table in tables:
                print(f"  - {table[0]}")
        
        # Проверяем количество записей
        print(f"\n📊 Статистика:")
        print(f"  Пользователей: {User.objects.count()}")
        print(f"  Проверок: {Check.objects.count()}")
        print(f"  Платежей: {Payment.objects.count()}")
        
        # Показываем несколько пользователей
        users = User.objects.all()[:5]
        if users:
            print(f"\n👥 Последние пользователи:")
            for user in users:
                print(f"  - ID: {user.tg_id}, Баланс: ${user.balance}, Язык: {user.language}")
        else:
            print(f"\n❌ Пользователей не найдено")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
