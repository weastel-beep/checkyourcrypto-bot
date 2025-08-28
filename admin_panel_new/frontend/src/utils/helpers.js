/**
 * Утилиты для работы с приложением
 */

/**
 * Создает debounced функцию
 * @param {Function} func - функция для debounce
 * @param {number} wait - время ожидания в миллисекундах
 * @returns {Function} - debounced функция
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Форматирует дату в читаемый вид
 * @param {string|Date} date - дата для форматирования
 * @returns {string} - отформатированная дата
 */
export function formatDate(date) {
  if (!date) return ''
  
  const d = new Date(date)
  return d.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Форматирует число с разделителями
 * @param {number} num - число для форматирования
 * @returns {string} - отформатированное число
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

/**
 * Обрезает текст до указанной длины
 * @param {string} text - текст для обрезки
 * @param {number} length - максимальная длина
 * @returns {string} - обрезанный текст
 */
export function truncateText(text, length = 100) {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

/**
 * Проверяет, является ли значение пустым
 * @param {*} value - значение для проверки
 * @returns {boolean} - true если пустое
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * Копирует текст в буфер обмена
 * @param {string} text - текст для копирования
 * @returns {Promise<boolean>} - успешность операции
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    console.error('Ошибка копирования в буфер обмена:', err)
    return false
  }
}

/**
 * Генерирует случайный ID
 * @param {number} length - длина ID
 * @returns {string} - случайный ID
 */
export function generateId(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}
