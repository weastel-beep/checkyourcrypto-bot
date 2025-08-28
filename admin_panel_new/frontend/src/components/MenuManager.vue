<template>
  <div class="menu-manager">
    <div class="header">
      <h2>🎛️ Управление меню бота</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ Создать меню
      </button>
    </div>

    <!-- Список меню -->
    <div class="menu-list">
      <div v-for="menu in menus" :key="menu.id" class="menu-card">
        <div class="menu-header">
          <h3>{{ menu.name }} ({{ menu.language }})</h3>
          <div class="menu-actions">
            <button @click="editMenu(menu)" class="btn btn-sm btn-secondary">
              ✏️ Редактировать
            </button>
            <button @click="deleteMenu(menu.id)" class="btn btn-sm btn-danger">
              🗑️ Удалить
            </button>
          </div>
        </div>
        
        <div class="menu-preview">
          <h4>Предварительный просмотр:</h4>
          <div class="keyboard-preview">
            <div v-for="(row, rowIndex) in getMenuStructure(menu)" :key="rowIndex" class="keyboard-row">
              <button 
                v-for="item in row" 
                :key="item.id" 
                class="keyboard-button"
                :class="{ 'has-callback': item.callback_data }"
              >
                {{ item.text }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="menu-info">
          <span class="badge" :class="menu.is_active ? 'badge-success' : 'badge-warning'">
            {{ menu.is_active ? 'Активно' : 'Неактивно' }}
          </span>
          <span class="badge badge-info">{{ menu.menu_type }}</span>
          <span class="text-muted">{{ formatDate(menu.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования меню -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Редактировать меню' : 'Создать новое меню' }}</h3>
          <button @click="closeModal" class="btn-close">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveMenu">
            <div class="form-group">
              <label>Название меню:</label>
              <input 
                v-model="menuForm.name" 
                type="text" 
                placeholder="main_menu"
                required
              />
            </div>
            
            <div class="form-group">
              <label>Язык:</label>
              <select v-model="menuForm.language" required>
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Тип меню:</label>
              <select v-model="menuForm.menu_type" required>
                <option value="reply_keyboard">Reply Keyboard</option>
                <option value="inline_keyboard">Inline Keyboard</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>
                Структура меню:
                <button type="button" @click="addRow" class="btn btn-sm btn-secondary">
                  ➕ Добавить строку
                </button>
              </label>
              
              <div class="menu-structure-editor">
                <div v-for="(row, rowIndex) in menuForm.structure" :key="rowIndex" class="structure-row">
                  <div class="row-header">
                    <span>Строка {{ rowIndex + 1 }}</span>
                    <button type="button" @click="removeRow(rowIndex)" class="btn btn-sm btn-danger">
                      🗑️
                    </button>
                  </div>
                  
                  <div class="row-buttons">
                    <div v-for="(button, buttonIndex) in row" :key="buttonIndex" class="button-editor">
                      <input 
                        v-model="button.text" 
                        type="text" 
                        placeholder="Текст кнопки"
                        class="button-text"
                      />
                      <input 
                        v-model="button.callback" 
                        type="text" 
                        placeholder="Callback (опционально)"
                        class="button-callback"
                      />
                      <button type="button" @click="removeButton(rowIndex, buttonIndex)" class="btn btn-sm btn-danger">
                        🗑️
                      </button>
                    </div>
                    
                    <button type="button" @click="addButton(rowIndex)" class="btn btn-sm btn-secondary">
                      ➕ Кнопка
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label>
                <input v-model="menuForm.is_active" type="checkbox" />
                Активно
              </label>
            </div>
            
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn btn-secondary">
                Отмена
              </button>
              <button type="submit" class="btn btn-primary">
                {{ showEditModal ? 'Сохранить' : 'Создать' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Импорт меню -->
    <div class="import-section">
      <h3>📥 Импорт меню</h3>
      <div class="import-form">
        <textarea 
          v-model="importData" 
          placeholder="Вставьте JSON структуру меню..."
          rows="10"
        ></textarea>
        <button @click="importMenus" class="btn btn-primary">
          📥 Импортировать
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import menuService from '../services/menus.js'

export default {
  name: 'MenuManager',
  setup() {
    const menus = ref([])
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingMenu = ref(null)
    const importData = ref('')
    
    const menuForm = ref({
      name: '',
      language: 'ru',
      menu_type: 'reply_keyboard',
      structure: [[]],
      is_active: true
    })

    // Загрузка меню
    const loadMenus = async () => {
      try {
        const response = await menuService.getMenus()
        menus.value = response.menus || []
      } catch (error) {
        console.error('Ошибка загрузки меню:', error)
      }
    }

    // Получение структуры меню
    const getMenuStructure = (menu) => {
      return menuService.getMenuStructure(menu)
    }

    // Редактирование меню
    const editMenu = (menu) => {
      editingMenu.value = menu
      menuForm.value = {
        name: menu.name,
        language: menu.language,
        menu_type: menu.menu_type,
        structure: getMenuStructure(menu).map(row => 
          row.map(item => ({
            text: item.text,
            callback: item.callback_data || ''
          }))
        ),
        is_active: menu.is_active
      }
      showEditModal.value = true
    }

    // Удаление меню
    const deleteMenu = async (menuId) => {
      if (!confirm('Вы уверены, что хотите удалить это меню?')) return
      
      try {
        await menuService.deleteMenu(menuId)
        await loadMenus()
      } catch (error) {
        console.error('Ошибка удаления меню:', error)
      }
    }

    // Сохранение меню
    const saveMenu = async () => {
      try {
        const menuData = {
          menu_name: menuForm.value.name,
          language: menuForm.value.language,
          menu_type: menuForm.value.menu_type,
          structure: menuForm.value.structure
        }

        if (showEditModal.value && editingMenu.value) {
          await menuService.updateMenu(editingMenu.value.id, menuData)
        } else {
          await menuService.createMenu(menuData)
        }

        closeModal()
        await loadMenus()
      } catch (error) {
        console.error('Ошибка сохранения меню:', error)
      }
    }

    // Импорт меню
    const importMenus = async () => {
      try {
        const data = JSON.parse(importData.value)
        await menuService.importMenus(data)
        importData.value = ''
        await loadMenus()
      } catch (error) {
        console.error('Ошибка импорта меню:', error)
        alert('Ошибка импорта: ' + error.message)
      }
    }

    // Управление структурой меню
    const addRow = () => {
      menuForm.value.structure.push([])
    }

    const removeRow = (rowIndex) => {
      menuForm.value.structure.splice(rowIndex, 1)
    }

    const addButton = (rowIndex) => {
      menuForm.value.structure[rowIndex].push({ text: '', callback: '' })
    }

    const removeButton = (rowIndex, buttonIndex) => {
      menuForm.value.structure[rowIndex].splice(buttonIndex, 1)
    }

    // Закрытие модального окна
    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingMenu.value = null
      menuForm.value = {
        name: '',
        language: 'ru',
        menu_type: 'reply_keyboard',
        structure: [[]],
        is_active: true
      }
    }

    // Форматирование даты
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('ru-RU')
    }

    onMounted(() => {
      loadMenus()
    })

    return {
      menus,
      showCreateModal,
      showEditModal,
      menuForm,
      importData,
      getMenuStructure,
      editMenu,
      deleteMenu,
      saveMenu,
      importMenus,
      addRow,
      removeRow,
      addButton,
      removeButton,
      closeModal,
      formatDate
    }
  }
}
</script>

<style scoped>
.menu-manager {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.menu-list {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
}

.menu-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.menu-actions {
  display: flex;
  gap: 10px;
}

.menu-preview {
  margin-bottom: 15px;
}

.keyboard-preview {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background: #f8f9fa;
}

.keyboard-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.keyboard-row:last-child {
  margin-bottom: 0;
}

.keyboard-button {
  padding: 8px 16px;
  border: 1px solid #007bff;
  border-radius: 4px;
  background: white;
  color: #007bff;
  font-size: 14px;
  cursor: default;
}

.keyboard-button.has-callback {
  background: #007bff;
  color: white;
}

.menu-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.badge-success {
  background: #28a745;
  color: white;
}

.badge-warning {
  background: #ffc107;
  color: black;
}

.badge-info {
  background: #17a2b8;
  color: white;
}

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

.modal {
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
  border-bottom: 1px solid #ddd;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.menu-structure-editor {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
}

.structure-row {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.row-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.row-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.button-editor {
  display: flex;
  gap: 5px;
  align-items: center;
}

.button-text {
  width: 150px;
}

.button-callback {
  width: 120px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.import-section {
  border-top: 1px solid #ddd;
  padding-top: 20px;
}

.import-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.import-form textarea {
  font-family: monospace;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.text-muted {
  color: #6c757d;
  font-size: 12px;
}
</style>
