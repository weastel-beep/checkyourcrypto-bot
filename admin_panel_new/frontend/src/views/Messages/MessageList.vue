<template>
  <div style="min-height: 100vh; background: #f5f7fa;">
    <!-- Header -->
    <Header />

    <!-- Main Content -->
    <main style="max-width: 1200px; margin: 0 auto; padding: 30px 20px;">
      <!-- Page Header -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
          <h2 style="margin: 0; color: #2d3748; font-size: 24px; font-weight: bold;">Сообщения</h2>
          <p style="margin: 5px 0 0; color: #718096; font-size: 14px;">Управление массовыми сообщениями</p>
        </div>
        <router-link to="/messages/create" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; background: #4299e1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; text-decoration: none;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">
          <span style="font-size: 16px;">➕</span>
          Создать сообщение
        </router-link>
      </div>

      <!-- Loading State -->
      <div v-if="loading" style="text-align: center; padding: 40px;">
        <div style="font-size: 18px; color: #718096;">Загрузка сообщений...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" style="background: #fed7d7; border: 1px solid #feb2b2; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
        <div style="color: #e53e3e; font-size: 16px; font-weight: 500;">{{ error }}</div>
        <button @click="loadMessages" style="margin-top: 12px; padding: 8px 16px; background: #e53e3e; color: white; border: none; border-radius: 6px; cursor: pointer;">Повторить</button>
      </div>

      <!-- Messages Table -->
      <div v-else style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid #e2e8f0;">
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Название</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Статус</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Отправлено</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Дата создания</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="message in messages" :key="message.id" style="border-bottom: 1px solid #f7fafc;">
                <td style="padding: 16px; color: #2d3748; font-size: 14px; font-weight: 500;">{{ message.title }}</td>
                <td style="padding: 16px;">
                  <span :style="getStatusStyle(message.status)" style="padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                    {{ getStatusText(message.status) }}
                  </span>
                </td>
                <td style="padding: 16px; color: #2d3748; font-size: 14px;">{{ message.sent_count }}/{{ message.total_users }}</td>
                <td style="padding: 16px; color: #718096; font-size: 14px;">{{ formatDate(message.created_at) }}</td>
                <td style="padding: 16px;">
                  <button @click="viewMessage(message.id)" style="color: #4299e1; background: none; border: none; cursor: pointer; font-size: 14px; margin-right: 12px; transition: color 0.2s;" onmouseover="this.style.color='#3182ce'" onmouseout="this.style.color='#4299e1'">Просмотр</button>
                  <button @click="sendMessage(message.id)" style="color: #3182ce; background: none; border: none; cursor: pointer; font-size: 14px; margin-right: 12px; transition: color 0.2s;" onmouseover="this.style.color='#3182ce'" onmouseout="this.style.color='#4299e1'">Отправить</button>
                  <button @click="deleteMessage(message.id)" style="color: #e53e3e; background: none; border: none; cursor: pointer; font-size: 14px; transition: color 0.2s;" onmouseover="this.style.color='#c53030'" onmouseout="this.style.color='#e53e3e'">Удалить</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Header from '@/components/Layout/Header.vue'

// API конфигурация
const API_BASE_URL = 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com'

export default {
  components: {
    Header
  },
  name: 'MessageList',
  setup() {
    const messages = ref([])
    const loading = ref(true)
    const error = ref(null)
    const router = useRouter()

    const loadMessages = async () => {
      try {
        loading.value = true
        error.value = null
        
        const response = await fetch(`${API_BASE_URL}/api/messages`)
        if (!response.ok) {
          let errorMessage = 'Ошибка загрузки сообщений'
          try {
            const errorData = await response.json()
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch (parseError) {
            console.error('Ошибка парсинга ответа:', parseError)
            errorMessage = `HTTP ${response.status}: ${response.statusText}`
          }
          throw new Error(errorMessage)
        }
        
        const data = await response.json()
        messages.value = data.messages || []
      } catch (err) {
        const errorMessage = err.message || 'Неизвестная ошибка при загрузке сообщений'
        error.value = errorMessage
        console.error('Ошибка загрузки сообщений:', err)
      } finally {
        loading.value = false
      }
    }

    const deleteMessage = async (messageId) => {
      if (!confirm('Вы уверены, что хотите удалить это сообщение?')) {
        return
      }
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/messages/${messageId}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          let errorMessage = 'Ошибка удаления сообщения'
          try {
            const errorData = await response.json()
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch (parseError) {
            console.error('Ошибка парсинга ответа:', parseError)
            errorMessage = `HTTP ${response.status}: ${response.statusText}`
          }
          throw new Error(errorMessage)
        }
        
        // Перезагружаем список
        await loadMessages()
      } catch (err) {
        const errorMessage = err.message || 'Неизвестная ошибка при удалении'
        alert('Ошибка удаления: ' + errorMessage)
      }
    }

    const sendMessage = async (messageId) => {
      if (!confirm('Отправить это сообщение всем пользователям?')) {
        return
      }
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/messages/${messageId}/send`, {
          method: 'POST'
        })
        
        if (!response.ok) {
          let errorMessage = 'Ошибка отправки сообщения'
          try {
            const errorData = await response.json()
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch (parseError) {
            console.error('Ошибка парсинга ответа:', parseError)
            errorMessage = `HTTP ${response.status}: ${response.statusText}`
          }
          throw new Error(errorMessage)
        }
        
        const data = await response.json()
        alert(data.message || 'Сообщение отправлено успешно')
        
        // Перезагружаем список
        await loadMessages()
      } catch (err) {
        const errorMessage = err.message || 'Неизвестная ошибка при отправке'
        alert('Ошибка отправки: ' + errorMessage)
      }
    }

    const viewMessage = (messageId) => {
      router.push(`/messages/${messageId}`)
    }

    const getStatusStyle = (status) => {
      const styles = {
        'DRAFT': { backgroundColor: '#e2e8f0', color: '#4a5568' },
        'SCHEDULED': { backgroundColor: '#fef5e7', color: '#d69e2e' },
        'SENDING': { backgroundColor: '#e6fffa', color: '#319795' },
        'COMPLETED': { backgroundColor: '#f0fff4', color: '#38a169' },
        'FAILED': { backgroundColor: '#fed7d7', color: '#e53e3e' },
        'CANCELLED': { backgroundColor: '#f7fafc', color: '#718096' }
      }
      return styles[status] || styles['DRAFT']
    }

    const getStatusText = (status) => {
      const texts = {
        'DRAFT': 'Черновик',
        'SCHEDULED': 'Запланировано',
        'SENDING': 'Отправляется',
        'COMPLETED': 'Завершено',
        'FAILED': 'Ошибка',
        'CANCELLED': 'Отменено'
      }
      return texts[status] || status
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('ru-RU')
    }

    const logout = () => {
      // Логика выхода
      router.push('/login')
    }

    onMounted(() => {
      loadMessages()
    })

    return {
      messages,
      loading,
      error,
      loadMessages,
      deleteMessage,
      sendMessage,
      viewMessage,
      getStatusStyle,
      getStatusText,
      formatDate,
      logout
    }
  }
}
</script>
