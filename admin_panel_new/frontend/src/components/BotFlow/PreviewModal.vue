<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>👁️ Предпросмотр сценария</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <div class="modal-body">
        <div v-if="scenario" class="preview-content">
          <div class="scenario-info">
            <h3>{{ scenario.name }}</h3>
            <p>{{ scenario.description }}</p>
            <div class="scenario-stats">
              <span>📊 {{ scenario.stages.length }} этапов</span>
              <span :class="['status', scenario.is_active ? 'active' : 'inactive']">
                {{ scenario.is_active ? '✅ Активен' : '❌ Неактивен' }}
              </span>
            </div>
          </div>

          <div class="stages-preview">
            <h4>🎭 Этапы сценария:</h4>
            <div class="stages-list">
              <div 
                v-for="(stage, index) in scenario.stages" 
                :key="stage.id"
                class="stage-preview"
              >
                <div class="stage-header">
                  <span class="stage-number">{{ index + 1 }}</span>
                  <h5>{{ stage.name }}</h5>
                </div>
                
                <div class="stage-details">
                  <div class="detail-item">
                    <strong>Триггер:</strong> {{ getTriggerText(stage.trigger) }}
                    <span v-if="stage.trigger_value"> → "{{ stage.trigger_value }}"</span>
                  </div>
                  
                  <div class="detail-item" v-if="stage.text_key || stage.custom_text">
                    <strong>Текст:</strong> 
                    <span v-if="stage.text_key">[{{ stage.text_key }}]</span>
                    <span v-else>{{ stage.custom_text }}</span>
                  </div>
                  
                  <div class="detail-item" v-if="stage.buttons?.length">
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
                  
                  <div class="detail-item" v-if="stage.conditions?.length">
                    <strong>Условия:</strong>
                    <ul class="conditions-list">
                      <li 
                        v-for="condition in stage.conditions" 
                        :key="condition.type"
                      >
                        {{ getConditionText(condition) }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="preview-actions">
            <button @click="testScenario" class="btn-success">
              🧪 Запустить тест
            </button>
            <button @click="$emit('close')" class="btn-secondary">
              Закрыть
            </button>
          </div>
        </div>

        <div v-else class="no-scenario">
          <p>Сценарий не выбран</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PreviewModal',
  props: {
    scenario: {
      type: Object,
      default: null
    }
  },
  emits: ['close'],
  
  setup(props) {
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

    const getConditionText = (condition) => {
      const conditionMap = {
        'user_blocked': 'Пользователь заблокирован',
        'balance_check': 'Проверка баланса',
        'free_check_limit': 'Лимит бесплатных проверок',
        'address_valid': 'Адрес валиден',
        'address_invalid': 'Адрес невалиден',
        'balance_sufficient': 'Баланс достаточен',
        'balance_insufficient': 'Баланс недостаточен'
      }
      
      const actionMap = {
        'show_message': 'Показать сообщение',
        'redirect': 'Перенаправить',
        'skip': 'Пропустить',
        'continue': 'Продолжить',
        'show_paid_options': 'Показать платные опции',
        'show_free_only': 'Показать только бесплатные'
      }
      
      const conditionText = conditionMap[condition.type] || condition.type
      const actionText = actionMap[condition.action] || condition.action
      
      return `${conditionText} → ${actionText}`
    }

    const testScenario = () => {
      if (props.scenario) {
        alert(`🧪 Тест сценария "${props.scenario.name}" запущен!\n\nПроверьте бота в Telegram.`)
      }
    }

    return {
      getTriggerText,
      getConditionText,
      testScenario
    }
  }
}
</script>

<style scoped>
.modal-overlay {
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

.modal-content {
  background: white;
  border-radius: 12px;
  width: 700px;
  max-width: 90%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  background: #4299e1;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
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

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.scenario-info {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.scenario-info h3 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
}

.scenario-info p {
  margin: 0 0 12px 0;
  color: #718096;
  font-size: 14px;
}

.scenario-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.status.active {
  color: #38a169;
}

.status.inactive {
  color: #e53e3e;
}

.stages-preview h4 {
  margin: 0 0 16px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.stages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stage-preview {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
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

.stage-header h5 {
  margin: 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.stage-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  font-size: 14px;
  color: #4a5568;
}

.detail-item strong {
  color: #2d3748;
  font-weight: 600;
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

.conditions-list {
  margin: 4px 0 0 0;
  padding-left: 20px;
  font-size: 13px;
}

.conditions-list li {
  margin-bottom: 4px;
  color: #4a5568;
}

.preview-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn-success,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-success {
  background: #38a169;
  color: white;
}

.btn-success:hover {
  background: #2f855a;
}

.btn-secondary {
  background: #718096;
  color: white;
}

.btn-secondary:hover {
  background: #4a5568;
}

.no-scenario {
  text-align: center;
  color: #718096;
  font-style: italic;
  padding: 40px;
}
</style>
