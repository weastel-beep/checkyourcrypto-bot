<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEdit ? 'Редактировать меню' : 'Создать меню' }}</h2>
        <button @click="closeModal" class="btn-close">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="saveMenu" class="modal-body">
        <!-- Основная информация -->
        <div class="form-section">
          <h3>Основная информация</h3>
          
          <div class="form-group">
            <label>Название меню:</label>
            <input 
              v-model="form.name" 
              type="text" 
              required
              placeholder="main_menu"
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Язык:</label>
              <select v-model="form.language" required>
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>

            <div class="form-group">
              <label>Тип меню:</label>
              <select v-model="form.menu_type" required>
                <option value="reply_keyboard">Reply Keyboard</option>
                <option value="inline_keyboard">Inline Keyboard</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>
              <input 
                v-model="form.is_active" 
                type="checkbox"
              >
              Активно
            </label>
          </div>
        </div>

        <!-- Элементы меню -->
        <div class="form-section">
          <div class="section-header">
            <h3>Элементы меню</h3>
            <button type="button" @click="addMenuItem" class="btn-add">
              <i class="fas fa-plus"></i> Добавить элемент
            </button>
          </div>

          <div class="menu-items">
            <div 
              v-for="(item, index) in form.items" 
              :key="index"
              class="menu-item"
            >
              <div class="item-header">
                <span>Элемент {{ index + 1 }}</span>
                <button 
                  type="button" 
                  @click="removeMenuItem(index)"
                  class="btn-remove"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>

              <div class="item-content">
                <div class="form-group">
                  <label>Текст кнопки:</label>
                  <input 
                    v-model="item.text" 
                    type="text" 
                    required
                    placeholder="🔍 Проверка"
                  >
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Ряд:</label>
                    <input 
                      v-model.number="item.row_position" 
                      type="number" 
                      min="0"
                      required
                    >
                  </div>

                  <div class="form-group">
                    <label>Колонка:</label>
                    <input 
                      v-model.number="item.column_position" 
                      type="number" 
                      min="0"
                      required
                    >
                  </div>
                </div>

                <div class="form-group" v-if="form.menu_type === 'inline_keyboard'">
                  <label>Callback Data:</label>
                  <input 
                    v-model="item.callback_data" 
                    type="text"
                    placeholder="check_address"
                  >
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Предварительный просмотр -->
        <div class="form-section">
          <h3>Предварительный просмотр</h3>
          <div class="keyboard-preview">
            <div 
              v-for="(row, rowIndex) in previewKeyboard" 
              :key="rowIndex"
              class="keyboard-row"
            >
              <button 
                v-for="(item, colIndex) in row" 
                :key="colIndex"
                class="preview-button"
                :class="form.menu_type"
              >
                {{ item.text }}
              </button>
            </div>
          </div>
        </div>

        <!-- Связки с текстами -->
        <div class="form-section">
          <h3>Связки с текстами</h3>
          <div class="text-links">
            <div 
              v-for="(link, index) in form.text_links" 
              :key="index"
              class="text-link"
            >
              <div class="form-row">
                <div class="form-group">
                  <label>Категория текста:</label>
                  <select v-model="link.text_category">
                    <option value="">Выберите категорию</option>
                    <option value="welcome">Приветствие</option>
                    <option value="main_menu">Главное меню</option>
                    <option value="check_button">Кнопка проверки</option>
                    <option value="balance_button">Кнопка баланса</option>
                    <option value="profile_button">Кнопка профиля</option>
                    <option value="faq_button">Кнопка FAQ</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Язык:</label>
                  <select v-model="link.language">
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                  </select>
                </div>

                <button 
                  type="button" 
                  @click="removeTextLink(index)"
                  class="btn-remove"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>

            <button type="button" @click="addTextLink" class="btn-add">
              <i class="fas fa-plus"></i> Добавить связку
            </button>
          </div>
        </div>

        <!-- Кнопки действий -->
        <div class="modal-footer">
          <button type="button" @click="closeModal" class="btn-secondary">
            Отмена
          </button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            {{ saving ? 'Сохранение...' : (isEdit ? 'Обновить' : 'Создать') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useMenuStore } from '@/stores/menuStore'

export default {
  name: 'MenuEditModal',
  props: {
    menu: {
      type: Object,
      default: null
    },
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const menuStore = useMenuStore()
    const saving = ref(false)

    const form = ref({
      name: '',
      language: 'ru',
      menu_type: 'reply_keyboard',
      is_active: true,
      items: [],
      text_links: []
    })

    // Инициализация формы
    if (props.menu) {
      form.value = {
        name: props.menu.name || '',
        language: props.menu.language || 'ru',
        menu_type: props.menu.menu_type || 'reply_keyboard',
        is_active: props.menu.is_active !== undefined ? props.menu.is_active : true,
        items: props.menu.items ? [...props.menu.items] : [],
        text_links: props.menu.text_links ? [...props.menu.text_links] : []
      }
    }

    const previewKeyboard = computed(() => {
      const rows = {}
      form.value.items.forEach(item => {
        if (!rows[item.row_position]) {
          rows[item.row_position] = {}
        }
        rows[item.row_position][item.column_position] = item
      })
      
      return Object.keys(rows).sort().map(rowIndex => {
        const row = rows[rowIndex]
        return Object.keys(row).sort().map(colIndex => row[colIndex])
      })
    })

    const addMenuItem = () => {
      const newItem = {
        text: '',
        callback_data: '',
        row_position: form.value.items.length,
        column_position: 0,
        is_active: true
      }
      form.value.items.push(newItem)
    }

    const removeMenuItem = (index) => {
      form.value.items.splice(index, 1)
    }

    const addTextLink = () => {
      form.value.text_links.push({
        text_category: '',
        language: form.value.language
      })
    }

    const removeTextLink = (index) => {
      form.value.text_links.splice(index, 1)
    }

    const saveMenu = async () => {
      saving.value = true
      
      try {
        if (props.isEdit) {
          await menuStore.updateMenu(props.menu.id, form.value)
        } else {
          await menuStore.createMenu(form.value)
        }
        
        emit('saved')
      } catch (error) {
        console.error('Ошибка сохранения меню:', error)
        alert('Ошибка сохранения меню')
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      emit('close')
    }

    return {
      form,
      saving,
      previewKeyboard,
      addMenuItem,
      removeMenuItem,
      addTextLink,
      removeTextLink,
      saveMenu,
      closeModal
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
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.menu-items {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 15px;
  background: #f8f9fa;
}

.menu-item {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.menu-item:last-child {
  margin-bottom: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 500;
  color: #333;
}

.item-content {
  display: grid;
  gap: 15px;
}

.keyboard-preview {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  background: #f8f9fa;
}

.keyboard-row {
  display: flex;
  gap: 5px;
  margin-bottom: 5px;
}

.keyboard-row:last-child {
  margin-bottom: 0;
}

.preview-button {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
  font-size: 12px;
  cursor: default;
  min-width: 80px;
  text-align: center;
}

.preview-button.reply_keyboard {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.preview-button.inline_keyboard {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.text-links {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 15px;
  background: #f8f9fa;
}

.text-link {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.text-link:last-child {
  margin-bottom: 0;
}

.btn-add,
.btn-remove {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-add {
  background: #28a745;
  color: white;
}

.btn-add:hover {
  background: #218838;
}

.btn-remove {
  background: #dc3545;
  color: white;
}

.btn-remove:hover {
  background: #c82333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-secondary,
.btn-primary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
