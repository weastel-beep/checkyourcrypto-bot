#!/usr/bin/env python3
"""
Скрипт для проверки пользователей админки
"""
import os
import sys
import django

# Добавляем путь к Django проекту
sys.path.append(os.path.join(os.path.dirname(__file__), 'admin_app'))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from core.admin_models import AdminUser

def main():
    print("👥 Проверка пользователей админки:")
    print("=" * 40)
    
    users = AdminUser.objects.all()
    
    if not users.exists():
        print("❌ Пользователей не найдено!")
        print("\nСоздаем тестового пользователя...")
        
        # Создаем тестового пользователя
        user = AdminUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Создан пользователь: {user.username}")
    else:
        print(f"✅ Найдено пользователей: {users.count()}")
        for user in users:
            print(f"  - {user.username} (email: {user.email})")
            print(f"    Staff: {user.is_staff}, Superuser: {user.is_superuser}")

if __name__ == "__main__":
    main()
