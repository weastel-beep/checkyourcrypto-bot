<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Создать сообщение</h1>
            <p class="text-sm text-gray-600">Новое массовое сообщение</p>
          </div>
          <router-link to="/messages" class="btn-secondary">
            ← Назад к списку
          </router-link>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="card">
            <h2 class="text-lg font-medium text-gray-900 mb-4">Основная информация</h2>
            
            <div class="grid grid-cols-1 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700">
                  Заголовок сообщения <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="form.title"
                  type="text" 
                  required
                  class="input mt-1"
                  placeholder="Например: Важное обновление бота"
                >
                <p class="mt-1 text-sm text-gray-500">
                  Краткое название сообщения, которое будет показано пользователям
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">
                  Содержание <span class="text-red-500">*</span>
                </label>
                <textarea 
                  v-model="form.content"
                  rows="6"
                  required
                  class="input mt-1"
                  placeholder="Введите текст сообщения"
                ></textarea>
                <p class="mt-1 text-sm text-gray-500">
                  Основной текст сообщения. Поддерживается Markdown форматирование
                </p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Язык</label>
                  <select v-model="form.language" class="input mt-1">
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                    <option value="es">Español</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Статус</label>
                  <select v-model="form.status" class="input mt-1">
                    <option value="DRAFT">Черновик</option>
                    <option value="SCHEDULED">Запланировано</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <h2 class="text-lg font-medium text-gray-900 mb-4">Настройки отправки</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700">Фильтр пользователей</label>
                <select v-model="form.user_filter" class="input mt-1">
                  <option value="all">👥 Все пользователи</option>
                  <option value="active">✅ Только активные</option>
                  <option value="with_balance">💰 С балансом</option>
                  <option value="language">🌍 По языку</option>
                </select>
                <p class="mt-1 text-sm text-gray-500">
                  Выберите, кому отправить сообщение
                </p>
              </div>

              <div v-if="form.status === 'SCHEDULED'">
                <label class="block text-sm font-medium text-gray-700">
                  Дата отправки <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="form.scheduled_at"
                  type="datetime-local" 
                  required
                  class="input mt-1"
                >
                <p class="mt-1 text-sm text-gray-500">
                  Выберите дату и время для отправки сообщения
                </p>
              </div>
            </div>
          </div>

          <div class="flex justify-end space-x-4">
            <router-link to="/messages" class="btn-secondary">
              Отмена
            </router-link>
            <button type="submit" :disabled="loading" class="btn-primary">
              {{ loading ? 'Создание...' : 'Создать сообщение' }}
            </button>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'

// API конфигурация
const API_BASE_URL = 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com'

export default {
  name: 'MessageCreate',
  setup() {
    const router = useRouter()
    const loading = ref(false)

    const form = reactive({
      title: '',
      content: '',
      language: 'ru',
      status: 'DRAFT',
      user_filter: 'all',
      scheduled_at: ''
    })

    // Устанавливаем время по умолчанию для запланированных сообщений
    watch(() => form.status, (newStatus) => {
      if (newStatus === 'SCHEDULED' && !form.scheduled_at) {
        const now = new Date()
        now.setHours(now.getHours() + 1) // +1 час от текущего времени
        form.scheduled_at = now.toISOString().slice(0, 16)
      }
    })

    const handleSubmit = async () => {
      if (!form.title.trim() || !form.content.trim()) {
        alert('Пожалуйста, заполните все обязательные поля')
        return
      }

      if (form.status === 'SCHEDULED' && !form.scheduled_at) {
        alert('Пожалуйста, укажите дату отправки для запланированного сообщения')
        return
      }

      loading.value = true

      try {
        const requestData = {
          title: form.title.trim(),
          content: form.content.trim(),
          language: form.language,
          status: form.status,
          user_filter: form.user_filter,
          scheduled_at: form.status === 'SCHEDULED' && form.scheduled_at ? form.scheduled_at : null
        }

        console.log('Отправляем данные:', requestData)

        const response = await fetch(`${API_BASE_URL}/api/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        if (!response.ok) {
          let errorMessage = 'Ошибка создания сообщения'
          try {
            const errorData = await response.json()
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch (parseError) {
            console.error('Ошибка парсинга ответа:', parseError)
            errorMessage = `HTTP ${response.status}: ${response.statusText}`
          }
          throw new Error(errorMessage)
        }

        const result = await response.json()
        alert('Сообщение успешно создано!')
        router.push('/messages')
      } catch (error) {
        console.error('Ошибка создания сообщения:', error)
        const errorMessage = error.message || 'Неизвестная ошибка при создании сообщения'
        alert('Ошибка создания сообщения: ' + errorMessage)
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
}

.input {
  @apply block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.btn-primary {
  @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2;
}
</style>
