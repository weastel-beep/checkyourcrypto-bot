#!/bin/bash

# 🚀 Production Bot Manager
# Работаем только с production ботом на сервере

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
PRODUCTION_BOT_URL="https://checkyourcrypto-bot-87c446f24699.herokuapp.com"
API_URL="https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com"
ADMIN_URL="https://checkyourcrypto-admin-ui-e1a641bd2ba6.herokuapp.com"

echo -e "${BLUE}🤖 PRODUCTION BOT MANAGER${NC}"
echo -e "${BLUE}========================${NC}"

case "$1" in
    "status")
        echo -e "${YELLOW}🔍 Проверяем статус production бота...${NC}"
        
        # Проверяем API
        echo -e "${BLUE}📡 API Status:${NC}"
        if curl -s "$API_URL/health" > /dev/null; then
            echo -e "${GREEN}✅ API работает${NC}"
        else
            echo -e "${RED}❌ API недоступен${NC}"
        fi
        
        # Проверяем админку
        echo -e "${BLUE}🖥️  Admin Panel Status:${NC}"
        if curl -s "$ADMIN_URL" > /dev/null; then
            echo -e "${GREEN}✅ Админка работает${NC}"
        else
            echo -e "${RED}❌ Админка недоступна${NC}"
        fi
        
        # Проверяем бота
        echo -e "${BLUE}🤖 Bot Status:${NC}"
        if curl -s "$PRODUCTION_BOT_URL" | grep -q "Application Error"; then
            echo -e "${RED}❌ Бот не работает (Application Error)${NC}"
        else
            echo -e "${GREEN}✅ Бот работает${NC}"
        fi
        
        echo -e "${BLUE}📊 Статистика:${NC}"
        echo -e "API: $API_URL"
        echo -e "Admin: $ADMIN_URL"
        echo -e "Bot: $PRODUCTION_BOT_URL"
        ;;
        
    "restart")
        echo -e "${YELLOW}🔄 Перезапуск production бота...${NC}"
        echo -e "${YELLOW}⚠️  Для перезапуска бота на Heroku используйте:${NC}"
        echo -e "${BLUE}heroku restart --app checkyourcrypto-bot${NC}"
        echo -e "${YELLOW}Или через Heroku Dashboard${NC}"
        ;;
        
    "logs")
        echo -e "${YELLOW}📋 Логи production бота:${NC}"
        echo -e "${BLUE}heroku logs --tail --app checkyourcrypto-bot${NC}"
        echo -e "${YELLOW}Для просмотра логов выполните команду выше${NC}"
        ;;
        
    "test")
        echo -e "${YELLOW}🧪 Тестирование API endpoints...${NC}"
        
        # Тест API
        echo -e "${BLUE}🔍 Тестируем API endpoints:${NC}"
        
        # Health check
        if curl -s "$API_URL/health" | grep -q "ok"; then
            echo -e "${GREEN}✅ /health - OK${NC}"
        else
            echo -e "${RED}❌ /health - FAILED${NC}"
        fi
        
        # Texts
        if curl -s "$API_URL/api/texts" | grep -q "texts"; then
            echo -e "${GREEN}✅ /api/texts - OK${NC}"
        else
            echo -e "${RED}❌ /api/texts - FAILED${NC}"
        fi
        
        # Users
        if curl -s "$API_URL/api/users" | grep -q "users"; then
            echo -e "${GREEN}✅ /api/users - OK${NC}"
        else
            echo -e "${RED}❌ /api/users - FAILED${NC}"
        fi
        
        # Scenarios
        if curl -s "$API_URL/api/scenarios" | grep -q "scenarios"; then
            echo -e "${GREEN}✅ /api/scenarios - OK${NC}"
        else
            echo -e "${RED}❌ /api/scenarios - FAILED${NC}"
        fi
        
        echo -e "${GREEN}🎉 Тестирование завершено!${NC}"
        ;;
        
    "monitor")
        echo -e "${YELLOW}📊 Мониторинг системы...${NC}"
        echo -e "${BLUE}Открываем мониторинг в браузере:${NC}"
        echo -e "${GREEN}🌐 API: $API_URL${NC}"
        echo -e "${GREEN}🖥️  Admin: $ADMIN_URL${NC}"
        echo -e "${GREEN}🤖 Bot: $PRODUCTION_BOT_URL${NC}"
        
        # Автоматически открываем в браузере
        if command -v open >/dev/null 2>&1; then
            open "$ADMIN_URL"
            echo -e "${GREEN}✅ Админка открыта в браузере${NC}"
        fi
        ;;
        
    "help"|"")
        echo -e "${BLUE}📖 Доступные команды:${NC}"
        echo -e "${GREEN}  status${NC}   - Проверить статус всех сервисов"
        echo -e "${GREEN}  test${NC}     - Протестировать API endpoints"
        echo -e "${GREEN}  restart${NC}  - Инструкции по перезапуску бота"
        echo -e "${GREEN}  logs${NC}     - Инструкции по просмотру логов"
        echo -e "${GREEN}  monitor${NC}  - Открыть мониторинг в браузере"
        echo -e "${GREEN}  help${NC}     - Показать эту справку"
        echo -e ""
        echo -e "${YELLOW}⚠️  ВАЖНО: Локальный бот отключен для избежания конфликтов${NC}"
        echo -e "${YELLOW}🤖 Работаем только с production ботом на сервере${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ Неизвестная команда: $1${NC}"
        echo -e "${YELLOW}Используйте: $0 help${NC}"
        exit 1
        ;;
esac
