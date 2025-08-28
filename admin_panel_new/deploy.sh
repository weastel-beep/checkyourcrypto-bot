#!/bin/bash

echo "🚀 Начинаем деплой админки на Heroku..."

# Проверяем, что мы в правильной директории
if [ ! -f "app/main.py" ]; then
    echo "❌ Ошибка: файл app/main.py не найден. Убедитесь, что вы в директории admin_panel_new"
    exit 1
fi

# Проверяем, что Heroku CLI установлен
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI не установлен. Установите его с https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Проверяем статус Heroku
echo "📋 Проверяем статус Heroku..."
heroku auth:whoami

# Создаем Procfile если его нет
if [ ! -f "Procfile" ]; then
    echo "📝 Создаем Procfile..."
    echo "web: uvicorn app.main:app --host=0.0.0.0 --port=\$PORT" > Procfile
fi

# Проверяем requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден"
    exit 1
fi

# Добавляем psutil в requirements.txt если его нет
if ! grep -q "psutil" requirements.txt; then
    echo "📝 Добавляем psutil в requirements.txt..."
    echo "psutil==5.9.5" >> requirements.txt
fi

# Коммитим изменения
echo "📦 Коммитим изменения..."
git add .
git commit -m "Fix auth endpoint and add logging improvements"

# Деплоим на Heroku
echo "🚀 Деплоим на Heroku..."
heroku container:push web --app checkyourcrypto-admin-api-new-51ea71c68148

if [ $? -eq 0 ]; then
    echo "✅ Деплой успешен!"
    
    # Ждем немного и проверяем
    echo "⏳ Ждем запуска сервера..."
    sleep 10
    
    # Проверяем health check
    echo "🔍 Проверяем health check..."
    curl -s "https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com/health"
    
    echo ""
    echo "🔍 Проверяем тестовый эндпоинт..."
    curl -s "https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com/test"
    
    echo ""
    echo "🔍 Проверяем auth эндпоинт..."
    curl -s -X POST "https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com/api/auth/login"
    
    echo ""
    echo "🎉 Деплой завершен! Проверьте админку:"
    echo "https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com/"
    
else
    echo "❌ Ошибка при деплое"
    exit 1
fi
