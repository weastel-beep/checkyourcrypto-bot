#!/bin/bash

# 🚨 СКРИПТ ДЛЯ ОЧИСТКИ СЕКРЕТОВ ИЗ ИСТОРИИ GIT
# ⚠️  ВНИМАНИЕ: Этот скрипт переписывает историю Git!
# ⚠️  Убедитесь, что у вас есть резервная копия репозитория!

set -e

echo "🚨 НАЧАЛО ОЧИСТКИ СЕКРЕТОВ ИЗ ИСТОРИИ GIT"
echo "=========================================="

# Проверяем, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: Не найден .git каталог. Убедитесь, что вы в корне git репозитория."
    exit 1
fi

# Проверяем статус рабочей директории
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Ошибка: Есть незакоммиченные изменения. Сначала закоммитьте или отмените их."
    git status
    exit 1
fi

echo "✅ Проверки пройдены. Начинаем очистку..."

# Список файлов с секретами для удаления
SECRET_FILES=(
    ".env.backup.20250826_165441"
    ".env_temp"
    "backups/*/code/.env*"
    "backups/*/code/*config.txt"
    "backups/*/code/heroku_config.txt"
)

echo "🗑️  Удаляем файлы с секретами из истории..."

# Используем git filter-branch для удаления файлов из истории
for file in "${SECRET_FILES[@]}"; do
    echo "Удаляем: $file"
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch '$file'" \
        --prune-empty --tag-name-filter cat -- --all
done

# Очищаем reflog
echo "🧹 Очищаем reflog..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Удаляем старые backup ветки если они есть
echo "🧹 Удаляем старые backup ветки..."
git for-each-ref --format='%(refname:short)' refs/original/ | xargs -n 1 git update-ref -d 2>/dev/null || true

echo "✅ Очистка завершена!"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo "1. Отзовите все найденные токены в соответствующих сервисах"
echo "2. Создайте новые токены"
echo "3. Обновите .env файлы с новыми токенами"
echo "4. Принудительно запушьте изменения: git push --force-with-lease --all"
echo "5. Уведомите всех разработчиков о необходимости переклонировать репозиторий"
echo ""
echo "⚠️  ВАЖНО: Все разработчики должны переклонировать репозиторий после этого!"
