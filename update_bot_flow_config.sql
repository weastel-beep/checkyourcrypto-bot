-- Обновление конфигурации Bot Flow Designer для правильной работы с динамическими кнопками

-- Обновляем этап "Результат проверки" с правильными условиями
UPDATE bot_scenarios 
SET stages = jsonb_set(
    stages,
    '{4}', -- Индекс этапа check_result_stage
    '{
        "id": "check_result_stage",
        "name": "Результат бесплатной проверки",
        "trigger": "check_completed",
        "text_key": "free_check_result",
        "buttons": [],
        "conditions": [
            {
                "type": "balance_sufficient",
                "action": "show_buttons",
                "buttons": ["🛡️ Глубокий AI-анализ", "📊 Показать пример", "🏠 Главное меню"]
            },
            {
                "type": "balance_insufficient", 
                "action": "show_buttons",
                "buttons": ["📊 Показать пример", "💰 Пополнить баланс", "🏠 Главное меню"]
            }
        ],
        "next_stage": "example_showcase",
        "custom_text": null,
        "trigger_value": null
    }'::jsonb
)
WHERE id = 'address_check_flow';

-- Добавляем новый этап "Показать пример"
UPDATE bot_scenarios 
SET stages = stages || '{
    "id": "example_showcase",
    "name": "Показать пример глубокого анализа",
    "trigger": "text_equals",
    "trigger_value": "📊 Показать пример",
    "text_key": "deep_analysis_example",
    "buttons": ["🛡️ Заказать AI-анализ", "💰 Пополнить баланс", "🔙 Назад", "👤 Личный кабинет"],
    "conditions": [
        {
            "type": "balance_sufficient",
            "action": "enable_button",
            "button": "🛡️ Заказать AI-анализ"
        },
        {
            "type": "balance_insufficient",
            "action": "disable_button", 
            "button": "🛡️ Заказать AI-анализ"
        }
    ],
    "next_stage": "payment_prompt",
    "custom_text": null
}'::jsonb
WHERE id = 'address_check_flow';

-- Добавляем этап "Пополнение баланса"
UPDATE bot_scenarios 
SET stages = stages || '{
    "id": "payment_prompt",
    "name": "Пополнение баланса",
    "trigger": "text_equals",
    "trigger_value": "💰 Пополнить баланс",
    "text_key": "payment_methods",
    "buttons": ["💳 Binance Pay", "🪙 Криптокошелек", "🔙 Назад", "🏠 Главное меню"],
    "conditions": [],
    "next_stage": "back_to_result",
    "custom_text": null
}'::jsonb
WHERE id = 'address_check_flow';

-- Добавляем этап "Возврат к результату"
UPDATE bot_scenarios 
SET stages = stages || '{
    "id": "back_to_result",
    "name": "Возврат к результату проверки",
    "trigger": "text_equals",
    "trigger_value": "🔙 Назад",
    "text_key": "free_check_result",
    "buttons": [],
    "conditions": [
        {
            "type": "balance_sufficient",
            "action": "show_buttons",
            "buttons": ["🛡️ Глубокий AI-анализ", "📊 Показать пример", "🏠 Главное меню"]
        },
        {
            "type": "balance_insufficient",
            "action": "show_buttons",
            "buttons": ["📊 Показать пример", "💰 Пополнить баланс", "🏠 Главное меню"]
        }
    ],
    "next_stage": "example_showcase",
    "custom_text": null
}'::jsonb
WHERE id = 'address_check_flow';
