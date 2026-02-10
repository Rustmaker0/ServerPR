<template>
  <div class="user-management-container">
    <!-- Форма входа для суперпользователя -->
    <div v-if="!isAuthenticated" class="login-container">
      <div class="row justify-content-center">
        <div class="col-md-4">
          <div class="card">
            <div class="card-header bg-primary text-white text-center">
              <h5 class="mb-0">
                <i class="bi bi-shield-lock"></i> Вход для суперпользователя
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="login">
                <div class="mb-3">
                  <label class="form-label">Логин</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="loginForm.username"
                    required
                    placeholder="Введите логин"
                  >
                </div>
                <div class="mb-3">
                  <label class="form-label">Пароль</label>
                  <input
                    type="password"
                    class="form-control"
                    v-model="loginForm.password"
                    required
                    placeholder="Введите пароль"
                  >
                </div>
                <div v-if="loginError" class="alert alert-danger">
                  {{ loginError }}
                </div>
                <button 
                  type="submit" 
                  class="btn btn-primary w-100"
                  :disabled="loginLoading"
                >
                  <span v-if="loginLoading" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi bi-box-arrow-in-right"></i> Войти
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Основной интерфейс управления пользователями -->
    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>
          <i class="bi bi-people"></i> Управление пользователями
        </h4>
        <div>
          <span class="text-muted me-3">
            Вы вошли как: <strong>{{ currentUser.username }}</strong>
          </span>
          <button class="btn btn-outline-secondary btn-sm" @click="logout">
            <i class="bi bi-box-arrow-right"></i> Выйти
          </button>
        </div>
      </div>

      <!-- Компактная панель фильтров -->
      <div class="card mb-3">
        <div class="card-body py-2">
          <div class="row g-2 align-items-center">
            <div class="col-auto">
              <button 
                class="btn btn-sm" 
                :class="showFilters ? 'btn-primary' : 'btn-outline-primary'"
                @click="showFilters = !showFilters"
              >
                <i class="bi bi-funnel"></i> Фильтры
                <span v-if="hasActiveFilters" class="badge bg-light text-dark ms-1">
                  {{ filteredUsers.length }}/{{ users.length }}
                </span>
              </button>
            </div>
            
            <div class="col-auto">
              <div class="input-group input-group-sm" style="width: 200px;">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input
                  type="text"
                  class="form-control"
                  v-model="filters.search"
                  placeholder="Быстрый поиск..."
                  @input="applyFilters"
                >
              </div>
            </div>

            <div class="col"></div>

            <div class="col-auto">
              <div class="btn-group btn-group-sm">
                <button 
                  class="btn btn-outline-secondary"
                  @click="clearFilters"
                  :disabled="!hasActiveFilters"
                >
                  <i class="bi bi-x-circle"></i> Очистить
                </button>
                <button 
                  class="btn btn-primary"
                  @click="applyFilters"
                >
                  <i class="bi bi-check-lg"></i> Применить
                </button>
              </div>
            </div>
          </div>

          <!-- Расширенные фильтры -->
          <div v-if="showFilters" class="mt-3 pt-3 border-top">
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label small">ID пользователя</label>
                <input
                  type="text"
                  class="form-control form-control-sm"
                  v-model="filters.id"
                  placeholder="Введите ID..."
                >
              </div>
              <div class="col-md-3">
                <label class="form-label small">Имя пользователя</label>
                <input
                  type="text"
                  class="form-control form-control-sm"
                  v-model="filters.username"
                  placeholder="Введите username..."
                >
              </div>
              <div class="col-md-3">
                <label class="form-label small">Имя</label>
                <input
                  type="text"
                  class="form-control form-control-sm"
                  v-model="filters.first_name"
                  placeholder="Введите имя..."
                >
              </div>
              <div class="col-md-3">
                <label class="form-label small">Фамилия</label>
                <input
                  type="text"
                  class="form-control form-control-sm"
                  v-model="filters.last_name"
                  placeholder="Введите фамилию..."
                >
              </div>
              <div class="col-md-3">
                <label class="form-label small">Email</label>
                <input
                  type="text"
                  class="form-control form-control-sm"
                  v-model="filters.email"
                  placeholder="Введите email..."
                >
              </div>
              <div class="col-md-3">
                <label class="form-label small">Статус</label>
                <select class="form-select form-select-sm" v-model="filters.is_active">
                  <option value="">Все статусы</option>
                  <option value="true">Активен</option>
                  <option value="false">Неактивен</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label small">Роль</label>
                <select class="form-select form-select-sm" v-model="filters.is_superuser">
                  <option value="">Все роли</option>
                  <option value="true">Суперпользователь</option>
                  <option value="false">Пользователь</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Список пользователей -->
        <div class="col-md-9">
          <div class="card">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-people"></i> Список пользователей
                <span v-if="hasActiveFilters" class="badge bg-light text-dark ms-2">
                  {{ filteredUsers.length }} из {{ users.length }}
                </span>
              </h5>
              <div class="d-flex align-items-center gap-2">
                <span class="text-light small">
                  <i class="bi bi-info-circle"></i> Найдено: {{ filteredUsers.length }}
                </span>
              </div>
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
                        <th>Superuser</th>
                        <th>Дата регистрации</th>
                        <th>Действия</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="user in filteredUsers" :key="user.id">
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
                        <td>
                          <span class="badge" :class="user.is_superuser ? 'bg-warning' : 'bg-secondary'">
                            {{ user.is_superuser ? 'Да' : 'Нет' }}
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
                              v-if="!user.is_superuser"
                              class="btn" 
                              :class="user.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                              @click="toggleBlock(user)"
                              :title="user.is_active ? 'Заблокировать' : 'Разблокировать'"
                              :disabled="blockLoading === user.id"
                            >
                              <span v-if="blockLoading === user.id" class="spinner-border spinner-border-sm"></span>
                              <i v-else :class="user.is_active ? 'bi bi-lock' : 'bi bi-unlock'"></i>
                            </button>
                            <button 
                              class="btn btn-outline-danger"
                              @click="confirmDelete(user)"
                              title="Удалить"
                              :disabled="user.is_superuser"
                            >
                              <i class="bi bi-trash"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="filteredUsers.length === 0" class="text-center text-muted py-4">
                  <i class="bi bi-people display-4"></i>
                  <p class="mt-2">Пользователи не найдены</p>
                  <button v-if="hasActiveFilters" class="btn btn-sm btn-outline-primary" @click="clearFilters">
                    <i class="bi bi-arrow-counterclockwise"></i> Очистить фильтры
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Формы управления -->
        <div class="col-md-3">
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

                <!-- Чекбокс для суперпользователя -->
                <div class="mb-2" v-if="!editingUser">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      v-model="userForm.is_superuser"
                      id="is_superuser"
                    >
                    <label class="form-check-label" for="is_superuser">
                      Суперпользователь
                    </label>
                  </div>
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
      <!-- Модальное окно подтверждения удаления -->
