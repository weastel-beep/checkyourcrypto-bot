-- Добавление недостающих шаблонов для новой логики бота

-- 1. Шаблон "deep_analysis_example" (пример глубокого анализа)
INSERT INTO bot_texts (category, language, content, is_active, version, created_at, updated_at) 
VALUES (
    'deep_analysis_example',
    'ru',
    '🔍 **ПРИМЕР ГЛУБОКОГО AI-АНАЛИЗА**

📝 Адрес: `{address}`
🌐 Сеть: Ethereum
✅ Тип проверки: Глубокий AI-анализ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 УРОВЕНЬ РИСКА: КРИТИЧЕСКИЙ (5/5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **ДЕТАЛЬНЫЙ АНАЛИЗ:**

🏷️ **Метка адреса:** Санкционированный кошелек
🌐 **Веб-сайт:** OFAC.gov
📊 **Статус адреса:** Заблокирован, Санкционирован

⚠️ **ОБНАРУЖЕННЫЕ РИСКИ:**
• Адрес в санкционном списке OFAC
• Блокировка транзакций
• Высокий риск конфискации средств
• Запрет на взаимодействие

🔍 **AI-РЕКОМЕНДАЦИИ:**
• ❌ НЕ РЕКОМЕНДУЕТСЯ к использованию
• Избегайте любых транзакций
• Проверьте источник средств
• Рассмотрите альтернативные адреса

💰 **СТОИМОСТЬ АНАЛИЗА:** {paid_check_price} USDT
⏱️ **ВРЕМЯ ПРОВЕРКИ:** 15-30 секунд',
    true,
    1,
    NOW(),
    NOW()
);

INSERT INTO bot_texts (category, language, content, is_active, version, created_at, updated_at) 
VALUES (
    'deep_analysis_example',
    'en',
    '🔍 **DEEP AI-ANALYSIS EXAMPLE**

📝 Address: `{address}`
🌐 Network: Ethereum
✅ Check Type: Deep AI Analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 RISK LEVEL: CRITICAL (5/5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **DETAILED ANALYSIS:**

🏷️ **Address Label:** Sanctioned Wallet
🌐 **Website:** OFAC.gov
📊 **Address Status:** Blocked, Sanctioned

⚠️ **DETECTED RISKS:**
• Address in OFAC sanctions list
• Transaction blocking
• High risk of fund confiscation
• Prohibition on interaction

🔍 **AI RECOMMENDATIONS:**
• ❌ NOT RECOMMENDED for use
• Avoid any transactions
• Check fund source
• Consider alternative addresses

💰 **ANALYSIS COST:** {paid_check_price} USDT
⏱️ **CHECK TIME:** 15-30 seconds',
    true,
    1,
    NOW(),
    NOW()
);

-- 2. Шаблон "payment_methods" (методы оплаты)
INSERT INTO bot_texts (category, language, content, is_active, version, created_at, updated_at) 
VALUES (
    'payment_methods',
    'ru',
    '💳 **ПОПОЛНЕНИЕ БАЛАНСА**

💰 Текущий баланс: {balance} USDT
💵 Стоимость анализа: {paid_check_price} USDT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **ДОСТУПНЫЕ МЕТОДЫ ОПЛАТЫ:**

🟢 **Binance Pay** (Рекомендуется)
• Мгновенное зачисление
• Без комиссий
• Поддержка USDT, BNB, BTC

🟡 **Криптокошелек**
• USDT (TRC20, ERC20)
• BTC, ETH, BNB
• Комиссия сети

📱 **Другие методы**
• Telegram Payments
• Криптобиржи
• P2P обмен

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **КАК ПОПОЛНИТЬ:**
1. Выберите метод оплаты
2. Укажите сумму
3. Следуйте инструкциям
4. Получите подтверждение

🆘 **Нужна помощь?** Обратитесь в поддержку',
    true,
    1,
    NOW(),
    NOW()
);

INSERT INTO bot_texts (category, language, content, is_active, version, created_at, updated_at) 
VALUES (
    'payment_methods',
    'en',
    '💳 **BALANCE TOP-UP**

💰 Current Balance: {balance} USDT
💵 Analysis Cost: {paid_check_price} USDT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 **AVAILABLE PAYMENT METHODS:**

🟢 **Binance Pay** (Recommended)
• Instant crediting
• No fees
• Support for USDT, BNB, BTC

🟡 **Crypto Wallet**
• USDT (TRC20, ERC20)
• BTC, ETH, BNB
• Network fee

📱 **Other Methods**
• Telegram Payments
• Cryptocurrency exchanges
• P2P exchange

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **HOW TO TOP UP:**
1. Select payment method
2. Enter amount
3. Follow instructions
4. Get confirmation

🆘 **Need help?** Contact support',
    true,
    1,
    NOW(),
    NOW()
);
