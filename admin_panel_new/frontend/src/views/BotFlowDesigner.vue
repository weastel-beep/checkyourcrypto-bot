<template>
  <BaseLayout>
    <div class="bot-flow-designer">
    <!-- Header -->
    <div class="header">
      <h1>🎨 Конструктор логики бота</h1>
      <div class="header-actions">
        <button @click="showInstructions = !showInstructions" class="btn-info">
          📖 Инструкции
        </button>
        <button @click="saveFlow" class="btn-primary">
          💾 Сохранить
        </button>
        <button @click="previewFlow" class="btn-secondary">
          👁️ Предпросмотр
        </button>
        <button @click="testFlow" class="btn-success">
          🧪 Тест
        </button>
      </div>
    </div>

    <!-- Instructions Modal -->
    <div v-if="showInstructions" class="instructions-modal" @click="showInstructions = false">
      <div class="instructions-content" @click.stop>
        <div class="instructions-header">
          <h2>📖 ИНСТРУКЦИЯ ДЛЯ ДАЛБАЕБОВ</h2>
          <button @click="showInstructions = false" class="btn-close">×</button>
        </div>
        
        <div class="instructions-body">
          <div class="instruction-section">
            <h3>🎯 ЧТО ЭТО ТАКОЕ?</h3>
            <p>Это <strong>визуальный конструктор</strong> для управления логикой бота. Вместо того чтобы лезть в код, ты можешь:</p>
            <ul>
              <li>🎭 Создавать сценарии (например, "Проверка адреса")</li>
              <li>📝 Редактировать тексты на каждом этапе</li>
              <li>🔘 Добавлять/убирать кнопки</li>
              <li>🔀 Настраивать условия (если баланс > 0, то...)</li>
              <li>🧪 Тестировать изменения в реальном времени</li>
            </ul>
          </div>

          <div class="instruction-section">
            <h3>🚀 КАК НАЧАТЬ?</h3>
            <ol>
              <li><strong>Создай сценарий:</strong> Нажми "➕ Добавить" в левой панели</li>
              <li><strong>Добавь этапы:</strong> В центре нажми "➕ Этап" для каждого шага</li>
              <li><strong>Настрой этап:</strong> В правой панели выбери триггер и текст</li>
              <li><strong>Добавь кнопки:</strong> Укажи какие кнопки показывать</li>
              <li><strong>Сохрани:</strong> Нажми "💾 Сохранить"</li>
            </ol>
          </div>

          <div class="instruction-section">
            <h3>🎭 ТРИГГЕРЫ (КОГДА СРАБАТЫВАЕТ ЭТАП)</h3>
            <ul>
              <li><strong>Команда /start:</strong> Когда пользователь запускает бота</li>
              <li><strong>Текст равен:</strong> Когда пользователь пишет точный текст (например, "🔍 Проверка")</li>
              <li><strong>Текст содержит:</strong> Когда в сообщении есть определенные слова</li>
              <li><strong>Callback данные:</strong> Когда нажимается inline кнопка</li>
              <li><strong>Ввод адреса:</strong> Когда пользователь отправляет криптоадрес</li>
              <li><strong>Проверка баланса:</strong> Когда нужно проверить баланс пользователя</li>
            </ul>
          </div>

          <div class="instruction-section">
            <h3>📝 ТЕКСТЫ</h3>
            <ul>
              <li><strong>Ключ текста:</strong> Выбери из существующих текстов (welcome, main_menu_text, etc.)</li>
              <li><strong>Пользовательский текст:</strong> Или напиши свой текст</li>
              <li><strong>Переменные:</strong> Используй {user.balance}, {address}, {risk_score}</li>
            </ul>
          </div>

          <div class="instruction-section">
            <h3>🔘 КНОПКИ</h3>
            <ul>
              <li><strong>Reply кнопки:</strong> Обычные кнопки под сообщением</li>
              <li><strong>Inline кнопки:</strong> Кнопки прямо в сообщении</li>
              <li><strong>Эмодзи:</strong> Используй эмодзи для красоты (🔍, 💰, 👤)</li>
            </ul>
          </div>

          <div class="instruction-section">
            <h3>🔀 УСЛОВИЯ</h3>
            <ul>
              <li><strong>Пользователь заблокирован:</strong> Показать сообщение о блокировке</li>
              <li><strong>Проверка баланса:</strong> Если баланс > 0, показать платные опции</li>
              <li><strong>Лимит бесплатных проверок:</strong> Проверить время до следующей бесплатной проверки</li>
              <li><strong>Адрес валиден:</strong> Проверить правильность криптоадреса</li>
            </ul>
          </div>

          <div class="instruction-section">
            <h3>💡 ПРИМЕРЫ СЦЕНАРИЕВ</h3>
            
            <div class="example-scenario">
              <h4>🔍 Сценарий "Проверка адреса"</h4>
              <ol>
                <li><strong>Этап 1:</strong> Триггер "Текст равен" → "🔍 Проверка"</li>
                <li><strong>Этап 2:</strong> Показать "Отправьте адрес" + кнопки</li>
                <li><strong>Этап 3:</strong> Триггер "Ввод адреса" → проверить валидность</li>
                <li><strong>Этап 4:</strong> Если баланс > 0 → показать выбор типа проверки</li>
                <li><strong>Этап 5:</strong> Выполнить проверку и показать результат</li>
              </ol>
            </div>

            <div class="example-scenario">
              <h4>💰 Сценарий "Пополнение баланса"</h4>
              <ol>
                <li><strong>Этап 1:</strong> Триггер "Текст равен" → "💰 Пополнить"</li>
                <li><strong>Этап 2:</strong> Показать методы оплаты + кнопки</li>
                <li><strong>Этап 3:</strong> Обработать платеж</li>
              </ol>
            </div>
          </div>

          <div class="instruction-section">
            <h3>⚠️ ВАЖНЫЕ МОМЕНТЫ</h3>
            <ul>
              <li>✅ <strong>Всегда сохраняй</strong> изменения перед тестированием</li>
              <li>✅ <strong>Тестируй</strong> сценарии в реальном боте</li>
              <li>✅ <strong>Проверяй</strong> все языки (ru/en)</li>
              <li>❌ <strong>Не удаляй</strong> важные этапы без замены</li>
              <li>❌ <strong>Не забывай</strong> про условия и переходы</li>
            </ul>
          </div>

          <div class="instruction-section">
            <h3>🆘 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ</h3>
            <ol>
              <li>Проверь, что сценарий <strong>активен</strong></li>
              <li>Убедись, что все <strong>триггеры</strong> настроены правильно</li>
              <li>Проверь <strong>тексты</strong> на ошибки</li>
              <li>Посмотри <strong>логи</strong> в админке</li>
              <li>Если ничего не помогает - <strong>напиши в поддержку</strong></li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Left Panel: Scenarios -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>📋 Сценарии</h3>
          <button @click="addScenario" class="btn-add">
            ➕ Добавить
          </button>
        </div>
        
        <div class="scenarios-list">
          <div 
            v-for="scenario in scenarios" 
            :key="scenario.id"
            :class="['scenario-item', { active: selectedScenario?.id === scenario.id }]"
            @click="selectScenario(scenario)"
          >
            <div class="scenario-info">
              <h4>{{ scenario.name }}</h4>
              <p>{{ scenario.description }}</p>
              <div class="scenario-stats">
                <span>{{ scenario.stages.length }} этапов</span>
                <span :class="['status', scenario.is_active ? 'active' : 'inactive']">
                  {{ scenario.is_active ? 'Активен' : 'Неактивен' }}
                </span>
              </div>
            </div>
            <div class="scenario-actions">
              <button @click.stop="editScenario(scenario)" class="btn-edit">✏️</button>
              <button @click.stop="deleteScenario(scenario)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Center Panel: Flow Designer -->
      <div class="center-panel">
        <div class="panel-header">
          <h3>🎭 {{ selectedScenario?.name || 'Выберите сценарий' }}</h3>
          <div class="flow-actions">
            <button @click="addStage" class="btn-add">➕ Этап</button>
            <button @click="addCondition" class="btn-add">🔀 Условие</button>
          </div>
        </div>

        <div class="flow-canvas" ref="flowCanvas">
          <!-- Flow Stages -->
          <div class="flow-stages">
            <div 
              v-for="(stage, index) in selectedScenario?.stages || []" 
              :key="stage.id"
              :class="['flow-stage', { selected: selectedStage?.id === stage.id }]"
              @click="selectStage(stage)"
            >
              <div class="stage-header">
                <span class="stage-number">{{ index + 1 }}</span>
                <h4>{{ stage.name }}</h4>
                <button @click.stop="deleteStage(stage)" class="btn-remove">×</button>
              </div>
              
              <div class="stage-content">
                <div class="stage-trigger">
                  <strong>Триггер:</strong> {{ getTriggerText(stage.trigger) }}
                </div>
                
                <div class="stage-text">
                  <strong>Текст:</strong> {{ stage.text_key || 'Не задан' }}
                </div>
                
                <div class="stage-buttons" v-if="stage.buttons?.length">
                  <strong>Кнопки:</strong>
                  <div class="buttons-preview">
                    <span 
                      v-for="button in stage.buttons" 
                      :key="button"
                      class="button-preview"
                    >
                      {{ button }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Stage Connections -->
              <div class="stage-connections">
                <div class="connection-line" v-if="index < selectedScenario.stages.length - 1"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Stage Editor -->
      <div class="right-panel">
        <div class="panel-header">
          <h3>📝 Редактор этапа</h3>
        </div>

        <div v-if="selectedStage" class="stage-editor">
          <!-- Basic Info -->
          <div class="form-section">
            <h4>Основная информация</h4>
            
            <div class="form-group">
              <label>Название этапа:</label>
              <input v-model="selectedStage.name" type="text" placeholder="Приветствие">
            </div>

            <div class="form-group">
              <label>Триггер:</label>
              <select v-model="selectedStage.trigger">
                <option value="command_start">Команда /start</option>
                <option value="text_equals">Текст равен</option>
                <option value="text_contains">Текст содержит</option>
                <option value="callback_data">Callback данные</option>
                <option value="address_input">Ввод адреса</option>
                <option value="balance_check">Проверка баланса</option>
              </select>
            </div>

            <div class="form-group" v-if="selectedStage.trigger === 'text_equals'">
              <label>Значение триггера:</label>
              <input v-model="selectedStage.trigger_value" type="text" placeholder="🔍 Проверка">
            </div>
          </div>

          <!-- Text Management -->
          <div class="form-section">
            <h4>Тексты</h4>
            
            <div class="form-group">
              <label>Текст сообщения:</label>
              <select v-model="selectedStage.text_key" class="text-select">
                <option value="">Выберите текст из базы данных</option>
                <option 
                  v-for="text in availableTexts" 
                  :key="text.key" 
                  :value="text.key"
                >
                  {{ text.name }} - {{ text.content ? text.content.substring(0, 50) + '...' : 'Нет содержимого' }}
                </option>
              </select>
              
              <!-- Предпросмотр выбранного текста -->
              <div v-if="selectedStage.text_key && getSelectedTextContent()" class="text-preview">
                <h5>📝 Предпросмотр текста:</h5>
                <div class="preview-content">
                  {{ getSelectedTextContent() }}
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Пользовательский текст:</label>
              <textarea 
                v-model="selectedStage.custom_text" 
                placeholder="Или введите свой текст..."
                rows="3"
              ></textarea>
            </div>
          </div>

          <!-- Buttons -->
          <div class="form-section">
            <h4>Кнопки</h4>
            
            <div class="buttons-list">
              <div 
                v-for="(button, index) in selectedStage.buttons" 
                :key="index"
                class="button-item"
              >
                <input v-model="selectedStage.buttons[index]" type="text" placeholder="🔍 Проверка">
                <button @click="removeButton(index)" class="btn-remove">×</button>
              </div>
            </div>
            
            <button @click="addButton" class="btn-add">➕ Добавить кнопку</button>
          </div>

          <!-- Conditions -->
          <div class="form-section">
            <h4>🔀 Условия и переходы</h4>
            <p class="section-description">Настройте когда и как переходить к следующему этапу</p>
            
            <div class="conditions-list">
              <div 
                v-for="(condition, index) in selectedStage.conditions" 
                :key="index"
                class="condition-item"
              >
                <div class="condition-header">
                  <span class="condition-number">Условие {{ index + 1 }}</span>
                  <button @click="removeCondition(index)" class="btn-remove">×</button>
                </div>
                
                <div class="condition-content">
                  <div class="condition-group">
                    <label>Если:</label>
                    <select v-model="condition.type" class="condition-select">
                      <option value="">Выберите условие</option>
                      <option value="user_blocked">👤 Пользователь заблокирован</option>
                      <option value="balance_sufficient">💰 Баланс >= {{ getPaidCheckPrice() }} USDT</option>
                      <option value="balance_insufficient">⚠️ Баланс < {{ getPaidCheckPrice() }} USDT</option>
                      <option value="free_check_limit">⏰ Лимит бесплатных проверок</option>
                      <option value="address_valid">✅ Адрес валиден</option>
                      <option value="address_invalid">❌ Адрес невалиден</option>
                      <option value="paid_check_available">🛡️ Доступна платная проверка</option>
                      <option value="free_check_available">🆓 Доступна бесплатная проверка</option>
                    </select>
                  </div>
                  
                  <div class="condition-group">
                    <label>То:</label>
                    <select v-model="condition.action" class="condition-select">
                      <option value="">Выберите действие</option>
                      <option value="show_message">💬 Показать сообщение</option>
                      <option value="redirect">➡️ Перейти к этапу</option>
                      <option value="skip">⏭️ Пропустить этап</option>
                      <option value="block">🚫 Заблокировать</option>
                      <option value="show_choice">📋 Показать выбор</option>
                      <option value="execute_check">🔍 Выполнить проверку</option>
                    </select>
                  </div>
                  
                  <div class="condition-group" v-if="condition.action === 'redirect'">
                    <label>Перейти к:</label>
                    <select v-model="condition.target_stage" class="condition-select">
                      <option value="">Выберите этап</option>
                      <option 
                        v-for="stage in availableNextStages" 
                        :key="stage.id"
                        :value="stage.id"
                      >
                        {{ stage.name }} ({{ getStageDescription(stage) }})
                      </option>
                    </select>
                    <small class="help-text">Выберите этап, к которому перейти при выполнении условия</small>
                  </div>
                  
                  <div class="condition-group" v-if="condition.action === 'show_message'">
                    <label>Текст сообщения:</label>
                    <select v-model="condition.text_key" class="condition-select">
                      <option value="">Выберите текст</option>
                      <option 
                        v-for="text in availableTexts" 
                        :key="text.key" 
                        :value="text.key"
                      >
                        {{ text.name }} - {{ text.content ? text.content.substring(0, 30) + '...' : 'Нет содержимого' }}
                      </option>
                    </select>
                    <small class="help-text">Выберите текст сообщения, которое покажется пользователю</small>
                  </div>
                  
                  <div class="condition-group" v-if="condition.action === 'show_choice'">
                    <label>Показать выбор:</label>
                    <select v-model="condition.choice_type" class="condition-select">
                      <option value="">Выберите тип выбора</option>
                      <option value="check_type">Тип проверки (бесплатная/платная)</option>
                      <option value="payment_method">Способ оплаты</option>
                      <option value="main_menu">Главное меню</option>
                    </select>
                    <small class="help-text">Показать пользователю выбор из нескольких опций</small>
                  </div>
                  
                  <div class="condition-group" v-if="condition.action === 'execute_check'">
                    <label>Тип проверки:</label>
                    <select v-model="condition.check_type" class="condition-select">
                      <option value="">Выберите тип проверки</option>
                      <option value="free_check">Бесплатная проверка</option>
                      <option value="paid_check">Платная проверка (AI-анализ)</option>
                    </select>
                    <small class="help-text">Выполнить выбранный тип проверки адреса</small>
                  </div>
                </div>
              </div>
            </div>
            
            <button @click="addCondition" class="btn-add">➕ Добавить условие</button>
            
            <div class="conditions-help">
              <h5>💡 Как работают условия:</h5>
              <ul>
                <li><strong>💰 Баланс >= {{ getPaidCheckPrice() }} USDT:</strong> У пользователя достаточно денег → показать платные опции</li>
                <li><strong>⚠️ Баланс < {{ getPaidCheckPrice() }} USDT:</strong> У пользователя недостаточно денег → показать только бесплатную проверку</li>
                <li><strong>✅ Адрес валиден:</strong> Адрес корректный → продолжить проверку</li>
                <li><strong>❌ Адрес невалиден:</strong> Адрес неправильный → показать ошибку</li>
                <li><strong>⏰ Лимит бесплатных проверок:</strong> Превышен лимит → предложить платную</li>
              </ul>
              
              <h5>🎯 Что происходит дальше:</h5>
              <ul>
                <li><strong>➡️ Перейти к этапу:</strong> Переключиться на другой этап сценария</li>
                <li><strong>💬 Показать сообщение:</strong> Отправить пользователю текст</li>
                <li><strong>📋 Показать выбор:</strong> Дать пользователю кнопки для выбора</li>
                <li><strong>🔍 Выполнить проверку:</strong> Запустить проверку адреса</li>
              </ul>
            </div>
          </div>

          <!-- Next Stage -->
          <div class="form-section">
            <h4>Следующий этап</h4>
            
            <div class="form-group">
              <label>Переход к:</label>
              <select v-model="selectedStage.next_stage">
                <option value="">Остаться на месте</option>
                <option 
                  v-for="stage in availableNextStages" 
                  :key="stage.id"
                  :value="stage.id"
                >
                  {{ stage.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div v-else class="no-selection">
          <p>Выберите этап для редактирования</p>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <ScenarioModal 
      v-if="showScenarioModal"
      :scenario="editingScenario"
      @close="closeScenarioModal"
      @save="saveScenario"
    />

    <!-- Preview Modal -->
    <PreviewModal 
      v-if="showPreviewModal"
      :scenario="selectedScenario"
      @close="closePreviewModal"
    />
  </div>
  </BaseLayout>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import BaseLayout from '@/components/Layout/BaseLayout.vue'
import ScenarioModal from '@/components/BotFlow/ScenarioModal.vue'
import PreviewModal from '@/components/BotFlow/PreviewModal.vue'
import { botFlowService } from '@/services/botFlow'

export default {
  name: 'BotFlowDesigner',
  components: {
    BaseLayout,
    ScenarioModal,
    PreviewModal
  },
  
  setup() {
    const scenarios = ref([])
    const selectedScenario = ref(null)
    const selectedStage = ref(null)
    const editingScenario = ref(null)
    const showScenarioModal = ref(false)
    const showPreviewModal = ref(false)
    const showInstructions = ref(false)
    const flowCanvas = ref(null)
    const availableTexts = ref([])

    // Computed
    const availableNextStages = computed(() => {
      if (!selectedScenario.value) return []
      return selectedScenario.value.stages.filter(stage => stage.id !== selectedStage.value?.id)
    })

    // Methods
    const loadScenarios = async () => {
      try {
        scenarios.value = await botFlowService.getScenarios()
      } catch (error) {
        console.error('Error loading scenarios:', error)
      }
    }

    const loadAvailableTexts = async () => {
      try {
        console.log('🔄 Начинаю загрузку текстов...')
        availableTexts.value = await botFlowService.getAvailableTexts()
        console.log('📝 Загружено текстов:', availableTexts.value.length)
        console.log('📝 Первые 5 текстов:', availableTexts.value.slice(0, 5))
      } catch (error) {
        console.error('❌ Error loading texts:', error)
      }
    }

    const getSelectedTextContent = () => {
      if (!selectedStage.value?.text_key) return null
      const text = availableTexts.value.find(t => t.key === selectedStage.value.text_key)
      return text?.content || null
    }

    const getStageDescription = (stage) => {
      const descriptions = {
        'welcome_stage_v2': 'Приветствие пользователя',
        'main_menu_v2': 'Главное меню с кнопками',
        'check_button_v2': 'Показ инструкций проверки',
        'address_input_v2': 'Ожидание ввода адреса',
        'balance_check_v2': 'Проверка баланса пользователя',
        'choice_stage_v2': 'Выбор типа проверки',
        'free_check_v2': 'Бесплатная проверка',
        'free_result_v2': 'Результат бесплатной проверки',
        'paid_check_v2': 'Платная проверка',
        'paid_result_v2': 'Результат платной проверки'
      }
      return descriptions[stage.id] || stage.trigger || 'Этап'
    }

    const getPaidCheckPrice = () => {
      const savedPrice = localStorage.getItem('paidCheckPrice')
      return savedPrice ? parseFloat(savedPrice) : 1.0
    }

    const selectScenario = (scenario) => {
      selectedScenario.value = scenario
      selectedStage.value = null
    }

    const selectStage = (stage) => {
      selectedStage.value = { ...stage }
    }

    const addScenario = () => {
      editingScenario.value = {
        id: null,
        name: 'Новый сценарий',
        description: '',
        is_active: true,
        stages: []
      }
      showScenarioModal.value = true
    }

    const editScenario = (scenario) => {
      editingScenario.value = { ...scenario }
      showScenarioModal.value = true
    }

    const saveScenario = async (scenario) => {
      try {
        if (scenario.id) {
          await botFlowService.updateScenario(scenario)
        } else {
          await botFlowService.createScenario(scenario)
        }
        await loadScenarios()
        closeScenarioModal()
      } catch (error) {
        console.error('Error saving scenario:', error)
      }
    }

    const deleteScenario = async (scenario) => {
      if (confirm('Удалить сценарий?')) {
        try {
          await botFlowService.deleteScenario(scenario.id)
          await loadScenarios()
        } catch (error) {
          console.error('Error deleting scenario:', error)
        }
      }
    }

    const addStage = () => {
      if (!selectedScenario.value) return
      
      const newStage = {
        id: `stage_${Date.now()}`,
        name: 'Новый этап',
        trigger: 'text_equals',
        trigger_value: '',
        text_key: '',
        custom_text: '',
        buttons: [],
        conditions: [],
        next_stage: ''
      }
      
      selectedScenario.value.stages.push(newStage)
      selectStage(newStage)
    }

    const deleteStage = (stage) => {
      if (!selectedScenario.value) return
      
      const index = selectedScenario.value.stages.findIndex(s => s.id === stage.id)
      if (index > -1) {
        selectedScenario.value.stages.splice(index, 1)
        selectedStage.value = null
      }
    }

    const addButton = () => {
      if (!selectedStage.value) return
      selectedStage.value.buttons.push('')
    }

    const removeButton = (index) => {
      if (!selectedStage.value) return
      selectedStage.value.buttons.splice(index, 1)
    }

    const addCondition = () => {
      if (!selectedStage.value) return
      selectedStage.value.conditions.push({
        type: 'user_blocked',
        action: 'show_message'
      })
    }

    const removeCondition = (index) => {
      if (!selectedStage.value) return
      selectedStage.value.conditions.splice(index, 1)
    }

    const getTriggerText = (trigger) => {
      const triggerMap = {
        'command_start': 'Команда /start',
        'text_equals': 'Текст равен',
        'text_contains': 'Текст содержит',
        'callback_data': 'Callback данные',
        'address_input': 'Ввод адреса',
        'balance_check': 'Проверка баланса'
      }
      return triggerMap[trigger] || trigger
    }

    const saveFlow = async () => {
      if (!selectedScenario.value) return
      
      try {
        await botFlowService.updateScenario(selectedScenario.value)
        alert('Сценарий сохранен!')
      } catch (error) {
        console.error('Error saving flow:', error)
        alert('Ошибка при сохранении')
      }
    }

    const previewFlow = () => {
      if (!selectedScenario.value) return
      showPreviewModal.value = true
    }

    const testFlow = async () => {
      if (!selectedScenario.value) return
      
      try {
        await botFlowService.testScenario(selectedScenario.value.id)
        alert('Тест запущен! Проверьте бота.')
      } catch (error) {
        console.error('Error testing flow:', error)
        alert('Ошибка при запуске теста')
      }
    }

    const closeScenarioModal = () => {
      showScenarioModal.value = false
      editingScenario.value = null
    }

    const closePreviewModal = () => {
      showPreviewModal.value = false
    }

    // Watcher для автоматического сохранения при изменении этапа
    watch(selectedStage, async (newStage, oldStage) => {
      if (newStage && oldStage && selectedScenario.value) {
        // Находим индекс измененного этапа
        const stageIndex = selectedScenario.value.stages.findIndex(s => s.id === newStage.id)
        if (stageIndex !== -1) {
          // Обновляем этап в сценарии
          selectedScenario.value.stages[stageIndex] = { ...newStage }
          
          // Автоматически сохраняем
          try {
            console.log('🔄 Автосохранение этапа:', newStage.name, 'text_key:', newStage.text_key)
            await botFlowService.updateScenario(selectedScenario.value)
            console.log('✅ Этап автосохранен')
          } catch (error) {
            console.error('❌ Ошибка автосохранения:', error)
          }
        }
      }
    }, { deep: true })

    // Lifecycle
    onMounted(() => {
      console.log('🚀 Flow Designer mounted, загружаю данные...')
      loadScenarios()
      loadAvailableTexts()
    })

    return {
      scenarios,
      selectedScenario,
      selectedStage,
      editingScenario,
      showScenarioModal,
      showPreviewModal,
      showInstructions,
      flowCanvas,
      availableTexts,
      availableNextStages,
      
      selectScenario,
      selectStage,
      addScenario,
      editScenario,
      saveScenario,
      deleteScenario,
      addStage,
      deleteStage,
      addButton,
      removeButton,
      addCondition,
      removeCondition,
      getTriggerText,
      getSelectedTextContent,
      getStageDescription,
      getPaidCheckPrice,
      saveFlow,
      previewFlow,
      testFlow,
      closeScenarioModal,
      closePreviewModal
    }
  }
}
</script>

<style scoped>
.bot-flow-designer {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  height: calc(100vh - 100px);
}

.left-panel {
  width: 300px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.center-panel {
  flex: 0.4;
  min-width: 400px;
  background: white;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 0.6;
  min-width: 500px;
  background: white;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
}

.scenarios-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.scenario-item {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.scenario-item:hover {
  border-color: #4299e1;
  box-shadow: 0 2px 4px rgba(66, 153, 225, 0.1);
}

.scenario-item.active {
  border-color: #4299e1;
  background: #ebf8ff;
}

.scenario-info h4 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.scenario-info p {
  margin: 0 0 12px 0;
  color: #718096;
  font-size: 14px;
}

.scenario-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.status.active {
  color: #38a169;
}

.status.inactive {
  color: #e53e3e;
}

.scenario-actions {
  display: flex;
  gap: 8px;
}

.flow-canvas {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.flow-stages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.flow-stage {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.flow-stage:hover {
  border-color: #4299e1;
  box-shadow: 0 4px 8px rgba(66, 153, 225, 0.1);
}

.flow-stage.selected {
  border-color: #4299e1;
  background: #ebf8ff;
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.stage-number {
  background: #4299e1;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.stage-header h4 {
  margin: 0;
  flex: 1;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.stage-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stage-content > div {
  font-size: 14px;
  color: #4a5568;
}

.stage-buttons {
  margin-top: 8px;
}

.buttons-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.button-preview {
  background: #e2e8f0;
  color: #4a5568;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.stage-connections {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
}

.connection-line {
  width: 2px;
  height: 20px;
  background: #4299e1;
}

.stage-editor {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4299e1;
}

.buttons-list,
.conditions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.button-item,
.condition-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.button-item input,
.condition-item select {
  flex: 1;
}

.no-selection {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
  font-style: italic;
}

/* Buttons */
.btn-primary,
.btn-secondary,
.btn-success,
.btn-add,
.btn-edit,
.btn-delete,
.btn-remove {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover {
  background: #3182ce;
}

.btn-secondary {
  background: #718096;
  color: white;
}

.btn-secondary:hover {
  background: #4a5568;
}

.btn-success {
  background: #38a169;
  color: white;
}

.btn-success:hover {
  background: #2f855a;
}

.btn-add {
  background: #48bb78;
  color: white;
}

.btn-add:hover {
  background: #38a169;
}

.btn-edit {
  background: #ed8936;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.btn-edit:hover {
  background: #dd6b20;
}

.btn-delete {
  background: #e53e3e;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.btn-delete:hover {
  background: #c53030;
}

.btn-remove {
  background: #e53e3e;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

 .btn-remove:hover {
   background: #c53030;
 }

/* Conditions Styles */
.conditions-list {
  margin-bottom: 20px;
}

.condition-item {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.condition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.condition-number {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.condition-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.condition-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.condition-group label {
  font-weight: 500;
  color: #4a5568;
  font-size: 13px;
}

.condition-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.condition-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.conditions-help {
  background: #ebf8ff;
  border: 1px solid #bee3f8;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.conditions-help h5 {
  margin: 0 0 12px 0;
  color: #2b6cb0;
  font-size: 14px;
  font-weight: 600;
}

.conditions-help ul {
  margin: 0;
  padding-left: 20px;
}

.conditions-help li {
  margin-bottom: 6px;
  color: #4a5568;
  font-size: 13px;
}

 .section-description {
   color: #718096;
   font-size: 13px;
   margin: 0 0 16px 0;
   font-style: italic;
 }

 .btn-info {
   background: #3182ce;
   color: white;
 }

 .btn-info:hover {
   background: #2c5aa0;
 }

 /* Instructions Modal */
 .instructions-modal {
   position: fixed;
   top: 0;
   left: 0;
   right: 0;
   bottom: 0;
   background: rgba(0, 0, 0, 0.5);
   display: flex;
   align-items: center;
   justify-content: center;
   z-index: 1000;
 }

 .instructions-content {
   background: white;
   border-radius: 12px;
   max-width: 800px;
   max-height: 90vh;
   width: 90%;
   overflow: hidden;
   display: flex;
   flex-direction: column;
 }

 .instructions-header {
   background: #4299e1;
   color: white;
   padding: 20px;
   display: flex;
   justify-content: space-between;
   align-items: center;
 }

 .instructions-header h2 {
   margin: 0;
   font-size: 20px;
   font-weight: bold;
 }

 .btn-close {
   background: none;
   border: none;
   color: white;
   font-size: 24px;
   cursor: pointer;
   padding: 0;
   width: 30px;
   height: 30px;
   display: flex;
   align-items: center;
   justify-content: center;
   border-radius: 50%;
   transition: background 0.2s;
 }

 .btn-close:hover {
   background: rgba(255, 255, 255, 0.2);
 }

 .instructions-body {
   flex: 1;
   overflow-y: auto;
   padding: 20px;
 }

 .instruction-section {
   margin-bottom: 30px;
 }

 .instruction-section h3 {
   color: #2d3748;
   font-size: 18px;
   font-weight: 600;
   margin: 0 0 16px 0;
   border-bottom: 2px solid #e2e8f0;
   padding-bottom: 8px;
 }

 .instruction-section p {
   color: #4a5568;
   line-height: 1.6;
   margin: 0 0 16px 0;
 }

 .instruction-section ul,

/* Улучшенные стили для выбора текстов */
.text-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  margin-bottom: 12px;
}

.text-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.text-preview {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
}

.text-preview h5 {
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 14px;
  font-weight: 600;
}

.preview-content {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  color: #4a5568;
  line-height: 1.5;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

/* Улучшенные стили для условий */
.condition-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  margin-bottom: 8px;
}

.condition-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.condition-group label {
  display: block;
  margin-bottom: 6px;
  color: #2d3748;
  font-size: 13px;
  font-weight: 600;
}

.help-text {
  display: block;
  margin-top: 4px;
  color: #718096;
  font-size: 11px;
  font-style: italic;
}
 .instruction-section ol {
   color: #4a5568;
   line-height: 1.6;
   margin: 0 0 16px 0;
   padding-left: 20px;
 }

 .instruction-section li {
   margin-bottom: 8px;
 }

 .instruction-section strong {
   color: #2d3748;
   font-weight: 600;
 }

 .example-scenario {
   background: #f7fafc;
   border: 1px solid #e2e8f0;
   border-radius: 8px;
   padding: 16px;
   margin: 16px 0;
 }

 .example-scenario h4 {
   color: #2d3748;
   font-size: 16px;
   font-weight: 600;
   margin: 0 0 12px 0;
 }

 .example-scenario ol {
   margin: 0;
   padding-left: 20px;
 }

 .example-scenario li {
   margin-bottom: 6px;
   color: #4a5568;
 }
</style>
ты же 