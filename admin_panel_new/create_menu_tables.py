#!/usr/bin/env python3
"""
Скрипт для создания таблиц меню в базе данных
"""

import psycopg2
import os

def create_menu_tables():
    """Создает таблицы для системы управления меню"""
    
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
        
        # Создаем таблицу bot_menus
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_menus (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                language VARCHAR(10) NOT NULL,
                menu_type VARCHAR(20) NOT NULL,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица bot_menus создана")
        
        # Создаем таблицу bot_menu_items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_menu_items (
                id SERIAL PRIMARY KEY,
                menu_id INTEGER REFERENCES bot_menus(id) ON DELETE CASCADE,
                text VARCHAR(100) NOT NULL,
                callback_data VARCHAR(100),
                row_position INTEGER NOT NULL,
                column_position INTEGER NOT NULL,
                parent_item_id INTEGER REFERENCES bot_menu_items(id),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица bot_menu_items создана")
        
        # Добавляем поле menu_item_id в таблицу bot_texts если его нет
        cursor.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'bot_texts' AND column_name = 'menu_item_id'
                ) THEN
                    ALTER TABLE bot_texts ADD COLUMN menu_item_id INTEGER REFERENCES bot_menu_items(id);
                END IF;
            END $$;
        """)
        print("✅ Поле menu_item_id добавлено в bot_texts (если не существовало)")
        
        # Создаем индексы для оптимизации
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_menus_name_lang ON bot_menus(name, language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_menu_items_menu_id ON bot_menu_items(menu_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_menu_items_position ON bot_menu_items(row_position, column_position)")
        print("✅ Индексы созданы")
        
        # Сохраняем изменения
        conn.commit()
        print("\n🎉 Все таблицы меню созданы успешно!")
        
        # Проверяем созданные таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('bot_menus', 'bot_menu_items')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Созданные таблицы ({len(tables)}):")
        for table in tables:
            print(f"  • {table[0]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Готово!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    create_menu_tables()
