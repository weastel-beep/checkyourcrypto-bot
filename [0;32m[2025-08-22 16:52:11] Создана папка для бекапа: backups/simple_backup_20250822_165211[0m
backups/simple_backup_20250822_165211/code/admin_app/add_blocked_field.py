#!/usr/bin/env python
"""
Скрипт для добавления поля is_blocked в таблицу users
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def add_blocked_field():
    """Добавляет поле is_blocked в таблицу users"""
    with connection.cursor() as cursor:
        # Проверяем, существует ли поле
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'is_blocked'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Поле is_blocked уже существует")
            return
        
        # Добавляем поле
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN is_blocked BOOLEAN NOT NULL DEFAULT FALSE;
        """)
        
        print("Поле is_blocked добавлено успешно")

if __name__ == '__main__':
    print("Добавляем поле is_blocked...")
    add_blocked_field()
    print("Операция завершена!")
