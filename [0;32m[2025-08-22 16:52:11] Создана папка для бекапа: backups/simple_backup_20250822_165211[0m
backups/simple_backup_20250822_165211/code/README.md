# Check Your Crypto

Telegram-бот для проверки криптовалютных адресов на безопасность и риски.

## 🚀 Быстрый старт

### Локальная разработка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd checkyourcrypto
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
cp env.example .env
# Отредактируйте .env файл с вашими значениями
```

5. **Настройте базу данных:**
```bash
# Создайте PostgreSQL базу данных
createdb checkyourcrypto

# Примените миграции
alembic upgrade head
```

6. **Запустите компоненты:**
```bash
# Основной бот
python -m bot.main

# Админка (в отдельном терминале)
python -m admin_app.manage runserver

# Alerts бот (в отдельном терминале)
python -m alerts_bot.main
```

## 🏗️ Архитектура

- **`bot/`** - Основной Telegram-бот (aiogram v3)
- **`alerts_bot/`** - Бот для оповещений операторов
- **`admin_app/`** - Django админка для управления контентом
- **`common/`** - Общие компоненты (модели, конфигурация)
- **`alembic/`** - Миграции базы данных

## 🔧 Конфигурация

### Обязательные переменные окружения:

- `BOT_TOKEN` - Токен основного Telegram-бота
- `ALERT_BOT_TOKEN` - Токен бота для оповещений
- `OPS_CHAT_ID` - ID чата для операционных уведомлений
- `METASLEUTH_API_KEY` - Ключ API MetaSleuth
- `DATABASE_URL` - URL базы данных PostgreSQL
- `ADMIN_SECRET` - Секрет для входа в админку

### Поддерживаемые блокчейны:

BTC, ETH, TRON, Solana, Optimism, Cronos, BSC, Gnosis, Polygon, Manta, BitTorrent, Fantom, Boba, zkSync, CLV, Polygon zkEVM, WEMIX, Moonbeam, Moonriver, Mantle, Base, Arbitrum, Celo, Avalanche, Linea, Blast, Aurora

## 🚀 Деплой на Heroku

1. **Создайте приложение:**
```bash
heroku create your-app-name
```

2. **Добавьте PostgreSQL:**
```bash
heroku addons:create heroku-postgresql:mini
```

3. **Настройте переменные окружения:**
```bash
heroku config:set BOT_TOKEN=your_token
heroku config:set ALERT_BOT_TOKEN=your_token
heroku config:set OPS_CHAT_ID=your_chat_id
heroku config:set METASLEUTH_API_KEY=your_key
heroku config:set ADMIN_SECRET=your_secret
heroku config:set AWS_S3_BUCKET=your_bucket
heroku config:set AWS_ACCESS_KEY_ID=your_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
heroku config:set AWS_REGION=us-east-1
```

4. **Примените миграции:**
```bash
heroku run alembic upgrade head
```

5. **Запустите процессы:**
```bash
heroku ps:scale web=1 worker=1 alerts=1
```

## 📊 Мониторинг

- **Health Check:** `https://your-app.herokuapp.com/health`
- **Sentry:** Автоматический мониторинг ошибок
- **Alerts Bot:** Уведомления в Telegram чат операторов

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=.

# Только unit тесты
pytest tests/unit/

# Только интеграционные тесты
pytest tests/integration/
```

## 🔄 Бэкапы

### Автоматический бэкап:
```bash
# Ежедневный бэкап в S3
scripts/backup_db.sh
```

### Восстановление:
```bash
# Восстановление из бэкапа
scripts/restore_db.sh latest_backup.sql.gz
```

## 📝 API Документация

### MetaSleuth Integration

- **Wallet Screening API:** Проверка рисков адреса
- **Address Label API:** Получение меток и информации

### Основные эндпоинты

- `POST /api/check/` - Проверка адреса
- `GET /api/user/{tg_id}/` - Информация о пользователе
- `POST /api/payment/` - Создание платежа

## 🤝 Разработка

### Структура коммитов:
- `feat:` - Новая функциональность
- `fix:` - Исправление багов
- `docs:` - Документация
- `refactor:` - Рефакторинг
- `test:` - Тесты

### Code Style:
```bash
# Форматирование
black .
isort .

# Проверка стиля
flake8 .
mypy .
```

## 📞 Поддержка

- **Telegram:** @CheckYourCrypto_bot
- **Email:** support@checkyourcrypto.com
- **Issues:** GitHub Issues

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.
