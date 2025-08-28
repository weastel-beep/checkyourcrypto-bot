import axios from 'axios'

// Создаем экземпляр axios с базовой конфигурацией
const apiService = axios.create({
  baseURL: 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Интерцептор для добавления токена авторизации
apiService.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерцептор для обработки ответов
apiService.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Обработка ошибок авторизации
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export { apiService }
