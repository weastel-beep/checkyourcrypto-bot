import api from './api'

export const authService = {
  async login(username, password) {
    console.log('AuthService: Starting login...', { username })
    
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    try {
      console.log('AuthService: Sending request to API...')
      const response = await api.post('/auth/login', formData)
      console.log('AuthService: API response:', response.data)
      
      if (response.data && response.data.access_token) {
        localStorage.setItem('token', response.data.access_token)
        console.log('AuthService: Token saved to localStorage')
        return response.data
      } else {
        console.error('AuthService: No access token in response:', response.data)
        throw new Error('No access token in response')
      }
    } catch (error) {
      console.error('AuthService: Login error:', error)
      if (error.response) {
        console.error('AuthService: Response status:', error.response.status)
        console.error('AuthService: Response data:', error.response.data)
      }
      throw error
    }
  },
  
  async logout() {
    console.log('AuthService: Logging out...')
    localStorage.removeItem('token')
  },
  
  async getCurrentUser() {
    try {
      console.log('AuthService: Getting current user...')
      const response = await api.get('/auth/me')
      console.log('AuthService: Current user response:', response.data)
      return response.data
    } catch (error) {
      console.error('AuthService: Get current user error:', error)
      return { username: 'Admin' }
    }
  },
  
  isAuthenticated() {
    const token = localStorage.getItem('token')
    console.log('AuthService: Checking authentication, token exists:', !!token)
    return !!token
  },
  
  getToken() {
    const token = localStorage.getItem('token')
    console.log('AuthService: Getting token:', token ? 'exists' : 'not found')
    return token
  }
}
