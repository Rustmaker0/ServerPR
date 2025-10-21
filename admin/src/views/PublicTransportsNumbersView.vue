<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import _ from 'lodash';

//const measurings = ref([]);
//const transports = ref([]);
//const intensivitys = ref([]);
//const peoplesInPublicsTransport = ref([]);
const publicTransports = ref([]);
const publicTransportsNumbers = ref([]);

const loading = ref(false);

const ToAdd = ref({});
const ToEdit = ref({});

const publicTransportsById = computed(() => {
	return _.keyBy(publicTransports.value, x => x.id)
})
/*
async function fetchMeasurings(){
	loading.value = true;
	const r = await axios.get("/api/measurings/")
	console.log(r.data);
	measurings.value = r.data;
	loading.value = false;
}

async function fetchTransports(){
	loading.value = true;
	const r = await axios.get("/api/transports/")
	console.log(r.data);
	transports.value = r.data;
	loading.value = false;
}

async function fetchIntensivitys(){
	loading.value = true;
	const r = await axios.get("/api/intensivitys/")
	console.log(r.data);
	intensivitys.value = r.data;
	loading.value = false;
}

async function fetchPeoplesInPublicsTransport(){
	loading.value = true;
	const r = await axios.get("/api/peoplesInPublicsTransport/")
	console.log(r.data);
	peoplesInPublicsTransport.value = r.data;
	loading.value = false;
}
*/
async function fetchPublicTransports(){
	loading.value = true;
	const r = await axios.get("/api/publicTransports/")
	console.log(r.data);
	publicTransports.value = r.data;
	loading.value = false;
}

async function fetchPublicTransportsNumbers(){
	loading.value = true;
	const r = await axios.get("/api/publicTransportsNumbers/")
	console.log(r.data);
	publicTransportsNumbers.value = r.data;
	loading.value = false;
}

//Кнопки

async function onUpdate(){
	await axios.put(`/api/publicTransportsNumbers/${ToEdit.value.id}/`, {
		...ToEdit.value});
	await fetchPublicTransports()
	await fetchPublicTransportsNumbers()

}

async function onAdd(){
	await axios.post("/api/publicTransportsNumbers/", {
		...ToAdd.value});
	await fetchPublicTransports()
	await fetchPublicTransportsNumbers()
}

async function onDelete(Item){
	if (!confirm('Удалить эту запись?')) return;
	await axios.delete(`/api/publicTransportsNumbers/${Item.id}/`)
	await fetchPublicTransports()
	await fetchPublicTransportsNumbers()
}

async function onEdit(Item){
	ToEdit.value = {...Item};
	await fetchPublicTransports()
	await fetchPublicTransportsNumbers()
}

// Загрузка (Get)
onBeforeMount(async() => {
	//await fetchMeasurings()
	//await fetchTransports()
	//await fetchIntensivitys()
	//await fetchPeoplesInPublicsTransport()
	await fetchPublicTransports()
	await fetchPublicTransportsNumbers()
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
						<input type="text" class="form-control" v-model="ToEdit.number"/> 
						<label for="floatingInput">Номер ТС</label> 
					</div> 
				</div> 
				<div class="col-auto"> 
					<div class="form-floating"> 
						<select name="" id="" class="form-select" v-model="ToEdit.public_transport">
							<option :value="g.id" v-for="g in publicTransports">{{g.name}}</option>
						</select> 
						<label for="floatingInput" >Тип ТС</label> 
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
							v-model="ToAdd.number"
							required/> 
							<label for="floatingInput">Номер ТС</label> 
						</div> 
					</div> 
					<div class="col-auto"> 
						<div class="form-floating"> 
							<select class="form-select" v-model="ToAdd.public_transport" required>
								<option :value="g.id" v-for="g in publicTransports">{{g.name}}</option>
							</select> 
							<label for="floatingInput" >Тип ТС</label> 
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
        <th>Тип транспорта (id)</th>
        <th>Номер</th>
        <th>Действия</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in publicTransportsNumbers" :key="item.id">
        <td>
          {{ publicTransportsById[item.public_transport]?.name }} 
          <small class="text-muted">({{ item.public_transport }})</small>
        </td>
        <td>{{ item.number }}</td>
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
