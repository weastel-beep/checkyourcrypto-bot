#!/usr/bin/env python3
"""
Скрипт для проверки реальных пользователей в старой базе данных
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

def check_real_users():
    """Проверяем реальных пользователей в базе данных"""
    print("🔍 Проверяем реальных пользователей в базе данных...")
    
    with connection.cursor() as cursor:
        # Получаем всех пользователей
        cursor.execute("""
            SELECT tg_id, username, language, balance, is_blocked, 
                   last_free_check, referral_code, referrer_id, 
                   created_at, updated_at
            FROM users
            ORDER BY created_at
        """)
        users = cursor.fetchall()
        
        print(f"📊 Найдено пользователей: {len(users)}")
        print("\n👥 Список пользователей:")
        print("-" * 80)
        
        for i, user in enumerate(users, 1):
            print(f"{i:2d}. ID: {user[0]}")
            print(f"    Username: {user[1] or 'Не указан'}")
            print(f"    Language: {user[2] or 'ru'}")
            print(f"    Balance: {user[3] or 0.0}")
            print(f"    Blocked: {user[4]}")
            print(f"    Created: {user[8]}")
            print(f"    Updated: {user[9]}")
            print("-" * 80)
        
        # Статистика
        print("\n📈 Статистика:")
        blocked_count = sum(1 for user in users if user[4])
        active_count = len(users) - blocked_count
        total_balance = sum(user[3] or 0 for user in users)
        
        print(f"   Активных пользователей: {active_count}")
        print(f"   Заблокированных пользователей: {blocked_count}")
        print(f"   Общий баланс: {total_balance}")
        
        # Языки
        languages = {}
        for user in users:
            lang = user[2] or 'ru'
            languages[lang] = languages.get(lang, 0) + 1
        
        print(f"   Языки: {languages}")

if __name__ == "__main__":
    check_real_users()
