<template>
  <div class="user-management-container">
    <div class="row">
      <!-- Список пользователей -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-people"></i> Список пользователей
            </h5>
            <button class="btn btn-light btn-sm" @click="fetchUsers">
              <i class="bi bi-arrow-clockwise"></i> Обновить
            </button>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>

            <div v-else>
              <div class="table-responsive">
                <table class="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Имя пользователя</th>
                      <th>Email</th>
                      <th>Имя</th>
                      <th>Фамилия</th>
                      <th>Статус</th>
                      <th>Дата регистрации</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id">
                      <td>{{ user.id }}</td>
                      <td>{{ user.username }}</td>
                      <td>{{ user.email }}</td>
                      <td>{{ user.first_name || '-' }}</td>
                      <td>{{ user.last_name || '-' }}</td>
                      <td>
                        <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-danger'">
                          {{ user.is_active ? 'Активен' : 'Неактивен' }}
                        </span>
                      </td>
                      <td>{{ formatDate(user.date_joined) }}</td>
                      <td>
                        <div class="btn-group btn-group-sm">
                          <button 
                            class="btn btn-outline-primary"
                            @click="editUser(user)"
                            title="Редактировать"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button 
                            class="btn btn-outline-danger"
                            @click="confirmDelete(user)"
                            title="Удалить"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="users.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-people display-4"></i>
                <p class="mt-2">Пользователи не найдены</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Формы управления -->
      <div class="col-md-4">
        <!-- Форма добавления/редактирования -->
        <div class="card mb-4">
          <div class="card-header bg-info text-white">
            <h6 class="mb-0">
              <i class="bi" :class="editingUser ? 'bi-pencil' : 'bi-person-plus'"></i>
              {{ editingUser ? 'Редактирование пользователя' : 'Добавление пользователя' }}
            </h6>
          </div>
          <div class="card-body">
            <form @submit.prevent="editingUser ? updateUser() : registerUser()">
              <div class="mb-2">
                <label class="form-label">Имя пользователя *</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="userForm.username"
                  required
                  :disabled="editingUser"
                >
              </div>

              <div class="mb-2">
                <label class="form-label">Email *</label>
                <input
                  type="email"
                  class="form-control"
                  v-model="userForm.email"
                  required
                >
              </div>

              <div class="mb-2">
                <label class="form-label">Имя</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="userForm.first_name"
                >
              </div>

              <div class="mb-2">
                <label class="form-label">Фамилия</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="userForm.last_name"
                >
              </div>

              <div v-if="!editingUser" class="mb-2">
                <label class="form-label">Пароль *</label>
                <input
                  type="password"
                  class="form-control"
                  v-model="userForm.password"
                  required
                  minlength="6"
                >
              </div>

              <div v-if="!editingUser" class="mb-3">
                <label class="form-label">Подтверждение пароля *</label>
                <input
                  type="password"
                  class="form-control"
                  v-model="userForm.password_confirm"
                  required
                >
              </div>

              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-success"
                  :disabled="formLoading"
                >
                  <span v-if="formLoading" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi" :class="editingUser ? 'bi-check' : 'bi-person-plus'"></i>
                  {{ editingUser ? 'Обновить' : 'Добавить' }}
                </button>
                
                <button 
                  v-if="editingUser"
                  type="button" 
                  class="btn btn-secondary"
                  @click="cancelEdit"
                >
                  <i class="bi bi-x"></i> Отмена
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Импорт из Excel -->
        <div class="card">
          <div class="card-header bg-warning text-dark">
            <h6 class="mb-0">
              <i class="bi bi-file-earmark-excel"></i> Импорт из Excel
            </h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Excel файл</label>
              <input
                type="file"
                class="form-control"
                ref="excelFileInput"
                accept=".xlsx,.xls"
                @change="onFileSelect"
              >
              <div class="form-text">
                <a href="#" @click.prevent="downloadTemplate" class="small">
                  <i class="bi bi-download"></i> Скачать шаблон
                </a>
              </div>
            </div>

            <button 
              class="btn btn-warning w-100"
              @click="importUsers"
              :disabled="!selectedFile || excelLoading"
            >
              <span v-if="excelLoading" class="spinner-border spinner-border-sm me-2"></span>
              <i class="bi bi-upload"></i> Импортировать
            </button>

            <!-- Результаты импорта -->
            <div v-if="importResult" class="mt-3">
              <div class="alert" :class="importResult.total_errors > 0 ? 'alert-warning' : 'alert-success'">
                <h6 class="alert-heading">Результаты импорта</h6>
                <p class="mb-1">Создано: {{ importResult.total_created }}</p>
                <p class="mb-1">Ошибок: {{ importResult.total_errors }}</p>
              </div>

              <div v-if="importResult.errors && importResult.errors.length > 0" class="mt-2">
                <button 
                  class="btn btn-sm btn-outline-danger w-100"
                  @click="showErrors = !showErrors"
                >
                  Показать ошибки
                </button>
                
                <div v-if="showErrors" class="mt-2">
                  <div 
                    v-for="(error, index) in importResult.errors" 
                    :key="index"
                    class="small text-danger mb-1"
                  >
                    {{ error }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal fade show" style="display: block; background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Подтверждение удаления</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            Вы уверены, что хотите удалить пользователя <strong>{{ userToDelete?.username }}</strong>?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">
              Отмена
            </button>
            <button type="button" class="btn btn-danger" @click="deleteUser" :disabled="deleteLoading">
              <span v-if="deleteLoading" class="spinner-border spinner-border-sm me-2"></span>
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

// Состояние
const users = ref([])
const loading = ref(false)
const formLoading = ref(false)
const excelLoading = ref(false)
const deleteLoading = ref(false)
const showDeleteModal = ref(false)
const showErrors = ref(false)
const editingUser = ref(null)
const selectedFile = ref(null)
const importResult = ref(null)
const userToDelete = ref(null)

// Формы
const userForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: ''
})

