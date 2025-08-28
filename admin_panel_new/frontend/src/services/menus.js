import api from './api'

export const menuService = {
  // Получить список всех меню
  async getMenus(page = 1, limit = 10) {
    try {
      const response = await api.get(`/menus?page=${page}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения меню:', error)
      throw error
    }
  },

  // Получить конкретное меню
  async getMenu(menuId) {
    try {
      const response = await api.get(`/menus/${menuId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка получения меню:', error)
      throw error
    }
  },

  // Создать новое меню
  async createMenu(menuData) {
    try {
      const response = await api.post('/menus', menuData)
      return response.data
    } catch (error) {
      console.error('Ошибка создания меню:', error)
      throw error
    }
  },

  // Обновить меню
  async updateMenu(menuId, menuData) {
    try {
      const response = await api.put(`/menus/${menuId}`, menuData)
      return response.data
    } catch (error) {
      console.error('Ошибка обновления меню:', error)
      throw error
    }
  },

  // Удалить меню
  async deleteMenu(menuId) {
    try {
      const response = await api.delete(`/menus/${menuId}`)
      return response.data
    } catch (error) {
      console.error('Ошибка удаления меню:', error)
      throw error
    }
  },

  // Импортировать меню
  async importMenus(importData) {
    try {
      const response = await api.post('/menus/import', importData)
      return response.data
    } catch (error) {
      console.error('Ошибка импорта меню:', error)
      throw error
    }
  },

  // Получить структуру меню для отображения
  getMenuStructure(menu) {
    if (!menu || !menu.items) return []
    
    // Группируем элементы по строкам
    const rows = {}
    menu.items.forEach(item => {
      if (!rows[item.row_position]) {
        rows[item.row_position] = []
      }
      rows[item.row_position].push(item)
    })
    
    // Сортируем строки и элементы в строках
    return Object.keys(rows)
      .sort((a, b) => parseInt(a) - parseInt(b))
      .map(rowPos => 
        rows[rowPos].sort((a, b) => a.column_position - b.column_position)
      )
  },

  // Создать структуру меню для отправки
  createMenuStructure(rows) {
    return rows.map(row => 
      row.map(item => ({
        text: item.text,
        callback: item.callback_data
      }))
    )
  }
}

export default menuService
