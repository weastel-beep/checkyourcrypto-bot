# 🚀 Check Your Crypto Admin Panel

Современная админ-панель для бота Check Your Crypto, построенная на FastAPI + Vue.js.

## 📋 Структура проекта

```
admin_panel_new/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI приложение
│   │   ├── core/           # Основные компоненты
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── api/           # API роуты
│   │   └── services/      # Бизнес-логика
│   ├── requirements.txt
│   └── Procfile
├── frontend/              # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue компоненты
│   │   ├── views/        # Страницы
│   │   ├── stores/       # Pinia stores
│   │   └── services/     # API сервисы
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🛠️ Технологический стек

### Backend (FastAPI)
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **Pydantic** - валидация данных
- **JWT** - аутентификация
- **PostgreSQL** - база данных

### Frontend (Vue.js)
- **Vue 3** - прогрессивный фреймворк
- **Vue Router** - маршрутизация
- **Pinia** - управление состоянием
- **Tailwind CSS** - стили
- **Chart.js** - графики
- **Axios** - HTTP клиент

## 🚀 Быстрый старт

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 Функционал

### ✅ Реализовано
- [x] Аутентификация (JWT)
- [x] Дашборд с статистикой
- [x] Графики активности
- [x] API структура
- [x] Модели данных

### 🔄 В разработке
- [ ] Управление пользователями
- [ ] Массовые сообщения
- [ ] Управление текстами
- [ ] Vue.js компоненты
- [ ] Деплой на Heroku

## 🌐 API Endpoints

### Аутентификация
- `POST /api/auth/login` - вход в систему
- `GET /api/auth/me` - информация о пользователе

### Дашборд
- `GET /api/dashboard/stats` - статистика
- `GET /api/dashboard/charts/user-activity` - график активности
- `GET /api/dashboard/charts/blockchain` - график блокчейнов
- `GET /api/dashboard/charts/revenue` - график выручки

## 🔐 Безопасность

- JWT токены для аутентификации
- Хеширование паролей (bcrypt)
- CORS настройки
- Валидация данных (Pydantic)

## 📈 Мониторинг

- Health check эндпоинт: `/health`
- Автоматическая документация: `/docs`
- ReDoc документация: `/redoc`

## 🚀 Деплой

### Heroku
```bash
# Backend
heroku create checkyourcrypto-admin-api
git push heroku main

# Frontend
heroku create checkyourcrypto-admin-frontend
git push heroku main
```

## 📝 Лицензия

MIT License

---

**Создано для Check Your Crypto Bot** 🚀
