#!/bin/bash

# Скрипт для быстрого бэкапа перед изменениями
# Использование: ./backup_before_changes.sh [описание изменений]

DATE=$(date +"%Y%m%d_%H%M%S")
DESCRIPTION=${1:-"manual_changes"}
BACKUP_DIR="backups/manual_backup_${DATE}_${DESCRIPTION}"

echo "🔄 Создаем бэкап: ${BACKUP_DIR}"

# Создаем папки
mkdir -p "${BACKUP_DIR}/code"
mkdir -p "${BACKUP_DIR}/config"
mkdir -p "${BACKUP_DIR}/database"

echo "📁 Создаем папки..."

# Копируем код (исключая ненужные файлы)
echo "📦 Копируем код..."
rsync -av --exclude='node_modules' \
         --exclude='venv' \
         --exclude='__pycache__' \
         --exclude='.git' \
         --exclude='backups' \
         --exclude='logs' \
         --exclude='*.pyc' \
         --exclude='.DS_Store' \
         . "${BACKUP_DIR}/code/"

# Бэкап конфигов
echo "⚙️ Копируем конфиги..."
cp .env* "${BACKUP_DIR}/config/" 2>/dev/null || true
cp Procfile "${BACKUP_DIR}/config/" 2>/dev/null || true
cp requirements.txt "${BACKUP_DIR}/config/" 2>/dev/null || true
cp alembic.ini "${BACKUP_DIR}/config/" 2>/dev/null || true

# Бэкап базы данных (если есть DATABASE_URL)
if [ ! -z "$DATABASE_URL" ]; then
    echo "🗄️ Бэкап базы данных..."
    pg_dump "$DATABASE_URL" > "${BACKUP_DIR}/database/database_backup.sql" 2>/dev/null || echo "⚠️ Не удалось создать бэкап БД"
else
    echo "⚠️ DATABASE_URL не установлен, пропускаем бэкап БД"
fi

# Создаем файл с информацией о бэкапе
cat > "${BACKUP_DIR}/backup_info.txt" << EOF
Бэкап создан: $(date)
Описание: ${DESCRIPTION}
Ветка: $(git branch --show-current)
Коммит: $(git rev-parse HEAD)
Файлы изменены: $(git status --porcelain | wc -l)
EOF

echo "✅ Бэкап создан: ${BACKUP_DIR}"
echo "📋 Информация о бэкапе:"
cat "${BACKUP_DIR}/backup_info.txt"

# Коммитим в Git
echo "🔄 Коммитим в Git..."
git add .
git commit -m "Backup before: ${DESCRIPTION} (${DATE})" || echo "⚠️ Не удалось создать коммит"

echo "🎉 Бэкап завершен!"
echo "📁 Папка: ${BACKUP_DIR}"
echo "💡 Для восстановления: cp -r ${BACKUP_DIR}/code/* ."
