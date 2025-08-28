#!/bin/bash

# 🧹 СКРИПТ АВТОМАТИЧЕСКОЙ ОЧИСТКИ ПРОЕКТА
# Удаляет временные файлы, кэш и старые бекапы

set -e

echo "🧹 НАЧАЛО АВТОМАТИЧЕСКОЙ ОЧИСТКИ ПРОЕКТА"
echo "=========================================="

# Проверяем, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: Не найден .git каталог. Убедитесь, что вы в корне git репозитория."
    exit 1
fi

echo "✅ Проверки пройдены. Начинаем очистку..."

# 1. Удаление Python кэша
echo "🗑️  Удаляем Python кэш..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# 2. Очистка логов (оставляем только последние 100 строк)
echo "📝 Очищаем старые логи..."
if [ -d "logs" ]; then
    find logs/ -name "*.log" -type f -exec sh -c 'tail -100 "$1" > "$1.tmp" && mv "$1.tmp" "$1"' _ {} \; 2>/dev/null || true
fi

# 3. Удаление node_modules из бекапов
echo "🗑️  Удаляем node_modules из бекапов..."
find backups/ -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true

# 4. Удаление venv из бекапов
echo "🗑️  Удаляем venv из бекапов..."
find backups/ -name "venv" -type d -exec rm -rf {} + 2>/dev/null || true

# 5. Удаление вложенных бекапов
echo "🗑️  Удаляем вложенные бекапы..."
find backups/ -path "*/backups/*" -type d -exec rm -rf {} + 2>/dev/null || true

# 6. Удаление временных файлов
echo "🗑️  Удаляем временные файлы..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true

# 7. Удаление старых бекапов (оставляем только последние 2)
echo "🗑️  Удаляем старые бекапы..."
if [ -d "backups" ]; then
    cd backups
    # Сортируем по дате и удаляем все кроме последних 2
    ls -1t | tail -n +3 | xargs -r rm -rf
    cd ..
fi

# 8. Очистка логов в бекапах
echo "📝 Очищаем логи в бекапах..."
find backups/ -name "*.log" -type f -delete 2>/dev/null || true

# 9. Удаление временных скриптов из бекапов
echo "🗑️  Удаляем временные скрипты из бекапов..."
find backups/ -name "fix_*.py" -delete 2>/dev/null || true
find backups/ -name "test_*.py" -delete 2>/dev/null || true
find backups/ -name "update_*.py" -delete 2>/dev/null || true
find backups/ -name "create_*.py" -delete 2>/dev/null || true

# 10. Проверка размера
echo "📊 Проверяем размер проекта..."
TOTAL_SIZE=$(du -sh . | cut -f1)
echo "✅ Общий размер проекта: $TOTAL_SIZE"

# 11. Проверка на большие файлы
echo "🔍 Ищем большие файлы..."
find . -type f -size +100M 2>/dev/null | head -5 | while read file; do
    echo "⚠️  Большой файл: $file ($(du -sh "$file" | cut -f1))"
done

echo ""
echo "✅ АВТОМАТИЧЕСКАЯ ОЧИСТКА ЗАВЕРШЕНА!"
echo ""
echo "📋 РЕЗУЛЬТАТЫ:"
echo "- Удален Python кэш"
echo "- Очищены старые логи"
echo "- Удалены node_modules из бекапов"
echo "- Удалены venv из бекапов"
echo "- Удалены вложенные бекапы"
echo "- Удалены временные файлы"
echo "- Оставлены только последние 2 бекапа"
echo ""
echo "📊 Размер проекта: $TOTAL_SIZE"
echo ""
echo "💡 Рекомендации:"
echo "- Запускайте этот скрипт еженедельно"
echo "- Настройте cron для автоматического запуска"
echo "- Мониторьте размер проекта регулярно"
