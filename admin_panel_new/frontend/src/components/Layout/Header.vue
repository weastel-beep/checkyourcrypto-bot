<template>
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
            <router-link to="/bot-flow-designer" style="text-decoration: none; color: #4a5568; font-weight: 500; padding: 8px 16px; border-radius: 6px; transition: all 0.2s;" :style="{ backgroundColor: $route.path === '/bot-flow-designer' ? '#e6fffa' : 'transparent', color: $route.path === '/bot-flow-designer' ? '#319795' : '#4a5568' }">
              🤖 Конструктор бота
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
</template>

<script>
import { authService } from '@/services/auth'

export default {
  name: 'Header',
  methods: {
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
