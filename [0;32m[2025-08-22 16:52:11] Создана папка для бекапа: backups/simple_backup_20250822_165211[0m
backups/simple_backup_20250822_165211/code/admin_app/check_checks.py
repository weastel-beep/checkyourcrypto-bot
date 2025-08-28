#!/usr/bin/env python
"""
Скрипт для проверки значений в таблице checks
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def check_checks_data():
    """Проверяем данные в таблице checks"""
    print("🔍 Проверяем данные в таблице checks...")
    
    with connection.cursor() as cursor:
        # Получаем общее количество проверок
        cursor.execute("SELECT COUNT(*) FROM checks")
        total_checks = cursor.fetchone()[0]
        print(f"📊 Найдено проверок: {total_checks}")
        
        # Получаем последние 10 проверок
        cursor.execute("""
            SELECT id, user_id, address, chain, type, created_at 
            FROM checks 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        checks = cursor.fetchall()
        print(f"📋 Показываем последние {len(checks)} проверок:")
        print()
        
        for i, check in enumerate(checks, 1):
            check_id, user_id, address, chain, check_type, created_at = check
            print(f"🔍 Проверка #{i}:")
            print(f"   ID: {check_id}")
            print(f"   Пользователь: {user_id}")
            print(f"   Адрес: {address[:20]}...")
            print(f"   Цепочка: {chain}")
            print(f"   Тип: '{check_type}' (тип данных: {type(check_type)})")
            print(f"   Дата: {created_at}")
            print()

if __name__ == '__main__':
    check_checks_data()
