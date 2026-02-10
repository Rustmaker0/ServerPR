<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import _ from 'lodash';

const peoplesInPublicsTransport = ref([]);
const publicTransports = ref([]);
const publicTransportsNumbers = ref([]);
const loading = ref(false);

const ToAdd = ref({});
const ToEdit = ref({});

const publicTransportsById = computed(() => {
	return _.keyBy(publicTransports.value, x => x.id)
})

const publicTransportsNumbersById = computed(() => {
	return _.keyBy(publicTransportsNumbers.value, x => x.id)
})

async function fetchPeoplesInPublicsTransport(){
	loading.value = true;
	const r = await axios.get("/api/peoplesInPublicsTransport/")
	console.log(r.data);
	peoplesInPublicsTransport.value = r.data;
	loading.value = false;
}
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
async function onDelete(Item){
	await axios.delete(`/api/intensivitys/${Item.id}/`)
  await fetchTransports()
	await fetchIntensivitys()
}

// Загрузка (Get)
onBeforeMount(async() => {
	await fetchPeoplesInPublicsTransport()
	await fetchPublicTransports()
	await fetchPublicTransportsNumbers()
	})

</script>

<template>
<div class="container-fluid">
  
	<!-- Добавление -->
	<div class="p-2"> 
			
		<div v-if="loading">Загрузка...</div>

    <!-- Таблица -->
    <div class="table-responsive">
      <table class="table align-middle">
        <thead>
          <tr>
            <th v-for="(header, index) in ['ID', 'Сидячих мест', 'Стоячих мест', 'Вошло человек', 'Вышло человек', 'Время замера', 'Название общественного ТС (id)', 'Измерение_id', 'Действия']" 
                :key="index">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in peoplesInPublicsTransport" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.sitting_place}}</td>
            <td>{{ item.standing_place}}</td>
            <td>{{ item.entering_people}}</td>
            <td>{{ item.leaving_people}}</td>
            <td>{{ item.time}}</td>
            <td>
    {{ publicTransportsNumbersById[item.public_transport_number]?.number }} 
    {{ publicTransportsById[publicTransportsNumbersById[item.public_transport_number]?.public_transport]?.name }} 
    ({{ item.public_transport_number }})
  </td>
            <td>{{ item.measuring}}</td>
            
            <td>
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
