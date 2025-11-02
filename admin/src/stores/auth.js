// auth.js - упрощенная версия
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const currentUser = ref(null)
  const authToken = ref(null)

  const isAdmin = computed(() => {
    return isAuthenticated.value && currentUser.value?.is_superuser
  })

  const login = (userData, token) => {
    isAuthenticated.value = true
    currentUser.value = userData
    authToken.value = token
    
    localStorage.setItem('adminAuth', JSON.stringify({
      user: userData,
      token: token,
      timestamp: Date.now()
    }))
    
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
    }
  }

  const logout = () => {
    isAuthenticated.value = false
    currentUser.value = null
    authToken.value = null
    
    localStorage.removeItem('adminAuth')
    delete axios.defaults.headers.common['Authorization']
  }

  const checkAuth = () => {
    const savedAuth = localStorage.getItem('adminAuth')
    if (savedAuth) {
      try {
        const authData = JSON.parse(savedAuth)
        
        // Проверяем срок действия (24 часа)
        const isExpired = Date.now() - authData.timestamp > 24 * 60 * 60 * 1000
        
        if (!isExpired && authData.user?.is_superuser) {
          // Восстанавливаем авторизацию без проверки на сервере
          login(authData.user, authData.token)
          return true
        }
      } catch (e) {
        console.error('Error parsing auth data:', e)
      }
    }
    
    logout()
    return false
  }

  return {
    isAuthenticated,
    currentUser,
    isAdmin,
    login,
    logout,
    checkAuth
  }
})