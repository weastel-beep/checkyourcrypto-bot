import { defineStore } from 'pinia'
import api from '@/services/api'

export const useTextStore = defineStore('text', {
  state: () => ({
    texts: [],
    loading: false,
    error: null
  }),

  getters: {
    getTexts: (state) => state.texts,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },

  actions: {
    async fetchTexts() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get('/unified/texts')
        this.texts = response.data
      } catch (error) {
        console.error('Error fetching texts:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async createText(textData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.post('/unified/texts', textData)
        this.texts.push(response.data)
        return response.data
      } catch (error) {
        console.error('Error creating text:', error)
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateText(id, textData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.put(`/unified/texts/${id}`, textData)
        const index = this.texts.findIndex(text => text.id === id)
        if (index !== -1) {
          this.texts[index] = response.data
        }
        return response.data
      } catch (error) {
        console.error('Error updating text:', error)
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteText(id) {
      this.loading = true
      this.error = null
      
      try {
        await api.delete(`/unified/texts/${id}`)
        this.texts = this.texts.filter(text => text.id !== id)
      } catch (error) {
        console.error('Error deleting text:', error)
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    getTextById(id) {
      return this.texts.find(text => text.id === id)
    },

    getTextsByCategory(category) {
      return this.texts.filter(text => text.category === category)
    },

    getTextsByLanguage(language) {
      return this.texts.filter(text => text.language === language)
    }
  }
})
