import axios from 'axios'
import logger from '../utils/logger'

// Создаем экземпляр axios
const api = axios.create({
  baseURL: 'https://checkyourcrypto-admin-api-new-51ea71c68148.herokuapp.com/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для добавления токена и логирования запросов
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Добавляем timestamp для измерения времени выполнения
    config.metadata = { startTime: new Date() }
    
    // Логируем запрос
    logger.apiRequest(config.method?.toUpperCase(), config.url, {
      hasAuth: !!token,
      timeout: config.timeout
    })
    
    return config
  },
  (error) => {
    logger.error('API Request Error', error, {
      type: 'api_request_error'
    })
    return Promise.reject(error)
  }
)

// Interceptor для обработки ответов и ошибок
api.interceptors.response.use(
  (response) => {
    // Вычисляем время выполнения
    const duration = new Date() - response.config.metadata.startTime
    
    // Логируем успешный ответ
    logger.apiResponse(
      response.config.method?.toUpperCase(),
      response.config.url,
      response.status,
      duration,
      {
        dataSize: JSON.stringify(response.data).length
      }
    )
    
    return response
  },
  (error) => {
    // Вычисляем время выполнения для ошибок
    const duration = error.config?.metadata?.startTime 
      ? new Date() - error.config.metadata.startTime 
      : 0
    
    // Логируем ошибку
    logger.apiError(
      error.config?.method?.toUpperCase(),
      error.config?.url,
      error.response?.status,
      error,
      {
        duration: `${duration}ms`,
        timeout: error.code === 'ECONNABORTED'
      }
    )
    
    // Обработка 401 ошибки (неавторизован)
    if (error.response?.status === 401) {
      logger.warn('User session expired, redirecting to login', {
        type: 'session_expired'
      })
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default api
