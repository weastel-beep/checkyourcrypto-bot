#!/usr/bin/env python
"""
Скрипт для создания администратора на продакшене
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from core.admin_models import AdminUser

def create_admin():
    """Создает администратора"""
    username = input("Введите имя пользователя (admin): ") or 'admin'
    email = input("Введите email: ")
    password = input("Введите пароль: ")
    
    if not email or not password:
        print("❌ Email и пароль обязательны!")
        return
    
    # Проверяем, существует ли уже пользователь
    if AdminUser.objects.filter(username=username).exists():
        print(f"❌ Пользователь {username} уже существует!")
        return
    
    # Создаем администратора
    user = AdminUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='superadmin',
        is_staff=True,
        is_superuser=True
    )
    
    print(f"✅ Администратор создан успешно!")
    print(f"👤 Username: {username}")
    print(f"📧 Email: {email}")
    print(f"👑 Role: {user.role}")

if __name__ == '__main__':
    create_admin()
