/**
 * Структурированный логгер для фронтенда
 */

class Logger {
  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development'
  }

  /**
   * Логирование информационных сообщений
   */
  info(message, data = {}) {
    const logData = {
      level: 'info',
      message,
      timestamp: new Date().toISOString(),
      ...data
    }
    
    if (this.isDevelopment) {
      console.log('ℹ️', message, data)
    }
    
    // В продакшене можно отправлять в внешний сервис логирования
    this.sendToLogService(logData)
  }

  /**
   * Логирование предупреждений
   */
  warn(message, data = {}) {
    const logData = {
      level: 'warn',
      message,
      timestamp: new Date().toISOString(),
      ...data
    }
    
    if (this.isDevelopment) {
      console.warn('⚠️', message, data)
    }
    
    this.sendToLogService(logData)
  }

  /**
   * Логирование ошибок
   */
  error(message, error = null, data = {}) {
    const logData = {
      level: 'error',
      message,
      timestamp: new Date().toISOString(),
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack
      } : null,
      ...data
    }
    
    if (this.isDevelopment) {
      console.error('❌', message, error, data)
    }
    
    this.sendToLogService(logData)
  }

  /**
   * Логирование отладочной информации
   */
  debug(message, data = {}) {
    if (!this.isDevelopment) return
    
    const logData = {
      level: 'debug',
      message,
      timestamp: new Date().toISOString(),
      ...data
    }
    
    console.debug('🔍', message, data)
    this.sendToLogService(logData)
  }

  /**
   * Логирование API запросов
   */
  apiRequest(method, url, data = {}) {
    this.info('API Request', {
      type: 'api_request',
      method,
      url,
      ...data
    })
  }

  /**
   * Логирование API ответов
   */
  apiResponse(method, url, status, duration, data = {}) {
    this.info('API Response', {
      type: 'api_response',
      method,
      url,
      status,
      duration: `${duration}ms`,
      ...data
    })
  }

  /**
   * Логирование API ошибок
   */
  apiError(method, url, status, error, data = {}) {
    this.error('API Error', error, {
      type: 'api_error',
      method,
      url,
      status,
      ...data
    })
  }

  /**
   * Логирование действий пользователя
   */
  userAction(action, component, data = {}) {
    this.info('User Action', {
      type: 'user_action',
      action,
      component,
      ...data
    })
  }

  /**
   * Логирование производительности
   */
  performance(operation, duration, data = {}) {
    this.info('Performance', {
      type: 'performance',
      operation,
      duration: `${duration}ms`,
      ...data
    })
  }

  /**
   * Отправка логов во внешний сервис
   */
  async sendToLogService(logData) {
    try {
      // В продакшене можно отправлять в Sentry, LogRocket или другой сервис
      if (!this.isDevelopment) {
        // Пример отправки в внешний API
        // await fetch('/api/logs', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(logData)
        // })
      }
    } catch (error) {
      // Не логируем ошибки логирования, чтобы избежать бесконечного цикла
      console.error('Failed to send log to external service:', error)
    }
  }
}

// Создаем единственный экземпляр логгера
const logger = new Logger()

export default logger
