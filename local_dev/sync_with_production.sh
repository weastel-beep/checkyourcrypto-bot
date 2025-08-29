#!/bin/bash

# Скрипт для синхронизации локальной среды с продакшеном
# Использование: ./sync_with_production.sh [db|config|all]

set -e

echo "🔄 Синхронизация с продакшеном CheckYourCrypto"

# Функция для синхронизации базы данных
sync_database() {
    echo "🗄️ Синхронизация базы данных..."
    
    # Создаем бэкап продакшена
    echo "📦 Создание бэкапа продакшена..."
    heroku pg:backups:capture -a checkyourcrypto-bot
    
    # Скачиваем бэкап
    echo "⬇️ Скачивание бэкапа..."
    heroku pg:backups:download -a checkyourcrypto-bot -o latest.dump
    
    # Останавливаем локальные сервисы
    echo "🛑 Остановка локальных сервисов..."
    docker-compose down
    
    # Удаляем старые данные
    echo "🗑️ Удаление старых данных..."
    docker volume rm local_dev_postgres_data 2>/dev/null || true
    
    # Запускаем PostgreSQL
    echo "🔧 Запуск PostgreSQL..."
    docker-compose up -d postgres_local
    
    # Ждем готовности
    echo "⏳ Ожидание готовности PostgreSQL..."
    sleep 15
    
    # Восстанавливаем данные
    echo "📥 Восстановление данных..."
    pg_restore --host=localhost --port=5433 --username=local_user --dbname=checkyourcrypto_local --clean --if-exists latest.dump
    
    # Удаляем временный файл
    rm -f latest.dump
    
    echo "✅ База данных синхронизирована!"
}

# Функция для синхронизации конфигурации
sync_config() {
    echo "⚙️ Синхронизация конфигурации..."
    
    # Копируем переменные окружения из продакшена
    echo "📋 Получение переменных окружения..."
    heroku config -a checkyourcrypto-bot > production_config.txt
    
    echo "✅ Конфигурация сохранена в production_config.txt"
    echo "📝 Проверьте файл и обновите .env при необходимости"
}

# Функция для полной синхронизации
sync_all() {
    echo "🔄 Полная синхронизация..."
    sync_database
    sync_config
    
    echo "🎉 Полная синхронизация завершена!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Проверьте production_config.txt"
    echo "2. Обновите .env файл при необходимости"
    echo "3. Запустите локальную среду: ./start_local_dev.sh all"
}

# Основная логика
case "${1:-all}" in
    "db")
        sync_database
        ;;
    "config")
        sync_config
        ;;
    "all")
        sync_all
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo ""
        echo "📋 Доступные команды:"
        echo "   db     - синхронизировать только базу данных"
        echo "   config - синхронизировать только конфигурацию"
        echo "   all    - полная синхронизация (по умолчанию)"
        exit 1
        ;;
esac
