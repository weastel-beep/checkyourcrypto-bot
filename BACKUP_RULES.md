# 🔄 Правила бэкапа через GitHub

## 📋 Основные принципы

### 1. **Всегда коммитить перед изменениями**
```bash
# Перед любыми изменениями
git add .
git commit -m "Backup before [описание изменений]"
git push origin main
```

### 2. **Создавать ветки для экспериментов**
```bash
# Для экспериментов
git checkout -b experiment/[название-эксперимента]
# ... делаем изменения ...
git push origin experiment/[название-эксперимента]
```

### 3. **Тегировать важные версии**
```bash
# После успешного деплоя
git tag -a v1.2.3 -m "Stable version 1.2.3"
git push origin v1.2.3
```

---

## 🚨 Критические моменты для бэкапа

### Перед изменением:
- [ ] **API эндпоинтов**
- [ ] **Структуры базы данных**
- [ ] **Конфигурации деплоя**
- [ ] **Основной бизнес-логики**

### После успешного деплоя:
- [ ] **Создать тег версии**
- [ ] **Обновить документацию**
- [ ] **Проверить работоспособность**

---

## 📁 Структура бэкапов

### 1. **Автоматические бэкапы (GitHub)**
```
main/                    # Основная ветка (всегда стабильная)
├── v1.2.3/             # Теги стабильных версий
├── hotfix/             # Срочные исправления
└── feature/            # Новые функции
```

### 2. **Локальные бэкапы**
```
backups/
├── manual_backup_YYYYMMDD_HHMMSS/
│   ├── code/           # Копия кода
│   ├── database_backup.sql
│   └── config_backup/
└── auto_backup_YYYYMMDD_HHMMSS/
```

---

## 🔧 Команды для бэкапа

### Быстрый бэкап перед изменениями:
```bash
#!/bin/bash
# backup_before_changes.sh

DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/manual_backup_${DATE}"

echo "Creating backup: ${BACKUP_DIR}"

# Создаем папку
mkdir -p "${BACKUP_DIR}/code"
mkdir -p "${BACKUP_DIR}/config"

# Копируем код (исключая node_modules, venv, etc)
rsync -av --exclude='node_modules' --exclude='venv' --exclude='__pycache__' --exclude='.git' . "${BACKUP_DIR}/code/"

# Бэкап базы данных
pg_dump $DATABASE_URL > "${BACKUP_DIR}/database_backup.sql"

# Бэкап конфигов
cp .env* "${BACKUP_DIR}/config/" 2>/dev/null || true
cp Procfile "${BACKUP_DIR}/config/" 2>/dev/null || true

echo "Backup created: ${BACKUP_DIR}"
```

### Автоматический бэкап через GitHub Actions:
```yaml
# .github/workflows/backup.yml
name: Auto Backup

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Каждый день в 2:00

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Create backup
        run: |
          DATE=$(date +"%Y%m%d_%H%M%S")
          echo "Creating backup: $DATE"
          # Логика бэкапа
          
      - name: Upload backup
        uses: actions/upload-artifact@v2
        with:
          name: backup-${{ github.sha }}
          path: backup/
```

---

## 🚀 Восстановление из бэкапа

### Из GitHub:
```bash
# Восстановить конкретную версию
git checkout v1.2.3

# Восстановить из ветки
git checkout feature/backup-branch
```

### Из локального бэкапа:
```bash
# Восстановить код
cp -r backups/manual_backup_20250828_143000/code/* .

# Восстановить базу данных
psql $DATABASE_URL < backups/manual_backup_20250828_143000/database_backup.sql

# Восстановить конфиги
cp backups/manual_backup_20250828_143000/config/* .
```

---

## 📊 Мониторинг бэкапов

### Проверка статуса:
```bash
# Последние коммиты
git log --oneline -10

# Последние теги
git tag --sort=-version:refname | head -5

# Статус веток
git branch -a
```

### Автоматические проверки:
- [ ] **GitHub Actions** - автоматические тесты
- [ ] **Heroku Health Checks** - проверка работоспособности
- [ ] **Database Integrity** - проверка целостности БД

---

## ⚠️ Важные напоминания

1. **НЕ коммитить секреты** в Git
2. **Всегда тестировать** перед деплоем
3. **Документировать изменения** в commit messages
4. **Создавать теги** для стабильных версий
5. **Проверять работоспособность** после восстановления

---

## 🔗 Полезные ссылки

- **GitHub Repository**: https://github.com/username/checkyourcrypto
- **Heroku Dashboard**: https://dashboard.heroku.com/apps
- **Database Dashboard**: https://data.heroku.com/databases
