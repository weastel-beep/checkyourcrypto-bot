<template>
  <div class="sidebar bg-white shadow-lg h-full">
    <div class="p-6">
      <div class="flex items-center mb-8">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
          <span class="text-white font-bold text-sm">C</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900">Check Your Crypto Admin</h1>
      </div>
      
      <nav class="space-y-2">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="sidebar-link"
          :class="{ 'active': $route.path === item.path }"
        >
          <component :is="item.icon" class="w-5 h-5 mr-3" />
          {{ item.name }}
        </router-link>
      </nav>
    </div>
    
    <div class="absolute bottom-6 left-6 right-6">
      <button 
        @click="logout"
        class="w-full flex items-center px-4 py-2 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 transition-colors duration-200"
      >
        <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Выйти
      </button>
    </div>
  </div>
</template>

<script>
import { authService } from '@/services/auth'

export default {
  name: 'Sidebar',
  data() {
    console.log('Sidebar: Initializing component')
    const items = [
      {
        name: 'Дашборд',
        path: '/dashboard',
        icon: 'DashboardIcon'
      },
      {
        name: 'Пользователи',
        path: '/users',
        icon: 'UsersIcon'
      },
      {
        name: 'Сообщения',
        path: '/messages',
        icon: 'MessagesIcon'
      },
      {
        name: 'Тексты',
        path: '/texts',
        icon: 'TextsIcon'
      },
      {
        name: 'Конструктор бота',
        path: '/bot-flow-designer',
        icon: 'BotFlowIcon'
      },
      {
        name: 'Логи админа',
        path: '/admin-actions',
        icon: 'LogsIcon'
      }
    ]
    console.log('Sidebar: Menu items:', items)
    return {
      menuItems: items
    }
  },
  methods: {
    async logout() {
      await authService.logout()
      this.$router.push('/login')
    }
  },
  components: {
    DashboardIcon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z" />
        </svg>
      `
    },
    UsersIcon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      `
    },
    MessagesIcon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      `
    },
    TextsIcon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      `
    },
    BotFlowIcon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      `
    },
    LogsIcon: {
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      `
    },

  }
}
</script>

<style scoped>
.sidebar-link {
  @apply flex items-center px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200;
}

.sidebar-link.active {
  @apply bg-blue-50 text-blue-700;
}
</style>
