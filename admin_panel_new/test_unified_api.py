#!/usr/bin/env python3
"""
Тест единых эндпоинтов Admin API
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_unified_api():
    """Тестирование единых эндпоинтов"""
    base_url = "http://localhost:8001"
    
    print("🧪 Тестирование единых эндпоинтов Admin API")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Тест 1: Health check
        print("1️⃣ Тестирую health check...")
        try:
            response = await client.get(f"{base_url}/api/unified/health")
            print(f"   ✅ Health check: {response.status_code}")
            print(f"   📄 Ответ: {response.json()}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        print()
        
        # Тест 2: Получение текстов
        print("2️⃣ Тестирую получение текстов...")
        try:
            response = await client.get(f"{base_url}/api/unified/texts")
            print(f"   ✅ Получение текстов: {response.status_code}")
            texts = response.json()
            print(f"   📄 Количество текстов: {len(texts)}")
        except Exception as e:
            print(f"   ❌ Получение текстов failed: {e}")
        
        print()
        
        # Тест 3: Получение сценариев
        print("3️⃣ Тестирую получение сценариев...")
        try:
            response = await client.get(f"{base_url}/api/unified/scenarios")
            print(f"   ✅ Получение сценариев: {response.status_code}")
            scenarios = response.json()
            print(f"   📄 Количество сценариев: {len(scenarios)}")
        except Exception as e:
            print(f"   ❌ Получение сценариев failed: {e}")
        
        print()
        
        # Тест 4: Получение настроек
        print("4️⃣ Тестирую получение настроек...")
        try:
            response = await client.get(f"{base_url}/api/unified/settings")
            print(f"   ✅ Получение настроек: {response.status_code}")
            settings = response.json()
            print(f"   📄 Количество настроек: {len(settings)}")
        except Exception as e:
            print(f"   ❌ Получение настроек failed: {e}")
        
        print()
        
        # Тест 5: Обратная совместимость - bot-flow/scenarios
        print("5️⃣ Тестирую обратную совместимость (bot-flow/scenarios)...")
        try:
            response = await client.get(f"{base_url}/api/unified/bot-flow/scenarios")
            print(f"   ✅ Bot-flow scenarios: {response.status_code}")
            scenarios = response.json()
            print(f"   📄 Количество сценариев: {len(scenarios)}")
        except Exception as e:
            print(f"   ❌ Bot-flow scenarios failed: {e}")
        
        print()
        
        # Тест 6: Обратная совместимость - bot-flow/texts
        print("6️⃣ Тестирую обратную совместимость (bot-flow/texts)...")
        try:
            response = await client.get(f"{base_url}/api/unified/bot-flow/texts")
            print(f"   ✅ Bot-flow texts: {response.status_code}")
            texts = response.json()
            print(f"   📄 Количество текстов: {len(texts)}")
        except Exception as e:
            print(f"   ❌ Bot-flow texts failed: {e}")
        
        print()
        
        # Тест 7: Старые эндпоинты (для совместимости)
        print("7️⃣ Тестирую старые эндпоинты (совместимость)...")
        try:
            response = await client.get(f"{base_url}/api/bot-flow/scenarios")
            print(f"   ✅ Старые bot-flow scenarios: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Старые bot-flow scenarios failed: {e}")
        
        try:
            response = await client.get(f"{base_url}/api/bot-flow/texts")
            print(f"   ✅ Старые bot-flow texts: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Старые bot-flow texts failed: {e}")
        
        try:
            response = await client.get(f"{base_url}/api/texts")
            print(f"   ✅ Старые texts: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Старые texts failed: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов единых эндпоинтов...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        asyncio.run(test_unified_api())
        print()
        print("✅ Тестирование завершено!")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
