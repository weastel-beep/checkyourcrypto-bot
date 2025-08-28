# Обновленная логика Bot Flow Designer

## 📋 НОВАЯ АРХИТЕКТУРА ЭТАПОВ:

### 1. **free_result_v2** (Обновленный этап результата бесплатной проверки)

```javascript
{
  id: 'free_result_v2',
  name: 'Результат бесплатной проверки',
  trigger: 'check_completed',
  text_key: 'free_check_result',
  buttons: [], // Динамические кнопки на основе баланса
  conditions: [
    {
      type: 'balance_sufficient',
      action: 'show_buttons',
      buttons: ['🛡️ Глубокий AI-анализ', '📊 Показать пример', '🏠 Главное меню']
    },
    {
      type: 'balance_insufficient',
      action: 'show_buttons', 
      buttons: ['📊 Показать пример', '💰 Пополнить баланс', '🏠 Главное меню']
    }
  ],
  next_stage: 'example_showcase' // По умолчанию
}
```

### 2. **example_showcase** (Новый этап - показать пример)

```javascript
{
  id: 'example_showcase',
  name: 'Показать пример глубокого анализа',
  trigger: 'text_equals',
  trigger_value: '📊 Показать пример',
  text_key: 'deep_analysis_example',
  buttons: ['🛡️ Заказать AI-анализ', '💰 Пополнить баланс', '🔙 Назад', '👤 Личный кабинет'],
  conditions: [
    {
      type: 'balance_sufficient',
      action: 'enable_button',
      button: '🛡️ Заказать AI-анализ'
    },
    {
      type: 'balance_insufficient',
      action: 'disable_button',
      button: '🛡️ Заказать AI-анализ'
    }
  ],
  next_stage: 'paid_check_v2' // При нажатии "Заказать"
}
```

### 3. **payment_prompt** (Новый этап - пополнение баланса)

```javascript
{
  id: 'payment_prompt',
  name: 'Пополнение баланса',
  trigger: 'text_equals',
  trigger_value: '💰 Пополнить баланс',
  text_key: 'payment_methods',
  buttons: ['💳 Binance Pay', '🪙 Криптокошелек', '🔙 Назад', '🏠 Главное меню'],
  next_stage: 'payment_processing'
}
```

### 4. **back_to_result** (Новый этап - возврат к результату)

```javascript
{
  id: 'back_to_result',
  name: 'Возврат к результату проверки',
  trigger: 'text_equals',
  trigger_value: '🔙 Назад',
  text_key: 'free_check_result',
  buttons: [], // Динамические кнопки снова
  conditions: [
    {
      type: 'balance_sufficient',
      action: 'show_buttons',
      buttons: ['🛡️ Глубокий AI-анализ', '📊 Показать пример', '🏠 Главное меню']
    },
    {
      type: 'balance_insufficient',
      action: 'show_buttons',
      buttons: ['📊 Показать пример', '💰 Пополнить баланс', '🏠 Главное меню']
    }
  ],
  next_stage: 'example_showcase'
}
```

## 🔧 ОБНОВЛЕНИЯ В КОДЕ:

### 1. Обновить `common/services_package/scenario_executor.py`:

```python
# Добавить новые условия
elif condition_type == "balance_sufficient":
    paid_check_price = await SettingService.get_paid_check_price(session)
    return user_obj.balance >= paid_check_price

elif condition_type == "balance_insufficient":
    paid_check_price = await SettingService.get_paid_check_price(session)
    return user_obj.balance < paid_check_price
```

### 2. Обновить `common/services_package/placeholder_service.py`:

```python
# Добавить новые плейсхолдеры
PLACEHOLDERS = {
    # ... существующие ...
    'balance': 'get_user_balance',
    'paid_check_price': 'get_paid_check_price',
    'label': 'get_address_label',
    'address_type': 'get_address_type', 
    'website': 'get_website',
    'address_status': 'get_address_status'
}
```

### 3. Обновить `bot/handlers/checks.py`:

```python
# Добавить обработку новых кнопок
async def handle_example_button(update, context):
    # Показать пример глубокого анализа
    pass

async def handle_payment_button(update, context):
    # Показать методы оплаты
    pass

async def handle_back_button(update, context):
    # Вернуться к результату проверки
    pass
```

## 📝 ИНСТРУКЦИИ ДЛЯ АДМИНКИ:

### 1. Создать новые шаблоны:
- `deep_analysis_example` (пример анализа)
- `payment_methods` (методы оплаты)

### 2. Обновить существующий шаблон:
- `free_check_result` (с новыми плейсхолдерами)

### 3. Создать новые этапы в конструкторе:
- `example_showcase`
- `payment_prompt` 
- `back_to_result`

### 4. Обновить существующий этап:
- `free_result_v2` (с динамическими кнопками)

## 🎯 ЛОГИКА РАБОТЫ:

1. **Пользователь делает бесплатную проверку**
2. **Показывается результат с динамическими кнопками:**
   - Если баланс достаточный: "Глубокий AI-анализ", "Показать пример", "Главное меню"
   - Если баланс недостаточный: "Показать пример", "Пополнить баланс", "Главное меню"

3. **При нажатии "Показать пример":**
   - Показывается пример глубокого анализа
   - Кнопки: "Заказать AI-анализ" (активна только при достаточном балансе), "Пополнить баланс", "Назад", "Личный кабинет"

4. **При нажатии "Пополнить баланс":**
   - Показываются методы оплаты
   - Кнопки: "Binance Pay", "Криптокошелек", "Назад", "Главное меню"

5. **При нажатии "Назад":**
   - Возврат к результату бесплатной проверки
   - Снова показываются динамические кнопки

## 🚀 СЛЕДУЮЩИЕ ШАГИ:

1. ✅ Создать новые шаблоны в админке
2. ✅ Обновить существующий шаблон
3. ✅ Создать новые этапы в конструкторе
4. ✅ Обновить код для поддержки новых условий
5. ✅ Добавить обработчики новых кнопок
6. ✅ Протестировать логику
