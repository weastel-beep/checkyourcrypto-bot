#!/usr/bin/env python
"""
Скрипт для добавления поля username в таблицу users
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def add_username_field():
    """Добавляет поле username в таблицу users"""
    with connection.cursor() as cursor:
        # Проверяем, существует ли поле
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'username'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Поле username уже существует")
            return
        
        # Добавляем поле
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN username VARCHAR(100) NULL;
        """)
        
        print("Поле username добавлено успешно")

if __name__ == '__main__':
    print("Добавляем поле username...")
    add_username_field()
    print("Операция завершена!")
