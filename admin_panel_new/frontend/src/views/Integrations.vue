<template>
  <div class="integrations-page">
    <div class="page-header">
      <h1>Управление интеграциями</h1>
      <p>Настройка провайдеров для проверок и платежей</p>
    </div>

    <!-- Статус интеграций -->
    <div class="status-section">
      <h2>Статус системы</h2>
      <div class="status-grid">
        <div class="status-card" :class="healthStatus.overall_status">
          <h3>Общий статус</h3>
          <div class="status-indicator">
            <span class="status-dot" :class="healthStatus.overall_status"></span>
            {{ healthStatus.overall_status === 'healthy' ? 'Здоров' : 'Проблемы' }}
          </div>
        </div>
        
        <div class="status-card" :class="healthStatus.redis.status">
          <h3>Redis кеш</h3>
          <div class="status-indicator">
            <span class="status-dot" :class="healthStatus.redis.status"></span>
            {{ healthStatus.redis.connected ? 'Подключен' : 'Отключен' }}
          </div>
        </div>
        
        <div class="status-card" :class="healthStatus.free_check.status">
          <h3>Бесплатные проверки</h3>
          <div class="status-indicator">
            <span class="status-dot" :class="healthStatus.free_check.status"></span>
            {{ healthStatus.free_check.active_provider || 'Не настроен' }}
          </div>
        </div>
        
        <div class="status-card" :class="healthStatus.paid_check.status">
          <h3>Платные проверки</h3>
          <div class="status-indicator">
            <span class="status-dot" :class="healthStatus.paid_check.status"></span>
            {{ healthStatus.paid_check.active_provider || 'Не настроен' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Управление провайдерами -->
    <div class="providers-section">
      <h2>Управление провайдерами</h2>
      
      <!-- Бесплатные проверки -->
      <div class="provider-group">
        <h3>Бесплатные проверки</h3>
        <div class="provider-controls">
          <select v-model="selectedFreeProvider" @change="switchFreeProvider">
            <option value="">Выберите провайдера</option>
            <option v-for="provider in freeProviders" :key="provider" :value="provider">
              {{ provider }}
            </option>
          </select>
          <button @click="switchFreeProvider" :disabled="!selectedFreeProvider">
            Переключить
          </button>
        </div>
        <p class="current-provider">
          Текущий: <strong>{{ currentFreeProvider || 'Не выбран' }}</strong>
        </p>
      </div>

      <!-- Платные проверки -->
      <div class="provider-group">
        <h3>Платные проверки</h3>
        <div class="provider-controls">
          <select v-model="selectedPaidProvider" @change="switchPaidProvider">
            <option value="">Выберите провайдера</option>
            <option v-for="provider in paidProviders" :key="provider" :value="provider">
              {{ provider }}
            </option>
          </select>
          <button @click="switchPaidProvider" :disabled="!selectedPaidProvider">
            Переключить
          </button>
        </div>
        <p class="current-provider">
          Текущий: <strong>{{ currentPaidProvider || 'Не выбран' }}</strong>
        </p>
      </div>
    </div>

    <!-- Управление кешем -->
    <div class="cache-section">
      <h2>Управление кешем</h2>
      <div class="cache-controls">
        <button @click="clearCache('free_checks')" class="cache-btn">
          Очистить кеш бесплатных проверок
        </button>
        <button @click="clearCache('paid_checks')" class="cache-btn">
          Очистить кеш платных проверок
        </button>
        <button @click="clearCache()" class="cache-btn danger">
          Очистить весь кеш
        </button>
      </div>
      
      <!-- Статистика кеша -->
      <div class="cache-stats" v-if="cacheStats">
        <h3>Статистика кеша</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Всего записей:</span>
            <span class="stat-value">{{ cacheStats.total_keys || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Бесплатные проверки:</span>
            <span class="stat-value">{{ cacheStats.cache_types?.free_checks || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Платные проверки:</span>
            <span class="stat-value">{{ cacheStats.cache_types?.paid_checks || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Статистика использования -->
    <div class="stats-section">
      <h2>Статистика использования</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Бесплатные проверки</h3>
          <div class="stat-content">
            <p>Активных провайдеров: {{ integrationStats.providers?.free_check?.active_providers || 0 }}</p>
            <p>Всего провайдеров: {{ integrationStats.providers?.free_check?.total_providers || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <h3>Платные проверки</h3>
          <div class="stat-content">
            <p>Активных провайдеров: {{ integrationStats.providers?.paid_check?.active_providers || 0 }}</p>
            <p>Всего провайдеров: {{ integrationStats.providers?.paid_check?.total_providers || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Уведомления -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

export default {
  name: 'Integrations',
  setup() {
    const healthStatus = ref({
      overall_status: 'unknown',
      redis: { connected: false, status: 'unknown' },
      free_check: { active_provider: null, status: 'unknown' },
      paid_check: { active_provider: null, status: 'unknown' }
    })
    
    const freeProviders = ref(['metasleuth', 'provider2', 'provider3'])
    const paidProviders = ref(['ai_analysis', 'deep_scan'])
    
    const selectedFreeProvider = ref('')
    const selectedPaidProvider = ref('')
    const currentFreeProvider = ref('')
    const currentPaidProvider = ref('')
    
    const cacheStats = ref(null)
    const integrationStats = ref({})
    
    const notification = ref({
      show: false,
      message: '',
      type: 'info'
    })

    const showNotification = (message, type = 'info') => {
      notification.value = {
        show: true,
        message,
        type
      }
      setTimeout(() => {
        notification.value.show = false
      }, 5000)
    }

    const loadHealthStatus = async () => {
      try {
        const response = await api.get('/integrations/health')
        healthStatus.value = response.data
      } catch (error) {
        console.error('Ошибка загрузки статуса здоровья:', error)
        showNotification('Ошибка загрузки статуса здоровья', 'error')
      }
    }

    const loadProviders = async () => {
      try {
        const response = await api.get('/integrations/providers')
        const data = response.data
        
        currentFreeProvider.value = data.free_check?.active_provider || ''
        currentPaidProvider.value = data.paid_check?.active_provider || ''
        
        selectedFreeProvider.value = currentFreeProvider.value
        selectedPaidProvider.value = currentPaidProvider.value
      } catch (error) {
        console.error('Ошибка загрузки провайдеров:', error)
        showNotification('Ошибка загрузки провайдеров', 'error')
      }
    }

    const loadCacheStats = async () => {
      try {
        const response = await api.get('/integrations/stats')
        cacheStats.value = response.data.cache
        integrationStats.value = response.data.providers
      } catch (error) {
        console.error('Ошибка загрузки статистики:', error)
        showNotification('Ошибка загрузки статистики', 'error')
      }
    }

    const switchFreeProvider = async () => {
      if (!selectedFreeProvider.value) return
      
      try {
        const response = await api.put('/integrations/free-check', {
          provider_name: selectedFreeProvider.value
        })
        
        if (response.data.success) {
          currentFreeProvider.value = selectedFreeProvider.value
          showNotification('Провайдер бесплатных проверок переключен', 'success')
          await loadHealthStatus()
        }
      } catch (error) {
        console.error('Ошибка переключения провайдера:', error)
        showNotification('Ошибка переключения провайдера', 'error')
      }
    }

    const switchPaidProvider = async () => {
      if (!selectedPaidProvider.value) return
      
      try {
        const response = await api.put('/integrations/paid-check', {
          provider_name: selectedPaidProvider.value
        })
        
        if (response.data.success) {
          currentPaidProvider.value = selectedPaidProvider.value
          showNotification('Провайдер платных проверок переключен', 'success')
          await loadHealthStatus()
        }
      } catch (error) {
        console.error('Ошибка переключения провайдера:', error)
        showNotification('Ошибка переключения провайдера', 'error')
      }
    }

    const clearCache = async (cacheType = null) => {
      try {
        const response = await api.post('/integrations/cache/clear', {
          cache_type: cacheType
        })
        
        if (response.data.success) {
          const message = cacheType 
            ? `Кеш ${cacheType} очищен` 
            : 'Весь кеш очищен'
          showNotification(message, 'success')
          await loadCacheStats()
        }
      } catch (error) {
        console.error('Ошибка очистки кеша:', error)
        showNotification('Ошибка очистки кеша', 'error')
      }
    }

    onMounted(async () => {
      await Promise.all([
        loadHealthStatus(),
        loadProviders(),
        loadCacheStats()
      ])
    })

    return {
      healthStatus,
      freeProviders,
      paidProviders,
      selectedFreeProvider,
      selectedPaidProvider,
      currentFreeProvider,
      currentPaidProvider,
      cacheStats,
      integrationStats,
      notification,
      switchFreeProvider,
      switchPaidProvider,
      clearCache
    }
  }
}
</script>

<style scoped>
.integrations-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.status-section,
.providers-section,
.cache-section,
.stats-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-section h2,
.providers-section h2,
.cache-section h2,
.stats-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 10px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.status-card {
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #3498db;
  background: #f8f9fa;
}

.status-card.healthy {
  border-left-color: #27ae60;
  background: #d5f4e6;
}

.status-card.unhealthy {
  border-left-color: #e74c3c;
  background: #fadbd8;
}

.status-card h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #95a5a6;
}

.status-dot.healthy {
  background: #27ae60;
}

.status-dot.unhealthy {
  background: #e74c3c;
}

.provider-group {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
}

.provider-group h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.provider-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.provider-controls select {
  flex: 1;
  padding: 10px;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  font-size: 14px;
}

.provider-controls button {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.provider-controls button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.provider-controls button:hover:not(:disabled) {
  background: #2980b9;
}

.current-provider {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.cache-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.cache-btn {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cache-btn.danger {
  background: #e74c3c;
}

.cache-btn:hover {
  opacity: 0.9;
}

.cache-stats h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.stat-label {
  color: #7f8c8d;
}

.stat-value {
  font-weight: bold;
  color: #2c3e50;
}

.stat-card {
  padding: 20px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  background: #f8f9fa;
}

.stat-card h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 5px 0;
  color: #7f8c8d;
}

.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 4px;
  color: white;
  z-index: 1000;
  max-width: 300px;
}

.notification.success {
  background: #27ae60;
}

.notification.error {
  background: #e74c3c;
}

.notification.info {
  background: #3498db;
}

@media (max-width: 768px) {
  .integrations-page {
    padding: 10px;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .provider-controls {
    flex-direction: column;
  }
  
  .cache-controls {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
