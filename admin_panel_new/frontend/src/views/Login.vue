<template>
  <div style="min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: white; border-radius: 10px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 400px; width: 100%;">
      
      <!-- Header -->
      <div style="text-align: center; margin-bottom: 30px;">
        <div style="width: 60px; height: 60px; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;">
          <span style="color: white; font-size: 24px; font-weight: bold;">C</span>
        </div>
        <h1 style="margin: 0; color: #333; font-size: 24px; font-weight: bold;">Check Your Crypto</h1>
        <p style="margin: 5px 0 0; color: #666; font-size: 14px;">Админ-панель</p>
      </div>

      <!-- Demo Info -->
      <div style="background: #f8f9ff; border: 1px solid #e1e5ff; border-radius: 8px; padding: 15px; margin-bottom: 25px;">
        <p style="margin: 0 0 10px; color: #4a5568; font-size: 14px; font-weight: 600;">Демо доступ:</p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
          <div>Логин: <code style="background: #e1e5ff; padding: 2px 6px; border-radius: 4px;">admin</code></div>
          <div>Пароль: <code style="background: #e1e5ff; padding: 2px 6px; border-radius: 4px;">admin123</code></div>
        </div>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin">
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: #4a5568; font-size: 14px; font-weight: 500;">Имя пользователя</label>
          <input 
            v-model="form.username"
            type="text" 
            required 
            style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; box-sizing: border-box;"
            placeholder="Введите имя пользователя"
          >
        </div>

        <div style="margin-bottom: 25px;">
          <label style="display: block; margin-bottom: 8px; color: #4a5568; font-size: 14px; font-weight: 500;">Пароль</label>
          <input 
            v-model="form.password"
            type="password" 
            required 
            style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; box-sizing: border-box;"
            placeholder="Введите пароль"
          >
        </div>

        <!-- Error Message -->
        <div v-if="error" style="background: #fed7d7; border: 1px solid #feb2b2; color: #c53030; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-size: 14px;">
          {{ error }}
        </div>

        <!-- Success Message -->
        <div v-if="success" style="background: #c6f6d5; border: 1px solid #9ae6b4; color: #22543d; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-size: 14px;">
          {{ success }}
        </div>

        <!-- Login Button -->
        <button 
          type="submit" 
          :disabled="loading"
          style="width: 100%; padding: 12px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; opacity: 1; transition: opacity 0.2s;"
          :style="{ opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }"
        >
          <span v-if="loading">Вход...</span>
          <span v-else>Войти в систему</span>
        </button>
      </form>

      <!-- Footer -->
      <div style="text-align: center; margin-top: 25px;">
        <p style="margin: 0; color: #a0aec0; font-size: 12px;">© 2024 Check Your Crypto</p>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from '@/services/auth'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: 'admin',
        password: 'admin123'
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        console.log('Login component: Starting login process...')
        const result = await authService.login(this.form.username, this.form.password)
        console.log('Login component: Login successful:', result)
        
        this.success = 'Вход выполнен успешно! Перенаправление...'
        
        // Небольшая задержка чтобы пользователь увидел сообщение
        setTimeout(() => {
          console.log('Login component: Redirecting to dashboard...')
          this.$router.push('/dashboard')
        }, 1000)
        
      } catch (error) {
        console.error('Login component: Login failed:', error)
        this.error = error.response?.data?.error || error.message || 'Ошибка входа в систему'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
