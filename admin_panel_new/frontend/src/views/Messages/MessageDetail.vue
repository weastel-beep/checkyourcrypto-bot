<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Детали сообщения</h1>
            <p class="text-sm text-gray-600">Просмотр и управление массовым сообщением</p>
          </div>
          <router-link to="/messages" class="btn-secondary">
            ← Назад к списку
          </router-link>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="text-lg text-gray-600">Загрузка сообщения...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
          <div class="text-red-800 font-medium">{{ error }}</div>
          <button @click="loadMessage" class="mt-4 btn-primary">Повторить</button>
        </div>

        <!-- Message Details -->
        <div v-else-if="message" class="space-y-6">
          <!-- Message Header -->
          <div class="card">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="text-xl font-bold text-gray-900">{{ message.title }}</h2>
                <p class="text-sm text-gray-600 mt-1">ID: {{ message.id }}</p>
              </div>
              <div class="flex space-x-2">
                <!-- Action Buttons -->
                <button 
                  v-if="message.status === 'DRAFT' || message.status === 'SCHEDULED'"
                  @click="sendMessage"
                  :disabled="sending"
                  class="btn-primary"
                >
                  {{ sending ? 'Отправка...' : '📤 Отправить' }}
                </button>
                
                <button 
                  v-if="message.status === 'SENDING'"
                  @click="pauseMessage"
                  :disabled="pausing"
                  class="btn-warning"
                >
                  {{ pausing ? 'Пауза...' : '⏸️ Пауза' }}
                </button>
                
                <button 
                  v-if="message.status === 'PAUSED'"
                  @click="resumeMessage"
                  :disabled="resuming"
                  class="btn-success"
                >
                  {{ resuming ? 'Возобновление...' : '▶️ Возобновить' }}
                </button>
                
                <button 
                  v-if="['DRAFT', 'SCHEDULED', 'SENDING', 'PAUSED'].includes(message.status)"
                  @click="cancelMessage"
                  :disabled="cancelling"
                  class="btn-danger"
                >
                  {{ cancelling ? 'Отмена...' : '❌ Отменить' }}
                </button>
                
                <router-link :to="`/messages/${message.id}/edit`" class="btn-secondary">
                  ✏️ Редактировать
                </router-link>
              </div>
            </div>
          </div>

          <!-- Progress Section -->
          <div v-if="['SENDING', 'PAUSED'].includes(message.status)" class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Прогресс отправки</h3>
            
            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-4 mb-4">
              <div 
                class="h-4 rounded-full transition-all duration-300"
                :class="getProgressBarClass(message.status)"
                :style="{ width: `${progressPercentage}%` }"
              ></div>
            </div>
            
            <!-- Progress Stats -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{{ message.total_users || 0 }}</div>
                <div class="text-sm text-gray-600">Всего получателей</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ message.sent_count || 0 }}</div>
                <div class="text-sm text-gray-600">Отправлено</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ message.failed_count || 0 }}</div>
                <div class="text-sm text-gray-600">Ошибок</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-purple-600">{{ progressPercentage }}%</div>
                <div class="text-sm text-gray-600">Прогресс</div>
              </div>
            </div>
            
            <!-- Speed Info -->
            <div v-if="progressData.speed_info" class="bg-gray-50 rounded-lg p-4">
              <h4 class="font-medium text-gray-900 mb-2">Скорость отправки</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Сообщений в секунду:</span>
                  <span class="font-medium ml-2">{{ progressData.speed_info.messages_per_second }}</span>
                </div>
                <div>
                  <span class="text-gray-600">Прошло времени:</span>
                  <span class="font-medium ml-2">{{ formatTime(progressData.speed_info.elapsed_time_seconds) }}</span>
                </div>
                <div>
                  <span class="text-gray-600">Осталось времени:</span>
                  <span class="font-medium ml-2">{{ formatTime(progressData.speed_info.estimated_remaining_time) }}</span>
                </div>
              </div>
            </div>
            
            <!-- Batch Info -->
            <div v-if="progressData.current_batch" class="mt-4 text-sm text-gray-600">
              Пакет {{ progressData.current_batch }} из {{ progressData.total_batches }}
            </div>
          </div>

          <!-- Message Content -->
          <div class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Содержание</h3>
            <div class="bg-gray-50 rounded-lg p-4">
              <pre class="whitespace-pre-wrap text-gray-800">{{ message.content }}</pre>
            </div>
          </div>

          <!-- Statistics -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="card">
              <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{{ message.total_users || 0 }}</div>
                <div class="text-sm text-gray-600">Всего получателей</div>
              </div>
            </div>
            <div class="card">
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ message.sent_count || 0 }}</div>
                <div class="text-sm text-gray-600">Отправлено</div>
              </div>
            </div>
            <div class="card">
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ message.failed_count || 0 }}</div>
                <div class="text-sm text-gray-600">Ошибок</div>
              </div>
            </div>
          </div>

          <!-- Message Properties -->
          <div class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Свойства сообщения</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Статус</label>
                <div class="mt-1">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :style="getStatusStyle(message.status)"
                  >
                    {{ getStatusText(message.status) }}
                  </span>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Язык</label>
                <div class="mt-1 text-gray-900">{{ getLanguageText(message.language) }}</div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Фильтр пользователей</label>
                <div class="mt-1 text-gray-900">{{ getUserFilterText(message.user_filter) }}</div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Дата создания</label>
                <div class="mt-1 text-gray-900">{{ formatDate(message.created_at) }}</div>
              </div>
              <div v-if="message.scheduled_at">
                <label class="block text-sm font-medium text-gray-700">Запланировано на</label>
                <div class="mt-1 text-gray-900">{{ formatDate(message.scheduled_at) }}</div>
              </div>
              <div v-if="message.sent_at">
                <label class="block text-sm font-medium text-gray-700">Отправлено</label>
                <div class="mt-1 text-gray-900">{{ formatDate(message.sent_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// API конфигурация
const API_BASE_URL = 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com'

export default {
  name: 'MessageDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const message = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const sending = ref(false)
    const pausing = ref(false)
    const resuming = ref(false)
    const cancelling = ref(false)
    const progressData = ref({})
    let progressInterval = null

    const progressPercentage = computed(() => {
      if (!message.value || !message.value.total_users) return 0
      return Math.round((message.value.sent_count || 0) / message.value.total_users * 100)
    })

    const loadMessage = async () => {
      try {
        loading.value = true
        error.value = null
        
        const response = await fetch(`${API_BASE_URL}/api/messages/${route.params.id}`)
        if (!response.ok) {
          throw new Error('Сообщение не найдено')
        }
        
        message.value = await response.json()
        
        // Загружаем прогресс если сообщение отправляется
        if (['SENDING', 'PAUSED'].includes(message.value.status)) {
          await loadProgress()
        }
      } catch (err) {
        error.value = err.message
        console.error('Ошибка загрузки сообщения:', err)
      } finally {
        loading.value = false
      }
    }

    const loadProgress = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/messages/${route.params.id}/progress`)
        if (response.ok) {
          progressData.value = await response.json()
        }
      } catch (err) {
        console.error('Ошибка загрузки прогресса:', err)
      }
    }

    const sendMessage = async () => {
      if (!confirm('Отправить это сообщение всем пользователям?')) {
        return
      }
      
      try {
        sending.value = true
        
        const response = await fetch(`${API_BASE_URL}/api/messages/${message.value.id}/send`, {
          method: 'POST'
        })
        
        if (!response.ok) {
          throw new Error('Ошибка отправки сообщения')
        }
        
        const result = await response.json()
        alert(result.message)
        
        // Перезагружаем сообщение и начинаем отслеживание прогресса
        await loadMessage()
        startProgressTracking()
      } catch (err) {
        alert('Ошибка отправки: ' + err.message)
      } finally {
        sending.value = false
      }
    }

    const pauseMessage = async () => {
      try {
        pausing.value = true
        
        const response = await fetch(`${API_BASE_URL}/api/messages/${message.value.id}/action`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'pause' })
        })
        
        if (!response.ok) {
          throw new Error('Ошибка приостановки сообщения')
        }
        
        const result = await response.json()
        alert(result.message)
        
        await loadMessage()
        stopProgressTracking()
      } catch (err) {
        alert('Ошибка приостановки: ' + err.message)
      } finally {
        pausing.value = false
      }
    }

    const resumeMessage = async () => {
      try {
        resuming.value = true
        
        const response = await fetch(`${API_BASE_URL}/api/messages/${message.value.id}/action`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'resume' })
        })
        
        if (!response.ok) {
          throw new Error('Ошибка возобновления сообщения')
        }
        
        const result = await response.json()
        alert(result.message)
        
        await loadMessage()
        startProgressTracking()
      } catch (err) {
        alert('Ошибка возобновления: ' + err.message)
      } finally {
        resuming.value = false
      }
    }

    const cancelMessage = async () => {
      if (!confirm('Отменить отправку этого сообщения?')) {
        return
      }
      
      try {
        cancelling.value = true
        
        const response = await fetch(`${API_BASE_URL}/api/messages/${message.value.id}/action`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'cancel' })
        })
        
        if (!response.ok) {
          throw new Error('Ошибка отмены сообщения')
        }
        
        const result = await response.json()
        alert(result.message)
        
        await loadMessage()
        stopProgressTracking()
      } catch (err) {
        alert('Ошибка отмены: ' + err.message)
      } finally {
        cancelling.value = false
      }
    }

    const startProgressTracking = () => {
      if (progressInterval) {
        clearInterval(progressInterval)
      }
      
      progressInterval = setInterval(async () => {
        if (['SENDING', 'PAUSED'].includes(message.value?.status)) {
          await loadProgress()
          await loadMessage()
        } else {
          stopProgressTracking()
        }
      }, 2000) // Обновляем каждые 2 секунды
    }

    const stopProgressTracking = () => {
      if (progressInterval) {
        clearInterval(progressInterval)
        progressInterval = null
      }
    }

    const getProgressBarClass = (status) => {
      switch (status) {
        case 'SENDING':
          return 'bg-blue-600'
        case 'PAUSED':
          return 'bg-yellow-500'
        case 'COMPLETED':
          return 'bg-green-600'
        case 'FAILED':
          return 'bg-red-600'
        default:
          return 'bg-gray-400'
      }
    }

    const getStatusStyle = (status) => {
      const styles = {
        'DRAFT': { backgroundColor: '#6B7280', color: 'white' },
        'SCHEDULED': { backgroundColor: '#3B82F6', color: 'white' },
        'SENDING': { backgroundColor: '#10B981', color: 'white' },
        'PAUSED': { backgroundColor: '#F59E0B', color: 'white' },
        'COMPLETED': { backgroundColor: '#059669', color: 'white' },
        'FAILED': { backgroundColor: '#DC2626', color: 'white' },
        'CANCELLED': { backgroundColor: '#6B7280', color: 'white' }
      }
      return styles[status] || styles['DRAFT']
    }

    const getStatusText = (status) => {
      const texts = {
        'DRAFT': 'Черновик',
        'SCHEDULED': 'Запланировано',
        'SENDING': 'Отправляется',
        'PAUSED': 'Приостановлено',
        'COMPLETED': 'Завершено',
        'FAILED': 'Ошибка',
        'CANCELLED': 'Отменено'
      }
      return texts[status] || status
    }

    const getLanguageText = (language) => {
      const languages = {
        'ru': 'Русский',
        'en': 'English',
        'es': 'Español'
      }
      return languages[language] || language
    }

    const getUserFilterText = (filter) => {
      const filters = {
        'all': 'Все пользователи',
        'active': 'Активные пользователи',
        'language': 'По языку'
      }
      return filters[filter] || filter
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('ru-RU')
    }

    const formatTime = (seconds) => {
      if (!seconds || seconds === 0) return '-'
      
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)
      
      if (hours > 0) {
        return `${hours}ч ${minutes}м ${secs}с`
      } else if (minutes > 0) {
        return `${minutes}м ${secs}с`
      } else {
        return `${secs}с`
      }
    }

    onMounted(() => {
      loadMessage()
    })

    onUnmounted(() => {
      stopProgressTracking()
    })

    return {
      message,
      loading,
      error,
      sending,
      pausing,
      resuming,
      cancelling,
      progressData,
      progressPercentage,
      loadMessage,
      sendMessage,
      pauseMessage,
      resumeMessage,
      cancelMessage,
      getProgressBarClass,
      getStatusStyle,
      getStatusText,
      getLanguageText,
      getUserFilterText,
      formatDate,
      formatTime
    }
  }
}
</script>

<style scoped>
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.btn-primary {
  @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-success {
  @apply px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-warning {
  @apply px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-danger {
  @apply px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
