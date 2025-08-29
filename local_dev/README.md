# 🏠 Локальная среда разработки CheckYourCrypto

Этот раздел содержит локальную среду разработки для быстрого тестирования бота и админки без деплоя на Heroku.

## 🚀 Быстрый старт

### 1. Подготовка
```bash
# Убедитесь, что у вас установлены:
# - Docker и Docker Compose
# - Python 3.9+
# - Файл .env с настройками бота

# Сделайте скрипт исполняемым
chmod +x start_local_dev.sh
```

### 2. Запуск локальной среды
```bash
# Запустить всю инфраструктуру + админку
./start_local_dev.sh all

# Или по частям:
./start_local_dev.sh infrastructure  # Только PostgreSQL + Redis
./start_local_dev.sh admin           # + Локальная админка
./start_local_dev.sh bot             # + Локальный бот
```

### 3. Доступные сервисы
- 🌐 **Admin API**: http://localhost:8001
- 📋 **API Docs**: http://localhost:8001/docs
- 📊 **PostgreSQL**: localhost:5433
- 🔴 **Redis**: localhost:6380

## 🔧 Управление

### Команды управления
```bash
./start_local_dev.sh stop    # Остановить все сервисы
./start_local_dev.sh logs    # Показать логи
./start_local_dev.sh reset   # Сбросить базу данных
```

### Запуск локального бота
```bash
# После запуска инфраструктуры и админки:
./start_local_dev.sh bot
```

## 📁 Структура

```
local_dev/
├── docker-compose.yml      # Docker конфигурация
├── start_local_dev.sh      # Скрипт управления
├── local_bot/              # Локальная версия бота
│   └── main.py            # Точка входа локального бота
├── local_admin/            # Локальная версия админки
└── README.md              # Этот файл
```

## 🔄 Рабочий процесс

### Для разработки бота:
1. Запустите инфраструктуру: `./start_local_dev.sh infrastructure`
2. Запустите админку: `./start_local_dev.sh admin`
3. Запустите локального бота: `./start_local_dev.sh bot`
4. Тестируйте изменения в реальном времени
5. При необходимости деплойте на Heroku

### Для разработки админки:
1. Запустите инфраструктуру: `./start_local_dev.sh infrastructure`
2. Запустите админку: `./start_local_dev.sh admin`
3. Изменения в коде админки автоматически перезагружаются
4. Тестируйте API через http://localhost:8001/docs

## 🌍 Переменные окружения

Локальная среда автоматически устанавливает:
- `ENVIRONMENT=local`
- `API_BASE_URL=http://localhost:8001`
- `DATABASE_URL=postgresql://local_user:local_password@localhost:5433/checkyourcrypto_local`

## 🗄️ База данных

### Подключение к локальной БД:
```bash
# Через psql
psql -h localhost -p 5433 -U local_user -d checkyourcrypto_local

# Через Docker
docker exec -it checkyourcrypto_postgres_local psql -U local_user -d checkyourcrypto_local
```

### Синхронизация с продакшеном:
```bash
# Экспорт данных из продакшена
heroku pg:backups:capture -a checkyourcrypto-bot
heroku pg:backups:download -a checkyourcrypto-bot

# Импорт в локальную БД
pg_restore --host=localhost --port=5433 --username=local_user --dbname=checkyourcrypto_local latest.dump
```

## 🐛 Отладка

### Просмотр логов:
```bash
# Все сервисы
./start_local_dev.sh logs

# Конкретный сервис
docker-compose logs -f local_admin_api
docker-compose logs -f postgres_local
```

### Проверка статуса:
```bash
docker-compose ps
```

## ⚠️ Важные замечания

1. **Локальная БД изолирована** от продакшена
2. **Изменения в коде** автоматически перезагружаются
3. **Переменные окружения** переопределяются для локальной среды
4. **Порты** настроены так, чтобы не конфликтовать с другими сервисами

## 🔗 Полезные ссылки

- [Docker Compose документация](https://docs.docker.com/compose/)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [python-telegram-bot документация](https://python-telegram-bot.readthedocs.io/)
