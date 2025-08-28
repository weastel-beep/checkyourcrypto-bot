#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы управления массовой рассылкой
"""
import requests
import json
import time
from datetime import datetime

# Конфигурация
BASE_URL = "https://checkyourcrypto-bot-87c446f24699.herokuapp.com"
LOGIN_URL = f"{BASE_URL}/api/panel/login/"
MESSAGES_URL = f"{BASE_URL}/api/panel/messages/"
SESSIONS_URL = f"{BASE_URL}/api/panel/mass-send/sessions/"

# Данные для входа (замените на реальные)
LOGIN_DATA = {
    'username': 'admin',
    'password': 'admin123'
}

def login():
    """Вход в систему"""
    print("🔐 Вход в систему...")
    
    session = requests.Session()
    
    # Выполняем вход без CSRF токена (защита отключена)
    response = session.post(LOGIN_URL, data=LOGIN_DATA, allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ Вход выполнен успешно")
        return session
    else:
        print(f"❌ Ошибка входа: {response.status_code}")
        print(f"Ответ: {response.text[:200]}...")
        return None

def get_messages(session):
    """Получение списка сообщений"""
    print("\n📋 Получение списка сообщений...")
    
    response = session.get(MESSAGES_URL)
    if response.status_code != 200:
        print(f"❌ Ошибка получения сообщений: {response.status_code}")
        return None
    
    print("✅ Список сообщений получен")
    return response.text

def create_test_message(session):
    """Создание тестового сообщения"""
    print("\n📝 Создание тестового сообщения...")
    
    # Данные сообщения (без CSRF токена)
    message_data = {
        'title': f'Тестовая рассылка {datetime.now().strftime("%H:%M:%S")}',
        'content': 'Это тестовое сообщение для проверки новой системы массовой рассылки! 🚀',
        'user_filter': 'all',
        'send_type': 'now'
    }
    
    response = session.post(f"{MESSAGES_URL}create/", data=message_data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                message_id = result.get('message_id')
                print(f"✅ Сообщение создано! ID: {message_id}")
                return message_id
            else:
                print(f"❌ Ошибка создания: {result.get('error')}")
                return None
        except json.JSONDecodeError:
            print("❌ Неверный JSON ответ")
            return None
    else:
        print(f"❌ Ошибка HTTP: {response.status_code}")
        return None

def start_mass_send(session, message_id):
    """Запуск массовой рассылки"""
    print(f"\n🚀 Запуск массовой рассылки для сообщения {message_id}...")
    
    # Параметры рассылки (без CSRF токена)
    send_data = {
        'user_filter': 'all',
        'batch_size': '10',  # Маленький размер для теста
        'delay_between_batches': '1',
        'delay_between_messages': '0.1'
    }
    
    response = session.post(f"{MESSAGES_URL}{message_id}/start-mass-send/", data=send_data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                session_id = result.get('session_id')
                print(f"✅ Рассылка запущена! Сессия ID: {session_id}")
                return session_id
            else:
                print(f"❌ Ошибка запуска: {result.get('error')}")
                return None
        except json.JSONDecodeError:
            print("❌ Неверный JSON ответ")
            return None
    else:
        print(f"❌ Ошибка HTTP: {response.status_code}")
        return None

def monitor_session(session, session_id, duration=30):
    """Мониторинг сессии рассылки"""
    print(f"\n📊 Мониторинг сессии {session_id} в течение {duration} секунд...")
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        response = session.get(f"{SESSIONS_URL}{session_id}/status/")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    status_data = result.get('status', {})
                    
                    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
                    print(f"📈 Статус: {status_data.get('status', 'Неизвестно')}")
                    print(f"📊 Прогресс: {status_data.get('progress', 0)}%")
                    print(f"📨 Отправлено: {status_data.get('sent', 0)}/{status_data.get('total', 0)}")
                    print(f"❌ Ошибки: {status_data.get('failed', 0)}")
                    print(f"⏭️ Пропущено: {status_data.get('skipped', 0)}")
                    
                    if status_data.get('eta'):
                        print(f"⏱️ ETA: {status_data.get('eta')}")
                    
                    # Проверяем завершение
                    if status_data.get('status') in ['COMPLETED', 'FAILED', 'CANCELLED']:
                        print(f"✅ Рассылка завершена со статусом: {status_data.get('status')}")
                        break
                        
                else:
                    print(f"❌ Ошибка получения статуса: {result.get('error')}")
                    break
            except json.JSONDecodeError:
                print("❌ Неверный JSON ответ")
                break
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            break
        
        time.sleep(2)  # Пауза между запросами

def get_session_details(session, session_id):
    """Получение детальной информации о сессии"""
    print(f"\n📋 Детальная информация о сессии {session_id}...")
    
    response = session.get(f"{SESSIONS_URL}{session_id}/details/")
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                details = result.get('details', {})
                
                print(f"📝 Сообщение: {details.get('message_title')}")
                print(f"📊 Статистика получателей:")
                
                for stat in details.get('recipients_stats', []):
                    print(f"  - {stat.get('status')}: {stat.get('count')}")
                
                if details.get('recent_errors'):
                    print(f"❌ Последние ошибки:")
                    for error in details.get('recent_errors', [])[:3]:
                        print(f"  - Пользователь {error.get('user_id')}: {error.get('error')}")
                else:
                    print("✅ Ошибок нет")
                    
            else:
                print(f"❌ Ошибка получения деталей: {result.get('error')}")
        except json.JSONDecodeError:
            print("❌ Неверный JSON ответ")
    else:
        print(f"❌ Ошибка HTTP: {response.status_code}")

def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ УПРАВЛЕНИЯ МАССОВОЙ РАССЫЛКОЙ")
    print("=" * 60)
    
    # Вход в систему
    session = login()
    if not session:
        return
    
    # Получаем список сообщений
    messages_html = get_messages(session)
    if not messages_html:
        return
    
    # Создаем тестовое сообщение
    message_id = create_test_message(session)
    if not message_id:
        return
    
    # Запускаем массовую рассылку
    session_id = start_mass_send(session, message_id)
    if not session_id:
        return
    
    # Мониторим сессию
    monitor_session(session, session_id, duration=30)
    
    # Получаем детальную информацию
    get_session_details(session, session_id)
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    import re
    main()
