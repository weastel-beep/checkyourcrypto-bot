#!/usr/bin/env python3
import os
import psycopg2
from datetime import datetime

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://u1glakv0mt2d3o:pdead7d9e454266737da00f1bb46b02b3c9a510a1b9303c927028be67887ff34f@c34u0gd6rbe7bo.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/deh4vhcbuk7858")

def check_real_postgres_users():
    """Проверяем реальных пользователей в PostgreSQL базе данных"""
    print("🔍 Подключаемся к PostgreSQL базе данных...")
    print(f"📡 URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Локальная БД'}")
    
    try:
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Подключение к PostgreSQL успешно!")
        
        # Проверяем все таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n📋 Найдено таблиц: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*80)
        
        # Проверяем таблицу users
        print("👥 Проверяем таблицу 'users':")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Всего пользователей в таблице 'users': {user_count}")
        
        if user_count > 0:
            cursor.execute("""
                SELECT tg_id, username, language, balance, is_blocked, created_at, updated_at
                FROM users 
                ORDER BY created_at DESC
                LIMIT 20
            """)
            users = cursor.fetchall()
            
            print(f"\n📋 Последние {len(users)} пользователей:")
            for i, user in enumerate(users, 1):
                print(f"{'='*80}")
                print(f" {i}. ID: {user[0]}")
                print(f"    Username: {user[1] or 'Не указан'}")
                print(f"    Language: {user[2]}")
                print(f"    Balance: {user[3]}")
                print(f"    Blocked: {user[4]}")
                print(f"    Created: {user[5]}")
                print(f"    Updated: {user[6]}")
        
        # Проверяем другие таблицы на наличие пользователей
        print("\n" + "="*80)
        print("🔍 Проверяем другие таблицы на наличие пользователей:")
        
        for table in tables:
            table_name = table[0]
            if table_name != 'users':
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"📊 Таблица '{table_name}': {count} записей")
                        
                        # Показываем структуру таблицы
                        cursor.execute(f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table_name}'
                            ORDER BY ordinal_position
                        """)
                        columns = cursor.fetchall()
                        print(f"   Структура: {', '.join([f'{col[0]}({col[1]})' for col in columns])}")
                        
                        # Показываем первые записи
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        rows = cursor.fetchall()
                        for j, row in enumerate(rows, 1):
                            print(f"   {j}. {row}")
                        print()
                except Exception as e:
                    print(f"❌ Ошибка при проверке таблицы '{table_name}': {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")

if __name__ == "__main__":
    check_real_postgres_users()
