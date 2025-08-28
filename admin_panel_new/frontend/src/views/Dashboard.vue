<template>
  <BaseLayout>
      <!-- Loading State -->
      <div v-if="loading" style="text-align: center; padding: 40px;">
        <div style="font-size: 18px; color: #718096;">Загрузка данных...</div>
      </div>

      <!-- Dashboard Content -->
      <div v-else>
        <!-- Stats Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
          <!-- Total Users -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 16px;">
              <div style="width: 48px; height: 48px; background: linear-gradient(45deg, #4299e1, #3182ce); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 20px;">👥</span>
              </div>
              <div>
                <p style="margin: 0 0 4px; color: #718096; font-size: 14px; font-weight: 500;">Всего пользователей</p>
                <p style="margin: 0; color: #2d3748; font-size: 28px; font-weight: bold;">{{ stats.total_users || 0 }}</p>
                <p style="margin: 4px 0 0; color: #48bb78; font-size: 12px;">+12% с прошлой недели</p>
              </div>
            </div>
          </div>

          <!-- Checks Today -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 16px;">
              <div style="width: 48px; height: 48px; background: linear-gradient(45deg, #48bb78, #38a169); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 20px;">✅</span>
              </div>
              <div>
                <p style="margin: 0 0 4px; color: #718096; font-size: 14px; font-weight: 500;">Проверок сегодня</p>
                <p style="margin: 0; color: #2d3748; font-size: 28px; font-weight: bold;">{{ stats.checks_today || 0 }}</p>
                <p style="margin: 4px 0 0; color: #48bb78; font-size: 12px;">+8% с вчера</p>
              </div>
            </div>
          </div>

          <!-- Revenue Today -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 16px;">
              <div style="width: 48px; height: 48px; background: linear-gradient(45deg, #ed8936, #dd6b20); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 20px;">💰</span>
              </div>
              <div>
                <p style="margin: 0 0 4px; color: #718096; font-size: 14px; font-weight: 500;">Выручка сегодня</p>
                <p style="margin: 0; color: #2d3748; font-size: 28px; font-weight: bold;">${{ stats.revenue_today || 0 }}</p>
                <p style="margin: 4px 0 0; color: #48bb78; font-size: 12px;">+15% с вчера</p>
              </div>
            </div>
          </div>

          <!-- Average Check -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 16px;">
              <div style="width: 48px; height: 48px; background: linear-gradient(45deg, #9f7aea, #805ad5); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 20px;">📊</span>
              </div>
              <div>
                <p style="margin: 0 0 4px; color: #718096; font-size: 14px; font-weight: 500;">Средний чек</p>
                <p style="margin: 0; color: #2d3748; font-size: 28px; font-weight: bold;">${{ stats.avg_check_amount || 0 }}</p>
                <p style="margin: 4px 0 0; color: #48bb78; font-size: 12px;">+5% с прошлой недели</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts and Additional Stats -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 30px;">
          <!-- User Activity Chart -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
              <h3 style="margin: 0; color: #2d3748; font-size: 18px; font-weight: 600;">Активность пользователей</h3>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #718096; font-size: 14px;">За неделю</span>
                <div style="width: 12px; height: 12px; background: #4299e1; border-radius: 50%;"></div>
              </div>
            </div>
            <div style="height: 300px;">
              <div v-if="userActivityChart" style="width: 100%; height: 100%;">
                <div style="display: flex; align-items: end; justify-content: space-between; height: 240px; gap: 8px;">
                  <div v-for="(value, index) in userActivityChart.data" :key="index" style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;">
                    <div style="background: #4299e1; border-radius: 4px; width: 100%; transition: height 0.3s;" :style="{ height: (value / Math.max(...userActivityChart.data)) * 200 + 'px' }"></div>
                    <span style="color: #718096; font-size: 12px;">{{ userActivityChart.labels[index] }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Settings -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <h3 style="margin: 0 0 24px; color: #2d3748; font-size: 18px; font-weight: 600;">⚙️ Настройки бота</h3>
            
            <div style="display: flex; flex-direction: column; gap: 16px;">
              <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px; background: #f7fafc; border-radius: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div style="width: 32px; height: 32px; background: #fed7d7; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: #e53e3e; font-size: 16px;">🛡️</span>
                  </div>
                  <div>
                    <p style="margin: 0; color: #2d3748; font-size: 14px; font-weight: 500;">Стоимость платной проверки</p>
                    <p style="margin: 4px 0 0; color: #718096; font-size: 12px;">Минимальная сумма для AI-анализа</p>
                  </div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <input 
                    v-model="paidCheckPrice" 
                    type="number" 
                    min="0.1" 
                    step="0.1"
                    style="width: 80px; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px; text-align: center; font-size: 14px;"
                    @change="updatePaidCheckPrice"
                  >
                  <span style="color: #2d3748; font-size: 14px; font-weight: 500;">USDT</span>
                  <button 
                    @click="updatePaidCheckPrice"
                    style="background: #4299e1; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-size: 12px; cursor: pointer;"
                  >
                    💾 Сохранить
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Additional Stats -->
          <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <h3 style="margin: 0 0 24px; color: #2d3748; font-size: 18px; font-weight: 600;">Дополнительная статистика</h3>
            
            <div style="display: flex; flex-direction: column; gap: 16px;">
              <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px; background: #f7fafc; border-radius: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div style="width: 32px; height: 32px; background: #c6f6d5; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: #38a169; font-size: 16px;">💰</span>
                  </div>
                  <span style="color: #4a5568; font-size: 14px; font-weight: 500;">Всего платежей</span>
                </div>
                <span style="color: #2d3748; font-size: 18px; font-weight: bold;">{{ stats.total_payments || 0 }}</span>
              </div>

              <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px; background: #f7fafc; border-radius: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div style="width: 32px; height: 32px; background: #fed7d7; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: #e53e3e; font-size: 16px;">📈</span>
                  </div>
                  <span style="color: #4a5568; font-size: 14px; font-weight: 500;">Общая выручка</span>
                </div>
                <span style="color: #2d3748; font-size: 18px; font-weight: bold;">${{ stats.total_revenue || 0 }}</span>
              </div>
            </div>

            <!-- Quick Actions -->
            <div style="margin-top: 32px;">
              <h4 style="margin: 0 0 16px; color: #2d3748; font-size: 14px; font-weight: 600;">Быстрые действия</h4>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <router-link to="/messages/create" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; background: #4299e1; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; text-decoration: none;" onmouseover="this.style.background='#3182ce'" onmouseout="this.style.background='#4299e1'">
                  <span style="font-size: 16px;">➕</span>
                  Создать рассылку
                </router-link>
                <button style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; background: #f7fafc; color: #4a5568; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#edf2f7'" onmouseout="this.style.background='#f7fafc'">
                  <span style="font-size: 16px;">📊</span>
                  Экспорт данных
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
  </BaseLayout>
</template>

<script>
import { authService } from '@/services/auth'
import { dashboardService } from '@/services/dashboard'
import BaseLayout from '@/components/Layout/BaseLayout.vue'

export default {
  components: {
    BaseLayout
  },
  name: 'Dashboard',
  data() {
    return {
      currentUser: null,
      stats: {},
      userActivityChart: null,
      loading: false,
      paidCheckPrice: 1.0 // Стоимость платной проверки по умолчанию
    }
  },
  async mounted() {
    await this.loadData()
    await this.loadSettings()
  },
  methods: {
    async loadData() {
      this.loading = true
      
      try {
        console.log('Loading dashboard data...')
        // Загружаем данные параллельно
        const [stats, userActivity, currentUser] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getUserActivityChart(),
          authService.getCurrentUser()
        ])
        
        console.log('Dashboard data loaded:', { stats, userActivity, currentUser })
        
        this.stats = stats
        this.userActivityChart = userActivity
        this.currentUser = currentUser
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        // Fallback data
        this.stats = {
          total_users: 1250,
          total_checks: 5430,
          total_payments: 89,
          total_revenue: 1250.50,
          checks_today: 45,
          revenue_today: 25.00,
          avg_check_amount: 14.05
        }
        this.userActivityChart = {
          labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
          data: [120, 190, 300, 500, 200, 300, 450]
        }
        this.currentUser = { username: 'Admin' }
      } finally {
        this.loading = false
      }
    },
    
    async logout() {
      try {
        await authService.logout()
        this.$router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        this.$router.push('/login')
      }
    },
    
    async loadSettings() {
      try {
        // Загружаем настройки из API
        const response = await fetch('https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com/api/settings/paid_check_price')
        
        if (response.ok) {
          const data = await response.json()
          this.paidCheckPrice = parseFloat(data.value)
          console.log('💰 Загружена стоимость платной проверки:', this.paidCheckPrice, 'USDT')
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
      } catch (error) {
        console.error('Error loading settings:', error)
        throw error
      }
    },
    
    async updatePaidCheckPrice() {
      try {
        // Отправляем на сервер для сохранения в БД
        const response = await fetch('https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com/api/settings/paid_check_price', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            value: this.paidCheckPrice.toString()
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        console.log('💰 Стоимость платной проверки обновлена:', this.paidCheckPrice, 'USDT')
        
        // Показываем уведомление
        alert(`✅ Стоимость платной проверки обновлена: ${this.paidCheckPrice} USDT`)
      } catch (error) {
        console.error('Error updating price:', error)
        alert('❌ Ошибка при обновлении стоимости: ' + error.message)
      }
    }
  }
}
</script>
