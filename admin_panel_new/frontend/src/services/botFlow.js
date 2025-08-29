import api from './api'

// Функция для получения стоимости платной проверки
const getPaidCheckPrice = () => {
  const savedPrice = localStorage.getItem('paidCheckPrice')
  return savedPrice ? parseFloat(savedPrice) : 1.0
}

export const botFlowService = {
  // Получить все сценарии
  async getScenarios() {
    try {
      console.log('🔄 Загружаю сценарии из единого API...')
      const response = await api.get('/unified/scenarios')
      console.log('✅ Сценарии загружены из единого API:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error fetching scenarios:', error)
      console.log('📋 Возвращаю mock данные...')
      // Возвращаем тестовые данные для демонстрации
      return [
        {
          id: 'address_check_flow',
          name: 'Проверка адреса',
          description: 'Основной сценарий проверки криптоадресов',
          is_active: true,
          stages: [
            {
              id: 'welcome_stage',
              name: 'Приветствие',
              trigger: 'command_start',
              text_key: 'welcome',
              buttons: ['🔍 Проверка', '💰 Пополнить', '👤 Личный кабинет', '📁 FAQ'],
              conditions: [],
              next_stage: 'main_menu'
            },
            {
              id: 'check_button_stage',
              name: 'Кнопка проверки',
              trigger: 'text_equals',
              trigger_value: '🔍 Проверка',
              text_key: 'enter_address',
              buttons: ['💰 Пополнить', '📁 FAQ', '👤 Личный кабинет'],
              conditions: [
                {
                  type: 'user_blocked',
                  action: 'show_message',
                  text_key: 'user_blocked'
                }
              ],
              next_stage: 'address_input'
            },
            {
              id: 'address_input_stage',
              name: 'Ввод адреса',
              trigger: 'address_input',
              text_key: '',
              custom_text: 'Проверяю адрес...',
              buttons: [],
              conditions: [
                {
                  type: 'address_valid',
                  action: 'continue',
                  next_stage: 'balance_check'
                },
                {
                  type: 'address_invalid',
                  action: 'show_message',
                  text_key: 'invalid_address'
                }
              ],
              next_stage: 'balance_check'
            },
            {
              id: 'balance_check_stage',
              name: 'Проверка баланса',
              trigger: 'balance_check',
              text_key: '',
              custom_text: 'Выберите тип проверки:',
              buttons: ['✅ Бесплатная', '🛡️ Платная (1 USDT)'],
              conditions: [
                {
                  type: 'balance_sufficient',
                  action: 'show_paid_options'
                },
                {
                  type: 'balance_insufficient',
                  action: 'show_free_only'
                }
              ],
              next_stage: 'check_result'
            },
            {
              id: 'check_result_stage',
              name: 'Результат проверки',
              trigger: 'check_completed',
              text_key: '',
              custom_text: 'Результат проверки адреса',
              buttons: ['🛡️ Глубокий анализ', '💰 Пополнить', '🏠 Главное меню'],
              conditions: [],
              next_stage: ''
            }
          ]
        },
        {
          id: 'address_check_v2',
          name: 'Проверка адреса v2',
          description: 'Улучшенный сценарий проверки с условной логикой баланса',
          is_active: true,
          stages: [
            {
              id: 'welcome_stage_v2',
              name: 'Приветствие',
              trigger: 'command_start',
              text_key: 'welcome',
              buttons: ['🔍 Проверка', '💰 Пополнить', '👤 Личный кабинет', '📁 FAQ'],
              conditions: [],
              next_stage: 'main_menu_v2'
            },
            {
              id: 'main_menu_v2',
              name: 'Главное меню',
              trigger: 'text_equals',
              trigger_value: '🏠 Главное меню',
              text_key: 'main_menu_hint',
              buttons: ['🔍 Проверка', '💰 Пополнить', '👤 Личный кабинет', '📁 FAQ'],
              conditions: [],
              next_stage: 'check_button_v2'
            },
            {
              id: 'check_button_v2',
              name: 'Кнопка проверки',
              trigger: 'text_equals',
              trigger_value: '🔍 Проверка',
              text_key: 'main_menu',
              buttons: ['💰 Пополнить', '📁 FAQ', '👤 Личный кабинет'],
              conditions: [
                {
                  type: 'user_blocked',
                  action: 'show_message',
                  text_key: 'user_blocked'
                }
              ],
              next_stage: 'address_input_v2'
            },
            {
              id: 'address_input_v2',
              name: 'Ввод адреса',
              trigger: 'address_input',
              text_key: 'check_address_prompt',
              buttons: [],
              conditions: [
                {
                  type: 'address_valid',
                  action: 'continue',
                  next_stage: 'balance_check_v2'
                },
                {
                  type: 'address_invalid',
                  action: 'show_message',
                  text_key: 'invalid_address'
                }
              ],
              next_stage: 'balance_check_v2'
            },
            {
              id: 'balance_check_v2',
              name: 'Проверка баланса',
              trigger: 'balance_check',
              text_key: '',
              custom_text: 'Проверяю ваш баланс...',
              buttons: [],
              conditions: [
                {
                  type: 'balance_sufficient',
                  action: 'redirect',
                  target_stage: 'choice_stage_v2'
                },
                {
                  type: 'balance_insufficient',
                  action: 'redirect',
                  target_stage: 'free_check_v2'
                }
              ],
              next_stage: 'choice_stage_v2'
            },
            {
              id: 'choice_stage_v2',
              name: 'Выбор типа проверки',
              trigger: 'user_choice',
              text_key: 'check_choice',
              buttons: [`✅ Бесплатная проверка`, `🛡️ Глубокий AI-анализ (${getPaidCheckPrice()} USDT)`, '🏠 Главное меню'],
              conditions: [],
              next_stage: 'check_result_v2'
            },
            {
              id: 'free_check_v2',
              name: 'Бесплатная проверка',
              trigger: 'free_check',
              text_key: '',
              custom_text: 'Выполняю бесплатную проверку...',
              buttons: [],
              conditions: [],
              next_stage: 'free_result_v2'
            },
            {
              id: 'free_result_v2',
              name: 'Результат бесплатной проверки',
              trigger: 'check_completed',
              text_key: '',
              custom_text: 'Результат бесплатной проверки адреса',
              buttons: [`🛡️ Глубокий AI-анализ (${getPaidCheckPrice()} USDT)`, '📊 Пример Глубокого AI-анализа', '🏠 Главное меню'],
              conditions: [],
              next_stage: ''
            },
            {
              id: 'paid_check_v2',
              name: 'Платная проверка',
              trigger: 'paid_check',
              text_key: '',
              custom_text: 'Выполняю глубокий AI-анализ...',
              buttons: [],
              conditions: [],
              next_stage: 'paid_result_v2'
            },
            {
              id: 'paid_result_v2',
              name: 'Результат платной проверки',
              trigger: 'check_completed',
              text_key: 'deep_analysis_report',
              buttons: ['🏠 Главное меню', '🔍 Проверить другой адрес'],
              conditions: [],
              next_stage: ''
            }
          ]
        },
        {
          id: 'payment_flow',
          name: 'Пополнение баланса',
          description: 'Сценарий для пополнения баланса пользователя',
          is_active: true,
          stages: [
            {
              id: 'payment_start',
              name: 'Начало оплаты',
              trigger: 'text_equals',
              trigger_value: '💰 Пополнить',
              text_key: '',
              custom_text: 'Выберите способ оплаты:',
              buttons: ['💳 Binance Pay', '🧪 Тестовый платеж', '🏠 Главное меню'],
              conditions: [],
              next_stage: 'payment_processing'
            },
            {
              id: 'payment_processing',
              name: 'Обработка платежа',
              trigger: 'payment_initiated',
              text_key: '',
              custom_text: 'Обрабатываю платеж...',
              buttons: [],
              conditions: [],
              next_stage: 'payment_success'
            }
          ]
        }
      ]
    }
  },

  // Создать новый сценарий
  async createScenario(scenario) {
    try {
      const response = await api.post('/bot-flow/scenarios', scenario)
      return response.data
    } catch (error) {
      console.error('Error creating scenario:', error)
      throw error
    }
  },

  // Обновить сценарий
  async updateScenario(scenario) {
    try {
      console.log('🔄 Отправляем обновление сценария:', scenario)
      const response = await api.put(`/bot-flow/scenarios/${scenario.id}`, scenario)
      console.log('✅ Сценарий обновлен:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error updating scenario:', error)
      throw error
    }
  },

  // Удалить сценарий
  async deleteScenario(scenarioId) {
    try {
      await api.delete(`/bot-flow/scenarios/${scenarioId}`)
    } catch (error) {
      console.error('Error deleting scenario:', error)
      throw error
    }
  },

  // Тестировать сценарий
  async testScenario(scenarioId) {
    try {
      const response = await api.post(`/bot-flow/scenarios/${scenarioId}/test`)
      return response.data
    } catch (error) {
      console.error('Error testing scenario:', error)
      throw error
    }
  },

  // Получить предпросмотр сценария
  async previewScenario(scenarioId) {
    try {
      const response = await api.get(`/bot-flow/scenarios/${scenarioId}/preview`)
      return response.data
    } catch (error) {
      console.error('Error previewing scenario:', error)
      throw error
    }
  },

  // Получить доступные тексты
  async getAvailableTexts() {
    try {
      const response = await api.get('/unified/texts')
      return response.data
    } catch (error) {
      console.error('Error fetching texts:', error)
      // Возвращаем тестовые данные с реальным содержимым
      return [
        { 
          key: 'welcome', 
          name: 'Приветствие',
          content: '👋 **CheckYourCrypto AI** — умный бот для защиты ваших криптоактивов...'
        },
        { 
          key: 'main_menu', 
          name: 'Главное меню',
          content: '🔍 **Проверка криптоадреса**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💰 **Ваш баланс:** {balance} USDT...'
        },
        { 
          key: 'check_address_prompt', 
          name: 'Запрос адреса',
          content: '🔍 **Проверка криптоадреса**\n\nОтправьте мне адрес для проверки!'
        },
        { 
          key: 'check_choice', 
          name: 'Выбор типа проверки',
          content: '🔍 **Выберите тип проверки адреса**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📍 **Адрес:** `{address}`\n⛓️ **Блокчейн:** {chain}\n💰 **Ваш баланс:** {balance} USDT...'
        },
        { 
          key: 'invalid_address', 
          name: 'Неверный адрес',
          content: '❌ **Неверный адрес**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nПожалуйста, отправьте корректный криптоадрес...'
        },
        { 
          key: 'checking_address', 
          name: 'Проверка адреса',
          content: '🔍 Проверяю адрес {chain}...\n\n⏳ Это займет несколько секунд...'
        },
        { 
          key: 'error_occurred', 
          name: 'Ошибка',
          content: '❌ Произошла ошибка при проверке адреса.\n\nПопробуйте позже или обратитесь в поддержку.'
        },
        { 
          key: 'faq_content', 
          name: 'FAQ',
          content: '📁 **Часто задаваемые вопросы**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n**Как проверить адрес?**\n1. Отправьте криптоадрес...'
        },
        { 
          key: 'user_blocked', 
          name: 'Пользователь заблокирован',
          content: '🚫 Ваш аккаунт заблокирован. Обратитесь к администратору.'
        },
        { 
          key: 'deep_analysis_report', 
          name: 'Отчет глубокого анализа',
          content: '🛡️ **Глубокий AI-анализ адреса**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📍 **Адрес:** `{address}`\n⛓️ **Блокчейн:** {chain}\n🤖 **AI-анализ:** Полный...'
        }
      ]
    }
  },

  // Получить статистику сценариев
  async getScenarioStats() {
    try {
      const response = await api.get('/bot-flow/stats')
      return response.data
    } catch (error) {
      console.error('Error fetching stats:', error)
      return {
        total_scenarios: 2,
        active_scenarios: 2,
        total_stages: 7,
        total_conditions: 8,
        last_updated: new Date().toISOString()
      }
    }
  }
}
