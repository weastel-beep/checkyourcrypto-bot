<template>
  <div style="min-height: 100vh; background: #f5f7fa;">
    <!-- Header -->
    <header style="background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-bottom: 1px solid #e2e8f0;">
      <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">
          <div>
            <h1 style="margin: 0; color: #2d3748; font-size: 28px; font-weight: bold;">Пользователь #{{ $route.params.id }}</h1>
            <p style="margin: 5px 0 0; color: #718096; font-size: 14px;">Детальная информация</p>
          </div>
          <div style="display: flex; align-items: center; gap: 15px;">
            <router-link to="/admin-actions" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; border: 1px solid #e2e8f0; background: white; transition: all 0.2s;" onmouseover="this.style.backgroundColor='#f7fafc'" onmouseout="this.style.backgroundColor='white'">
              📋 Все логи
            </router-link>
            <router-link to="/users" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; border: 1px solid #e2e8f0; background: white; transition: all 0.2s;" @mouseover="onBackButtonHover" @mouseout="onBackButtonLeave">
              ← Назад к списку
            </router-link>
          </div>
        </div>
      </div>
    </header>

    <main style="max-width: 1200px; margin: 0 auto; padding: 30px 20px;">
      <div style="padding: 0;">
        <!-- Loading state -->
        <div v-if="loading" style="display: flex; justify-content: center; align-items: center; padding: 48px;">
          <div style="width: 48px; height: 48px; border: 4px solid #e2e8f0; border-top: 4px solid #4299e1; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        </div>

        <!-- Error state -->
        <div v-else-if="error" style="background: #fed7d7; border: 1px solid #feb2b2; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
          <div style="text-align: center;">
            <div style="color: #e53e3e; font-size: 18px; font-weight: 500; margin-bottom: 8px;">Ошибка загрузки</div>
            <p style="color: #4a5568;">{{ error }}</p>
            <button @click="loadUser" style="margin-top: 16px; padding: 8px 16px; border: 1px solid #e53e3e; border-radius: 6px; color: white; background: #e53e3e; font-size: 14px; font-weight: 500; cursor: pointer;">
              Попробовать снова
            </button>
          </div>
        </div>

        <!-- User data -->
        <div v-else-if="user" style="display: grid; grid-template-columns: 1fr; gap: 24px;">
          <!-- User Info -->
          <div>
            <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
              <h2 style="margin: 0 0 24px; color: #2d3748; font-size: 20px; font-weight: 600;">Информация о пользователе</h2>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px;">
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Telegram ID</label>
                  <p style="margin: 0; font-size: 16px; font-family: monospace; color: #2d3748; background: #f7fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">{{ user.id }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Username</label>
                  <p style="margin: 0; font-size: 16px; color: #2d3748; background: #f7fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">{{ user.username || 'Не указан' }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Баланс</label>
                  <p style="margin: 0; font-size: 16px; font-weight: 600; color: #38a169; background: #f0fff4; padding: 12px; border-radius: 6px; border: 1px solid #c6f6d5;">${{ user.balance || 0 }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Статус</label>
                  <span :style="user.is_blocked ? 'background: #fed7d7; color: #e53e3e; border-color: #feb2b2' : 'background: #f0fff4; color: #38a169; border-color: #c6f6d5'" 
                        style="padding: 8px 12px; display: inline-flex; font-size: 14px; font-weight: 600; border-radius: 6px; border: 1px solid;">
                    {{ user.is_blocked ? 'Заблокирован' : 'Активен' }}
                  </span>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Язык</label>
                  <p style="margin: 0; font-size: 16px; color: #2d3748; background: #f7fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">{{ user.language || 'ru' }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Дата регистрации</label>
                  <p style="margin: 0; font-size: 16px; color: #2d3748; background: #f7fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">{{ formatDate(user.created_at) }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Последнее обновление</label>
                  <p style="margin: 0; font-size: 16px; color: #2d3748; background: #f7fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">{{ formatDate(user.updated_at) }}</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-top: 24px;">
              <h2 style="margin: 0 0 24px; color: #2d3748; font-size: 20px; font-weight: 600;">Действия</h2>
              <div style="display: flex; flex-wrap: wrap; gap: 16px;">
                <button @click="showBalanceModal = true" style="padding: 8px 16px; border: none; border-radius: 6px; color: white; background: #4299e1; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;" @mouseover="onBalanceButtonHover" @mouseout="onBalanceButtonLeave">
                  Изменить баланс
                </button>
                <button @click="toggleBlockUser" :style="user.is_blocked ? 'background: #38a169' : 'background: #e53e3e'" style="padding: 8px 16px; border: none; border-radius: 6px; color: white; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;" @mouseover="onBlockButtonHover" @mouseout="onBlockButtonLeave">
                  {{ user.is_blocked ? 'Разблокировать' : 'Заблокировать' }}
                </button>
                <button @click="openMessageModal" style="padding: 8px 16px; border: 1px solid #e2e8f0; border-radius: 6px; color: #4a5568; background: white; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;" @mouseover="onMessageButtonHover" @mouseout="onMessageButtonLeave">
                  Отправить сообщение
                </button>
              </div>
            </div>

            <!-- User Actions Log -->
            <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-top: 24px;">
              <h2 style="margin: 0 0 24px; color: #2d3748; font-size: 20px; font-weight: 600;">Логи действий пользователя</h2>
              <div v-if="userActionsLoading" style="text-align: center; padding: 20px;">
                <div style="font-size: 16px; color: #718096;">Загрузка логов...</div>
              </div>
              <div v-else-if="userActions.length === 0" style="text-align: center; padding: 20px; color: #718096;">
                Нет действий для этого пользователя
              </div>
              <div v-else style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                  <thead>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Дата</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Действие</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Администратор</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Детали</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="action in userActions" :key="action.id" style="border-bottom: 1px solid #f7fafc;">
                      <td style="padding: 16px; color: #718096; font-size: 14px;">{{ formatDate(action.created_at) }}</td>
                      <td style="padding: 16px;">
                        <span :style="getActionStyle(action.action_type)" style="padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                          {{ getActionText(action.action_type) }}
                        </span>
                      </td>
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
            </div>

            <!-- User Checks -->
            <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-top: 24px;">
              <h2 style="margin: 0 0 24px; color: #2d3748; font-size: 20px; font-weight: 600;">Проверки адресов</h2>
              <div v-if="userChecksLoading" style="text-align: center; padding: 20px;">
                <div style="font-size: 16px; color: #718096;">Загрузка проверок...</div>
              </div>
              <div v-else-if="userChecks.length === 0" style="text-align: center; padding: 20px; color: #718096;">
                Нет проверок для этого пользователя
              </div>
              <div v-else style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                  <thead>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Дата</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Адрес</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Блокчейн</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Тип</th>
                      <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Результат</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="check in userChecks" :key="check.id" style="border-bottom: 1px solid #f7fafc;">
                      <td style="padding: 16px; color: #718096; font-size: 14px;">{{ formatDate(check.created_at) }}</td>
                      <td style="padding: 16px; color: #2d3748; font-size: 14px; font-family: monospace;">{{ check.address }}</td>
                      <td style="padding: 16px; color: #2d3748; font-size: 14px;">{{ check.chain }}</td>
                      <td style="padding: 16px; color: #2d3748; font-size: 14px;">{{ check.type }}</td>
                      <td style="padding: 16px;">
                        <div v-if="check.result && check.result.screening" style="max-width: 200px;">
                          <span :style="getRiskStyle(check.result.screening.risk)" style="padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                            {{ getRiskText(check.result.screening.risk) }}
                          </span>
                          <div v-if="check.result.label && check.result.label.label" style="margin-top: 4px; font-size: 12px; color: #718096;">
                            {{ check.result.label.label }}
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div>
            <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
              <h2 style="margin: 0 0 24px; color: #2d3748; font-size: 20px; font-weight: 600;">Статистика</h2>
              <div style="display: flex; flex-direction: column; gap: 24px;">
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Всего проверок</label>
                  <p style="margin: 0; font-size: 32px; font-weight: bold; color: #4299e1;">{{ stats.total_checks || 0 }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Платежей</label>
                  <p style="margin: 0; font-size: 32px; font-weight: bold; color: #38a169;">{{ stats.total_payments || 0 }}</p>
                </div>
                <div>
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Последняя активность</label>
                  <p style="margin: 0; font-size: 14px; color: #2d3748;">{{ formatDate(stats.last_activity) || 'Неизвестно' }}</p>
                </div>
                <div v-if="stats.last_check">
                  <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 8px;">Последняя проверка</label>
                  <div style="background: #f7fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                    <p style="margin: 0 0 4px; font-size: 12px; font-family: monospace; color: #2d3748; word-break: break-all;">{{ stats.last_check.address }}</p>
                    <p style="margin: 0 0 4px; font-size: 12px; color: #718096;">{{ stats.last_check.chain }} - {{ stats.last_check.type }}</p>
                    <p style="margin: 0; font-size: 12px; color: #718096;">{{ formatDate(stats.last_check.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Balance Modal -->
    <div v-if="showBalanceModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50;">
      <div style="background: white; border-radius: 12px; padding: 24px; width: 100%; max-width: 400px; margin: 0 16px;">
        <h3 style="margin: 0 0 16px; color: #2d3748; font-size: 20px; font-weight: 600;">Изменить баланс</h3>
        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 4px;">Новый баланс ($)</label>
          <input v-model="newBalance" type="number" step="0.01" style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 16px;">
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 12px;">
          <button @click="showBalanceModal = false" style="padding: 8px 16px; border: 1px solid #e2e8f0; border-radius: 6px; color: #4a5568; background: white; font-size: 14px; font-weight: 500; cursor: pointer;">
            Отмена
          </button>
          <button @click="updateBalance" style="padding: 8px 16px; border: none; border-radius: 6px; color: white; background: #4299e1; font-size: 14px; font-weight: 500; cursor: pointer;">
            Сохранить
          </button>
        </div>
      </div>
    </div>

    <!-- Message Modal -->
    <div v-if="showMessageModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50;">
      <div style="background: white; border-radius: 12px; padding: 24px; width: 100%; max-width: 400px; margin: 0 16px;">
        <h3 style="margin: 0 0 16px; color: #2d3748; font-size: 20px; font-weight: 600;">Отправить сообщение</h3>
        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 14px; font-weight: 500; color: #4a5568; margin-bottom: 4px;">Сообщение</label>
          <textarea v-model="messageText" rows="4" style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 16px; resize: vertical;"></textarea>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 12px;">
          <button @click="showMessageModal = false" style="padding: 8px 16px; border: 1px solid #e2e8f0; border-radius: 6px; color: #4a5568; background: white; font-size: 14px; font-weight: 500; cursor: pointer;">
            Отмена
          </button>
          <button @click="sendMessage" style="padding: 8px 16px; border: none; border-radius: 6px; color: white; background: #4299e1; font-size: 14px; font-weight: 500; cursor: pointer;">
            Отправить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

<script>
import { userService } from '@/services/users'

export default {
  name: 'UserDetail',
  data() {
    return {
      user: null,
      stats: {
        total_checks: 0,
        total_payments: 0
      },
      loading: true,
      error: null,
      showBalanceModal: false,
      showMessageModal: false,
      newBalance: 0,
      messageText: '',
      userActions: [],
      userActionsLoading: true,
      userChecks: [],
      userChecksLoading: true
    }
  },
  async mounted() {
    console.log('UserDetail: Component mounted')
    await this.loadUser()
    await this.loadUserStats()
    await this.loadUserActions()
    await this.loadUserChecks()
  },
  methods: {
    async loadUser() {
      console.log('UserDetail: Loading user data...')
      this.loading = true
      this.error = null
      try {
        const userId = this.$route.params.id
        console.log('UserDetail: User ID:', userId)
        this.user = await userService.getUser(userId)
        console.log('UserDetail: User data loaded:', this.user)
        this.newBalance = this.user.balance || 0
        this.loading = false
      } catch (error) {
        console.error('UserDetail: Error loading user:', error)
        this.error = 'Не удалось загрузить данные пользователя'
        this.loading = false
      }
    },
    async loadUserStats() {
      console.log('UserDetail: Loading user stats...')
      try {
        const userId = this.$route.params.id
        this.stats = await userService.getUserStats(userId)
        console.log('UserDetail: User stats loaded:', this.stats)
      } catch (error) {
        console.error('UserDetail: Error loading user stats:', error)
        // Используем fallback статистику
        this.stats = {
          total_checks: 0,
          total_payments: 0,
          last_activity: null
        }
      }
    },
    async loadUserActions() {
      console.log('UserDetail: Loading user actions...')
      this.userActionsLoading = true
      try {
        const userId = this.$route.params.id
        this.userActions = await userService.getUserActions(userId)
        console.log('UserDetail: User actions loaded:', this.userActions)
      } catch (error) {
        console.error('UserDetail: Error loading user actions:', error)
        this.userActions = []
      } finally {
        this.userActionsLoading = false
      }
    },
    async loadUserChecks() {
      console.log('UserDetail: Loading user checks...')
      this.userChecksLoading = true
      try {
        const userId = this.$route.params.id
        this.userChecks = await userService.getUserChecks(userId)
        console.log('UserDetail: User checks loaded:', this.userChecks)
      } catch (error) {
        console.error('UserDetail: Error loading user checks:', error)
        this.userChecks = []
      } finally {
        this.userChecksLoading = false
      }
    },
    formatDate(date) {
      if (!date) return 'Не указано'
      return new Date(date).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getActionStyle(actionType) {
      switch (actionType) {
        case 'update_balance':
          return { background: '#e6fffa', color: '#276749', border: '1px solid #a5f3c1' }
        case 'block_user':
          return { background: '#fffbeb', color: '#96531a', border: '1px solid #fcd34d' }
        case 'unblock_user':
          return { background: '#e6fffa', color: '#276749', border: '1px solid #a5f3c1' }
        case 'send_message':
          return { background: '#e6f7ff', color: '#1a365d', border: '1px solid #90cdf4' }
        default:
          return { background: '#f7fafc', color: '#4a5568', border: '1px solid #e2e8f0' }
      }
    },
    getActionText(actionType) {
      switch (actionType) {
        case 'update_balance':
          return 'Изменил баланс'
        case 'block_user':
          return 'Заблокировал'
        case 'unblock_user':
          return 'Разблокировал'
        case 'send_message':
          return 'Отправил сообщение'
        default:
          return actionType
      }
    },
    getRiskStyle(risk) {
      switch (risk) {
        case 'high':
          return { background: '#fde68a', color: '#92400e', border: '1px solid #fcd34d' }
        case 'medium':
          return { background: '#fef3c7', color: '#d69e2e', border: '1px solid #fcd34d' }
        case 'low':
          return { background: '#e6f7ff', color: '#1a365d', border: '1px solid #90cdf4' }
        default:
          return { background: '#f7fafc', color: '#4a5568', border: '1px solid #e2e8f0' }
      }
    },
    getRiskText(risk) {
      switch (risk) {
        case 'high':
          return 'Высокий риск'
        case 'medium':
          return 'Средний риск'
        case 'low':
          return 'Низкий риск'
        default:
          return 'Неизвестный риск'
      }
    },
    async toggleBlockUser() {
      console.log('UserDetail: Toggling block status for user:', this.user.id)
      try {
        if (this.user.is_blocked) {
          await userService.unblockUser(this.user.id)
          this.user.is_blocked = false
          console.log('UserDetail: User unblocked')
        } else {
          await userService.blockUser(this.user.id)
          this.user.is_blocked = true
          console.log('UserDetail: User blocked')
        }
        await this.loadUserActions() // Обновляем логи после изменения статуса
      } catch (error) {
        console.error('UserDetail: Error toggling block status:', error)
      }
    },
    async updateBalance() {
      console.log('UserDetail: Updating balance to:', this.newBalance)
      try {
        const response = await userService.updateBalance(this.user.id, this.newBalance)
        this.user.balance = this.newBalance
        this.showBalanceModal = false
        console.log('UserDetail: Balance updated successfully:', response)
        alert(`Баланс обновлен! Старый: $${response.old_balance}, Новый: $${response.new_balance}`)
        await this.loadUserActions() // Обновляем логи после изменения баланса
      } catch (error) {
        console.error('UserDetail: Error updating balance:', error)
        alert('Ошибка при обновлении баланса: ' + (error.response?.data?.detail || error.message))
      }
    },
    openMessageModal() {
      console.log('UserDetail: openMessageModal called')
      console.log('UserDetail: Current user:', this.user)
      this.showMessageModal = true
    },
    async sendMessage() {
      console.log('UserDetail: sendMessage called')
      console.log('UserDetail: messageText:', this.messageText)
      console.log('UserDetail: user.id:', this.user?.id)
      
      if (!this.messageText.trim()) {
        console.log('UserDetail: Empty message, showing alert')
        alert('Введите текст сообщения')
        return
      }
      
      if (!this.user?.id) {
        console.log('UserDetail: No user ID available')
        alert('Ошибка: ID пользователя не найден')
        return
      }
      
      try {
        console.log('UserDetail: Calling userService.sendMessage...')
        const response = await userService.sendMessage(this.user.id, this.messageText)
        console.log('UserDetail: Message sent successfully:', response)
        
        this.showMessageModal = false
        this.messageText = ''
        alert('Сообщение отправлено успешно!')
        
        console.log('UserDetail: Reloading user actions...')
        await this.loadUserActions()
        console.log('UserDetail: User actions reloaded')
      } catch (error) {
        console.error('UserDetail: Error sending message:', error)
        console.error('UserDetail: Error details:', error.response?.data)
        alert('Ошибка при отправке сообщения: ' + (error.response?.data?.detail || error.message))
      }
    },
    onBalanceButtonHover() {
      this.$el.style.backgroundColor = '#3182ce';
    },
    onBalanceButtonLeave() {
      this.$el.style.backgroundColor = '#4299e1';
    },
    onBlockButtonHover() {
      this.$el.style.backgroundColor = '#2f855a';
    },
    onBlockButtonLeave() {
      this.$el.style.backgroundColor = '#38a169';
    },
    onMessageButtonHover() {
      this.$el.style.backgroundColor = '#f7fafc';
    },
    onMessageButtonLeave() {
      this.$el.style.backgroundColor = 'white';
    },
    onBackButtonHover() {
      this.$el.style.backgroundColor = '#f7fafc';
    },
    onBackButtonLeave() {
      this.$el.style.backgroundColor = 'white';
    }
  }
}
</script>
