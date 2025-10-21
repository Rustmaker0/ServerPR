<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import _ from 'lodash';


const publicTransports= ref([]);

const loading = ref(false);

const ToAdd = ref({});
const ToEdit = ref({});


async function fetchPublicTransports(){
	loading.value = true;
	const r = await axios.get("/api/publicTransports/")
	console.log(r.data);
	publicTransports.value = r.data;
	loading.value = false;
}

//Кнопки

async function onUpdate(){
	await axios.put(`/api/publicTransports/${ToEdit.value.id}/`, {
		...ToEdit.value});
	await fetchPublicTransports()
}

async function onAdd(){
	await axios.post("/api/publicTransports/", {
		...ToAdd.value});
	await fetchPublicTransports()
}

async function onDelete(Item){
	if (!confirm('Удалить эту запись?')) return;
	await axios.delete(`/api/publicTransports/${Item.id}/`)
	await fetchPublicTransports()
}

async function onEdit(Item){
	ToEdit.value = {...Item};
	await fetchPublicTransports()
}

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
				<button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdate()">Сохранить</button>
			</div>
			</div>
		</div>
		</div>

	<!-- Добавление -->
		<div class="p-2"> 
			<form @submit.prevent.stop="onAdd">
				<div class="row"> 
					<div class="col-auto"> 
						<div class="form-floating"> 
							<input type="text" class="form-control" 
							v-model="ToAdd.name"
							required/> 
							<label for="floatingInput">Название ТС</label> 
						</div> 
					</div> 
					<div class="col-auto"> 
						<button class="btn btn-primary">Добавить</button>
					</div>
				</div>
			</form>


		<div v-if="loading">Загрузка...</div>

	<!-- Таблица -->
		<div class="table-responsive">
  <table class="table align-middle">
    <thead>
      <tr>
        <th>ID</th>
        <th>Название</th>
        <th>Действия</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in publicTransports" :key="item.id">
        <td>{{ item.id }}</td>
        <td>{{ item.name }}</td>
        <td>
          <button class="btn btn-sm btn-success me-2"
		  		@click="onEdit(item)"
                data-bs-toggle="modal" 
                data-bs-target="#editModal">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-danger" @click="onDelete(item)">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
	</div>
	</div>
</template>

<style lang="scss" scoped>
.table-responsive {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 1rem;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 500;
  border-bottom: 2px solid #dee2e6;
}

.table td, .table th {
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
</style>
