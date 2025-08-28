# Check Your Crypto - Админка

Современная веб-админка для управления ботом Check Your Crypto.

## 🚀 Быстрый деплой на Render.com (бесплатно)

### 1. Подготовка репозитория

1. Убедитесь, что все файлы закоммичены в git
2. Создайте репозиторий на GitHub/GitLab

### 2. Деплой на Render.com

1. Зайдите на [render.com](https://render.com) и создайте аккаунт
2. Нажмите "New +" → "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройте параметры:
   - **Name:** `checkyourcrypto-admin`
   - **Environment:** `Python 3`
   - **Build Command:** `chmod +x build.sh && ./build.sh`
   - **Start Command:** `gunicorn wsgi:application`
   - **Root Directory:** `admin_app`

5. В разделе "Environment Variables" добавьте:
   - `DJANGO_SETTINGS_MODULE`: `settings`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`

6. Нажмите "Create Web Service"

### 3. Создание администратора

После деплоя выполните в терминале Render:

```bash
python create_admin.py
```

И следуйте инструкциям для создания первого администратора.

## 🔧 Локальная разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка базы данных

```bash
python setup_db.py
```

### Запуск сервера

```bash
python manage.py runserver
```

### Создание суперпользователя

```bash
python create_superuser.py
```

## 📱 Доступ к админке

- **URL:** `https://your-app-name.onrender.com/api/admin/login/`
- **Локально:** `http://localhost:8000/api/admin/login/`

## 🎯 Функции админки

### ✅ Реализовано:
- 🔐 Аутентификация с ролями (суперадмин, админ, модератор)
- 📊 Дашборд с аналитикой
- 👥 Управление пользователями бота
- 💬 Система массовых сообщений
- 📝 Управление текстами бота
- 📋 Логирование действий администраторов
- 🎨 Современный интерфейс (Tailwind CSS + Alpine.js)

### 🚧 В разработке:
- 🔐 2FA аутентификация
- 📈 Расширенная аналитика
- 📧 Система приглашений
- 🤖 Интеграция с Telegram API

## 🛠 Технический стек

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** Tailwind CSS + Alpine.js
- **Database:** PostgreSQL (продакшен) / SQLite (разработка)
- **Authentication:** JWT + Session-based
- **Deployment:** Render.com

## 📁 Структура проекта

```
admin_app/
├── core/
│   ├── admin_models.py    # Модели админки
│   ├── admin_views.py     # Views админки
│   ├── models.py          # Модели бота
│   └── urls.py           # URL маршруты
├── templates/
│   └── admin/            # Шаблоны админки
├── build.sh              # Скрипт сборки
├── render.yaml           # Конфигурация Render
├── requirements.txt      # Зависимости
└── settings.py          # Настройки Django
```

## 🔒 Безопасность

- JWT токены для API
- Ролевая система доступа
- Логирование всех действий
- CSRF защита
- XSS защита

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Render Dashboard
2. Убедитесь, что все переменные окружения настроены
3. Проверьте, что база данных создана и миграции применены
