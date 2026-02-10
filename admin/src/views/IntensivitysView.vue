<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import axios from 'axios';
import _ from 'lodash';

const intensivitys = ref([]);
const transports = ref([]);
const loading = ref(false);

const ToAdd = ref({});
const ToEdit = ref({});

const transportsById = computed(() => {
	return _.keyBy(transports.value, x => x.id)
})

async function fetchIntensivitys(){
	loading.value = true;
	const r = await axios.get("/api/intensivitys/")
	console.log(r.data);
	intensivitys.value = r.data;
	loading.value = false;
}
async function fetchTransports(){
	loading.value = true;
	const r = await axios.get("/api/transports/")
	console.log(r.data);
	transports.value = r.data;
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
	await fetchIntensivitys()
  await fetchTransports()
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
            <th v-for="(header, index) in ['ID', 'Количество', 'Название ТС (id)', 'Измерение_id', 'Действия']" 
                :key="index">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in intensivitys" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.quanity}}</td>
            <td>{{ transportsById[item.transport]?.name }} ({{item.transport}})</td> 
            <td>{{ item.measuring }}</td>
            
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
