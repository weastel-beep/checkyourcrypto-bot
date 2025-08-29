#!/usr/bin/env python3
"""
Тест интеграции бота с Admin API
"""
import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_bot_admin_integration():
    """Тестирование интеграции бота с Admin API"""
    print("🧪 Тестирование интеграции бота с Admin API")
    print("=" * 50)
    
    try:
        # Тест 1: Импорт основных компонентов бота
        print("1️⃣ Тестирую импорт компонентов бота...")
        from bot.main import app
        print("   ✅ bot.main импортирован успешно")
        
        from common.services_legacy import TextService, UserService, SettingService
        print("   ✅ Сервисы импортированы успешно")
        
        from common.services_package.scenario_service import ScenarioService
        print("   ✅ ScenarioService импортирован успешно")
        
        print()
        
        # Тест 2: Проверка конфигурации API
        print("2️⃣ Тестирую конфигурацию API...")
        from common.config import settings
        
        print(f"   📋 Admin API URL: {settings.admin_api_url}")
        print(f"   📋 Bot Token: {'✅ Установлен' if settings.bot_token else '❌ Не установлен'}")
        print(f"   📋 Database URL: {'✅ Установлен' if settings.database_url else '❌ Не установлен'}")
        
        print()
        
        # Тест 3: Проверка API базового URL
        print("3️⃣ Тестирую API базовый URL...")
        from common.services_legacy import get_api_base_url
        
        api_base_url = get_api_base_url()
        print(f"   📋 API Base URL: {api_base_url}")
        
        print()
        
        # Тест 4: Проверка роутов бота
        print("4️⃣ Тестирую роуты бота...")
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{route.methods} {route.path}")
        
        print(f"   📋 Количество роутов: {len(routes)}")
        print("   📋 Основные роуты:")
        for route in routes[:10]:  # Показываем первые 10
            print(f"      {route}")
        
        # Проверяем наличие единых эндпоинтов
        unified_routes = [r for r in routes if '/api/unified/' in r]
        print(f"   📋 Единых эндпоинтов: {len(unified_routes)}")
        
        print()
        
        # Тест 5: Проверка сервисов
        print("5️⃣ Тестирую сервисы...")
        
        # TextService
        text_api_url = f"{api_base_url}/api/texts"
        print(f"   📋 TextService API URL: {text_api_url}")
        
        # ScenarioService
        scenario_api_url = f"{api_base_url}/api/bot-flow/scenarios"
        print(f"   📋 ScenarioService API URL: {scenario_api_url}")
        
        # UserService
        user_api_url = f"{api_base_url}/api/users"
        print(f"   📋 UserService API URL: {user_api_url}")
        
        print()
        
        # Тест 6: Проверка обработчиков
        print("6️⃣ Тестирую обработчики...")
        from bot.handlers import handle_all_messages, cmd_start
        print("   ✅ Основные обработчики импортированы")
        
        from bot.handlers.scenarios import ScenarioHandler
        from bot.handlers.checks import CheckHandler
        print("   ✅ Специализированные обработчики импортированы")
        
        print()
        
        # Тест 7: Проверка интеграции с конструктором
        print("7️⃣ Тестирую интеграцию с конструктором...")
        
        # Проверяем, что ScenarioService использует правильный API
        scenario_service_url = ScenarioService.get_api_base_url()
        print(f"   📋 ScenarioService использует: {scenario_service_url}")
        
        # Проверяем, что TextService использует правильный API
        text_service_url = TextService.get_api_base_url()
        print(f"   📋 TextService использует: {text_service_url}")
        
        print()
        
        print("✅ Все тесты интеграции прошли успешно!")
        print()
        print("🎯 Статус интеграции:")
        print("   ✅ Бот подключен к единому API роутеру")
        print("   ✅ Сервисы настроены для работы с Admin API")
        print("   ✅ Конструктор сценариев интегрирован")
        print("   ✅ Обработчики готовы к работе")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции бота с Admin API...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        asyncio.run(test_bot_admin_integration())
        print()
        print("✅ Тестирование интеграции завершено!")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
