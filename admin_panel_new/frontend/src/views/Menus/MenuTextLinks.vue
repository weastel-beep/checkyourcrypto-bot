<template>
  <div class="menu-text-links">
    <div class="header">
      <h1>Связки меню с текстами</h1>
      <p class="description">
        Управляйте связками между кнопками меню и текстами. 
        Это позволяет динамически изменять тексты кнопок через админку.
      </p>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <div class="filter-group">
        <label>Язык:</label>
        <select v-model="filters.language" @change="loadLinks">
          <option value="">Все языки</option>
          <option value="ru">Русский</option>
          <option value="en">English</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Меню:</label>
        <select v-model="filters.menu" @change="loadLinks">
          <option value="">Все меню</option>
          <option v-for="menu in menus" :key="menu.id" :value="menu.name">
            {{ menu.name }}
          </option>
        </select>
      </div>
      
      <button @click="loadLinks" class="btn btn-primary">
        🔄 Обновить
      </button>
    </div>

    <!-- Таблица связок -->
    <div class="table-container">
      <table v-if="links.length > 0">
        <thead>
          <tr>
            <th>Кнопка</th>
            <th>Меню</th>
            <th>Категория текста</th>
            <th>Язык</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="link in links" :key="link.id">
            <td>
              <span class="button-text">{{ link.button_text }}</span>
            </td>
            <td>{{ link.menu_name }}</td>
            <td>
              <span class="text-category">{{ link.text_category }}</span>
            </td>
            <td>
              <span class="language-badge" :class="link.language">
                {{ link.language.toUpperCase() }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button @click="editLink(link)" class="btn btn-sm btn-secondary">
                  ✏️ Редактировать
                </button>
                <button @click="deleteLink(link.id)" class="btn btn-sm btn-danger">
                  🗑️ Удалить
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="empty-state">
        <div class="empty-icon">🔗</div>
        <h3>Связки не найдены</h3>
        <p>Создайте первую связку между кнопкой меню и текстом</p>
        <button @click="showCreateModal = true" class="btn btn-primary">
          ➕ Создать связку
        </button>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Редактировать связку' : 'Создать связку' }}</h3>
          <button @click="closeModal" class="btn-close">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveLink">
            <div class="form-group">
              <label>Элемент меню:</label>
              <select v-model="linkForm.menu_item_id" required>
                <option value="">Выберите элемент меню</option>
                <option v-for="item in menuItems" :key="item.id" :value="item.id">
                  {{ item.text }} ({{ item.menu_name }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Категория текста:</label>
              <input 
                v-model="linkForm.text_category" 
                type="text" 
                placeholder="Например: check_button"
                required
              />
            </div>
            
            <div class="form-group">
              <label>Язык:</label>
              <select v-model="linkForm.language" required>
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">
            Отмена
          </button>
          <button @click="saveLink" class="btn btn-primary">
            {{ showEditModal ? 'Обновить' : 'Создать' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Кнопка создания -->
    <div v-if="links.length > 0" class="create-button">
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ Создать связку
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useMenuStore } from '@/stores/menuStore'
import { useTextStore } from '@/stores/textStore'
import { debounce } from '@/utils/helpers'

export default {
  name: 'MenuTextLinks',
  setup() {
    const menuStore = useMenuStore()
    const textStore = useTextStore()
    
    const links = ref([])
    const menus = ref([])
    const menuItems = ref([])
    
    const filters = reactive({
      language: '',
      menu: ''
    })
    
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingLink = ref(null)
    
    const linkForm = reactive({
      menu_item_id: '',
      text_category: '',
      language: 'ru'
    })
    
    const loadLinks = async () => {
      try {
        const params = {}
        if (filters.language) params.language = filters.language
        if (filters.menu) params.menu = filters.menu
        
        const response = await menuStore.getTextLinks(params)
        links.value = response.links || []
      } catch (error) {
        console.error('Ошибка загрузки связок:', error)
      }
    }
    
    const loadMenus = async () => {
      try {
        const response = await menuStore.getMenus()
        menus.value = response.menus || []
      } catch (error) {
        console.error('Ошибка загрузки меню:', error)
      }
    }
    
    const loadMenuItems = async () => {
      try {
        const response = await menuStore.getAllMenuItems()
        menuItems.value = response.items || []
      } catch (error) {
        console.error('Ошибка загрузки элементов меню:', error)
      }
    }
    
    const editLink = (link) => {
      editingLink.value = link
      linkForm.menu_item_id = link.menu_item_id
      linkForm.text_category = link.text_category
      linkForm.language = link.language
      showEditModal.value = true
    }
    
    const deleteLink = async (linkId) => {
      if (!confirm('Вы уверены, что хотите удалить эту связку?')) return
      
      try {
        await menuStore.deleteTextLink(linkId)
        await loadLinks()
      } catch (error) {
        console.error('Ошибка удаления связки:', error)
      }
    }
    
    const saveLink = async () => {
      try {
        if (showEditModal.value) {
          await menuStore.updateTextLink(editingLink.value.id, linkForm)
        } else {
          await menuStore.createTextLink(linkForm)
        }
        
        closeModal()
        await loadLinks()
      } catch (error) {
        console.error('Ошибка сохранения связки:', error)
      }
    }
    
    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingLink.value = null
      Object.assign(linkForm, {
        menu_item_id: '',
        text_category: '',
        language: 'ru'
      })
    }
    
    onMounted(async () => {
      await Promise.all([
        loadLinks(),
        loadMenus(),
        loadMenuItems()
      ])
    })
    
    return {
      links,
      menus,
      menuItems,
      filters,
      showCreateModal,
      showEditModal,
      linkForm,
      loadLinks: debounce(loadLinks, 300),
      editLink,
      deleteLink,
      saveLink,
      closeModal
    }
  }
}
</script>

<style scoped>
.menu-text-links {
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.description {
  color: #7f8c8d;
  margin: 0;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

.button-text {
  font-weight: 500;
  color: #2c3e50;
}

.text-category {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.language-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.language-badge.ru {
  background: #e8f5e8;
  color: #2e7d32;
}

.language-badge.en {
  background: #fff3e0;
  color: #f57c00;
}

.actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.create-button {
  margin-top: 20px;
  text-align: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}
</style>
