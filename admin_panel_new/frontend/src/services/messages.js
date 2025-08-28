import api from './api'

export const messageService = {
  async getMessages() {
    console.log('MessageService: Getting messages...')
    try {
      const response = await api.get('/messages')
      console.log('MessageService: Messages response:', response.data)
      return response.data
    } catch (error) {
      console.error('MessageService: Error getting messages:', error)
      throw error
    }
  },
  
  async getMessage(messageId) {
    console.log('MessageService: Getting message:', messageId)
    try {
      const response = await api.get(`/messages/${messageId}`)
      console.log('MessageService: Message response:', response.data)
      return response.data
    } catch (error) {
      console.error('MessageService: Error getting message:', error)
      throw error
    }
  },
  
  async createMessage(messageData) {
    console.log('MessageService: Creating message:', messageData)
    try {
      const response = await api.post('/messages', messageData)
      console.log('MessageService: Create response:', response.data)
      return response.data
    } catch (error) {
      console.error('MessageService: Error creating message:', error)
      throw error
    }
  },
  
  async sendMessage(messageId) {
    console.log('MessageService: Sending message:', messageId)
    try {
      const response = await api.post(`/messages/${messageId}/send`)
      console.log('MessageService: Send response:', response.data)
      return response.data
    } catch (error) {
      console.error('MessageService: Error sending message:', error)
      throw error
    }
  },
  
  async deleteMessage(messageId) {
    console.log('MessageService: Deleting message:', messageId)
    try {
      const response = await api.delete(`/messages/${messageId}`)
      console.log('MessageService: Delete response:', response.data)
      return response.data
    } catch (error) {
      console.error('MessageService: Error deleting message:', error)
      throw error
    }
  }
}
