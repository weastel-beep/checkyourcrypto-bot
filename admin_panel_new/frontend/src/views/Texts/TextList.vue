<template>
  <div style="min-height: 100vh; background: #f5f7fa;">
    <!-- Header -->
    <Header />

    <!-- Main Content -->
    <main style="max-width: 1200px; margin: 0 auto; padding: 30px 20px;">
      <!-- Page Header -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
          <h2 style="margin: 0; color: #2d3748; font-size: 24px; font-weight: bold;">Тексты бота</h2>
          <p style="margin: 5px 0 0; color: #718096; font-size: 14px;">Управление текстами для разных языков</p>
        </div>
        <button style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; background: #4299e1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">
          <span style="font-size: 16px;">➕</span>
          Добавить текст
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" style="text-align: center; padding: 40px;">
        <div style="font-size: 18px; color: #718096;">Загрузка текстов...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" style="background: #fed7d7; border: 1px solid #feb2b2; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
        <div style="color: #e53e3e; font-size: 16px; font-weight: 500;">{{ error }}</div>
        <button @click="loadTexts" style="margin-top: 12px; padding: 8px 16px; background: #e53e3e; color: white; border: none; border-radius: 6px; cursor: pointer;">Повторить</button>
      </div>

      <!-- Texts Table -->
      <div v-else style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
        <!-- Filters -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
          <h3 style="margin: 0; color: #2d3748; font-size: 18px; font-weight: 600;">Список текстов</h3>
          <div style="display: flex; gap: 12px;">
            <select v-model="selectedCategory" style="padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; outline: none; transition: border-color 0.2s;" onfocus="this.style.borderColor='#4299e1'" onblur="this.style.borderColor='#e2e8f0'">
              <option value="">Все категории</option>
              <option value="welcome">Приветствие</option>
              <option value="main_menu">Главное меню</option>
              <option value="check">Проверка</option>
              <option value="payment">Оплата</option>
            </select>
            <select v-model="selectedLanguage" style="padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; outline: none; transition: border-color 0.2s;" onfocus="this.style.borderColor='#4299e1'" onblur="this.style.borderColor='#e2e8f0'">
              <option value="">Все языки</option>
              <option value="ru">Русский</option>
              <option value="en">English</option>
              <option value="es">Español</option>
            </select>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 16px;">
          <div v-for="category in filteredTexts" :key="category" style="background: #f7fafc; border-radius: 8px; padding: 20px; border: 1px solid #e2e8f0;">
            <!-- Category Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <h4 style="margin: 0; color: #2d3748; font-size: 16px; font-weight: 600;">{{ getCategoryText(category) }}</h4>
              <button @click="editCategory(category)" style="color: #4299e1; background: none; border: none; cursor: pointer; font-size: 14px; font-weight: 500; transition: color 0.2s;" onmouseover="this.style.color='#3182ce'" onmouseout="this.style.color='#4299e1'">
                ✏️ Редактировать
              </button>
            </div>
            
            <!-- Language Tabs -->
            <div style="display: flex; gap: 8px; margin-bottom: 12px;">
              <button 
                v-for="lang in ['ru', 'en']" 
                :key="lang"
                @click="selectedLanguage = lang"
                :style="selectedLanguage === lang ? 'background: #4299e1; color: white;' : 'background: white; color: #4a5568;'"
                style="padding: 6px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s;"
              >
                {{ getLanguageText(lang) }}
              </button>
            </div>
            
            <!-- Content Preview -->
            <div style="background: white; border-radius: 6px; padding: 12px; border: 1px solid #e2e8f0;">
              <div v-if="groupedTexts[category] && groupedTexts[category][selectedLanguage]" style="color: #2d3748; font-size: 14px; line-height: 1.5;">
                {{ groupedTexts[category][selectedLanguage].content }}
              </div>
              <div v-else style="color: #718096; font-style: italic; font-size: 14px;">
                Текст для {{ getLanguageText(selectedLanguage) }} не найден
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Text Edit Modal -->
    <TextEdit 
      :showModal="showEditModal" 
      :category="editingCategory"
      :texts="groupedTexts[editingCategory] || {}"
      @close="closeEditModal" 
      @saved="onTextSaved"
    />
  </div>
</template>

<script>
import { authService } from '@/services/auth'
import Header from '@/components/Layout/Header.vue'
import TextEdit from './TextEdit.vue'

const API_BASE_URL = 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com'

export default {
  components: {
    Header,
    TextEdit
  },
  name: 'TextList',
  data() {
    return {
      selectedCategory: '',
      selectedLanguage: 'ru',
      texts: [],
      loading: false,
      error: null,
      showEditModal: false,
      editingCategory: null
    }
  },
  computed: {
    groupedTexts() {
      const grouped = {}
      this.texts.forEach(text => {
        if (!grouped[text.category]) {
          grouped[text.category] = {}
        }
        grouped[text.category][text.language] = text
      })
      return grouped
    },
    
    filteredTexts() {
      const grouped = this.groupedTexts
      const categories = Object.keys(grouped)
      
      if (this.selectedCategory) {
        return categories.filter(cat => cat === this.selectedCategory)
      }
      
      return categories
    }
  },
  async mounted() {
    await this.loadTexts()
  },
  methods: {
    async loadTexts() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`${API_BASE_URL}/api/texts`)
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        const data = await response.json()
        this.texts = data.texts || []
      } catch (error) {
        console.error('Ошибка загрузки текстов:', error)
        this.error = 'Ошибка загрузки текстов: ' + error.message
      } finally {
        this.loading = false
      }
    },
    
    async deleteText(textId) {
      if (!confirm('Вы уверены, что хотите удалить этот текст?')) {
        return
      }
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/texts/${textId}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || `HTTP ${response.status}`)
        }
        
        await this.loadTexts()
        alert('Текст успешно удален!')
      } catch (error) {
        console.error('Ошибка удаления текста:', error)
        alert('Ошибка удаления текста: ' + error.message)
      }
    },
    
    editCategory(category) {
      this.editingCategory = category
      this.showEditModal = true
    },

    closeEditModal() {
      this.showEditModal = false
      this.editingCategory = null
    },

    onTextSaved(updatedTexts) {
      // Обновляем тексты в списке
      updatedTexts.forEach(updatedText => {
        const index = this.texts.findIndex(t => t.id === updatedText.id)
        if (index !== -1) {
          this.texts[index] = { ...this.texts[index], ...updatedText }
        }
      })
    },
    
    getCategoryText(category) {
      const categories = {
        'welcome': 'Приветствие',
        'main_menu': 'Главное меню',
        'check': 'Проверка',
        'payment': 'Оплата',
        'user_blocked': 'Пользователь заблокирован',
        'enter_address': 'Введите адрес',
        'invalid_address': 'Неверный адрес',
        'checking_address': 'Проверка адреса',
        'error_occurred': 'Произошла ошибка',
        'select_chain': 'Выберите сеть',
        'faq_content': 'FAQ'
      }
      return categories[category] || category
    },
    getLanguageText(language) {
      const languages = {
        'ru': 'Русский',
        'en': 'English',
        'es': 'Español'
      }
      return languages[language] || language
    },
    
    async logout() {
      try {
        await authService.logout()
        this.$router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        this.$router.push('/login')
      }
    }
  }
}
</script>
