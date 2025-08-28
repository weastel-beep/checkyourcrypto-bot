import api from './api'

export const dashboardService = {
  async getStats() {
    console.log('DashboardService: Getting stats...')
    try {
      const response = await api.get('/dashboard/stats')
      console.log('DashboardService: Stats response:', response.data)
      return response.data
    } catch (error) {
      console.error('DashboardService: Error getting stats:', error)
      throw error
    }
  },
  
  async getUserActivityChart() {
    console.log('DashboardService: Getting user activity chart...')
    try {
      const response = await api.get('/dashboard/charts/user-activity')
      console.log('DashboardService: User activity response:', response.data)
      return response.data
    } catch (error) {
      console.error('DashboardService: Error getting user activity:', error)
      throw error
    }
  }
}