<div v-if="showDeleteModal" class="modal fade show" style="display: block; background: rgba(0,0,0,0.5)">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Подтверждение удаления</h5>
        <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
      </div>
      <div class="modal-body">
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle"></i>
          <strong>Внимание! Это действие нельзя отменить.</strong>
        </div>
        
        <p>Вы уверены, что хотите удалить пользователя <strong>{{ userToDelete?.username }}</strong>?</p>
        
        <div class="alert alert-warning">
          <i class="bi bi-info-circle"></i>
          <strong>Важно:</strong> Все замеры, связанные с этим пользователем, также будут безвозвратно удалены.
        </div>

        <div v-if="userToDelete?.is_superuser" class="alert alert-warning mt-2">
          <i class="bi bi-shield-exclamation"></i> Внимание: это суперпользователь!
        </div>

        <div class="mt-3">
          <p class="text-muted small">
            <i class="bi bi-lightbulb"></i>
            Совет: Вместо удаления рассмотрите возможность 
            <strong>блокировки</strong> пользователя через кнопку 
            <i class="bi bi-lock"></i>. Это предотвратит вход в систему, 
            но сохранит все данные.
          </p>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">
          Отмена
        </button>
        <button 
          type="button" 
          class="btn btn-danger" 
          @click="deleteUser" 
          :disabled="deleteLoading || userToDelete?.is_superuser"
        >
          <span v-if="deleteLoading" class="spinner-border spinner-border-sm me-2"></span>
          <i class="bi bi-trash"></i> Удалить
        </button>
      </div>
    </div>
  </div>
