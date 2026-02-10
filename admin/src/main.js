import { createApp } from 'vue'
import { createPinia } from 'pinia'
import "bootstrap/dist/css/bootstrap.css"
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap"

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Восстанавливаем авторизацию при запуске приложения
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.checkAuth()

app.mount('#app')