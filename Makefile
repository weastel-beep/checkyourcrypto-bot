.PHONY: backup restore deploy logs

# Создание бекапа
backup:
	@echo "🤖 Создание бекапа..."
	@mkdir -p backups/backup_$(shell date +%Y%m%d_%H%M%S)
	@cp -r . backups/backup_$(shell date +%Y%m%d_%H%M%S)/code/
	@echo "✅ Бекап создан: backups/backup_$(shell date +%Y%m%d_%H%M%S)"

# Восстановление из бекапа
restore:
	@echo "🔄 Восстановление из бекапа..."
	@if [ -z "$(BACKUP_PATH)" ]; then \
		echo "❌ Укажите путь к бекапу: make restore BACKUP_PATH=backups/backup_YYYYMMDD_HHMMSS"; \
		exit 1; \
	fi
	@if [ ! -d "$(BACKUP_PATH)" ]; then \
		echo "❌ Бекап не найден: $(BACKUP_PATH)"; \
		exit 1; \
	fi
	@echo "📦 Восстанавливаем код..."
	@cp -r $(BACKUP_PATH)/code/* .
	@echo "✅ Восстановление завершено"

# Деплой на Heroku
deploy:
	@echo "🚀 Деплой на Heroku..."
	@git add .
	@git commit -m "🤖 Auto deploy $(shell date +%Y-%m-%d_%H:%M:%S)" || echo "No changes to commit"
	@git push heroku main
	@echo "✅ Деплой завершен"

# Просмотр логов
logs:
	@echo "📋 Просмотр логов Heroku..."
	@heroku logs --tail --app checkyourcrypto-bot

# Полный бекап с базой данных (требует DATABASE_URL)
backup-full:
	@echo "🗄️ Создание полного бекапа с базой данных..."
	@if [ -z "$(DATABASE_URL)" ]; then \
		echo "❌ Укажите DATABASE_URL: make backup-full DATABASE_URL=postgres://..."; \
		exit 1; \
	fi
	@mkdir -p backups/backup_$(shell date +%Y%m%d_%H%M%S)
	@cp -r . backups/backup_$(shell date +%Y%m%d_%H%M%S)/code/
	@pg_dump $(DATABASE_URL) > backups/backup_$(shell date +%Y%m%d_%H%M%S)/database_backup.sql
	@echo "✅ Полный бекап создан: backups/backup_$(shell date +%Y%m%d_%H%M%S)"

# Восстановление полного бекапа
restore-full:
	@echo "🔄 Восстановление полного бекапа..."
	@if [ -z "$(BACKUP_PATH)" ]; then \
		echo "❌ Укажите путь к бекапу: make restore-full BACKUP_PATH=backups/backup_YYYYMMDD_HHMMSS"; \
		exit 1; \
	fi
	@if [ -z "$(DATABASE_URL)" ]; then \
		echo "❌ Укажите DATABASE_URL: make restore-full BACKUP_PATH=... DATABASE_URL=postgres://..."; \
		exit 1; \
	fi
	@cp -r $(BACKUP_PATH)/code/* .
	@psql $(DATABASE_URL) < $(BACKUP_PATH)/database_backup.sql
	@echo "✅ Полное восстановление завершено"

# Очистка старых бекапов (старше 7 дней)
cleanup:
	@echo "🧹 Очистка старых бекапов..."
	@find backups/ -name "backup_*" -type d -mtime +7 -exec rm -rf {} \;
	@echo "✅ Очистка завершена"

# Помощь
help:
	@echo "🤖 Доступные команды:"
	@echo "  make backup          - Создать бекап кода"
	@echo "  make backup-full     - Создать полный бекап (код + БД)"
	@echo "  make restore         - Восстановить код из бекапа"
	@echo "  make restore-full    - Восстановить полный бекап"
	@echo "  make deploy          - Деплой на Heroku"
	@echo "  make logs            - Просмотр логов"
	@echo "  make cleanup         - Очистка старых бекапов"
	@echo ""
	@echo "📝 Примеры использования:"
	@echo "  make backup-full DATABASE_URL=postgres://user:pass@host/db"
	@echo "  make restore BACKUP_PATH=backups/backup_20250827_143000"
	@echo "  make restore-full BACKUP_PATH=backups/backup_20250827_143000 DATABASE_URL=postgres://..."

# Тестирование
.PHONY: test test-unit test-integration test-coverage test-lint install-test-deps

install-test-deps:
	@echo "📦 Установка зависимостей для тестирования..."
	pip install -r requirements-test.txt

test: install-test-deps
	@echo "🧪 Запуск всех тестов..."
	pytest tests/ -v --tb=short

test-unit: install-test-deps
	@echo "🧪 Запуск unit тестов..."
	pytest tests/unit/ -v --tb=short -m "not integration"

test-integration: install-test-deps
	@echo "🧪 Запуск интеграционных тестов..."
	pytest tests/integration/ -v --tb=short -m integration

test-coverage: install-test-deps
	@echo "📊 Запуск тестов с покрытием..."
	pytest tests/ -v --cov=bot --cov=common --cov-report=term-missing --cov-report=html:htmlcov

test-lint: install-test-deps
	@echo "🔍 Проверка кода..."
	flake8 bot/ common/
	black --check bot/ common/
	isort --check-only bot/ common/
	mypy bot/ common/ --ignore-missing-imports

test-security: install-test-deps
	@echo "🔒 Проверка безопасности..."
	bandit -r bot/ common/ -f json -o bandit-report.json
	safety check

test-fast: install-test-deps
	@echo "⚡ Быстрые тесты..."
	pytest tests/unit/ -v --tb=short -n auto

test-watch: install-test-deps
	@echo "👀 Тесты в режиме наблюдения..."
	pytest tests/ -v --tb=short -f
