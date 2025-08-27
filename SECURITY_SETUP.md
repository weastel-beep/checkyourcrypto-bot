# 🔒 НАСТРОЙКА БЕЗОПАСНОСТИ ПОСЛЕ ОЧИСТКИ СЕКРЕТОВ

## 1. Немедленные действия (КРИТИЧНО)

### Отзвать скомпрометированные токены:
1. **Telegram Bot Token**: Отзвать в @BotFather
2. **MetaSleuth API Keys**: Отзвать в MetaSleuth dashboard
3. **OpenAI API Key**: Отзвать в OpenAI dashboard

### Создать новые токены:
1. Создать новый Telegram Bot Token
2. Создать новые MetaSleuth API Keys
3. Создать новый OpenAI API Key

## 2. Очистка истории Git

### Выполнить скрипт очистки:
```bash
chmod +x cleanup_secrets.sh
./cleanup_secrets.sh
```

### Принудительно запушеть изменения:
```bash
git push --force-with-lease --all
git push --force-with-lease --tags
```

## 3. Настройка pre-commit хуков

### Установить detect-secrets:
```bash
pip install detect-secrets[YAML]
```

### Инициализировать baseline:
```bash
detect-secrets scan --baseline .secrets.baseline .
```

### Установить pre-commit хуки:
```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## 4. Обновление production среды

### Обновить переменные окружения:
1. Heroku: `heroku config:set BOT_TOKEN=new_token`
2. Render: Обновить в dashboard
3. Локальные серверы: Обновить .env файлы

### Перезапустить сервисы:
```bash
# Heroku
heroku restart

# Render
# Через dashboard или API

# Локальные серверы
sudo systemctl restart your-service
```

## 5. Уведомление команды

### Сообщить всем разработчикам:
- Переклонировать репозиторий
- Обновить локальные .env файлы
- Установить pre-commit хуки

## 6. Мониторинг

### Настроить автоматические проверки:
- GitHub Actions для сканирования секретов
- Регулярные аудиты безопасности
- Мониторинг подозрительной активности

## 7. Документация

### Обновить документацию:
- Добавить секцию безопасности в README
- Создать checklist для новых разработчиков
- Документировать процедуры безопасности

## Статус: В ПРОЦЕССЕ ВЫПОЛНЕНИЯ
