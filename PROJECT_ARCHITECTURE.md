# CheckYourCrypto - Архитектура проекта

## 🏗️ Общая структура

```
checkyourcrypto/
├── bot/                    # Telegram бот API
├── admin_panel_new/        # Админ панель (Frontend + Backend)
├── common/                 # Общие модули
├── alembic/               # Миграции базы данных
├── tests/                 # Тесты
└── logs/                  # Логи
```

## 🤖 Telegram Bot API (`bot/`)

**Назначение**: Обработка Telegram сообщений и проверка криптоадресов

**Основные файлы**:
- `bot/main.py` - Главный файл бота (FastAPI + Telegram)
- `bot/api.py` - API эндпоинты для бота
- `bot/handlers/` - Обработчики команд и сообщений
- `bot/health.py` - Health check эндпоинты
- `bot/middleware.py` - Middleware для логирования и метрик

**Эндпоинты**:
- `POST /webhook` - Webhook от Telegram
- `GET /health` - Health check
- `GET /api/stats` - Статистика бота

**База данных**: Использует общую БД через `common/database.py`

---

## 🖥️ Admin Panel API (`admin_panel_new/app/`)

**Назначение**: Управление сценариями бота и текстами

**Основные файлы**:
- `admin_panel_new/app/main.py` - Главный FastAPI сервер
- `admin_panel_new/app/api/` - API эндпоинты
- `admin_panel_new/app/models/` - Модели данных
- `admin_panel_new/app/schemas/` - Pydantic схемы

**Эндпоинты**:
- `POST /api/auth/login` - Авторизация
- `GET /api/bot-flow/scenarios` - Получение сценариев
- `GET /api/bot-flow/texts` - Получение текстов
- `GET /health` - Health check
- `GET /test` - Тестовый эндпоинт

**База данных**: Использует общую БД через `common/database.py`

---

## 🎨 Admin Panel Frontend (`admin_panel_new/frontend/`)

**Назначение**: Веб-интерфейс для управления ботом

**Технологии**: Vue.js 3 + Vite + Tailwind CSS

**Основные файлы**:
- `admin_panel_new/frontend/src/views/BotFlowDesigner.vue` - Flow Designer
- `admin_panel_new/frontend/src/services/api.js` - API клиент
- `admin_panel_new/frontend/src/utils/logger.js` - Логирование

**URL**: https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com

---

## 🔧 Common Modules (`common/`)

**Назначение**: Общие модули для всех частей системы

**Основные файлы**:
- `common/database.py` - Подключение к PostgreSQL
- `common/config.py` - Конфигурация
- `common/models.py` - Общие модели данных
- `common/services.py` - Бизнес-логика
- `common/integrations/` - Интеграции с внешними сервисами

---

## 🗄️ База данных

**Тип**: PostgreSQL (Heroku Postgres)

**Миграции**: Alembic (`alembic/`)

**Основные таблицы**:
- `users` - Пользователи бота
- `scenarios` - Сценарии бота
- `bot_texts` - Тексты бота
- `checks` - История проверок

---

## 🚀 Деплой

### Bot API
- **Heroku App**: `checkyourcrypto-bot`
- **Procfile**: `web: python bot/main.py`
- **URL**: https://checkyourcrypto-bot.herokuapp.com

### Admin Panel API
- **Heroku App**: `checkyourcrypto-admin-api-new`
- **Procfile**: `web: uvicorn admin_panel_new.app.main:app --host 0.0.0.0 --port $PORT`
- **URL**: https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com

### Admin Panel Frontend
- **Heroku App**: `checkyourcrypto-admin-ui`
- **Procfile**: `web: npm run preview`
- **URL**: https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com

---

## 🔄 Workflow

1. **Пользователь** отправляет адрес в Telegram боту
2. **Bot API** обрабатывает сообщение и выполняет проверку
3. **Admin Panel** позволяет настраивать сценарии и тексты
4. **Общая БД** хранит все данные

---

## 📝 Логирование

- **Bot API**: Структурированные логи в `logs/`
- **Admin API**: JSON логи в stdout
- **Frontend**: Console логи + структурированные логи

---

## 🧪 Тестирование

- **Unit тесты**: `tests/unit/`
- **Integration тесты**: `tests/integration/`
- **Запуск**: `pytest tests/`

---

## 🔑 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://...

# Bot
BOT_TOKEN=...
HEROKU_APP_NAME=...

# Admin Panel
ADMIN_API_URL=https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com
```

---

## 📚 Полезные команды

```bash
# Запуск бота локально
python bot/main.py

# Запуск админ API локально
cd admin_panel_new && uvicorn app.main:app --reload

# Запуск фронтенда локально
cd admin_panel_new/frontend && npm run dev

# Деплой на Heroku
git push heroku main

# Проверка логов
heroku logs --tail --app checkyourcrypto-admin-api-new
```
