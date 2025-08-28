<template>
  <div v-if="showModal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
    <div style="background: white; border-radius: 12px; padding: 24px; width: 95%; max-width: 800px; max-height: 90vh; overflow-y: auto;">
      <!-- Header -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <h3 style="margin: 0; color: #2d3748; font-size: 20px; font-weight: 600;">Редактирование: {{ getCategoryText(category) }}</h3>
        <button @click="closeModal" style="background: none; border: none; color: #718096; cursor: pointer; font-size: 20px; padding: 4px;">×</button>
      </div>

      <!-- Language Tabs -->
      <div style="display: flex; gap: 8px; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px;">
        <button 
          v-for="lang in ['ru', 'en']" 
          :key="lang"
          @click="selectedLanguage = lang"
          :style="selectedLanguage === lang ? 'background: #4299e1; color: white; border-color: #4299e1;' : 'background: white; color: #4a5568; border-color: #e2e8f0;'"
          style="padding: 8px 16px; border: 1px solid; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;"
        >
          {{ getLanguageText(lang) }}
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="saveTexts">
        <div v-for="lang in ['ru', 'en']" :key="lang" v-show="selectedLanguage === lang" style="margin-bottom: 20px;">
          <!-- Formatting Toolbar -->
          <div style="margin-bottom: 16px; padding: 12px; background: #e6fffa; border-radius: 8px; border: 2px solid #38b2ac;">
            <div style="margin-bottom: 8px;">
              <span style="color: #2d3748; font-size: 14px; font-weight: 600;">🎨 Форматирование текста:</span>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
              <button type="button" @click="insertFormat('**', '**')" style="padding: 8px 12px; background: #4299e1; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">B</button>
              <button type="button" @click="insertFormat('*', '*')" style="padding: 8px 12px; background: #4299e1; color: white; border: none; border-radius: 6px; font-size: 14px; font-style: italic; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">I</button>
              <button type="button" @click="insertFormat('`', '`')" style="padding: 8px 12px; background: #4299e1; color: white; border: none; border-radius: 6px; font-size: 14px; font-family: monospace; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">Code</button>
              <button type="button" @click="insertFormat('```\n', '\n```')" style="padding: 8px 12px; background: #4299e1; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">Block</button>
              <button type="button" @click="insertFormat('[', '](url)')" style="padding: 8px 12px; background: #4299e1; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">Link</button>
            </div>
            <div style="margin-top: 8px; font-size: 12px; color: #4a5568;">
              💡 Выделите текст и нажмите кнопку для форматирования
            </div>
          </div>
          
          <div style="margin-bottom: 16px;">
            <label style="display: block; margin-bottom: 8px; color: #4a5568; font-weight: 500;">Содержание ({{ getLanguageText(lang) }}):</label>
            <textarea 
              :ref="`textarea-${lang}`"
              v-model="editingTexts[lang].content" 
              rows="8"
              style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-family: inherit; resize: vertical; outline: none;"
              :placeholder="`Введите текст на ${getLanguageText(lang)}...`"
            ></textarea>
          </div>
          
          <!-- Preview -->
          <div style="margin-bottom: 16px;">
            <label style="display: block; margin-bottom: 8px; color: #4a5568; font-weight: 500;">Предпросмотр:</label>
            <div style="padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; background: #f9f9f9; min-height: 60px; white-space: pre-wrap; font-family: inherit;">
              <div v-html="formatPreview(editingTexts[lang].content)"></div>
            </div>
          </div>
        </div>

        <!-- Buttons -->
        <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
          <button 
            type="button" 
            @click="closeModal"
            style="padding: 12px 24px; background: #f7fafc; color: #4a5568; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; font-weight: 500; transition: background 0.2s;"
            onmouseover="this.style.background='#edf2f7'"
            onmouseout="this.style.background='#f7fafc'"
          >
            Отмена
          </button>
          <button 
            type="submit"
            :disabled="saving"
            style="padding: 12px 24px; background: #4299e1; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; transition: background 0.2s;"
            onmouseover="this.style.background='#3182ce'"
            onmouseout="this.style.background='#4299e1'"
            :style="{ opacity: saving ? 0.6 : 1, cursor: saving ? 'not-allowed' : 'pointer' }"
          >
            {{ saving ? 'Сохранение...' : 'Сохранить все переводы' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
const API_BASE_URL = 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com'

export default {
  name: 'TextEdit',
  props: {
    showModal: {
      type: Boolean,
      default: false
    },
    category: {
      type: String,
      default: ''
    },
    texts: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      selectedLanguage: 'ru',
      editingTexts: {
        ru: { content: '' },
        en: { content: '' }
      },
      saving: false
    }
  },
  watch: {
    texts: {
      handler(newTexts) {
        this.editingTexts = {
          ru: { ...newTexts.ru } || { content: '' },
          en: { ...newTexts.en } || { content: '' }
        }
      },
      immediate: true
    },
    selectedLanguage: {
      handler(newLang) {
        // Обновляем данные при смене языка
        this.$nextTick(() => {
          // Убеждаемся что данные синхронизированы
          if (this.editingTexts[newLang] && this.texts[newLang]) {
            this.editingTexts[newLang] = { ...this.texts[newLang] }
          }
        })
      }
    }
  },
  methods: {
    async saveTexts() {
      // Проверяем, что хотя бы один текст не пустой
      const hasContent = Object.values(this.editingTexts).some(text => text.content && text.content.trim())
      if (!hasContent) {
        alert('Хотя бы один перевод должен содержать текст')
        return
      }

      this.saving = true
      try {
        const promises = []
        
        // Сохраняем каждый перевод
        for (const [lang, text] of Object.entries(this.editingTexts)) {
          if (text.content && text.content.trim()) {
            if (text.id) {
              // Обновляем существующий
              promises.push(
                fetch(`${API_BASE_URL}/api/texts/${text.id}`, {
                  method: 'PUT',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ 
                    content: text.content,
                    is_active: true 
                  })
                }).then(res => {
                  if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`)
                  }
                  return res.json().then(data => ({ ...text, ...data }))
                })
              )
            } else {
              // Создаем новый
              promises.push(
                fetch(`${API_BASE_URL}/api/texts`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    category: this.category,
                    language: lang,
                    content: text.content,
                    is_active: true
                  })
                }).then(res => {
                  if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`)
                  }
                  return res.json().then(data => ({ ...text, ...data }))
                })
              )
            }
          }
        }

        const results = await Promise.all(promises)
        console.log('Результаты сохранения:', results)
        
        this.$emit('saved', results)
        this.closeModal()
        alert('Все переводы успешно сохранены!')
        
        // Принудительно перезагружаем данные в родительском компоненте
        if (this.$parent && this.$parent.loadTexts) {
          this.$parent.loadTexts()
        }
      } catch (error) {
        console.error('Ошибка сохранения текстов:', error)
        alert('Ошибка сохранения текстов: ' + error.message)
      } finally {
        this.saving = false
      }
    },

    closeModal() {
      this.$emit('close')
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

    insertFormat(before, after) {
      console.log('insertFormat вызван:', before, after)
      const textarea = this.$refs[`textarea-${this.selectedLanguage}`]
      if (!textarea || !textarea[0]) {
        console.error('Textarea не найден')
        return
      }
      
      const textareaEl = textarea[0]
      const start = textareaEl.selectionStart
      const end = textareaEl.selectionEnd
      const text = this.editingTexts[this.selectedLanguage].content
      
      console.log('Текущий текст:', text)
      console.log('Выделение:', start, end)
      
      const beforeText = text.substring(0, start)
      const selectedText = text.substring(start, end)
      const afterText = text.substring(end)
      
      const newText = beforeText + before + selectedText + after + afterText
      this.editingTexts[this.selectedLanguage].content = newText
      
      console.log('Новый текст:', newText)
      
      // Устанавливаем курсор после вставленного форматирования
      this.$nextTick(() => {
        textareaEl.focus()
        textareaEl.setSelectionRange(start + before.length, end + before.length)
      })
    },

    formatPreview(text) {
      if (!text) return ''
      
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code style="background: #e2e8f0; padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>')
        .replace(/```([\s\S]*?)```/g, '<pre style="background: #e2e8f0; padding: 8px; border-radius: 4px; font-family: monospace; white-space: pre-wrap;">$1</pre>')
        .replace(/\[(.*?)\]\(url\)/g, '<a href="#" style="color: #4299e1; text-decoration: underline;">$1</a>')
    }
  }
}
</script>
