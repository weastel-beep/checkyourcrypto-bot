#!/usr/bin/env python
"""
Скрипт для применения миграций на Heroku
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("Применяем миграции на Heroku...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("Миграции применены успешно!")
