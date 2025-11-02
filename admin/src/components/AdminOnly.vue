<template>
  <div>
    <!-- Показываем контент только админам -->
    <div v-if="authStore.isAdmin">
      <slot />
    </div>
    
    <!-- Сообщение для неавторизованных пользователей -->
    <div v-else class="admin-only-message">
      <div class="card">
        <div class="card-body text-center">
          <i class="bi bi-shield-lock display-4 text-muted"></i>
          <h5 class="card-title mt-3">Требуется авторизация</h5>
          <p class="card-text text-muted">
            Для доступа к этой странице необходимо войти как администратор.
          </p>
          <router-link to="/admin" class="btn btn-primary">
            <i class="bi bi-box-arrow-in-right"></i> Войти как администратор
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.admin-only-message {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
}

.card {
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>