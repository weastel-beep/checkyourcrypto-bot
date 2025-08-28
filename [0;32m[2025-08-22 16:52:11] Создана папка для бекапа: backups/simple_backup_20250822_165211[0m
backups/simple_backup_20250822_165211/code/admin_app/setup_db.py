#!/usr/bin/env python
"""
Скрипт для настройки базы данных админки
"""
import os
import sys
import django
import sqlite3

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from core.admin_models import AdminUser

def setup_database():
    """Настраивает базу данных"""
    print("🔧 Настройка базы данных...")
    
    # Создаем таблицы вручную
    with connection.cursor() as cursor:
        # Таблица admin_users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password VARCHAR(128) NOT NULL,
                last_login DATETIME NULL,
                is_superuser BOOLEAN NOT NULL,
                username VARCHAR(150) UNIQUE NOT NULL,
                first_name VARCHAR(150) NOT NULL,
                last_name VARCHAR(150) NOT NULL,
                email VARCHAR(254) NOT NULL,
                is_staff BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                date_joined DATETIME NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'moderator',
                telegram_id BIGINT NULL UNIQUE,
                two_factor_enabled BOOLEAN NOT NULL DEFAULT 0,
                two_factor_secret VARCHAR(32) NOT NULL DEFAULT '',
                last_login_ip VARCHAR(39) NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Таблица admin_invitations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(254) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'moderator',
                token VARCHAR(64) UNIQUE NOT NULL,
                invited_by_id INTEGER NOT NULL,
                is_used BOOLEAN NOT NULL DEFAULT 0,
                expires_at DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (invited_by_id) REFERENCES admin_users (id)
            )
        """)
        
        # Таблица admin_action_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action_type VARCHAR(20) NOT NULL,
                description TEXT NOT NULL,
                target_user_id BIGINT NULL,
                ip_address VARCHAR(39) NULL,
                user_agent TEXT NOT NULL DEFAULT '',
                created_at DATETIME NOT NULL,
                FOREIGN KEY (admin_id) REFERENCES admin_users (id)
            )
        """)
        
        # Таблица system_metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                active_users INTEGER NOT NULL,
                requests_per_minute INTEGER NOT NULL,
                bot_status VARCHAR(20) NOT NULL,
                database_connections INTEGER NOT NULL
            )
        """)
        
        # Таблица mass_messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mass_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                language VARCHAR(10) NOT NULL DEFAULT 'ru',
                created_by_id INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'draft',
                min_balance DECIMAL(10,2) NULL,
                max_balance DECIMAL(10,2) NULL,
                user_language VARCHAR(10) NOT NULL DEFAULT '',
                is_active BOOLEAN NOT NULL DEFAULT 1,
                scheduled_at DATETIME NULL,
                sent_at DATETIME NULL,
                total_users INTEGER NOT NULL DEFAULT 0,
                sent_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (created_by_id) REFERENCES admin_users (id)
            )
        """)
        
        # Таблица bot_texts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_type VARCHAR(50) NOT NULL,
                language VARCHAR(10) NOT NULL,
                content TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                version INTEGER NOT NULL DEFAULT 1,
                created_by_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                UNIQUE(text_type, language, version),
                FOREIGN KEY (created_by_id) REFERENCES admin_users (id)
            )
        """)
        
        print("✅ Таблицы созданы успешно!")
    
    # Создаем суперпользователя
    create_superuser()

def create_superuser():
    """Создает суперпользователя"""
    username = 'admin'
    email = 'admin@checkyourcrypto.com'
    password = 'admin123456'
    
    # Проверяем, существует ли уже пользователь
    if AdminUser.objects.filter(username=username).exists():
        print(f"👤 Пользователь {username} уже существует!")
        return
    
    # Создаем суперпользователя
    user = AdminUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='superadmin',
        is_staff=True,
        is_superuser=True
    )
    
    print(f"✅ Суперпользователь создан успешно!")
    print(f"👤 Username: {username}")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"👑 Role: {user.role}")
    print("\n⚠️  Не забудьте изменить пароль после первого входа!")

if __name__ == '__main__':
    setup_database()
