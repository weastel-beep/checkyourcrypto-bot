# 🛡️ Инструкция по восстановлению Check Your Crypto

## 📋 Обзор

Эта инструкция описывает полный процесс восстановления системы Check Your Crypto из бэкапа в случае любых проблем или сбоев.

## 🚨 Когда использовать восстановление

- **Сбой базы данных** - потеря данных, повреждение таблиц
- **Проблемы с кодом** - критические ошибки, неработающий бот
- **Проблемы с конфигурацией** - неправильные настройки
- **Восстановление после аварии** - полное восстановление системы

## 📦 Что включается в бэкап

### 1. База данных
- Все таблицы: `users`, `checks`, `payments`, `settings`, `texts`, `payment_methods`, `referrals`, `outbox`
- Полные данные в формате JSON
- SQL дамп (если доступен pg_dump)

### 2. Исходный код
- Все директории: `bot/`, `alerts_bot/`, `admin_app/`, `common/`, `alembic/`, `scripts/`, `tests/`
- Важные файлы: `requirements.txt`, `Procfile`, `runtime.txt`, `README.md`, `env.example`

### 3. Конфигурация
- Безопасная копия настроек (без секретов)
- `env.example` файл

### 4. Логи
- Все файлы логов из директории `logs/`

## 🔧 Создание бэкапа

### Автоматическое создание
```bash
# Создать полный бэкап
python scripts/backup.py
```

### Ручное создание
```bash
# Создать бэкап с дополнительными опциями
python scripts/backup_system.py
```

## 🔄 Восстановление системы

### 1. Быстрое восстановление (только база данных)
```bash
# Восстановить только базу данных
python scripts/restore_system.py backups/checkyourcrypto_backup_YYYYMMDD_HHMMSS.zip
```

### 2. Полное восстановление (код + база данных)
```bash
# Восстановить код и базу данных
python scripts/restore_system.py backups/checkyourcrypto_backup_YYYYMMDD_HHMMSS.zip --restore-code
```

### 3. Полное восстановление (все компоненты)
```bash
# Восстановить все компоненты
python scripts/restore_system.py backups/checkyourcrypto_backup_YYYYMMDD_HHMMSS.zip --restore-code --restore-config
```

### 4. Просмотр доступных бэкапов
```bash
# Показать список всех бэкапов
python scripts/restore_system.py --list
```

## 📋 Пошаговое восстановление

### Шаг 1: Подготовка
```bash
# 1. Остановите все процессы бота
pkill -f "python.*bot"
heroku ps:scale worker=0 --app checkyourcrypto-bot

# 2. Перейдите в директорию проекта
cd /path/to/checkyourcrypto

# 3. Активируйте виртуальное окружение
source venv/bin/activate
```

### Шаг 2: Выбор бэкапа
```bash
# Просмотрите доступные бэкапы
python scripts/restore_system.py --list

# Выберите нужный бэкап (самый свежий или конкретная дата)
```

### Шаг 3: Восстановление
```bash
# Восстановите систему
python scripts/restore_system.py backups/checkyourcrypto_backup_YYYYMMDD_HHMMSS.zip --restore-code
```

### Шаг 4: Проверка конфигурации
```bash
# 1. Проверьте переменные окружения
cat .env

# 2. Убедитесь, что все секреты на месте:
# - BOT_TOKEN
# - ALERT_BOT_TOKEN
# - METASLEUTH_WALLET_SCREENING_KEY
# - METASLEUTH_ADDRESS_LABEL_KEY
# - DATABASE_URL
# - ADMIN_SECRET
# - DJANGO_SECRET_KEY
```

### Шаг 5: Запуск системы
```bash
# 1. Примените миграции (если нужно)
alembic upgrade head

# 2. Запустите бота локально для тестирования
python -m bot.main

# 3. Если все работает, разверните на Heroku
git add .
git commit -m "Восстановление из бэкапа"
git push heroku main

# 4. Запустите worker на Heroku
heroku ps:scale worker=1 --app checkyourcrypto-bot
```

## 🔍 Проверка восстановления

### 1. Проверка базы данных
```bash
# Подключитесь к базе данных
heroku pg:psql --app checkyourcrypto-bot

# Проверьте количество записей
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM checks;
SELECT COUNT(*) FROM payments;
```

### 2. Проверка бота
```bash
# Проверьте логи
heroku logs --tail --app checkyourcrypto-bot

# Отправьте тестовое сообщение боту
```

### 3. Проверка админки
```bash
# Откройте админку
open https://checkyourcrypto-bot-87c446f24699.herokuapp.com/admin/
```

## 🚨 Аварийное восстановление

### Если бэкап поврежден
```bash
# 1. Попробуйте восстановить из другого бэкапа
python scripts/restore_system.py --list

# 2. Если нет бэкапов, используйте git
git log --oneline
git checkout <commit-hash>
```

### Если база данных недоступна
```bash
# 1. Проверьте статус Heroku PostgreSQL
heroku pg:info --app checkyourcrypto-bot

# 2. Если нужно, создайте новую базу
heroku addons:create heroku-postgresql:mini --app checkyourcrypto-bot

# 3. Обновите DATABASE_URL
heroku config:set DATABASE_URL=<new-database-url> --app checkyourcrypto-bot
```

### Если код поврежден
```bash
# 1. Восстановите из git
git reset --hard HEAD
git clean -fd

# 2. Или используйте последний рабочий коммит
git log --oneline
git reset --hard <working-commit-hash>
```

## 📊 Мониторинг после восстановления

### 1. Проверьте логи
```bash
# Мониторинг логов в реальном времени
heroku logs --tail --app checkyourcrypto-bot | grep -E "(ERROR|Exception|Failed)"
```

### 2. Проверьте метрики
```bash
# Статистика базы данных
heroku pg:info --app checkyourcrypto-bot

# Статистика dyno
heroku ps --app checkyourcrypto-bot
```

### 3. Тестовые проверки
- Отправьте команду `/start` боту
- Нажмите кнопку "🔍 Проверка"
- Отправьте тестовый адрес
- Проверьте платную проверку

## 🔧 Автоматизация

### Создание бэкапа по расписанию
```bash
# Добавьте в crontab (ежедневный бэкап в 2:00)
0 2 * * * cd /path/to/checkyourcrypto && python scripts/backup.py
```

### Мониторинг бэкапов
```bash
# Скрипт для проверки свежести бэкапов
python scripts/check_backups.py
```

## 📞 Поддержка

### Если восстановление не помогло
1. **Соберите информацию:**
   - Логи ошибок
   - Версия Python
   - Версии зависимостей
   - Статус Heroku

2. **Проверьте документацию:**
   - `docs_global_prompt.md`
   - `CURRENT_STATUS.md`
   - `README.md`

3. **Обратитесь к разработчику:**
   - Предоставьте полную информацию об ошибке
   - Приложите логи и конфигурацию

## ✅ Чек-лист восстановления

- [ ] Остановлены все процессы бота
- [ ] Выбран правильный бэкап
- [ ] Восстановлена база данных
- [ ] Восстановлен код (если нужно)
- [ ] Проверены переменные окружения
- [ ] Применены миграции
- [ ] Протестирован бот локально
- [ ] Развернут на Heroku
- [ ] Проверена работа в продакшене
- [ ] Создан новый бэкап после восстановления

---

**⚠️ Важно:** Всегда создавайте новый бэкап после успешного восстановления!
