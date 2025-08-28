<template>
  <div style="min-height: 100vh; background: #f5f7fa;">
    <!-- Header -->
    <header style="background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-bottom: 1px solid #e2e8f0;">
      <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">
          <div>
            <h1 style="margin: 0; color: #2d3748; font-size: 28px; font-weight: bold;">Check Your Crypto Admin</h1>
            <p style="margin: 5px 0 0; color: #718096; font-size: 14px;">Панель управления</p>
          </div>
          <div style="display: flex; align-items: center; gap: 15px;">
            <!-- Navigation Menu -->
            <nav style="display: flex; gap: 20px;">
              <router-link to="/dashboard" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; transition: all 0.2s;" :style="{ backgroundColor: $route.path === '/dashboard' ? '#e6fffa' : 'transparent', color: $route.path === '/dashboard' ? '#319795' : '#4a5568' }">
                📊 Дашборд
              </router-link>
              <router-link to="/users" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; transition: all 0.2s;" :style="{ backgroundColor: $route.path.startsWith('/users') ? '#e6fffa' : 'transparent', color: $route.path.startsWith('/users') ? '#319795' : '#4a5568' }">
                👥 Пользователи
              </router-link>
              <router-link to="/messages" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; transition: all 0.2s;" :style="{ backgroundColor: $route.path.startsWith('/messages') ? '#e6fffa' : 'transparent', color: $route.path.startsWith('/messages') ? '#319795' : '#4a5568' }">
                📨 Сообщения
              </router-link>
              <router-link to="/texts" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; transition: all 0.2s;" :style="{ backgroundColor: $route.path === '/texts' ? '#e6fffa' : 'transparent', color: $route.path === '/texts' ? '#319795' : '#4a5568' }">
                📝 Тексты
              </router-link>
              <router-link to="/admin-actions" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; transition: all 0.2s;" :style="{ backgroundColor: $route.path === '/admin-actions' ? '#e6fffa' : 'transparent', color: $route.path === '/admin-actions' ? '#319795' : '#4a5568' }">
                📋 Логи
              </router-link>
            </nav>
            
            <!-- User Menu -->
            <div style="display: flex; align-items: center; gap: 10px;">
              <div style="width: 40px; height: 40px; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 16px; font-weight: bold;">A</span>
              </div>
              <div>
                <p style="margin: 0; font-size: 14px; font-weight: 600; color: #2d3748;">Admin</p>
                <p style="margin: 0; font-size: 12px; color: #718096;">Администратор</p>
              </div>
              <button @click="logout" style="background: none; border: none; color: #718096; cursor: pointer; padding: 8px; border-radius: 4px; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#f7fafc'" onmouseout="this.style.backgroundColor='transparent'">
                🚪
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main style="max-width: 1200px; margin: 0 auto; padding: 30px 20px;">
      <!-- Page Header -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
          <h2 style="margin: 0; color: #2d3748; font-size: 24px; font-weight: bold;">Логи действий администратора</h2>
          <p style="margin: 5px 0 0; color: #718096; font-size: 14px;">История всех действий с пользователями</p>
        </div>
        <button @click="loadActions" style="padding: 8px 16px; background: #4299e1; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">
          Обновить
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" style="text-align: center; padding: 40px;">
        <div style="font-size: 18px; color: #718096;">Загрузка логов...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" style="background: #fed7d7; border: 1px solid #feb2b2; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
        <div style="color: #e53e3e; font-size: 16px; font-weight: 500;">{{ error }}</div>
        <button @click="loadActions" style="margin-top: 12px; padding: 8px 16px; background: #e53e3e; color: white; border: none; border-radius: 6px; cursor: pointer;">Повторить</button>
      </div>

      <!-- Actions Table -->
      <div v-else style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid #e2e8f0;">
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Дата</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Действие</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Пользователь</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Администратор</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Детали</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="action in actions" :key="action.id" style="border-bottom: 1px solid #f7fafc;">
                <td style="padding: 16px; color: #718096; font-size: 14px;">{{ formatDate(action.created_at) }}</td>
                <td style="padding: 16px;">
                  <span :style="getActionStyle(action.action_type)" style="padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                    {{ getActionText(action.action_type) }}
                  </span>
                </td>
                <td style="padding: 16px; color: #2d3748; font-size: 14px; font-weight: 500;">{{ action.user_id }}</td>
                <td style="padding: 16px; color: #2d3748; font-size: 14px;">{{ action.admin_id }}</td>
                <td style="padding: 16px; color: #718096; font-size: 14px;">
                  <div v-if="action.details" style="max-width: 300px;">
                    <div v-if="action.action_type === 'update_balance'">
                      Старый: ${{ action.details.old_balance }}, Новый: ${{ action.details.new_balance }}
                    </div>
                    <div v-else-if="action.action_type === 'send_message'">
                      {{ action.details.message_preview }}
                    </div>
                    <div v-else>
                      {{ JSON.stringify(action.details) }}
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Info -->
        <div style="margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
          <div style="color: #718096; font-size: 14px;">
            Показано {{ actions.length }} действий
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { authService } from '@/services/auth'
import { userService } from '@/services/users'

export default {
  name: 'AdminActions',
  data() {
    return {
      actions: [],
      loading: false,
      error: null
    }
  },
  async mounted() {
    console.log('AdminActions: Component mounted')
    await this.loadActions()
  },
  methods: {
    async loadActions() {
      console.log('AdminActions: Loading actions...')
      this.loading = true
      this.error = null
      
      try {
        const actions = await userService.getAdminActions()
        this.actions = actions
        console.log('AdminActions: Actions loaded:', actions)
      } catch (error) {
        console.error('AdminActions: Error loading actions:', error)
        this.error = 'Ошибка загрузки логов'
      } finally {
        this.loading = false
      }
    },
    
    formatDate(date) {
      if (!date) return 'Не указано'
      return new Date(date).toLocaleString('ru-RU')
    },
    
    getActionText(actionType) {
      const actionTexts = {
        'block_user': 'Блокировка',
        'unblock_user': 'Разблокировка',
        'update_balance': 'Изменение баланса',
        'send_message': 'Отправка сообщения'
      }
      return actionTexts[actionType] || actionType
    },
    
    getActionStyle(actionType) {
      const styles = {
        'block_user': 'background: #fed7d7; color: #e53e3e;',
        'unblock_user': 'background: #f0fff4; color: #38a169;',
        'update_balance': 'background: #e6fffa; color: #319795;',
        'send_message': 'background: #fef5e7; color: #d69e2e;'
      }
      return styles[actionType] || 'background: #f7fafc; color: #4a5568;'
    },
    
    async logout() {
      console.log('AdminActions: Logging out...')
      try {
        await authService.logout()
        this.$router.push('/login')
      } catch (error) {
        console.error('AdminActions: Logout error:', error)
        this.$router.push('/login')
      }
    }
  }
}
</script>
