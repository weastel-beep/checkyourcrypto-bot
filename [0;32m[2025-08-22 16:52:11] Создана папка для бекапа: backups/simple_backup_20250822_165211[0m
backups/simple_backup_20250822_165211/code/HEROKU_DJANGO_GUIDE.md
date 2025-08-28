# 🚀 Полное руководство по Heroku и Django для Check Your Crypto

## 📋 Содержание
1. [Архитектура Heroku](#архитектура-heroku)
2. [Конфигурация Django](#конфигурация-django)
3. [Переменные окружения](#переменные-окружения)
4. [База данных](#база-данных)
5. [Деплой](#деплой)
6. [Мониторинг](#мониторинг)
7. [Типичные проблемы и решения](#типичные-проблемы)
8. [Best Practices](#best-practices)

---

## 🏗️ Архитектура Heroku

### Структура приложения
```
checkyourcrypto/
├── admin_app/          # Django приложение
│   ├── core/          # Основные модели и views
│   ├── settings.py    # Django настройки
│   └── wsgi.py        # WSGI конфигурация
├── bot/               # Telegram бот
├── common/            # Общие модули
├── Procfile           # Heroku процессы
└── requirements.txt   # Зависимости
```

### Heroku процессы (Procfile)
```bash
web: cd admin_app && gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: python bot/main_simple.py
alerts: python -m alerts_bot.main
```

**Объяснение:**
- **web**: Django веб-приложение (админка)
- **worker**: Telegram бот для обработки сообщений
- **alerts**: Система уведомлений

### Dynos (контейнеры)
- **Web Dyno**: Обрабатывает HTTP запросы
- **Worker Dyno**: Фоновые задачи
- **Alerts Dyno**: Система уведомлений

---

## ⚙️ Конфигурация Django

### Ключевые настройки (settings.py)

#### 1. Переменные окружения
```python
import os
from dotenv import load_dotenv
load_dotenv()  # Загружает .env файл

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-secret')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
```

#### 2. База данных
```python
import dj_database_url

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./db.sqlite3')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}
```

#### 3. Статические файлы
```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

#### 4. WSGI конфигурация
```python
# admin_app/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
application = get_wsgi_application()
```

---

## 🔧 Переменные окружения

### Heroku Config Vars
```bash
# Установка переменных
heroku config:set BOT_TOKEN=your_token
heroku config:set DATABASE_URL=postgresql://...
heroku config:set DJANGO_SECRET_KEY=your_secret

# Просмотр всех переменных
heroku config --app checkyourcrypto-bot

# Просмотр конкретной переменной
heroku config:get BOT_TOKEN --app checkyourcrypto-bot
```

### Локальная разработка (.env)
```env
# Telegram
BOT_TOKEN=your_bot_token
ALERT_BOT_TOKEN=your_alert_token
OPS_CHAT_ID=your_chat_id

# Database
DATABASE_URL=sqlite:///./checkyourcrypto.db
SQLALCHEMY_DATABASE_URL=sqlite+aiosqlite:///./checkyourcrypto.db

# Django
DJANGO_SECRET_KEY=your_secret_key
ADMIN_SECRET=your_admin_secret

# Environment
DEBUG=true
ENVIRONMENT=development
```

### Автоматические переменные Heroku
- `PORT`: Порт для веб-приложения
- `DATABASE_URL`: PostgreSQL URL (автоматически)
- `HEROKU_APP_NAME`: Имя приложения
- `HEROKU_RELEASE_VERSION`: Версия релиза

---

## 🗄️ База данных

### PostgreSQL на Heroku
```python
# Django (синхронный)
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# SQLAlchemy (асинхронный)
@property
def sqlalchemy_database_url(self) -> str:
    django_db_url = os.getenv('DATABASE_URL')
    if django_db_url.startswith('postgresql://'):
        return django_db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return django_db_url
```

### Миграции
```bash
# Django миграции
heroku run python admin_app/manage.py migrate

# SQLAlchemy миграции (Alembic)
heroku run alembic upgrade head
```

### Бэкапы
```bash
# Создание бэкапа
heroku pg:backups:capture --app checkyourcrypto-bot

# Скачивание бэкапа
heroku pg:backups:download --app checkyourcrypto-bot
```

---

## 🚀 Деплой

### Процесс деплоя
```bash
# 1. Коммит изменений
git add .
git commit -m "Your changes"

# 2. Деплой на Heroku
git push heroku main

# 3. Применение миграций
heroku run python admin_app/manage.py migrate

# 4. Сбор статических файлов
heroku run python admin_app/manage.py collectstatic --noinput
```

### Buildpack
Heroku автоматически определяет Python приложение и использует:
- Python buildpack
- Установка зависимостей из `requirements.txt`
- Сбор статических файлов Django

### Runtime.txt
```txt
python-3.11.13
```
**Важно:** Указывать только major.minor версию для автоматических обновлений.

---

## 📊 Мониторинг

### Логи
```bash
# Просмотр логов в реальном времени
heroku logs --tail --app checkyourcrypto-bot

# Последние 100 строк
heroku logs --num 100 --app checkyourcrypto-bot

# Логи конкретного dyno
heroku logs --dyno web.1 --app checkyourcrypto-bot
```

### Статус приложения
```bash
# Статус dynos
heroku ps --app checkyourcrypto-bot

# Перезапуск приложения
heroku restart --app checkyourcrypto-bot

# Масштабирование
heroku ps:scale web=1 worker=1 --app checkyourcrypto-bot
```

### Health Check
```python
# admin_app/core/views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

---

## 🚨 Типичные проблемы и решения

### 1. Ошибка "No module named 'aiosqlite'"
**Причина:** SQLAlchemy пытается использовать SQLite на Heroku
**Решение:**
```python
# common/config.py
@property
def sqlalchemy_database_url(self) -> str:
    django_db_url = os.getenv('DATABASE_URL')
    if django_db_url.startswith('postgresql://'):
        return django_db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return django_db_url
```

### 2. Ошибка "'Settings' object has no attribute 'BOT_TOKEN'"
**Причина:** Django не может найти переменную окружения
**Решение:**
```python
# admin_app/settings.py
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'default-token')
```

### 3. Ошибка "column does not exist"
**Причина:** Несоответствие схемы базы данных
**Решение:**
```python
# Проверить схему
heroku pg:psql --app checkyourcrypto-bot
\d mass_messages

# Применить миграции
heroku run python admin_app/manage.py migrate
```

### 4. Ошибка "WSGI application could not be loaded"
**Причина:** Неправильный путь к WSGI приложению
**Решение:**
```python
# Procfile
web: cd admin_app && gunicorn wsgi:application

# admin_app/wsgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
```

### 5. Ошибка "Database connection failed"
**Причина:** Проблемы с подключением к PostgreSQL
**Решение:**
```bash
# Проверить статус базы данных
heroku pg:info --app checkyourcrypto-bot

# Перезапустить базу данных
heroku pg:restart --app checkyourcrypto-bot
```

---

## ✅ Best Practices

### 1. Переменные окружения
- ✅ Всегда используйте переменные окружения для секретов
- ✅ Не коммитьте .env файлы в git
- ✅ Используйте разные значения для dev/prod
- ✅ Валидируйте переменные при запуске

### 2. База данных
- ✅ Используйте миграции для изменений схемы
- ✅ Делайте бэкапы перед деплоем
- ✅ Тестируйте миграции на staging
- ✅ Используйте connection pooling

### 3. Логирование
- ✅ Структурированные логи
- ✅ Разные уровни для dev/prod
- ✅ Мониторинг ошибок (Sentry)
- ✅ Ротация логов

### 4. Безопасность
- ✅ HTTPS в продакшене
- ✅ Валидация входных данных
- ✅ Rate limiting
- ✅ CORS настройки

### 5. Производительность
- ✅ Кэширование статических файлов
- ✅ Оптимизация запросов к БД
- ✅ Асинхронная обработка
- ✅ Мониторинг метрик

---

## 🔄 Workflow разработки

### 1. Локальная разработка
```bash
# Настройка окружения
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск Django
cd admin_app
python manage.py runserver

# Запуск бота
python bot/main_simple.py
```

### 2. Тестирование
```bash
# Запуск тестов
pytest

# Проверка кода
black .
flake8 .
mypy .
```

### 3. Деплой
```bash
# Подготовка
git add .
git commit -m "Your changes"

# Деплой
git push heroku main

# Проверка
heroku logs --tail
```

### 4. Мониторинг
```bash
# Статус
heroku ps

# Логи
heroku logs --tail

# Метрики
heroku addons:open scout
```

---

## 📚 Полезные команды

### Heroku CLI
```bash
# Информация о приложении
heroku info --app checkyourcrypto-bot

# Переменные окружения
heroku config --app checkyourcrypto-bot

# Логи
heroku logs --tail --app checkyourcrypto-bot

# Консоль
heroku run python --app checkyourcrypto-bot

# База данных
heroku pg:psql --app checkyourcrypto-bot
```

### Django
```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic

# Shell
python manage.py shell
```

### Git
```bash
# Добавление Heroku remote
heroku git:remote -a checkyourcrypto-bot

# Деплой
git push heroku main

# Откат
heroku rollback
```

---

## 🎯 Заключение

Этот проект демонстрирует правильную архитектуру для Django приложения на Heroku:

1. **Разделение ответственности**: Django для веб-интерфейса, отдельные процессы для бота
2. **Правильная конфигурация БД**: PostgreSQL для продакшена, SQLite для разработки
3. **Безопасность**: Все секреты в переменных окружения
4. **Мониторинг**: Логирование и health checks
5. **Масштабируемость**: Асинхронная обработка и connection pooling

Следуя этим принципам, можно избежать большинства проблем при деплое Django приложений на Heroku.
