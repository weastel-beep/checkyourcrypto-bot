<template>
  <div style="min-height: 100vh; background: #f5f7fa;">
    <!-- Header -->
    <Header />

    <!-- Main Content -->
    <main style="max-width: 1200px; margin: 0 auto; padding: 30px 20px;">
      <!-- Page Header -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
          <h2 style="margin: 0; color: #2d3748; font-size: 24px; font-weight: bold;">Пользователи</h2>
          <p style="margin: 5px 0 0; color: #718096; font-size: 14px;">Управление пользователями бота</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" style="text-align: center; padding: 40px;">
        <div style="font-size: 18px; color: #718096;">Загрузка пользователей...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" style="background: #fed7d7; border: 1px solid #feb2b2; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
        <div style="color: #e53e3e; font-size: 16px; font-weight: 500;">{{ error }}</div>
        <button @click="loadUsers" style="margin-top: 12px; padding: 8px 16px; background: #e53e3e; color: white; border: none; border-radius: 6px; cursor: pointer;">Повторить</button>
      </div>

      <!-- Users Table -->
      <div v-else style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
        <!-- Search Bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
          <h3 style="margin: 0; color: #2d3748; font-size: 18px; font-weight: 600;">Список пользователей</h3>
          <div style="display: flex; gap: 12px;">
            <input 
              type="text" 
              placeholder="Поиск пользователей..."
              v-model="search"
              style="width: 256px; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; outline: none; transition: border-color 0.2s;"
              onfocus="this.style.borderColor='#4299e1'"
              onblur="this.style.borderColor='#e2e8f0'"
            >
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid #e2e8f0;">
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">ID</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Username</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Баланс</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Статус</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Дата регистрации</th>
                <th style="text-align: left; padding: 16px; color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id" style="border-bottom: 1px solid #f7fafc;">
                <td style="padding: 16px; color: #2d3748; font-size: 14px; font-weight: 500;">{{ user.id }}</td>
                <td style="padding: 16px; color: #2d3748; font-size: 14px;">{{ user.username || 'Не указан' }}</td>
                <td style="padding: 16px; color: #2d3748; font-size: 14px;">${{ user.balance }}</td>
                <td style="padding: 16px;">
                  <span :style="user.is_blocked ? 'background: #fed7d7; color: #e53e3e;' : 'background: #f0fff4; color: #38a169;'" style="padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                    {{ user.is_blocked ? 'Заблокирован' : 'Активен' }}
                  </span>
                </td>
                <td style="padding: 16px; color: #718096; font-size: 14px;">{{ formatDate(user.created_at) }}</td>
                <td style="padding: 16px;">
                  <div style="display: flex; gap: 8px; align-items: center;">
                    <router-link :to="`/users/${user.id}`" style="color: #4299e1; text-decoration: none; font-size: 14px; transition: color 0.2s;" onmouseover="this.style.color='#3182ce'" onmouseout="this.style.color='#4299e1'">Просмотр</router-link>
                    <button @click="toggleBlockUser(user)" :style="user.is_blocked ? 'color: #38a169;' : 'color: #e53e3e;'" style="background: none; border: none; cursor: pointer; font-size: 14px; transition: color 0.2s;" onmouseover="this.style.color=user.is_blocked ? '#2f855a' : '#c53030'" onmouseout="this.style.color=user.is_blocked ? '#38a169' : '#e53e3e'">
                      {{ user.is_blocked ? 'Разблокировать' : 'Заблокировать' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Info -->
        <div style="margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
          <div style="color: #718096; font-size: 14px;">
            Показано {{ filteredUsers.length }} из {{ total }} пользователей
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { authService } from '@/services/auth'
import { userService } from '@/services/users'
import Header from '@/components/Layout/Header.vue'

export default {
  components: {
    Header
  },
  name: 'UserList',
  data() {
    return {
      users: [],
      search: '',
      total: 0,
      loading: false,
      error: null
    }
  },
  async mounted() {
    console.log('UserList: Component mounted')
    await this.loadUsers()
  },
  computed: {
    filteredUsers() {
      if (!this.search) return this.users
      
      const searchLower = this.search.toLowerCase()
      return this.users.filter(user => 
        user.username?.toLowerCase().includes(searchLower) ||
        user.id.toString().includes(searchLower)
      )
    }
  },
  methods: {
    async loadUsers() {
      console.log('UserList: Loading users...')
      this.loading = true
      this.error = null
      
      try {
        const users = await userService.getUsers()
        this.users = users
        this.total = users.length
        console.log('UserList: Users loaded:', users)
      } catch (error) {
        console.error('UserList: Error loading users:', error)
        this.error = 'Ошибка загрузки пользователей'
        // Fallback data
        this.users = [
          { id: 123456789, username: 'test_user', balance: 10.50, is_blocked: false, created_at: '2024-01-15' },
          { id: 987654321, username: 'another_user', balance: 25.00, is_blocked: true, created_at: '2024-01-10' }
        ]
        this.total = this.users.length
      } finally {
        this.loading = false
      }
    },
    
    async toggleBlockUser(user) {
      console.log('UserList: Toggling block for user:', user.id)
      try {
        if (user.is_blocked) {
          await userService.unblockUser(user.id)
          user.is_blocked = false
          console.log('UserList: User unblocked')
        } else {
          await userService.blockUser(user.id)
          user.is_blocked = true
          console.log('UserList: User blocked')
        }
      } catch (error) {
        console.error('UserList: Error toggling user block:', error)
        alert('Ошибка при изменении статуса пользователя')
      }
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString('ru-RU')
    },
    
    async logout() {
      console.log('UserList: Logging out...')
      try {
        await authService.logout()
        this.$router.push('/login')
      } catch (error) {
        console.error('UserList: Logout error:', error)
        this.$router.push('/login')
      }
    }
  }
}
</script>
