import api from './api'

export const userService = {
  async getUsers() {
    console.log('UserService: Getting users...')
    try {
      const response = await api.get('/users')
      console.log('UserService: Users response:', response.data)
      // API возвращает { users: [...] }, поэтому берем response.data.users
      return response.data.users || []
    } catch (error) {
      console.error('UserService: Error getting users:', error)
      throw error
    }
  },
  
  async getUser(userId) {
    console.log('UserService: Getting user:', userId)
    try {
      const response = await api.get(`/users/${userId}`)
      console.log('UserService: User response:', response.data)
      return response.data
    } catch (error) {
      console.error('UserService: Error getting user:', error)
      throw error
    }
  },
  
  async updateUser(userId, userData) {
    const response = await api.put(`/users/${userId}`, userData)
    return response.data
  },
  
  async blockUser(userId) {
    console.log('UserService: Blocking user:', userId)
    try {
      const response = await api.post(`/users/${userId}/block`)
      console.log('UserService: Block response:', response.data)
      return response.data
    } catch (error) {
      console.error('UserService: Error blocking user:', error)
      throw error
    }
  },
  
  async unblockUser(userId) {
    console.log('UserService: Unblocking user:', userId)
    try {
      const response = await api.post(`/users/${userId}/unblock`)
      console.log('UserService: Unblock response:', response.data)
      return response.data
    } catch (error) {
      console.error('UserService: Error unblocking user:', error)
      throw error
    }
  },

  async updateBalance(userId, amount) {
    console.log('UserService: Updating balance for user:', userId, 'amount:', amount)
    try {
      const response = await api.post(`/users/${userId}/balance`, { amount })
      console.log('UserService: Update balance response:', response.data)
      return response.data
    } catch (error) {
      console.error('UserService: Error updating balance:', error)
      throw error
    }
  },

  async sendMessage(userId, message) {
    console.log('UserService: Sending message to user:', userId, 'message:', message)
    try {
      console.log('UserService: Making API request to:', `/users/${userId}/message`)
      const response = await api.post(`/users/${userId}/message`, { message })
      console.log('UserService: Send message response:', response.data)
      return response.data
    } catch (error) {
      console.error('UserService: Error sending message:', error)
      console.error('UserService: Error response:', error.response?.data)
      console.error('UserService: Error status:', error.response?.status)
      throw error
    }
  },

  async getUserStats(userId) {
    console.log('UserService: Getting stats for user:', userId)
    try {
      const response = await api.get(`/users/${userId}/stats`)
      console.log('UserService: User stats response:', response.data)
      return response.data
    } catch (error) {
      console.error('UserService: Error getting user stats:', error)
      throw error
    }
  },

  async getAdminActions() {
    console.log('UserService: Getting admin actions...')
    try {
      const response = await api.get('/admin/actions')
      console.log('UserService: Admin actions response:', response.data)
      return response.data.actions || []
    } catch (error) {
      console.error('UserService: Error getting admin actions:', error)
      throw error
    }
  },

  async getUserActions(userId) {
    console.log('UserService: Getting user actions for user:', userId)
    try {
      const response = await api.get('/admin/actions')
      console.log('UserService: All admin actions response:', response.data)
      // Фильтруем действия только для конкретного пользователя
      const userActions = response.data.actions.filter(action => action.user_id == userId)
      console.log('UserService: Filtered user actions:', userActions)
      return userActions
    } catch (error) {
      console.error('UserService: Error getting user actions:', error)
      throw error
    }
  },

  async getUserChecks(userId) {
    console.log('UserService: Getting user checks for user:', userId)
    try {
      const response = await api.get(`/users/${userId}/checks`)
      console.log('UserService: User checks response:', response.data)
      return response.data.checks || []
    } catch (error) {
      console.error('UserService: Error getting user checks:', error)
      throw error
    }
  }
}
