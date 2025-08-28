# CheckYourCrypto 🤖

Telegram бот для проверки криптовалютных адресов с AI-анализом рисков.

## 🚀 Быстрый старт

### Архитектура
- **Bot API** (`bot/`) - Telegram бот
- **Admin Panel** (`admin_panel_new/`) - Веб-интерфейс управления
- **Common** (`common/`) - Общие модули

### Деплой
```bash
# Bot API
git push heroku main

# Admin Panel API  
git push heroku main

# Admin Panel Frontend
cd admin_panel_new/frontend && npm run build
```

## 📚 Документация

- [Архитектура проекта](PROJECT_ARCHITECTURE.md)
- [Правила бэкапа](BACKUP_RULES.md)

## 🔧 Разработка

```bash
# Бэкап перед изменениями
./backup_before_changes.sh "описание изменений"

# Запуск локально
python bot/main.py                    # Bot API
cd admin_panel_new && uvicorn app.main:app --reload  # Admin API
cd admin_panel_new/frontend && npm run dev           # Frontend
```

## 🌐 URLs

- **Bot**: https://checkyourcrypto-bot.herokuapp.com
- **Admin API**: https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com
- **Admin UI**: https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com

## 📊 Статус

✅ **Bot API** - Работает  
✅ **Admin API** - Работает  
✅ **Admin UI** - Работает  
✅ **Database** - Работает  

---

**Последнее обновление**: 2025-08-28
