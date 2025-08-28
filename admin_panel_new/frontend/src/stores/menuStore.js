import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService } from '@/services/apiService'

export const useMenuStore = defineStore('menu', () => {
  const menus = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Получение списка меню
  const getMenus = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get('/api/menus', { params })
      menus.value = response.menus
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получение конкретного меню
  const getMenu = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get(`/api/menus/${id}`)
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Создание меню
  const createMenu = async (menuData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.post('/api/menus', menuData)
      
      // Добавляем новое меню в список
      menus.value.unshift(response)
      
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка создания меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Обновление меню
  const updateMenu = async (id, menuData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.put(`/api/menus/${id}`, menuData)
      
      // Обновляем меню в списке
      const index = menus.value.findIndex(menu => menu.id === id)
      if (index !== -1) {
        menus.value[index] = { ...menus.value[index], ...menuData }
      }
      
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка обновления меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Удаление меню
  const deleteMenu = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      await apiService.delete(`/api/menus/${id}`)
      
      // Удаляем меню из списка
      const index = menus.value.findIndex(menu => menu.id === id)
      if (index !== -1) {
        menus.value.splice(index, 1)
      }
      
      return true
    } catch (err) {
      error.value = err.message || 'Ошибка удаления меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Импорт меню
  const importMenus = async (importData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.post('/api/menus/import', importData)
      
      // Перезагружаем список меню
      await getMenus()
      
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка импорта меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получение меню для бота
  const getBotMenu = async (menuName, language = 'ru') => {
    try {
      const response = await apiService.get(`/api/bot/menus/${menuName}`, {
        params: { language }
      })
      return response
    } catch (err) {
      console.error('Ошибка получения меню для бота:', err)
      return null
    }
  }

  // Очистка ошибок
  const clearError = () => {
    error.value = null
  }

  // Сброс состояния
  const reset = () => {
    menus.value = []
    loading.value = false
    error.value = null
  }

  // Методы для работы со связками текстов
  const getTextLinks = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get('/api/menu-text-links', { params })
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки связок'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createTextLink = async (linkData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.post('/api/menu-text-links', linkData)
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка создания связки'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTextLink = async (linkId, linkData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.put(`/api/menu-text-links/${linkId}`, linkData)
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка обновления связки'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTextLink = async (linkId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.delete(`/api/menu-text-links/${linkId}`)
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка удаления связки'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAllMenuItems = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiService.get('/api/menu-items')
      return response
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки элементов меню'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    menus,
    loading,
    error,
    
    // Actions
    getMenus,
    getMenu,
    createMenu,
    updateMenu,
    deleteMenu,
    importMenus,
    getBotMenu,
    clearError,
    reset,
    
    // Text Links Actions
    getTextLinks,
    createTextLink,
    updateTextLink,
    deleteTextLink,
    getAllMenuItems
  }
})