const excelFileInput = ref(null)

// Методы
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/user/')
    users.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке пользователей:', error)
    alert('Ошибка при загрузке пользователей')
  } finally {
    loading.value = false
  }
}

const registerUser = async () => {
  formLoading.value = true
  try {
    const response = await axios.post('/api/user/register/', userForm)
    alert('Пользователь успешно зарегистрирован')
    resetForm()
    fetchUsers()
  } catch (error) {
    handleFormError(error)
  } finally {
    formLoading.value = false
  }
}

const editUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    password: '',
    password_confirm: ''
  })
}

const updateUser = async () => {
  formLoading.value = true
  try {
    const response = await axios.put(`/api/user/${editingUser.value.id}/`, userForm)
    alert('Пользователь успешно обновлен')
    resetForm()
    fetchUsers()
  } catch (error) {
    handleFormError(error)
  } finally {
    formLoading.value = false
  }
}

const cancelEdit = () => {
  editingUser.value = null
  resetForm()
}

const confirmDelete = (user) => {
  userToDelete.value = user
  showDeleteModal.value = true
}

const deleteUser = async () => {
  deleteLoading.value = true
  try {
    await axios.delete(`/api/user/${userToDelete.value.id}/`)
    alert('Пользователь успешно удален')
    showDeleteModal.value = false
    userToDelete.value = null
    fetchUsers()
  } catch (error) {
    alert('Ошибка при удалении пользователя')
    console.error(error)
  } finally {
    deleteLoading.value = false
  }
}

const onFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    importResult.value = null
    showErrors.value = false
  }
}

const downloadTemplate = async () => {
  try {
    const response = await axios.get('/api/user/download-template/', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'user_import_template.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    alert('Ошибка при скачивании шаблона')
  }
}

const importUsers = async () => {
  if (!selectedFile.value) {
    alert('Выберите файл для импорта')
    return
  }

  excelLoading.value = true
  try {
    const formData = new FormData()
    formData.append('excel_file', selectedFile.value)

    const response = await axios.post('/api/user/import-users/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    importResult.value = response.data
    selectedFile.value = null
    if (excelFileInput.value) {
      excelFileInput.value.value = ''
    }

    if (response.data.total_errors === 0) {
      fetchUsers() // Обновляем список если нет ошибок
    }
  } catch (error) {
    if (error.response?.data) {
      importResult.value = error.response.data
    } else {
      alert('Ошибка при импорте пользователей')
    }
  } finally {
    excelLoading.value = false
  }
}

const resetForm = () => {
  Object.assign(userForm, {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: ''
  })
  editingUser.value = null
}

const handleFormError = (error) => {
  if (error.response?.data) {
    const errors = error.response.data
    if (typeof errors === 'object') {
      const errorMessages = Object.values(errors).flat().join(', ')
      alert(`Ошибка: ${errorMessages}`)
    } else {
      alert(`Ошибка: ${errors}`)
    }
  } else {
    alert('Произошла ошибка')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

// Хуки
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.table-responsive {
  max-height: 600px;
  overflow-y: auto;
}

.badge {
  font-size: 0.75em;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
}

.modal {
  backdrop-filter: blur(2px);
}

.alert {
  font-size: 0.9rem;
}

.form-text a {
  text-decoration: none;
}

.form-text a:hover {
  text-decoration: underline;
}
</style>