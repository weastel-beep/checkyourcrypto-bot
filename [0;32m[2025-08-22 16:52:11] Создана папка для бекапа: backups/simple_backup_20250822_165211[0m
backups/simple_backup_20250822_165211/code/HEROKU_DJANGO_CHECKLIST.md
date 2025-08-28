# ✅ Чек-лист Heroku + Django для Check Your Crypto

## 🚀 Перед деплоем

### Переменные окружения
- [ ] `BOT_TOKEN` установлен в Heroku Config Vars
- [ ] `DATABASE_URL` автоматически настроен Heroku
- [ ] `DJANGO_SECRET_KEY` установлен
- [ ] `ADMIN_SECRET` установлен
- [ ] `DEBUG=false` для продакшена
- [ ] `ENVIRONMENT=production`

### База данных
- [ ] PostgreSQL addon подключен
- [ ] Django миграции применены: `heroku run python admin_app/manage.py migrate`
- [ ] SQLAlchemy миграции применены: `heroku run alembic upgrade head`
- [ ] Схема БД соответствует моделям

### Код
- [ ] Все изменения закоммичены в git
- [ ] Тесты проходят локально
- [ ] Линтеры не выдают ошибок
- [ ] Импорты исправлены для продакшена

---

## 🔧 После деплоя

### Проверка деплоя
- [ ] `git push heroku main` завершился успешно
- [ ] Build прошел без ошибок
- [ ] Приложение запустилось: `heroku ps`
- [ ] Логи без критических ошибок: `heroku logs --tail`

### Проверка функциональности
- [ ] Django админка доступна: `https://app.herokuapp.com/api/panel/`
- [ ] Health check работает: `https://app.herokuapp.com/health`
- [ ] Telegram бот отвечает
- [ ] Массовые сообщения работают

### Мониторинг
- [ ] Логирование настроено
- [ ] Ошибки отслеживаются
- [ ] Метрики собираются

---

## 🚨 Типичные проблемы

### 1. "No module named 'aiosqlite'"
**Проверка:**
- [ ] В `common/config.py` используется `sqlalchemy_database_url`
- [ ] На Heroku используется PostgreSQL, не SQLite
- [ ] `asyncpg` установлен в `requirements.txt`

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

### 2. "'Settings' object has no attribute 'BOT_TOKEN'"
**Проверка:**
- [ ] `BOT_TOKEN` установлен в Heroku Config Vars
- [ ] Django settings.py загружает переменные окружения
- [ ] Используется `django.conf.settings`, не `common.config`

**Решение:**
```python
# admin_app/settings.py
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'default-token')
```

### 3. "column does not exist"
**Проверка:**
- [ ] Схема БД соответствует моделям
- [ ] Миграции применены
- [ ] Имена колонок правильные

**Решение:**
```bash
# Проверить схему
heroku pg:psql --app app-name
\d table_name

# Применить миграции
heroku run python admin_app/manage.py migrate
```

### 4. "WSGI application could not be loaded"
**Проверка:**
- [ ] Procfile правильный
- [ ] WSGI файл существует
- [ ] Путь к settings модулю правильный

**Решение:**
```bash
# Procfile
web: cd admin_app && gunicorn wsgi:application

# admin_app/wsgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
```

---

## 🔄 Workflow для изменений

### 1. Локальная разработка
```bash
# Настройка
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Тестирование
pytest
black .
flake8 .
```

### 2. Подготовка к деплою
```bash
# Коммит
git add .
git commit -m "Description of changes"

# Проверка
heroku config --app app-name
```

### 3. Деплой
```bash
# Пуш на Heroku
git push heroku main

# Проверка логов
heroku logs --tail --app app-name
```

### 4. Пост-деплой проверка
```bash
# Статус
heroku ps --app app-name

# Миграции
heroku run python admin_app/manage.py migrate --app app-name

# Тестирование функциональности
curl https://app-name.herokuapp.com/health
```

---

## 📊 Мониторинг и поддержка

### Ежедневные проверки
- [ ] Логи без ошибок
- [ ] Бот отвечает
- [ ] Админка доступна
- [ ] База данных работает

### Еженедельные проверки
- [ ] Бэкап базы данных
- [ ] Обновление зависимостей
- [ ] Проверка метрик
- [ ] Очистка логов

### Ежемесячные проверки
- [ ] Обзор безопасности
- [ ] Оптимизация производительности
- [ ] Обновление документации
- [ ] Планирование улучшений

---

## 🛠️ Полезные команды

### Диагностика
```bash
# Статус приложения
heroku ps --app app-name

# Логи
heroku logs --tail --app app-name

# Переменные окружения
heroku config --app app-name

# Консоль
heroku run python --app app-name
```

### База данных
```bash
# Подключение к БД
heroku pg:psql --app app-name

# Информация о БД
heroku pg:info --app app-name

# Бэкап
heroku pg:backups:capture --app app-name
```

### Управление приложением
```bash
# Перезапуск
heroku restart --app app-name

# Масштабирование
heroku ps:scale web=1 worker=1 --app app-name

# Откат
heroku rollback --app app-name
```

---

## 🎯 Ключевые принципы

### 1. Безопасность
- ✅ Все секреты в переменных окружения
- ✅ HTTPS в продакшене
- ✅ Валидация входных данных
- ✅ Регулярные обновления

### 2. Надежность
- ✅ Автоматические бэкапы
- ✅ Мониторинг ошибок
- ✅ Health checks
- ✅ Graceful degradation

### 3. Производительность
- ✅ Кэширование
- ✅ Оптимизация запросов
- ✅ Асинхронная обработка
- ✅ Connection pooling

### 4. Поддерживаемость
- ✅ Документация
- ✅ Логирование
- ✅ Тестирование
- ✅ Версионирование

---

## 📞 Экстренные контакты

### Heroku Support
- [Heroku Status](https://status.heroku.com/)
- [Heroku Support](https://help.heroku.com/)

### Полезные ссылки
- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Внутренние ресурсы
- [HEROKU_DJANGO_GUIDE.md](./HEROKU_DJANGO_GUIDE.md)
- [DEPLOYMENT_REPORT.md](./DEPLOYMENT_REPORT.md)
- [CURRENT_STATUS.md](./CURRENT_STATUS.md)
