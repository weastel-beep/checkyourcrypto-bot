# 🏠 Локальная разработка CheckYourCrypto

## 📋 Обзор

Этот проект теперь поддерживает локальную разработку для быстрого тестирования без деплоя на Heroku.

## 🏗️ Архитектура

```
checkyourcrypto/
├── bot/                    # 🤖 Продакшен бот (Heroku)
├── admin_panel_new/        # 🖥️ Продакшен админка (Heroku)
├── local_dev/              # 🏠 Локальная среда разработки
│   ├── docker-compose.yml  # 🐳 Docker конфигурация
│   ├── local_bot/          # 🤖 Локальный бот
│   ├── local_admin/        # 🖥️ Локальная админка
│   └── scripts/            # 📜 Скрипты управления
└── common/                 # 🔧 Общие компоненты
```

## 🚀 Быстрый старт

### 1. Подготовка
```bash
# Убедитесь, что у вас установлены:
# - Docker и Docker Compose
# - Python 3.9+
# - Heroku CLI
# - Файл .env с настройками бота

cd local_dev
chmod +x *.sh
```

### 2. Синхронизация с продакшеном
```bash
# Синхронизировать базу данных и конфигурацию
./sync_with_production.sh all
```

### 3. Запуск локальной среды
```bash
# Запустить всю инфраструктуру
./start_local_dev.sh all

# В отдельном терминале запустить локального бота
./start_local_dev.sh bot
```

## 🔄 Рабочий процесс

### Для разработки бота:
1. **Синхронизация**: `./sync_with_production.sh all`
2. **Запуск инфраструктуры**: `./start_local_dev.sh infrastructure`
3. **Запуск админки**: `./start_local_dev.sh admin`
4. **Запуск бота**: `./start_local_dev.sh bot`
5. **Тестирование**: Изменения в коде бота применяются мгновенно
6. **Деплой**: При готовности деплойте на Heroku

### Для разработки админки:
1. **Синхронизация**: `./sync_with_production.sh all`
2. **Запуск инфраструктуры**: `./start_local_dev.sh infrastructure`
3. **Запуск админки**: `./start_local_dev.sh admin`
4. **Тестирование**: Изменения в коде админки перезагружаются автоматически
5. **API тестирование**: http://localhost:8001/docs

## 🌐 Доступные сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| Admin API | http://localhost:8001 | Локальная админка API |
| API Docs | http://localhost:8001/docs | Swagger документация |
| PostgreSQL | localhost:5433 | Локальная база данных |
| Redis | localhost:6380 | Локальный кэш |

## 🔧 Управление

### Основные команды:
```bash
# Запуск
./start_local_dev.sh all          # Вся инфраструктура + админка
./start_local_dev.sh infrastructure # Только PostgreSQL + Redis
./start_local_dev.sh admin         # + Локальная админка
./start_local_dev.sh bot           # + Локальный бот

# Управление
./start_local_dev.sh stop          # Остановить все сервисы
./start_local_dev.sh logs          # Показать логи
./start_local_dev.sh reset         # Сбросить базу данных

# Синхронизация
./sync_with_production.sh all      # Полная синхронизация
./sync_with_production.sh db       # Только база данных
./sync_with_production.sh config   # Только конфигурация
```

## 🗄️ База данных

### Подключение:
```bash
# Через psql
psql -h localhost -p 5433 -U local_user -d checkyourcrypto_local

# Через Docker
docker exec -it checkyourcrypto_postgres_local psql -U local_user -d checkyourcrypto_local
```

### Синхронизация с продакшеном:
```bash
# Автоматическая синхронизация
./sync_with_production.sh db

# Ручная синхронизация
heroku pg:backups:capture -a checkyourcrypto-bot
heroku pg:backups:download -a checkyourcrypto-bot
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

### Отладка бота:
```bash
# Локальный бот выводит логи в консоль
# Изменения в коде применяются мгновенно
```

## ⚙️ Конфигурация

### Переменные окружения:
Локальная среда автоматически устанавливает:
- `ENVIRONMENT=local`
- `API_BASE_URL=http://localhost:8001`
- `DATABASE_URL=postgresql://local_user:local_password@localhost:5433/checkyourcrypto_local`

### Файл .env:
Создайте файл `.env` в корне проекта с настройками бота:
```env
BOT_TOKEN=your_bot_token_here
API_BASE_URL=http://localhost:8001
DATABASE_URL=postgresql://local_user:local_password@localhost:5433/checkyourcrypto_local
ENVIRONMENT=local
```

## 🔄 Преимущества локальной разработки

### ✅ Быстрое тестирование
- Изменения применяются мгновенно
- Нет необходимости в деплое
- Быстрая отладка

### ✅ Изолированная среда
- Локальная БД не влияет на продакшен
- Можно экспериментировать безопасно
- Легкий сброс к чистому состоянию

### ✅ Синхронизация с продакшеном
- Общая схема БД
- Актуальные данные
- Совместимость конфигурации

### ✅ Удобное управление
- Простые команды
- Автоматическая настройка
- Подробная документация

## 🚨 Важные замечания

1. **Локальная БД изолирована** от продакшена
2. **Изменения в коде** автоматически перезагружаются
3. **Переменные окружения** переопределяются для локальной среды
4. **Порты** настроены так, чтобы не конфликтовать с другими сервисами
5. **Синхронизация** с продакшеном выполняется по требованию

## 🔗 Полезные ссылки

- [Docker Compose документация](https://docs.docker.com/compose/)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [python-telegram-bot документация](https://python-telegram-bot.readthedocs.io/)
- [Heroku CLI документация](https://devcenter.heroku.com/articles/heroku-cli)

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `./start_local_dev.sh logs`
2. Сбросьте БД: `./start_local_dev.sh reset`
3. Перезапустите: `./start_local_dev.sh stop && ./start_local_dev.sh all`
