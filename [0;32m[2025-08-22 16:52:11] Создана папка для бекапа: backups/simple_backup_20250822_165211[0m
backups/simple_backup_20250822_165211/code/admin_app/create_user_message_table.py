#!/usr/bin/env python
"""
Скрипт для создания таблицы UserMessage на Heroku
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def create_user_message_table():
    """Создает таблицу user_messages вручную"""
    with connection.cursor() as cursor:
        # Проверяем, существует ли таблица
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_messages'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Таблица user_messages уже существует")
            return
        
        # Создаем таблицу
        cursor.execute("""
            CREATE TABLE user_messages (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                message_type VARCHAR(20) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                language VARCHAR(10) NOT NULL,
                status VARCHAR(20) NOT NULL,
                sent_at TIMESTAMP WITH TIME ZONE NULL,
                delivered_at TIMESTAMP WITH TIME ZONE NULL,
                read_at TIMESTAMP WITH TIME ZONE NULL,
                error_message TEXT NOT NULL DEFAULT '',
                retry_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                mass_message_id BIGINT NULL,
                sent_by_id BIGINT NOT NULL
            );
        """)
        
        # Создаем индексы
        cursor.execute("""
            CREATE INDEX user_messages_user_id_created_at_idx 
            ON user_messages (user_id, created_at);
        """)
        
        cursor.execute("""
            CREATE INDEX user_messages_status_created_at_idx 
            ON user_messages (status, created_at);
        """)
        
        cursor.execute("""
            CREATE INDEX user_messages_message_type_created_at_idx 
            ON user_messages (message_type, created_at);
        """)
        
        print("Таблица user_messages создана успешно")

def update_admin_action_log():
    """Обновляет поле action_type в таблице admin_action_logs"""
    with connection.cursor() as cursor:
        # Проверяем текущий размер поля
        cursor.execute("""
            SELECT character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'admin_action_logs' 
            AND column_name = 'action_type';
        """)
        result = cursor.fetchone()
        
        if result and result[0] >= 25:
            print("Поле action_type уже имеет достаточный размер")
            return
        
        # Изменяем размер поля
        cursor.execute("""
            ALTER TABLE admin_action_logs 
            ALTER COLUMN action_type TYPE VARCHAR(25);
        """)
        
        print("Поле action_type обновлено успешно")

if __name__ == '__main__':
    print("Создаем таблицу user_messages...")
    create_user_message_table()
    
    print("Обновляем поле action_type...")
    update_admin_action_log()
    
    print("Все операции выполнены успешно!")
