<template>
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h3 class="text-center">Добавление пользователя</h3>
            </div>
            <div class="card-body">
              <form @submit.prevent="registerUser">
                <div class="mb-3">
                  <label for="username" class="form-label">Имя пользователя</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="formData.username"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">Пароль</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="formData.password"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="formData.email"
                    required
                  >
                </div>
                <!-- Если есть поля first_name и last_name, добавьте их -->
                <div class="mb-3">
                  <label for="first_name" class="form-label">Имя</label>
                  <input
                    type="text"
                    class="form-control"
                    id="first_name"
                    v-model="formData.first_name"
                  >
                </div>
                <div class="mb-3">
                  <label for="last_name" class="form-label">Фамилия</label>
                  <input
                    type="text"
                    class="form-control"
                    id="last_name"
                    v-model="formData.last_name"
                  >
                </div>
                <button type="submit" class="btn btn-primary w-100">Зарегистрироваться</button>
              </form>
              <div v-if="successMessage" class="alert alert-success mt-3">
                {{ successMessage }}
              </div>
              <div v-if="errorMessage" class="alert alert-danger mt-3">
                {{ errorMessage }}
              </div>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  
  const formData = ref({
      username: '',
      password: '',
      email: ''
  })
  
  const successMessage = ref('')
  const errorMessage = ref('')
  
  const registerUser = async () => {
    try {
        const response = await axios.post(
            'http://localhost:8000/api/register/',
            formData.value,
            {
                withCredentials: true,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            }
        )

        successMessage.value = 'Пользователь создан!'
        errorMessage.value = ''
        formData.value = {
            username: '',
            password: '',
            email: ''
        }
    } catch (error) {
        if (error.response && error.response.data) {
            const data = error.response.data;
            if (typeof data === 'object') {
                errorMessage.value = Object.entries(data)
                    .map(([field, messages]) => {
                        if (Array.isArray(messages)) {
                            return `${field}: ${messages.join(' ')}`
                        }
                        return `${field}: ${messages}`
                    })
                    .join('\n')
            } else {
                errorMessage.value = `Ошибка: ${data}`
            }
        } else {
            errorMessage.value = 'Ошибка подключения'
        }
    }
}
  
  // Функция для получения CSRF токена
  const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  </script>