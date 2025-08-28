# 🔄 ИНСТРУКЦИИ ПО ПОЛНОМУ БЕКАПУ СИСТЕМЫ CHECK YOUR CRYPTO

## 📋 ЧТО БЕКАПИМ

### 1. 💻 КОД ПРОЕКТА
- Весь исходный код Django приложения
- Конфигурационные файлы
- Шаблоны и статические файлы
- Миграции базы данных

### 2. 🗄️ БАЗА ДАННЫХ
- Все таблицы и данные
- Пользователи бота
- История проверок
- Платежи и транзакции
- Настройки системы

### 3. 🔧 СИСТЕМНЫЕ НАСТРОЙКИ
- Переменные окружения
- Конфигурация Heroku
- Настройки Django

## 🚀 КОМАНДЫ ДЛЯ БЕКАПА

### Шаг 1: Создание папки для бекапа
```bash
# Создаем папку с текущей датой и временем
BACKUP_DIR="backups/full_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📁 Создана папка для бекапа: $BACKUP_DIR"
```

### Шаг 2: Бэкап кода проекта
```bash
# Копируем весь проект (исключая ненужные файлы)
rsync -av --exclude='.git' \
         --exclude='__pycache__' \
         --exclude='*.pyc' \
         --exclude='.env' \
         --exclude='venv' \
         --exclude='node_modules' \
         --exclude='backups' \
         --exclude='*.log' \
         ./ "$BACKUP_DIR/code/"
echo "💻 Код проекта скопирован"
```

### Шаг 3: Бэкап базы данных
```bash
# Получаем DATABASE_URL из переменных окружения
DATABASE_URL=$(heroku config:get DATABASE_URL -a checkyourcrypto-bot-87c446f24699)

# Создаем дамп базы данных
pg_dump "$DATABASE_URL" > "$BACKUP_DIR/database_backup.sql"
echo "🗄️ База данных сохранена в $BACKUP_DIR/database_backup.sql"

# Также создаем сжатый вариант
gzip "$BACKUP_DIR/database_backup.sql"
echo "🗄️ База данных сжата в $BACKUP_DIR/database_backup.sql.gz"
```

### Шаг 4: Бэкап переменных окружения
```bash
# Сохраняем все переменные окружения
heroku config -a checkyourcrypto-bot-87c446f24699 > "$BACKUP_DIR/heroku_config.txt"
echo "🔧 Переменные окружения сохранены"

# Создаем .env файл для локальной разработки (без секретов)
cat > "$BACKUP_DIR/.env.example" << EOF
# Пример переменных окружения
# Скопируйте этот файл в .env и заполните реальными значениями

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# База данных
DATABASE_URL=postgresql://user:password@host:port/database

# Telegram Bot
BOT_TOKEN=your-bot-token-here

# Платежи
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key

# Другие настройки
ALLOWED_HOSTS=checkyourcrypto-bot-87c446f24699.herokuapp.com
EOF
echo "📝 Создан пример .env файла"
```

### Шаг 5: Бэкап системной информации
```bash
# Информация о системе
echo "=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===" > "$BACKUP_DIR/system_info.txt"
echo "Дата бекапа: $(date)" >> "$BACKUP_DIR/system_info.txt"
echo "Версия Python: $(python --version)" >> "$BACKUP_DIR/system_info.txt"
echo "Версия Django: $(python -c 'import django; print(django.get_version())')" >> "$BACKUP_DIR/system_info.txt"
echo "Версия PostgreSQL: $(psql --version)" >> "$BACKUP_DIR/system_info.txt"

# Информация о Heroku
echo "" >> "$BACKUP_DIR/system_info.txt"
echo "=== HEROKU ИНФОРМАЦИЯ ===" >> "$BACKUP_DIR/system_info.txt"
heroku info -a checkyourcrypto-bot-87c446f24699 >> "$BACKUP_DIR/system_info.txt"

# Список установленных пакетов
echo "" >> "$BACKUP_DIR/system_info.txt"
echo "=== УСТАНОВЛЕННЫЕ ПАКЕТЫ ===" >> "$BACKUP_DIR/system_info.txt"
pip freeze > "$BACKUP_DIR/requirements_backup.txt"
echo "📦 Список пакетов сохранен"
```

### Шаг 6: Создание архива
```bash
# Создаем финальный архив
ARCHIVE_NAME="checkyourcrypto_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$ARCHIVE_NAME" -C "$BACKUP_DIR" .
echo "📦 Создан архив: $ARCHIVE_NAME"

# Проверяем размер архива
ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
echo "📊 Размер архива: $ARCHIVE_SIZE"
```

### Шаг 7: Очистка временных файлов
```bash
# Удаляем временную папку
rm -rf "$BACKUP_DIR"
echo "🧹 Временные файлы удалены"
```

## 🔄 ВОССТАНОВЛЕНИЕ ИЗ БЕКАПА

### Восстановление кода:
```bash
# Распаковываем архив
tar -xzf checkyourcrypto_backup_YYYYMMDD_HHMMSS.tar.gz

# Копируем код в нужную папку
cp -r code/* /path/to/project/
```

### Восстановление базы данных:
```bash
# Распаковываем дамп если он сжат
gunzip database_backup.sql.gz

# Восстанавливаем базу данных
psql "$DATABASE_URL" < database_backup.sql
```

### Восстановление переменных окружения:
```bash
# Устанавливаем переменные в Heroku
heroku config:set $(cat heroku_config.txt | grep -v "^===" | tr '\n' ' ') -a checkyourcrypto-bot-87c446f24699
```

## 📊 ПРОВЕРКА БЕКАПА

### Проверка целостности архива:
```bash
tar -tzf checkyourcrypto_backup_YYYYMMDD_HHMMSS.tar.gz | head -20
```

### Проверка размера файлов:
```bash
ls -lh checkyourcrypto_backup_*.tar.gz
```

### Проверка базы данных:
```bash
# Проверяем, что дамп не пустой
wc -l database_backup.sql
```

## 🚨 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Безопасность**: Архив содержит чувствительные данные, храните его в безопасном месте
2. **Регулярность**: Рекомендуется делать бекап еженедельно
3. **Тестирование**: Периодически тестируйте восстановление из бекапа
4. **Версионирование**: Храните несколько версий бекапов

## 📞 В СЛУЧАЕ ПРОБЛЕМ

Если возникли проблемы с бекапом:
1. Проверьте подключение к интернету
2. Убедитесь, что у вас есть доступ к Heroku
3. Проверьте права доступа к файлам
4. Убедитесь, что PostgreSQL клиент установлен

## 🎯 АВТОМАТИЗАЦИЯ

Для автоматизации бекапа можно создать скрипт:
```bash
#!/bin/bash
# backup_script.sh
# Добавьте этот скрипт в cron для автоматических бекапов
# 0 2 * * 0 /path/to/backup_script.sh  # Каждое воскресенье в 2:00
```

---

**Дата создания инструкций:** $(date)
**Версия:** 1.0
**Автор:** AI Assistant
