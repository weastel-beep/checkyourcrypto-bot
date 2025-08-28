#!/bin/bash

# Скрипт для диагностики проблем с множественными ботами
echo "🔍 ДИАГНОСТИКА ПРОБЛЕМ С БОТАМИ"
echo "=================================="

echo ""
echo "1. Проверка процессов Python:"
echo "-----------------------------"
ps aux | grep python | grep -v grep | grep -E "(bot|main)" || echo "   Нет процессов Python с bot/main"

echo ""
echo "2. Проверка процессов бота:"
echo "---------------------------"
ps aux | grep "python.*bot/main.py" | grep -v grep || echo "   Нет процессов bot/main.py"

echo ""
echo "3. Проверка lock файла:"
echo "----------------------"
if [ -f ".bot.lock" ]; then
    echo "   Lock файл найден: .bot.lock"
    if [ -r ".bot.lock" ]; then
        PID=$(cat .bot.lock)
        echo "   PID в lock файле: $PID"
        
        if kill -0 "$PID" 2>/dev/null; then
            echo "   ✅ Процесс $PID жив"
            echo "   Информация о процессе:"
            ps -p "$PID" -o pid,ppid,cmd 2>/dev/null || echo "     Не удалось получить информацию"
        else
            echo "   ❌ Процесс $PID мертв"
        fi
    else
        echo "   ❌ Не удается прочитать lock файл"
    fi
else
    echo "   Lock файл не найден"
fi

echo ""
echo "4. Проверка файлов main.py:"
echo "---------------------------"
find . -name "main.py" -type f | head -10

echo ""
echo "5. Проверка активных портов:"
echo "----------------------------"
lsof -i :8000 -i :8080 -i :5000 2>/dev/null || echo "   Нет активных портов"

echo ""
echo "6. Проверка Heroku процессов:"
echo "----------------------------"
if command -v heroku &> /dev/null; then
    echo "   Heroku CLI найден"
    heroku ps --app checkyourcrypto-bot 2>/dev/null || echo "   Не удалось получить информацию о Heroku"
else
    echo "   Heroku CLI не установлен"
fi

echo ""
echo "7. Проверка логов:"
echo "-----------------"
if [ -f "bot.log" ]; then
    echo "   Последние 10 строк bot.log:"
    tail -10 bot.log
else
    echo "   Файл bot.log не найден"
fi

echo ""
echo "8. Рекомендации:"
echo "---------------"
echo "   Для остановки всех процессов: ./stop_bot.sh"
echo "   Для запуска бота: ./start_bot.sh"
echo "   Для принудительной очистки: rm -f .bot.lock && pkill -9 -f 'python.*bot/main.py'"
