#!/usr/bin/env python3
"""
Скрипт для проверки структуры базы данных
"""
import os
import sys
import django

# Добавляем путь к Django приложению
sys.path.append(os.path.join(os.path.dirname(__file__), 'admin_app'))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
django.setup()

from django.db import connection

def check_table_structure():
    """Проверяем структуру таблиц"""
    print("🔍 Проверяем структуру базы данных...")
    
    with connection.cursor() as cursor:
        # Проверяем таблицу users
        print("\n📋 Таблица 'users':")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Проверяем таблицу checks
        print("\n📋 Таблица 'checks':")
        cursor.execute("PRAGMA table_info(checks)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Проверяем таблицу payments
        print("\n📋 Таблица 'payments':")
        cursor.execute("PRAGMA table_info(payments)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Проверяем таблицу mass_messages
        print("\n📋 Таблица 'mass_messages':")
        cursor.execute("PRAGMA table_info(mass_messages)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Проверяем количество записей
        print("\n📊 Количество записей:")
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        print(f"  - Пользователей: {users_count}")
        
        cursor.execute("SELECT COUNT(*) FROM checks")
        checks_count = cursor.fetchone()[0]
        print(f"  - Проверок: {checks_count}")
        
        cursor.execute("SELECT COUNT(*) FROM payments")
        payments_count = cursor.fetchone()[0]
        print(f"  - Платежей: {payments_count}")
        
        cursor.execute("SELECT COUNT(*) FROM mass_messages")
        messages_count = cursor.fetchone()[0]
        print(f"  - Сообщений: {messages_count}")

if __name__ == "__main__":
    check_table_structure()
