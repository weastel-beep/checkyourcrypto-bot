#!/bin/bash

echo "🔍 Проверка процессов бота..."

# Проверяем процессы Python
echo "📋 Процессы Python:"
ps aux | grep python | grep -v grep

echo ""
echo "🤖 Процессы бота:"
ps aux | grep "bot/main.py" | grep -v grep

echo ""
echo "📊 Количество процессов бота:"
BOT_COUNT=$(ps aux | grep "bot/main.py" | grep -v grep | wc -l)
echo "        $BOT_COUNT"

echo ""
echo "🛑 Агрессивная остановка всех процессов бота..."

# Убиваем все процессы Python, которые содержат bot/main.py
pkill -f "python.*bot/main.py" 2>/dev/null || echo "pkill не нашел процессы"

# Дополнительно убиваем по имени процесса
pkill -f "bot/main.py" 2>/dev/null || echo "pkill bot/main.py не нашел процессы"

# Убиваем все процессы Python (более агрессивно)
echo "🛑 Убиваем все процессы Python..."
pkill -f python 2>/dev/null || echo "pkill python не нашел процессы"

# Ждем немного
sleep 2

echo ""
echo "🔍 Проверка после убийства:"
ps aux | grep "bot/main.py" | grep -v grep

echo ""
echo "📊 Количество процессов бота после убийства:"
AFTER_COUNT=$(ps aux | grep "bot/main.py" | grep -v grep | wc -l)
echo "        $AFTER_COUNT"

if [ "$AFTER_COUNT" -eq 0 ]; then
    echo "✅ Все процессы бота успешно остановлены"
else
    echo "⚠️  Остались процессы бота! Принудительное убийство..."
    ps aux | grep "bot/main.py" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null
    echo "🛑 Принудительно убиты все оставшиеся процессы"
fi

echo ""
echo "✅ Проверка завершена"