</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Состояние аутентификации из store
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => authStore.currentUser)

const loginLoading = ref(false)
const loginError = ref('')

// Форма входа
const loginForm = reactive({
  username: '',
  password: ''
})

// Состояние управления пользователями
const users = ref([])
const filteredUsers = ref([])
const loading = ref(false)
const formLoading = ref(false)
const excelLoading = ref(false)
const deleteLoading = ref(false)
const blockLoading = ref(null)
const showDeleteModal = ref(false)
const showErrors = ref(false)
const editingUser = ref(null)
const selectedFile = ref(null)
const importResult = ref(null)
const userToDelete = ref(null)

// Фильтры
const showFilters = ref(false)
const filters = reactive({
  search: '',
  id: '',
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  is_active: '',
  is_superuser: ''
})

// Формы
const userForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  is_superuser: false
})

const excelFileInput = ref(null)

// Computed properties
const hasActiveFilters = computed(() => {
  return Object.values(filters).some(value => value !== '')
})

// Методы аутентификации
const login = async () => {
  loginLoading.value = true
  loginError.value = ''
  
  try {
    const response = await axios.post('/api/user/superuser-login/', loginForm, {
      withCredentials: true
    })
    
    if (response.data.user && response.data.user.is_superuser) {
      // Используем store для входа
      authStore.login(response.data.user, response.data.token)
      fetchUsers()
    } else {
      loginError.value = 'Доступ разрешен только суперпользователям'
    }
  } catch (error) {
    if (error.response?.data?.error) {
      loginError.value = error.response.data.error
    } else {
      loginError.value = 'Ошибка при входе в систему'
    }
  } finally {
    loginLoading.value = false
  }
}

const logout = async () => {
  try {
    await axios.post('/api/user/logout/', {}, {
      withCredentials: true
    })
  } catch (error) {
    console.error('Ошибка при выходе:', error)
  } finally {
    // Используем store для выхода
    authStore.logout()
  }
}

// Методы управления пользователями
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/user/', {
      withCredentials: true
    })
    users.value = response.data
    filteredUsers.value = response.data
  } catch (error) {
    if (error.response?.status === 403) {
      logout()
    } else {
      console.error('Ошибка при загрузке пользователей:', error)
      alert('Ошибка при загрузке пользователей')
    }
  } finally {
    loading.value = false
  }
}
const toggleBlock = async (user) => {
  blockLoading.value = user.id
  try {
    // Используем PATCH запрос для обновления только поля is_active
    const response = await axios.patch(`/api/user/${user.id}/`, {
      is_active: !user.is_active
    })
    
    const action = user.is_active ? 'заблокирован' : 'разблокирован'
    alert(`Пользователь ${user.username} успешно ${action}`)
    fetchUsers() // Обновляем список
  } catch (error) {
    if (error.response?.status === 403) {
      logout()
    } else {
      alert(error.response?.data?.error || 'Ошибка при изменении статуса пользователя')
    }
  } finally {
    blockLoading.value = null
  }
}
// Методы фильтрации
const applyFilters = () => {
  let filtered = users.value

  // Быстрый поиск по всем полям
  if (filters.search) {
    const searchTerm = filters.search.toLowerCase()
    filtered = filtered.filter(user => 
      user.id.toString().includes(searchTerm) ||
      user.username.toLowerCase().includes(searchTerm) ||
      (user.first_name && user.first_name.toLowerCase().includes(searchTerm)) ||
      (user.last_name && user.last_name.toLowerCase().includes(searchTerm)) ||
      user.email.toLowerCase().includes(searchTerm)
    )
  }

  // Точные фильтры
  if (filters.id) {
    filtered = filtered.filter(user => 
      user.id.toString().includes(filters.id)
    )
  }

  if (filters.username) {
    filtered = filtered.filter(user => 
      user.username.toLowerCase().includes(filters.username.toLowerCase())
    )
  }

  if (filters.first_name) {
    filtered = filtered.filter(user => 
      user.first_name && user.first_name.toLowerCase().includes(filters.first_name.toLowerCase())
    )
  }

  if (filters.last_name) {
    filtered = filtered.filter(user => 
      user.last_name && user.last_name.toLowerCase().includes(filters.last_name.toLowerCase())
    )
  }

  if (filters.email) {
    filtered = filtered.filter(user => 
      user.email.toLowerCase().includes(filters.email.toLowerCase())
    )
  }

  if (filters.is_active !== '') {
    filtered = filtered.filter(user => 
      user.is_active.toString() === filters.is_active
    )
  }

  if (filters.is_superuser !== '') {
    filtered = filtered.filter(user => 
      user.is_superuser.toString() === filters.is_superuser
    )
  }

  filteredUsers.value = filtered
}

