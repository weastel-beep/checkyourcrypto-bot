#!/usr/bin/env python
"""
Скрипт для настройки админки на Heroku
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from core.admin_models import AdminUser
from django.core.management import call_command

def setup_heroku():
    """Настраивает админку на Heroku"""
    print("🔧 Настройка админки на Heroku...")
    
    # Применяем миграции
    try:
        call_command('migrate', verbosity=0)
        print("✅ Миграции применены успешно!")
    except Exception as e:
        print(f"❌ Ошибка применения миграций: {e}")
        return
    
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
    print(f"🌐 Админка доступна по адресу: https://checkyourcrypto-bot-87c446f24699.herokuapp.com/api/admin/login/")

if __name__ == '__main__':
    setup_heroku()
