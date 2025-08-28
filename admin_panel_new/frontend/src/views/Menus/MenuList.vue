<template>
  <div class="menu-list">
    <div class="header">
      <h1>Управление меню бота</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        <i class="fas fa-plus"></i> Создать меню
      </button>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <select v-model="filters.language" @change="loadMenus">
        <option value="">Все языки</option>
        <option value="ru">Русский</option>
        <option value="en">English</option>
      </select>
      <select v-model="filters.menu_type" @change="loadMenus">
        <option value="">Все типы</option>
        <option value="reply_keyboard">Reply Keyboard</option>
        <option value="inline_keyboard">Inline Keyboard</option>
      </select>
      <input 
        v-model="filters.search" 
        placeholder="Поиск по названию..."
        @input="debounceSearch"
      >
    </div>

    <!-- Список меню -->
    <div class="menu-grid">
      <div 
        v-for="menu in menus" 
        :key="menu.id" 
        class="menu-card"
        @click="editMenu(menu)"
      >
        <div class="menu-header">
          <h3>{{ menu.name }}</h3>
          <span :class="['status', menu.is_active ? 'active' : 'inactive']">
            {{ menu.is_active ? 'Активно' : 'Неактивно' }}
          </span>
        </div>
        
        <div class="menu-info">
          <p><strong>Язык:</strong> {{ getLanguageName(menu.language) }}</p>
          <p><strong>Тип:</strong> {{ getMenuTypeName(menu.menu_type) }}</p>
          <p><strong>Элементов:</strong> {{ menu.items.length }}</p>
        </div>

        <div class="menu-preview">
          <h4>Предварительный просмотр:</h4>
          <div class="keyboard-preview">
            <div 
              v-for="(row, rowIndex) in formatMenuItems(menu.items)" 
              :key="rowIndex"
              class="keyboard-row"
            >
              <button 
                v-for="(item, colIndex) in row" 
                :key="colIndex"
                class="preview-button"
                :class="menu.menu_type"
              >
                {{ item.text }}
              </button>
            </div>
          </div>
        </div>

        <div class="menu-actions">
          <button @click.stop="editMenu(menu)" class="btn-edit">
            <i class="fas fa-edit"></i> Редактировать
          </button>
          <button @click.stop="toggleMenuStatus(menu)" class="btn-toggle">
            <i :class="menu.is_active ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            {{ menu.is_active ? 'Деактивировать' : 'Активировать' }}
          </button>
          <button @click.stop="deleteMenu(menu)" class="btn-delete">
            <i class="fas fa-trash"></i> Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Пагинация -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="changePage(currentPage - 1)" 
        :disabled="currentPage === 1"
        class="btn-page"
      >
        <i class="fas fa-chevron-left"></i>
      </button>
      
      <span class="page-info">
        Страница {{ currentPage }} из {{ totalPages }}
      </span>
      
      <button 
        @click="changePage(currentPage + 1)" 
        :disabled="currentPage === totalPages"
        class="btn-page"
      >
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Модальное окно создания/редактирования -->
    <MenuEditModal 
      v-if="showCreateModal || showEditModal"
      :menu="editingMenu"
      :is-edit="showEditModal"
      @close="closeModal"
      @saved="onMenuSaved"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useMenuStore } from '@/stores/menuStore'
import MenuEditModal from './MenuEditModal.vue'
import { debounce } from '@/utils/helpers'

export default {
  name: 'MenuList',
  components: {
    MenuEditModal
  },
  setup() {
    const menuStore = useMenuStore()
    
    const menus = ref([])
    const currentPage = ref(1)
    const totalPages = ref(1)
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingMenu = ref(null)
    
    const filters = ref({
      language: '',
      menu_type: '',
      search: ''
    })

    const loadMenus = async () => {
      try {
        const response = await menuStore.getMenus({
          page: currentPage.value,
          limit: 12,
          ...filters.value
        })
        
        menus.value = response.menus
        totalPages.value = response.pages
      } catch (error) {
        console.error('Ошибка загрузки меню:', error)
      }
    }

    const editMenu = (menu) => {
      editingMenu.value = { ...menu }
      showEditModal.value = true
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingMenu.value = null
    }

    const onMenuSaved = () => {
      closeModal()
      loadMenus()
    }

    const toggleMenuStatus = async (menu) => {
      try {
        await menuStore.updateMenu(menu.id, {
          is_active: !menu.is_active
        })
        await loadMenus()
      } catch (error) {
        console.error('Ошибка изменения статуса:', error)
      }
    }

    const deleteMenu = async (menu) => {
      if (confirm(`Удалить меню "${menu.name}"?`)) {
        try {
          await menuStore.deleteMenu(menu.id)
          await loadMenus()
        } catch (error) {
          console.error('Ошибка удаления меню:', error)
        }
      }
    }

    const changePage = (page) => {
      currentPage.value = page
      loadMenus()
    }

    const debounceSearch = debounce(() => {
      currentPage.value = 1
      loadMenus()
    }, 300)

    const getLanguageName = (code) => {
      const languages = {
        ru: 'Русский',
        en: 'English'
      }
      return languages[code] || code
    }

    const getMenuTypeName = (type) => {
      const types = {
        reply_keyboard: 'Reply Keyboard',
        inline_keyboard: 'Inline Keyboard'
      }
      return types[type] || type
    }

    const formatMenuItems = (items) => {
      const rows = {}
      items.forEach(item => {
        if (!rows[item.row_position]) {
          rows[item.row_position] = {}
        }
        rows[item.row_position][item.column_position] = item
      })
      
      return Object.keys(rows).sort().map(rowIndex => {
        const row = rows[rowIndex]
        return Object.keys(row).sort().map(colIndex => row[colIndex])
      })
    }

    onMounted(() => {
      loadMenus()
    })

    return {
      menus,
      currentPage,
      totalPages,
      filters,
      showCreateModal,
      showEditModal,
      editingMenu,
      loadMenus,
      editMenu,
      closeModal,
      onMenuSaved,
      toggleMenuStatus,
      deleteMenu,
      changePage,
      debounceSearch,
      getLanguageName,
      getMenuTypeName,
      formatMenuItems
    }
  }
}
</script>

<style scoped>
.menu-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h1 {
  margin: 0;
  color: #333;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filters select,
.filters input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.menu-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.menu-header h3 {
  margin: 0;
  color: #333;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.active {
  background: #d4edda;
  color: #155724;
}

.status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.menu-info {
  margin-bottom: 20px;
}

.menu-info p {
  margin: 5px 0;
  color: #666;
}

.menu-preview {
  margin-bottom: 20px;
}

.menu-preview h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
}

.keyboard-preview {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
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

.menu-actions {
  display: flex;
  gap: 10px;
}

.btn-edit,
.btn-toggle,
.btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit {
  background: #007bff;
  color: white;
}

.btn-edit:hover {
  background: #0056b3;
}

.btn-toggle {
  background: #ffc107;
  color: #212529;
}

.btn-toggle:hover {
  background: #e0a800;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-delete:hover {
  background: #c82333;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.btn-page {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #0056b3;
}
</style>
