<script setup>
import { computed, ref, reactive, onBeforeMount, watch } from 'vue';
import axios from 'axios';
import _ from 'lodash';
import AdminOnly from '@/components/AdminOnly.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)
const isAuthenticated = computed(() => authStore.isAuthenticated)

// Добавляем watch для отладки
watch(isAdmin, (newVal) => {
  console.log('isAdmin changed:', newVal)
})

watch(isAuthenticated, (newVal) => {
  console.log('isAuthenticated changed:', newVal)
})

const publicTransports = ref([]);
const loading = ref(false);

// Инициализируем с начальными значениями
const ToAdd = ref({
  name: ''
});
const ToEdit = ref({
  name: ''
});

// Фильтры
const showFilters = ref(false);
const filters = reactive({
  search: '',
  id: '',
  name: ''
});

// Отфильтрованные данные
const filteredPublicTransports = computed(() => {
  let filtered = publicTransports.value;

  // Быстрый поиск по всем полям
  if (filters.search) {
    const searchTerm = filters.search.toLowerCase();
    filtered = filtered.filter(item => {
      const id = item.id?.toString() || '';
      const name = item.name?.toLowerCase() || '';
      
      return id.includes(searchTerm) ||
             name.includes(searchTerm);
    });
  }

  // Фильтр по ID
  if (filters.id) {
    filtered = filtered.filter(item => 
      item.id?.toString().includes(filters.id)
    );
  }

  // Фильтр по названию
  if (filters.name) {
    filtered = filtered.filter(item => 
      item.name?.toLowerCase().includes(filters.name.toLowerCase())
    );
  }

  return filtered;
});

// Проверка активных фильтров
const hasActiveFilters = computed(() => {
  return Object.values(filters).some(value => value !== '');
});

async function fetchPublicTransports(){
  loading.value = true;
  try {
    const r = await axios.get("/api/publicTransports/")
    console.log(r.data);
    publicTransports.value = r.data;
  } catch (error) {
    console.error('Ошибка при загрузке типов транспорта:', error);
  } finally {
    loading.value = false;
  }
}

//Кнопки

async function onUpdate(){
  try {
    await axios.put(`/api/publicTransports/${ToEdit.value.id}/`, {
      ...ToEdit.value
    });
    await fetchPublicTransports();
    // Сбрасываем форму после успешного обновления
    ToEdit.value = { name: '' };
  } catch (error) {
    console.error('Ошибка при обновлении:', error);
    alert('Ошибка при обновлении записи');
  }
}

async function onAdd(){
  try {
    await axios.post("/api/publicTransports/", {
      ...ToAdd.value
    });
    await fetchPublicTransports();
    // Очистка формы после добавления
    ToAdd.value = { name: '' };
  } catch (error) {
    console.error('Ошибка при добавлении:', error);
    alert('Ошибка при добавлении записи');
  }
}

async function onDelete(Item){
  if (!confirm('Удалить эту запись?')) return;
  try {
    await axios.delete(`/api/publicTransports/${Item.id}/`)
    await fetchPublicTransports()
  } catch (error) {
    console.error('Ошибка при удалении:', error);
    alert('Ошибка при удалении записи');
  }
}

async function onEdit(Item){
  ToEdit.value = {...Item};
}

// Методы фильтрации
const applyFilters = () => {
  // Фильтрация происходит автоматически через computed свойство
};

const clearFilters = () => {
  Object.assign(filters, {
    search: '',
    id: '',
    name: ''
  });
};

// Загрузка (Get)
onBeforeMount(async() => {
  await fetchPublicTransports()
})
</script>

<template> 
  <div class="container-fluid">
    <!-- Модальное окно -->
    <div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">Редактировать</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row"> 
              <div class="col"> 
                <div class="form-floating"> 
                  <input type="text" class="form-control" v-model="ToEdit.name"/> 
                  <label for="floatingInput">Название ТС</label> 
                </div> 
              </div> 
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Назад</button>
            <button v-if="isAdmin" type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdate()">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Панель фильтров -->
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
                {{ filteredPublicTransports.length }}/{{ publicTransports.length }}
              </span>
            </button>
          </div>
          
          <div class="col-auto">
            <div class="input-group input-group-sm" style="width: 250px;">
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
            <div class="col-md-4">
              <label class="form-label small">ID транспорта</label>
              <input
                type="text"
                class="form-control form-control-sm"
                v-model="filters.id"
                placeholder="Введите ID..."
              >
            </div>
            <div class="col-md-4">
              <label class="form-label small">Название</label>
              <input
                type="text"
                class="form-control form-control-sm"
                v-model="filters.name"
                placeholder="Введите название..."
              >
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Добавление - показываем только админам -->
    <div v-if="isAdmin" class="p-2 mb-3"> 
      <div class="card">
        <div class="card-header bg-success text-white">
          <h6 class="mb-0"><i class="bi bi-plus-circle"></i> Добавить тип общественного транспорта</h6>
        </div>
        <div class="card-body">
          <form @submit.prevent.stop="onAdd">
            <div class="row align-items-end"> 
              <div class="col-auto"> 
                <div class="form-floating"> 
                  <input type="text" class="form-control" 
                  v-model="ToAdd.name"
                  required/> 
                  <label for="floatingInput">Название ТС</label> 
                </div> 
              </div> 
              <div class="col-auto"> 
                <button class="btn btn-primary">
                  <i class="bi bi-plus-circle"></i> Добавить
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-3">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>

    <!-- Информация о статусе авторизации -->
    <div v-if="!isAuthenticated" class="alert alert-info mb-3">
      <i class="bi bi-info-circle"></i> Вы вошли как гость. Для редактирования данных войдите как администратор.
    </div>

    <!-- Таблица -->
    <div class="card">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="bi bi-bus-front"></i> Типы общественного транспорта</h5>
        <div v-if="isAuthenticated" class="text-light small">
          <i class="bi bi-person-check"></i> Вы вошли как: {{ authStore.currentUser?.username }}
        </div>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Название</th>
                <th v-if="isAdmin">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredPublicTransports" :key="item.id">
                <td>{{ item.id }}</td>
                <td>{{ item.name }}</td>
                <td v-if="isAdmin">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary"
                      @click="onEdit(item)"
                      data-bs-toggle="modal" 
                      data-bs-target="#editModal"
                      title="Редактировать">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" @click="onDelete(item)" title="Удалить">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Сообщение при отсутствии данных -->
          <div v-if="filteredPublicTransports.length === 0" class="text-center text-muted py-4">
            <i class="bi bi-inbox display-6"></i>
            <p class="mt-2 mb-3">Типы общественного транспорта не найдены</p>
            <button v-if="hasActiveFilters" class="btn btn-sm btn-outline-primary" @click="clearFilters">
              <i class="bi bi-arrow-counterclockwise"></i> Очистить фильтры
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.table-responsive {
  border-radius: 8px;
  overflow: hidden;
}

.table th {
  background-color: #eeeeee;
  font-weight: 500;
  border-bottom: 2px solid #dee2e6;
  padding: 0.75rem;
}

.table td {
  white-space: nowrap;
  vertical-align: middle;
  padding: 0.75rem;
}

.text-muted {
  color: #6c757d;
  font-size: 0.9em;
}

.btn-sm {
  padding: 0.35rem 0.65rem;
}

.form-floating {
  min-width: 150px;
}

.badge {
  font-size: 0.7em;
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
  font-weight: 500;
}
</style>