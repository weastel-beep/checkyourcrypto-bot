import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/auth'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import UserList from '@/views/Users/UserList.vue'
import UserDetail from '@/views/Users/UserDetail.vue'
import MessageList from '@/views/Messages/MessageList.vue'
import MessageCreate from '@/views/Messages/MessageCreate.vue'
import MessageDetail from '@/views/Messages/MessageDetail.vue'
import TextList from '@/views/Texts/TextList.vue'

import BotFlowDesigner from '@/views/BotFlowDesigner.vue'
import AdminActions from '@/views/AdminActions.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserList',
    component: UserList,
    meta: { requiresAuth: true }
  },
  {
    path: '/users/:id',
    name: 'UserDetail',
    component: UserDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'MessageList',
    component: MessageList,
    meta: { requiresAuth: true }
  },
  {
    path: '/messages/create',
    name: 'MessageCreate',
    component: MessageCreate,
    meta: { requiresAuth: true }
  },
  {
    path: '/messages/:id',
    name: 'MessageDetail',
    component: MessageDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/texts',
    name: 'TextList',
    component: TextList,
    meta: { requiresAuth: true }
  },

  {
    path: '/bot-flow-designer',
    name: 'BotFlowDesigner',
    component: BotFlowDesigner,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin-actions',
    name: 'AdminActions',
    component: AdminActions,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  console.log('Router navigation:', { from: from.path, to: to.path })
  
  if (to.meta.requiresAuth) {
    const isAuthenticated = authService.isAuthenticated()
    console.log('Current authentication status:', isAuthenticated)
    
    if (isAuthenticated) {
      console.log('User authenticated, allowing navigation to:', to.path)
      next()
    } else {
      console.log('User not authenticated, redirecting to login')
      next('/login')
    }
  } else {
    next()
  }
})

export default router
