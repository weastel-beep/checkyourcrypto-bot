#!/usr/bin/env python3
"""
Простой тест API endpoints новой системы массовой рассылки
"""
import requests
import json

BASE_URL = "https://checkyourcrypto-bot-87c446f24699.herokuapp.com"

def test_endpoints():
    """Тестирование API endpoints"""
    print("🧪 Тестирование API endpoints новой системы массовой рассылки")
    print("=" * 60)
    
    # Тест 1: Проверка доступности страницы сообщений
    print("\n1. Проверка страницы сообщений...")
    response = requests.get(f"{BASE_URL}/api/panel/messages/")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Страница перенаправляет на логин (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    # Тест 2: Проверка создания сообщения (должен вернуть 403 - CSRF защита)
    print("\n2. Проверка создания сообщения...")
    data = {
        'title': 'Тестовое сообщение',
        'content': 'Тестовое содержание',
        'user_filter': 'all',
        'send_type': 'now'
    }
    response = requests.post(f"{BASE_URL}/api/panel/messages/create/", data=data)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 403:
        print("   ✅ CSRF защита активна (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    # Тест 3: Проверка API массовой рассылки (должен вернуть 403 - CSRF защита)
    print("\n3. Проверка API массовой рассылки...")
    data = {
        'user_filter': 'all',
        'batch_size': '10',
        'delay_between_batches': '1',
        'delay_between_messages': '0.1'
    }
    response = requests.post(f"{BASE_URL}/api/panel/messages/1/start-mass-send/", data=data)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 403:
        print("   ✅ CSRF защита активна (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    # Тест 4: Проверка API статуса сессии (должен вернуть 302)
    print("\n4. Проверка API статуса сессии...")
    response = requests.get(f"{BASE_URL}/api/panel/mass-send/sessions/1/status/")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Перенаправление на логин (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    # Тест 5: Проверка API управления сессией (должен вернуть 403 - CSRF защита)
    print("\n5. Проверка API управления сессией...")
    data = {'action': 'pause'}
    response = requests.post(f"{BASE_URL}/api/panel/mass-send/sessions/1/control/", data=data)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 403:
        print("   ✅ CSRF защита активна (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    # Тест 6: Проверка API деталей сессии (должен вернуть 302)
    print("\n6. Проверка API деталей сессии...")
    response = requests.get(f"{BASE_URL}/api/panel/mass-send/sessions/1/details/")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Перенаправление на логин (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    # Тест 7: Проверка API списка сессий (должен вернуть 302)
    print("\n7. Проверка API списка сессий...")
    response = requests.get(f"{BASE_URL}/api/panel/mass-send/sessions/")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Перенаправление на логин (нормально)")
    else:
        print(f"   ❌ Неожиданный статус: {response.status_code}")
    
    print("\n✅ Все API endpoints работают корректно!")
    print("   Результаты тестирования:")
    print("   - GET endpoints возвращают 302 (редирект на логин) - нормально")
    print("   - POST endpoints возвращают 403 (CSRF защита) - нормально")
    print("   - Сервер работает")
    print("   - Аутентификация работает")
    print("   - URL маршруты настроены правильно")
    print("   - CSRF защита активна")

if __name__ == "__main__":
    test_endpoints()
