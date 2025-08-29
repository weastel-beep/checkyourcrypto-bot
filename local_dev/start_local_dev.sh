#!/bin/bash

# Скрипт для запуска локальной среды разработки
# Использование: ./start_local_dev.sh [bot|admin|all]

set -e

echo "🚀 Запуск локальной среды разработки CheckYourCrypto"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Функция для запуска инфраструктуры
start_infrastructure() {
    echo "🔧 Запуск инфраструктуры (PostgreSQL, Redis)..."
    cd "$(dirname "$0")"
    docker-compose up -d postgres_local redis_local
    
    echo "⏳ Ожидание готовности PostgreSQL..."
    sleep 10
    
    echo "✅ Инфраструктура запущена!"
    echo "   📊 PostgreSQL: localhost:5433"
    echo "   🔴 Redis: localhost:6380"
}

# Функция для запуска локальной админки
start_local_admin() {
    echo "🖥️ Запуск локальной админки..."
    cd "$(dirname "$0")"
    docker-compose up -d local_admin_api
    
    echo "✅ Локальная админка запущена!"
    echo "   🌐 Admin API: http://localhost:8001"
    echo "   📋 API Docs: http://localhost:8001/docs"
}

# Функция для запуска локального бота
start_local_bot() {
    echo "🤖 Запуск локального бота..."
    
    # Проверяем наличие .env файла
    if [ ! -f "../.env" ]; then
        echo "❌ Файл .env не найден. Создайте .env файл с настройками бота."
        exit 1
    fi
    
    # Загружаем переменные окружения
    export $(cat ../.env | grep -v '^#' | xargs)
    
    # Устанавливаем переменные для локальной разработки
    export ENVIRONMENT=local
    export API_BASE_URL=http://localhost:8001
    export DATABASE_URL=postgresql://local_user:local_password@localhost:5433/checkyourcrypto_local
    
    echo "🔧 Переменные окружения установлены:"
    echo "   🌍 ENVIRONMENT: $ENVIRONMENT"
    echo "   🌐 API_BASE_URL: $API_BASE_URL"
    echo "   🗄️ DATABASE_URL: $DATABASE_URL"
    
    # Запускаем локального бота
    cd "$(dirname "$0")/local_bot"
    python main.py
}

# Функция для остановки всех сервисов
stop_all() {
    echo "🛑 Остановка всех сервисов..."
    cd "$(dirname "$0")"
    docker-compose down
    
    echo "✅ Все сервисы остановлены!"
}

# Функция для просмотра логов
show_logs() {
    echo "📋 Показать логи..."
    cd "$(dirname "$0")"
    docker-compose logs -f
}

# Функция для сброса базы данных
reset_db() {
    echo "🗑️ Сброс локальной базы данных..."
    cd "$(dirname "$0")"
    docker-compose down -v
    docker-compose up -d postgres_local redis_local
    
    echo "✅ База данных сброшена!"
}

# Основная логика
case "${1:-all}" in
    "infrastructure")
        start_infrastructure
        ;;
    "admin")
        start_infrastructure
        start_local_admin
        ;;
    "bot")
        start_infrastructure
        start_local_admin
        start_local_bot
        ;;
    "all")
        start_infrastructure
        start_local_admin
        echo ""
        echo "🎉 Локальная среда разработки запущена!"
        echo ""
        echo "📋 Доступные сервисы:"
        echo "   🌐 Admin API: http://localhost:8001"
        echo "   📋 API Docs: http://localhost:8001/docs"
        echo "   📊 PostgreSQL: localhost:5433"
        echo "   🔴 Redis: localhost:6380"
        echo ""
        echo "🤖 Для запуска локального бота выполните:"
        echo "   ./start_local_dev.sh bot"
        echo ""
        echo "📋 Для просмотра логов:"
        echo "   ./start_local_dev.sh logs"
        ;;
    "stop")
        stop_all
        ;;
    "logs")
        show_logs
        ;;
    "reset")
        reset_db
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo ""
        echo "📋 Доступные команды:"
        echo "   infrastructure - запустить только инфраструктуру"
        echo "   admin         - запустить инфраструктуру + админку"
        echo "   bot           - запустить инфраструктуру + админку + бота"
        echo "   all           - запустить все сервисы (по умолчанию)"
        echo "   stop          - остановить все сервисы"
        echo "   logs          - показать логи"
        echo "   reset         - сбросить базу данных"
        exit 1
        ;;
esac
