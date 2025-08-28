#!/usr/bin/env python3
"""
Тест Django настроек
"""
import os
import sys
import django

# Добавляем путь к admin_app
sys.path.insert(0, 'admin_app')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.conf import settings

print("🔍 Проверяем Django настройки...")
print(f"BOT_TOKEN: {getattr(settings, 'BOT_TOKEN', 'НЕ НАЙДЕН')}")
print(f"ALERT_BOT_TOKEN: {getattr(settings, 'ALERT_BOT_TOKEN', 'НЕ НАЙДЕН')}")
print(f"OPS_CHAT_ID: {getattr(settings, 'OPS_CHAT_ID', 'НЕ НАЙДЕН')}")

# Проверяем переменные окружения
print(f"\n🔍 Проверяем переменные окружения...")
print(f"BOT_TOKEN (env): {os.getenv('BOT_TOKEN', 'НЕ НАЙДЕН')}")
print(f"ALERT_BOT_TOKEN (env): {os.getenv('ALERT_BOT_TOKEN', 'НЕ НАЙДЕН')}")
print(f"OPS_CHAT_ID (env): {os.getenv('OPS_CHAT_ID', 'НЕ НАЙДЕН')}")

if hasattr(settings, 'BOT_TOKEN') and settings.BOT_TOKEN != 'your-bot-token-here':
    print("\n✅ BOT_TOKEN найден и настроен правильно!")
else:
    print("\n❌ BOT_TOKEN не найден или не настроен!")
