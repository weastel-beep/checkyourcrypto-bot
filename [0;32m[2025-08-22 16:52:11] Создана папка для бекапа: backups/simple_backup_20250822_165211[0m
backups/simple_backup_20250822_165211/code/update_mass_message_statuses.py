#!/usr/bin/env python3
"""
Скрипт для обновления статусов массовых сообщений в базе данных
Обновляет строчные значения на заглавные для соответствия SQLAlchemy enum
"""
import os
import sys
import django

# Настройка Django
import sys
sys.path.insert(0, '/app/admin_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from core.admin_models import MassMessage

def update_mass_message_statuses():
    """Обновляет статусы массовых сообщений"""
    
    # Маппинг старых значений на новые
    status_mapping = {
        'draft': 'DRAFT',
        'scheduled': 'SCHEDULED', 
        'sending': 'SENDING',
        'completed': 'COMPLETED',
        'cancelled': 'CANCELLED',
        'failed': 'FAILED'
    }
    
    # Получаем все массовые сообщения
    messages = MassMessage.objects.all()
    updated_count = 0
    
    print(f"Найдено {messages.count()} массовых сообщений")
    
    for message in messages:
        old_status = message.status
        new_status = status_mapping.get(old_status)
        
        if new_status and old_status != new_status:
            print(f"Обновляем сообщение {message.id}: {old_status} -> {new_status}")
            message.status = new_status
            message.save()
            updated_count += 1
        elif old_status in status_mapping:
            print(f"Сообщение {message.id}: статус уже правильный ({old_status})")
        else:
            print(f"Сообщение {message.id}: неизвестный статус ({old_status})")
    
    print(f"\nОбновлено {updated_count} сообщений")

if __name__ == '__main__':
    print("Обновление статусов массовых сообщений...")
    update_mass_message_statuses()
    print("Обновление завершено!")