const clearFilters = () => {
  Object.assign(filters, {
    search: '',
    id: '',
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    is_active: '',
    is_superuser: ''
  })
  filteredUsers.value = users.value
}

const registerUser = async () => {
  formLoading.value = true
  try {
    const response = await axios.post('/api/user/register/', userForm)
    alert('Пользователь успешно зарегистрирован')
    resetForm()
    fetchUsers()
  } catch (error) {
    if (error.response?.status === 403) {
      logout()
    } else {
      handleFormError(error)
    }
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
    password_confirm: '',
    is_superuser: user.is_superuser,
    is_active: user.is_active
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
    if (error.response?.status === 403) {
      logout()
    } else {
      handleFormError(error)
    }
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
    const response = await axios.delete(`/api/user/${userToDelete.value.id}/`)
    
    // Показываем дополнительное предупреждение о количестве удаленных замеров
    const warningMsg = response.data.warning ? 
      `\n\n${response.data.warning}` : 
      ''
    
    alert(response.data.message + warningMsg)
    showDeleteModal.value = false
    userToDelete.value = null
    fetchUsers()
  } catch (error) {
    if (error.response?.status === 403) {
      logout()
    } else {
      alert(error.response?.data?.error || 'Ошибка при удалении пользователя')
    }
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
      fetchUsers()
    }
  } catch (error) {
    if (error.response?.status === 403) {
      logout()
    } else if (error.response?.data) {
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
    password_confirm: '',
    is_superuser: false
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
  // Проверяем авторизацию через store
  authStore.checkAuth()
  if (authStore.isAuthenticated) {
    fetchUsers()
  }
})
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.login-container .row {
  width: 100%;
}

.login-container .card {
  border: none;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-container .card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.login-container .card-header {
  background: linear-gradient(135deg, #1b5ea1 0%, #3498db 100%) !important;
  border-bottom: none;
  padding: 25px 20px;
}

.login-container .card-header h5 {
  font-size: 1.3rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.login-container .card-header .bi-shield-lock {
  font-size: 1.5rem;
  margin-right: 10px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.login-container .card-body {
  padding: 30px;
  background: #ffffff;
}

.login-container .form-label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.login-container .form-control {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 12px 15px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.login-container .form-control:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
  background: #ffffff;
}

.login-container .form-control::placeholder {
  color: #6c757d;
  opacity: 0.7;
}

.login-container .btn-primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.login-container .btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9 0%, #1f639b 100%);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.login-container .btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.login-container .btn-primary .spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.login-container .alert-danger {
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  font-weight: 500;
  padding: 12px 15px;
  border-left: 4px solid #ff6b6b;
}

.login-container .bi-box-arrow-in-right {
  margin-right: 8px;
}

/* Анимации */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-container .card {
  animation: fadeInUp 0.6s ease-out;
}

/* Адаптивность */
@media (max-width: 768px) {
  .login-container {
    padding: 30px 15px;
    min-height: 70vh;
  }
  
  .login-container .card-body {
    padding: 20px;
  }
  
  .login-container .card-header {
    padding: 20px 15px;
  }
  
  .login-container .card-header h5 {
    font-size: 1.1rem;
  }
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