<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEdit ? 'Редактировать сценарий' : 'Создать сценарий' }}</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <form @submit.prevent="saveScenario" class="modal-body">
        <div class="form-group">
          <label>Название сценария:</label>
          <input v-model="form.name" type="text" required placeholder="Проверка адреса">
        </div>

        <div class="form-group">
          <label>Описание:</label>
          <textarea v-model="form.description" rows="3" placeholder="Описание сценария..."></textarea>
        </div>

        <div class="form-group">
          <label>
            <input v-model="form.is_active" type="checkbox">
            Активен
          </label>
        </div>

        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn-secondary">
            Отмена
          </button>
          <button type="submit" class="btn-primary">
            {{ isEdit ? 'Обновить' : 'Создать' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'ScenarioModal',
  props: {
    scenario: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close', 'save'],
  
  setup(props, { emit }) {
    const form = ref({
      id: null,
      name: '',
      description: '',
      is_active: true,
      stages: []
    })

    const isEdit = computed(() => !!props.scenario.id)

    // Заполняем форму при изменении props
    watch(() => props.scenario, (newScenario) => {
      if (newScenario.id) {
        form.value = { ...newScenario }
      } else {
        form.value = {
          id: null,
          name: '',
          description: '',
          is_active: true,
          stages: []
        }
      }
    }, { immediate: true })

    const saveScenario = () => {
      emit('save', { ...form.value })
    }

    return {
      form,
      isEdit,
      saveScenario
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
  width: 500px;
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4299e1;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
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
</style>
