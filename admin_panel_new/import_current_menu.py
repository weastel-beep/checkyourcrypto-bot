#!/usr/bin/env python3
"""
Скрипт для импорта текущего меню бота в новую систему управления меню
"""

import psycopg2
import os
from datetime import datetime

def import_current_menu():
    """Импортирует текущее меню бота в новую систему"""
    
    # Получаем DATABASE_URL из переменных окружения
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return
    
    # Заменяем postgres:// на postgresql:// для psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Подключение к базе данных установлено")
        
        # Структура текущего главного меню
        current_menu_structure = {
            "main_menu": {
                "ru": [
                    [
                        {"text": "🔍 Проверка", "callback": "check_address"},
                        {"text": "💰 Пополнить", "callback": "add_balance"}
                    ],
                    [
                        {"text": "👤 Личный кабинет", "callback": "profile"},
                        {"text": "📁 FAQ", "callback": "faq"}
                    ]
                ],
                "en": [
                    [
                        {"text": "🔍 Check", "callback": "check_address"},
                        {"text": "💰 Top up", "callback": "add_balance"}
                    ],
                    [
                        {"text": "👤 Profile", "callback": "profile"},
                        {"text": "📁 FAQ", "callback": "faq"}
                    ]
                ]
            }
        }
        
        imported_count = 0
        
        for menu_name, languages in current_menu_structure.items():
            for language, structure in languages.items():
                print(f"📝 Импортируем меню: {menu_name} ({language})")
                
                # Создаем меню
                cursor.execute("""
                    INSERT INTO bot_menus (name, language, menu_type, is_active, created_at, updated_at)
                    VALUES (%s, %s, 'reply_keyboard', true, %s, %s)
                    RETURNING id
                """, (menu_name, language, datetime.now(), datetime.now()))
                
                menu_id = cursor.fetchone()[0]
                print(f"  ✅ Меню создано с ID: {menu_id}")
                
                # Создаем элементы меню
                for row_idx, row in enumerate(structure):
                    for col_idx, item in enumerate(row):
                        cursor.execute("""
                            INSERT INTO bot_menu_items (menu_id, text, callback_data, row_position, column_position, is_active, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, true, %s, %s)
                        """, (
                            menu_id,
                            item.get("text", ""),
                            item.get("callback", None),
                            row_idx,
                            col_idx,
                            datetime.now(),
                            datetime.now()
                        ))
                        print(f"    ✅ Кнопка добавлена: {item.get('text', '')}")
                
                imported_count += 1
        
        # Сохраняем изменения
        conn.commit()
        print(f"\n🎉 Импортировано {imported_count} меню!")
        
        # Проверяем результат
        cursor.execute("""
            SELECT m.name, m.language, COUNT(i.id) as items_count
            FROM bot_menus m
            LEFT JOIN bot_menu_items i ON m.id = i.menu_id
            GROUP BY m.id, m.name, m.language
            ORDER BY m.name, m.language
        """)
        
        menus = cursor.fetchall()
        print(f"\n📋 Импортированные меню ({len(menus)}):")
        for menu in menus:
            print(f"  • {menu[0]} ({menu[1]}): {menu[2]} кнопок")
        
        cursor.close()
        conn.close()
        print("\n✅ Импорт завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    import_current_menu()
