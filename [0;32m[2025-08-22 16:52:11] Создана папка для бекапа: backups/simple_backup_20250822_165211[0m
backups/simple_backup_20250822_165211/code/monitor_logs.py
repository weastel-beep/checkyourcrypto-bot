#!/usr/bin/env python3
"""
Скрипт для мониторинга логов бота Check Your Crypto
"""
import time
import os
import sys
from datetime import datetime

def monitor_logs(log_file='bot.log', lines_to_show=20):
    """Мониторинг логов в реальном времени"""
    print(f"🔍 Мониторинг логов: {log_file}")
    print(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Показываем последние строки
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                print("📋 Последние записи:")
                for line in lines[-lines_to_show:]:
                    print(line.rstrip())
                print("=" * 80)
    
    print("⏳ Ожидание новых записей... (Ctrl+C для выхода)")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # Перемещаемся в конец файла
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.rstrip()}")
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Мониторинг остановлен")
    except FileNotFoundError:
        print(f"❌ Файл логов {log_file} не найден")
        print("Убедитесь, что бот запущен и создает файл логов")

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'bot.log'
    monitor_logs(log_file)
