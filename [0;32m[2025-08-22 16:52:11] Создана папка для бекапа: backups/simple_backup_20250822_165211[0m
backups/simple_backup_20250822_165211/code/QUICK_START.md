# Quick Start - Check Your Crypto Bot

## 🚀 Быстрый старт

### 1. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 2. Проверка статуса системы
```bash
python scripts/smart_bot_manager.py status
```

### 3. Запуск бота

#### Для разработки (локальный бот):
```bash
./switch_to_local.sh
```

#### Для продакшена (Heroku):
```bash
./switch_to_heroku.sh
```

### 4. Проверка работы
```bash
python scripts/status.py
```

## 🔧 Основные команды

### Управление окружениями (РЕКОМЕНДУЕТСЯ):
```bash
# Показать статус
python scripts/environment_manager.py status

# Переключиться на локальную разработку
python scripts/environment_manager.py local

# Переключиться на продакшен
python scripts/environment_manager.py production

# Остановить все экземпляры
python scripts/environment_manager.py stop

# Показать справку
python scripts/environment_manager.py help
```

### Устаревшие команды (не рекомендуется):
```bash
# Старый менеджер (может вызывать конфликты)
python scripts/smart_bot_manager.py status
python scripts/smart_bot_manager.py start-local
python scripts/smart_bot_manager.py start-heroku
python scripts/smart_bot_manager.py stop-all
```

### Мониторинг:
```bash
# Статус системы
python scripts/status.py

# Логи локального бота
tail -f logs/main.log

# Логи Heroku
heroku logs --tail --source worker
```

## ⚠️ Важные моменты

1. **Используйте Environment Manager для переключения окружений**
2. **Только один экземпляр бота может работать одновременно**
3. **Автоматическая очистка Telegram API предотвращает конфликты**
4. **Всегда проверяйте статус перед началом работы**

## 🆘 Устранение проблем

### Конфликт экземпляров:
```bash
# Принудительная остановка и переключение
python scripts/environment_manager.py stop
python scripts/environment_manager.py local
```

### Heroku worker не останавливается:
```bash
# Принудительная остановка Heroku
heroku ps:scale worker=0
python scripts/environment_manager.py local
```

### Проблемы с Telegram API:
```bash
# Автоматическая очистка
python scripts/environment_manager.py stop
python scripts/environment_manager.py local
```

## 📚 Подробная документация

См. `docs/environment_management.md` для подробной информации по управлению окружениями.
