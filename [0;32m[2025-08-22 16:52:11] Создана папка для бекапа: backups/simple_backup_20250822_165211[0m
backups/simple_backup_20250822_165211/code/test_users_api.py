#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API пользователей новой админки
"""
import requests
import json
import time

# URL новой админки
BASE_URL = "https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com"

def test_health():
    """Тест health check"""
    print("🔍 Тестируем health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        print(f"📄 Ответ: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_users_api():
    """Тест API пользователей"""
    print("\n👥 Тестируем API пользователей...")
    try:
        response = requests.get(f"{BASE_URL}/api/users", timeout=10)
        print(f"✅ Users API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"📊 Найдено пользователей: {len(users)}")
            
            for i, user in enumerate(users, 1):
                print(f"  {i}. ID: {user.get('id')}, Username: {user.get('username')}, Balance: {user.get('balance')}, Blocked: {user.get('is_blocked')}")
            
            return True
        else:
            print(f"❌ API вернул статус: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Users API failed: {e}")
        return False

def test_user_detail():
    """Тест детальной информации о пользователе"""
    print("\n👤 Тестируем детальную информацию о пользователе...")
    try:
        # Тестируем с первым пользователем
        user_id = 123456789
        response = requests.get(f"{BASE_URL}/api/users/{user_id}", timeout=10)
        print(f"✅ User detail API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print(f"📊 Пользователь: {user.get('username')} (ID: {user.get('id')})")
            print(f"💰 Баланс: {user.get('balance')}")
            print(f"🚫 Заблокирован: {user.get('is_blocked')}")
            return True
        else:
            print(f"❌ API вернул статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ User detail API failed: {e}")
        return False

def test_dashboard_stats():
    """Тест статистики дашборда"""
    print("\n📊 Тестируем статистику дашборда...")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", timeout=10)
        print(f"✅ Dashboard stats API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"👥 Всего пользователей: {data.get('total_users')}")
            print(f"✅ Всего проверок: {data.get('total_checks')}")
            print(f"💰 Общая выручка: {data.get('total_revenue')}")
            return True
        else:
            print(f"❌ API вернул статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard stats API failed: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Начинаем тестирование API новой админки...")
    print("=" * 50)
    
    # Ждем немного, чтобы приложение запустилось
    print("⏳ Ждем запуска приложения...")
    time.sleep(5)
    
    # Тестируем все эндпоинты
    tests = [
        test_health,
        test_users_api,
        test_user_detail,
        test_dashboard_stats
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал с ошибкой: {e}")
            results.append(False)
    
    # Итоговая статистика
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА ТЕСТИРОВАНИЯ:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Успешных тестов: {passed}/{total}")
    print(f"❌ Неудачных тестов: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️ Есть проблемы с API")

if __name__ == "__main__":
    main()
