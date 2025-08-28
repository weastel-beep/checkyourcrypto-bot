#!/usr/bin/env python
"""
Скрипт для инициализации Django базы данных
"""
import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def init_database():
    """Инициализация базы данных"""
    print("Инициализация Django базы данных...")
    
    # Создаем таблицы для Django auth
    with connection.cursor() as cursor:
        # Создаем таблицу django_migrations если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied DATETIME(6) NOT NULL
            )
        """)
        
        # Создаем таблицу django_content_type если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_content_type (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_label VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                UNIQUE(app_label, model)
            )
        """)
        
        # Создаем таблицу auth_user если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password VARCHAR(128) NOT NULL,
                last_login DATETIME(6),
                is_superuser BOOLEAN NOT NULL,
                username VARCHAR(150) NOT NULL UNIQUE,
                first_name VARCHAR(150) NOT NULL,
                last_name VARCHAR(150) NOT NULL,
                email VARCHAR(254) NOT NULL,
                is_staff BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                date_joined DATETIME(6) NOT NULL
            )
        """)
        
        # Создаем суперпользователя
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("Создан суперпользователь: admin/admin123")
        else:
            print("Суперпользователь уже существует")
    
    print("База данных инициализирована!")

if __name__ == '__main__':
    init_database()
