<!-- ReportComponent.vue -->
<template>
  <div>
    <!-- Кнопка для открытия отчётов -->
    <button 
      v-if="isAdmin" 
      class="btn btn-outline-secondary btn-sm" 
      @click="openReportPanel"
      :class="{ 'btn-primary': showReports }"
    >
      <i class="bi bi-file-code"></i> Отчёт
    </button>

    <!-- Модальное окно -->
    <Teleport to="body">
      <div v-if="showReports" class="report-modal" @click.self="closeReportPanel">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-bar-chart-line"></i> Панель отчётов
              <span class="badge bg-light text-dark ms-2">Данных: {{ dataForReports.length }}</span>
            </h5>
            <div class="header-actions">
              <div class="dropdown" ref="dropdownRef">
                <button class="btn btn-sm btn-light" @click="toggleDropdown">
                  <i class="bi bi-download"></i> Сохранить как
                </button>
                <div v-if="dropdownOpen" class="dropdown-menu show">
                  <button class="dropdown-item" @click="exportPNG">
                    <i class="bi bi-file-image"></i> PNG
                  </button>
                  <div class="dropdown-divider"></div>
                  <button class="dropdown-item" @click="exportPDF">
                    <i class="bi bi-file-pdf"></i> PDF
                  </button>
                </div>
              </div>
              <button class="btn-close btn-close-white" @click="closeReportPanel"></button>
            </div>
          </div>

          <!-- Индикатор загрузки -->
          <div v-if="exporting" class="export-overlay">
            <div class="spinner-border text-light" role="status">
              <span class="visually-hidden">Генерация...</span>
            </div>
            <div class="text-light mt-2">{{ exportStatus }}</div>
          </div>

          <div class="modal-body" ref="reportContent">
            <!-- Информация о фильтрах -->
            <div class="filter-info alert alert-info">
              <i class="bi bi-funnel"></i>
              <strong>Фильтры:</strong> {{ filterDescription }}
              <span class="float-end">{{ generationDate }}</span>
              <div class="filter-footer mt-2 pt-2 border-top">
              </div>
            </div>

            <!-- Вкладки -->
            <ul class="nav nav-tabs">
              <li class="nav-item">
                <button class="nav-link" :class="{ active: activeTab === 'intensity' }" 
                        @click="activeTab = 'intensity'">
                  <i class="bi bi-car-front"></i> Интенсивность
                </button>
              </li>
              <li class="nav-item">
                <button class="nav-link" :class="{ active: activeTab === 'transport' }" 
                        @click="activeTab = 'transport'">
                  <i class="bi bi-bus-front"></i> Общественный транспорт
                </button>
              </li>
              <li class="nav-item">
                <button class="nav-link" :class="{ active: activeTab === 'summary' }" 
                        @click="activeTab = 'summary'">
                  <i class="bi bi-table"></i> Сводка
                </button>
              </li>
            </ul>

            <!-- Контент -->
            <div class="tab-content">
              <!-- Интенсивность -->
              <div v-show="activeTab === 'intensity'" ref="intensityTab" class="report-section">
                <div class="metrics-grid">
                  <div class="metric-card">
                    <div class="metric-label">Всего ТС</div>
                    <div class="metric-value">{{ formatNumber(intensityData.total) }}</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Средняя интенсивность</div>
                    <div class="metric-value">{{ formatNumber(intensityData.avgIntensity) }} <small>ед/час</small></div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Макс. интенсивность</div>
                    <div class="metric-value">{{ formatNumber(intensityData.maxIntensity) }} <small>ед/час</small></div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Измерений</div>
                    <div class="metric-value">{{ intensityData.count }}</div>
                  </div>
                </div>

                <div class="charts-grid">
                  <div class="chart-card">
                    <div class="chart-header">Распределение по типам транспорта</div>
                    <div class="chart-body">
                      <canvas ref="transportTypeChart"></canvas>
                    </div>
                  </div>
                  <div class="chart-card">
                    <div class="chart-header">Интенсивность по часам</div>
                    <div class="chart-body">
                      <canvas ref="intensityHourChart"></canvas>
                    </div>
                  </div>
                </div>

                <div class="charts-grid" v-if="hasMultipleDays">
                  <div class="chart-card">
                    <div class="chart-header">Интенсивность по дням</div>
                    <div class="chart-body">
                      <canvas ref="intensityDayChart"></canvas>
                    </div>
                  </div>
                  <div class="chart-card">
                    <div class="chart-header">Интенсивность по дням недели</div>
                    <div class="chart-body">
                      <canvas ref="weekdayChart"></canvas>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Общественный транспорт -->
              <div v-show="activeTab === 'transport'" ref="transportTab" class="report-section">
                <div class="metrics-grid">
                  <div class="metric-card">
                    <div class="metric-label">Всего записей</div>
                    <div class="metric-value">{{ transportData.count }}</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Всего пассажиров</div>
                    <div class="metric-value">{{ formatNumber(transportData.totalPassengers) }}</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Средняя заполняемость</div>
                    <div class="metric-value">{{ transportData.avgOccupancy }}%</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Маршрутов</div>
                    <div class="metric-value">{{ transportData.uniqueRoutes }}</div>
                  </div>
                </div>

                <div class="charts-grid">
                  <div class="chart-card">
                    <div class="chart-header">Распределение по типам транспорта</div>
                    <div class="chart-body">
                      <canvas ref="publicTransportTypeChart"></canvas>
                    </div>
                  </div>
                  <div class="chart-card">
                    <div class="chart-header">Распределение заполняемости</div>
                    <div class="chart-body">
                      <canvas ref="occupancyChart"></canvas>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Сводка -->
              <div v-show="activeTab === 'summary'" ref="summaryTab" class="report-section">
                <div class="row">
                  <div class="col-md-6">
                    <div class="card">
                      <div class="card-header bg-success text-white">Интенсивность движения</div>
                      <div class="card-body">
                        <table class="table">
                          <tr><td>Всего ТС:</td><td class="text-end">{{ formatNumber(intensityData.total) }}</td></tr>
                          <tr><td>Средняя интенсивность:</td><td class="text-end">{{ formatNumber(intensityData.avgIntensity) }} ед/час</td></tr>
                          <tr><td>Макс. интенсивность:</td><td class="text-end">{{ formatNumber(intensityData.maxIntensity) }} ед/час</td></tr>
                          <tr><td>Количество измерений:</td><td class="text-end">{{ intensityData.count }}</td></tr>
                        </table>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card">
                      <div class="card-header bg-primary text-white">Общественный транспорт</div>
                      <div class="card-body">
                        <table class="table">
                          <tr><td>Всего записей:</td><td class="text-end">{{ transportData.count }}</td></tr>
                          <tr><td>Всего пассажиров:</td><td class="text-end">{{ formatNumber(transportData.totalPassengers) }}</td></tr>
                          <tr><td>Средняя заполняемость:</td><td class="text-end">{{ transportData.avgOccupancy }}%</td></tr>
                          <tr><td>Уникальных маршрутов:</td><td class="text-end">{{ transportData.uniqueRoutes }}</td></tr>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Chart from 'chart.js/auto';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const props = defineProps({
  measurements: { type: Array, required: true },
  filteredMeasurements: { type: Array, required: true },
  transports: { type: Array, default: () => [] },
  publicTransports: { type: Array, default: () => [] },
  hiddenMeasurements: { type: Array, default: () => [] },
  hiddenIntensivities: { type: Array, default: () => [] },
  hiddenPassengers: { type: Array, default: () => [] },
  filters: { type: Object, default: () => ({}) }
});

const emit = defineEmits(['close']);
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.isAdmin);

// Состояние
const showReports = ref(false);
const activeTab = ref('intensity');
const exporting = ref(false);
const exportStatus = ref('');
const generationDate = ref('');
const dropdownOpen = ref(false);
const dropdownRef = ref(null);
const charts = {};

// Refs для элементов
const reportContent = ref(null);
const intensityTab = ref(null);
const transportTab = ref(null);
const summaryTab = ref(null);
const transportTypeChart = ref(null);
const intensityHourChart = ref(null);
const intensityDayChart = ref(null);
const weekdayChart = ref(null);
const publicTransportTypeChart = ref(null);
const occupancyChart = ref(null);

// Данные для отчётов (сортировка от самой ранней к поздней)
const dataForReports = computed(() => {
  return [...props.filteredMeasurements]
    .filter(m => !props.hiddenMeasurements.includes(m.id))
    .sort((a, b) => {
      const dateA = new Date(a.measurment_time || 0);
      const dateB = new Date(b.measurment_time || 0);
      return dateA - dateB; // От ранней к поздней
    });
});

const hasData = computed(() => dataForReports.value.length > 0);

// Проверка на несколько дней
const hasMultipleDays = computed(() => {
  if (dataForReports.value.length < 2) return false;
  const dates = new Set();
  dataForReports.value.forEach(m => {
    if (m.measurment_time) {
      dates.add(new Date(m.measurment_time).toDateString());
    }
  });
  return dates.size > 1;
});

// Описание фильтров
const filterDescription = computed(() => {
  const parts = [];
  if (props.filters.dateRange?.start || props.filters.dateRange?.end) {
    parts.push(`Даты: ${props.filters.dateRange.start || '...'} — ${props.filters.dateRange.end || '...'}`);
  }
  if (props.filters.timeRange?.start || props.filters.timeRange?.end) {
    parts.push(`Время: ${props.filters.timeRange.start || '00:00'}-${props.filters.timeRange.end || '23:59'}`);
  }
  if (props.filters.daysOfWeek?.length) {
    const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    parts.push(`Дни: ${props.filters.daysOfWeek.map(d => days[parseInt(d)]).join(', ')}`);
  }
  return parts.length ? parts.join(' • ') : 'Все данные';
});

// Данные интенсивности
const intensityData = computed(() => {
  let totalVehicles = 0;
  let totalIntensity = 0;
  let maxIntensity = 0;
  let count = 0;

  dataForReports.value.forEach(m => {
    const children = (m.children || []).filter(c => 
      c.transport && !props.hiddenIntensivities.includes(c.id)
    );
    if (children.length) {
      count++;
      const sum = children.reduce((acc, c) => acc + (c.quanity || 0), 0);
      totalVehicles += sum;
      const hours = (m.measurment_duration || 0) / 3600;
      const intensity = hours > 0 ? sum / hours : sum;
      totalIntensity += intensity;
      maxIntensity = Math.max(maxIntensity, intensity);
    }
  });

  return {
    total: totalVehicles,
    avgIntensity: count ? totalIntensity / count : 0,
    maxIntensity,
    count
  };
});

// Данные общественного транспорта
const transportData = computed(() => {
  let count = 0;
  let totalPassengers = 0;
  let totalOccupancy = 0;
  const routes = new Set();

  dataForReports.value.forEach(m => {
    const children = (m.children || []).filter(c => 
      !c.transport && !props.hiddenPassengers.includes(c.id)
    );
    children.forEach(c => {
      count++;
      const entered = c.entering_people || 0;
      const left = c.leaving_people || 0;
      totalPassengers += entered + left;
      
      const capacity = (c.sitting_place || 0) + (c.standing_place || 0);
      if (capacity > 0) {
        const occupancy = ((entered + left) / capacity) * 100;
        totalOccupancy += Math.min(occupancy, 100);
      }
      
      if (c.transport_number) routes.add(c.transport_number);
    });
  });

  return {
    count,
    totalPassengers,
    avgOccupancy: count ? Math.round(totalOccupancy / count) : 0,
    uniqueRoutes: routes.size
  };
});

// Форматирование
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0';
  return new Intl.NumberFormat('ru-RU').format(Math.round(num * 100) / 100);
};

// Управление
const openReportPanel = () => {
  showReports.value = true;
  document.body.style.overflow = 'hidden';
  generationDate.value = new Date().toLocaleString('ru-RU');
  nextTick(() => {
    generateAllCharts();
  });
};

const closeReportPanel = () => {
  showReports.value = false;
  document.body.style.overflow = '';
  destroyCharts();
  emit('close');
};

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

// Закрытие dropdown при клике вне
onMounted(() => {
  const handleClickOutside = (e) => {
    if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
      dropdownOpen.value = false;
    }
  };
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  destroyCharts();
  document.body.style.overflow = '';
});

// Генерация всех графиков
const generateAllCharts = () => {
  destroyCharts();
  nextTick(() => {
    setTimeout(() => {
      generateTransportTypeChart();
      generateIntensityHourChart();
      if (hasMultipleDays.value) {
        generateIntensityDayChart();
        generateWeekdayChart();
      }
      generatePublicTransportChart();
      generateOccupancyChart();
    }, 100);
  });
};

const destroyCharts = () => {
  Object.values(charts).forEach(chart => {
    if (chart) {
      try { chart.destroy(); } catch (e) {}
    }
  });
};

// График по типам транспорта
const generateTransportTypeChart = () => {
  if (!transportTypeChart.value) return;
  
  const counts = {};
  dataForReports.value.forEach(m => {
    (m.children || []).forEach(c => {
      if (c.transport && !props.hiddenIntensivities.includes(c.id)) {
        const t = props.transports.find(t => t.id === c.transport);
        if (t) counts[t.name] = (counts[t.name] || 0) + (c.quanity || 0);
      }
    });
  });

  if (!Object.keys(counts).length) counts['Нет данных'] = 1;

  charts.transportType = new Chart(transportTypeChart.value, {
    type: 'doughnut',
    data: {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

// График по часам
const generateIntensityHourChart = () => {
  if (!intensityHourChart.value) return;
  
  const hourData = new Array(24).fill(0);
  const hourCount = new Array(24).fill(0);
  
  let startHour = 0, endHour = 23;
  if (props.filters.timeRange?.start) {
    startHour = parseInt(props.filters.timeRange.start.split(':')[0]);
  }
  if (props.filters.timeRange?.end) {
    endHour = parseInt(props.filters.timeRange.end.split(':')[0]);
  }

  dataForReports.value.forEach(m => {
    if (!m.measurment_time) return;
    const hour = new Date(m.measurment_time).getHours();
    if (hour < startHour || hour > endHour) return;
    
    const children = (m.children || []).filter(c => 
      c.transport && !props.hiddenIntensivities.includes(c.id)
    );
    const sum = children.reduce((acc, c) => acc + (c.quanity || 0), 0);
    const hours = (m.measurment_duration || 0) / 3600;
    const intensity = hours > 0 ? sum / hours : sum;
    
    hourData[hour] += intensity;
    hourCount[hour]++;
  });

  const labels = [];
  const data = [];
  for (let h = startHour; h <= endHour; h++) {
    labels.push(`${h}:00`);
    data.push(hourCount[h] ? hourData[h] / hourCount[h] : 0);
  }

  charts.intensityHour = new Chart(intensityHourChart.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Средняя интенсивность (ед/час)',
        data,
        borderColor: '#36A2EB',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
};

// График по дням
const generateIntensityDayChart = () => {
  if (!intensityDayChart.value) return;
  
  const dayData = {};
  dataForReports.value.forEach(m => {
    if (!m.measurment_time) return;
    const date = new Date(m.measurment_time).toLocaleDateString('ru-RU');
    
    const children = (m.children || []).filter(c => 
      c.transport && !props.hiddenIntensivities.includes(c.id)
    );
    const sum = children.reduce((acc, c) => acc + (c.quanity || 0), 0);
    const hours = (m.measurment_duration || 0) / 3600;
    const intensity = hours > 0 ? sum / hours : sum;
    
    if (!dayData[date]) dayData[date] = { sum: 0, count: 0 };
    dayData[date].sum += intensity;
    dayData[date].count++;
  });

  // Сортировка от ранней к поздней
  const sortedDates = Object.keys(dayData).sort((a, b) => {
    const [d1, m1, y1] = a.split('.').map(Number);
    const [d2, m2, y2] = b.split('.').map(Number);
    return new Date(y1, m1-1, d1) - new Date(y2, m2-1, d2);
  });

  charts.intensityDay = new Chart(intensityDayChart.value, {
    type: 'bar',
    data: {
      labels: sortedDates,
      datasets: [{
        label: 'Средняя интенсивность (ед/час)',
        data: sortedDates.map(date => dayData[date].sum / dayData[date].count),
        backgroundColor: '#FF6384'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
};

// График по дням недели
const generateWeekdayChart = () => {
  if (!weekdayChart.value) return;
  
  const dayNames = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'];
  const dayData = new Array(7).fill(0);
  const dayCount = new Array(7).fill(0);
  
  dataForReports.value.forEach(m => {
    if (!m.measurment_time) return;
    const day = new Date(m.measurment_time).getDay();
    
    const children = (m.children || []).filter(c => 
      c.transport && !props.hiddenIntensivities.includes(c.id)
    );
    const sum = children.reduce((acc, c) => acc + (c.quanity || 0), 0);
    const hours = (m.measurment_duration || 0) / 3600;
    const intensity = hours > 0 ? sum / hours : sum;
    
    dayData[day] += intensity;
    dayCount[day]++;
  });

  const labels = [];
  const data = [];
  for (let i = 0; i < 7; i++) {
    if (dayCount[i] > 0) {
      labels.push(dayNames[i]);
      data.push(dayData[i] / dayCount[i]);
    }
  }

  charts.weekday = new Chart(weekdayChart.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Средняя интенсивность (ед/час)',
        data,
        backgroundColor: '#36A2EB'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
};

// График общественного транспорта
const generatePublicTransportChart = () => {
  if (!publicTransportTypeChart.value) return;
  
  const counts = {};
  dataForReports.value.forEach(m => {
    (m.children || []).forEach(c => {
      if (!c.transport && !props.hiddenPassengers.includes(c.id)) {
        const t = props.publicTransports.find(t => t.id === c.public_transport);
        if (t) {
          counts[t.name] = (counts[t.name] || 0) + (c.entering_people || 0) + (c.leaving_people || 0);
        }
      }
    });
  });

  if (!Object.keys(counts).length) counts['Нет данных'] = 1;

  charts.publicTransport = new Chart(publicTransportTypeChart.value, {
    type: 'doughnut',
    data: {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

// График заполняемости
const generateOccupancyChart = () => {
  if (!occupancyChart.value) return;
  
  const ranges = [0, 0, 0, 0, 0];
  dataForReports.value.forEach(m => {
    (m.children || []).forEach(c => {
      if (!c.transport && !props.hiddenPassengers.includes(c.id)) {
        const capacity = (c.sitting_place || 0) + (c.standing_place || 0);
        if (capacity > 0) {
          const passengers = (c.entering_people || 0) + (c.leaving_people || 0);
          const occ = (passengers / capacity) * 100;
          if (occ < 20) ranges[0]++;
          else if (occ < 40) ranges[1]++;
          else if (occ < 60) ranges[2]++;
          else if (occ < 80) ranges[3]++;
          else ranges[4]++;
        }
      }
    });
  });

  if (ranges.every(v => v === 0)) ranges[0] = 1;

  charts.occupancy = new Chart(occupancyChart.value, {
    type: 'pie',
    data: {
      labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
      datasets: [{
        data: ranges,
        backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#fd7e14', '#dc3545']
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

// Экспорт PNG
const exportPNG = async () => {
  dropdownOpen.value = false;
  exporting.value = true;
  exportStatus.value = 'Генерация PNG...';
  
  try {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const element = activeTab.value === 'intensity' ? intensityTab.value : 
                   activeTab.value === 'transport' ? transportTab.value : summaryTab.value;
    
    if (!element) return;
    
    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false
    });
    
    const link = document.createElement('a');
    link.download = `report_${activeTab.value}_${new Date().toISOString().split('T')[0]}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    
  } catch (error) {
    console.error('Export error:', error);
    alert('Ошибка при экспорте');
  } finally {
    exporting.value = false;
  }
};

// Экспорт PDF
const exportPDF = async () => {
  dropdownOpen.value = false;
  exporting.value = true;
  exportStatus.value = 'Генерация PDF...';
  
  try {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const element = activeTab.value === 'intensity' ? intensityTab.value : 
                   activeTab.value === 'transport' ? transportTab.value : summaryTab.value;
    
    if (!element) return;
    
    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false
    });
    
    const imgData = canvas.toDataURL('image/png');
    
    const pdf = new jsPDF({
      orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
      unit: 'px'
    });
    
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
    const maxPageHeight = pdf.internal.pageSize.getHeight();
    
    if (pdfHeight <= maxPageHeight) {
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
    } else {
      let remainingHeight = canvas.height;
      let currentPosition = 0;
      let pageNumber = 1;
      
      while (remainingHeight > 0) {
        if (pageNumber > 1) {
          pdf.addPage();
        }
        
        const pageCanvasHeight = Math.min(
          remainingHeight,
          (maxPageHeight * canvas.width) / pdfWidth
        );
        
        const pageCanvas = document.createElement('canvas');
        pageCanvas.width = canvas.width;
        pageCanvas.height = pageCanvasHeight;
        
        const ctx = pageCanvas.getContext('2d');
        ctx.drawImage(
          canvas, 
          0, currentPosition, canvas.width, pageCanvasHeight,
          0, 0, canvas.width, pageCanvasHeight
        );
        
        const pageImgData = pageCanvas.toDataURL('image/png');
        const pagePdfHeight = (pageCanvasHeight * pdfWidth) / canvas.width;
        
        pdf.addImage(pageImgData, 'PNG', 0, 0, pdfWidth, pagePdfHeight);
        
        currentPosition += pageCanvasHeight;
        remainingHeight -= pageCanvasHeight;
        pageNumber++;
      }
    }
    
    pdf.save(`report_${activeTab.value}_${new Date().toISOString().split('T')[0]}.pdf`);
    
  } catch (error) {
    console.error('Export error:', error);
    alert('Ошибка при экспорте');
  } finally {
    exporting.value = false;
  }
};

// Следим за изменениями
watch(() => props.filteredMeasurements, () => {
  if (showReports.value) {
    generationDate.value = new Date().toLocaleString('ru-RU');
    generateAllCharts();
  }
}, { deep: true });

watch(activeTab, () => {
  if (showReports.value) {
    nextTick(() => {
      generateAllCharts();
    });
  }
});
</script>

<style scoped>
.report-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
}

.modal-container {
  position: relative;
  width: 95%;
  max-width: 1400px;
  height: 90vh;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 30px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 1rem;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  position: relative;
}

.export-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 1060;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  backdrop-filter: blur(3px);
}

.filter-info {
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  flex-shrink: 0;
  background-color: #e3f2fd;
  border-left: 4px solid #007bff;
}

.filter-footer {
  font-size: 0.85rem;
  color: #6c757d;
}

.nav-tabs {
  margin-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0;
}

.nav-link {
  cursor: pointer;
  color: #495057;
  border: none;
  background: none;
  padding: 0.5rem 1rem;
  margin-right: 0.25rem;
}

.nav-link.active {
  color: #007bff;
  border-bottom: 2px solid #007bff;
  font-weight: 500;
}

.tab-content {
  min-height: 200px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: #f8f9fa;
  padding: 1.25rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-label {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 600;
  color: #212529;
  line-height: 1.2;
}

.metric-value small {
  font-size: 0.9rem;
  font-weight: normal;
  color: #6c757d;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.chart-header {
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  font-weight: 500;
}

.chart-body {
  padding: 1rem;
  height: 300px;
  position: relative;
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1070;
  min-width: 180px;
  background: white;
  border: 1px solid rgba(0,0,0,0.15);
  border-radius: 4px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
  margin-top: 0.25rem;
  padding: 0.5rem 0;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item i {
  margin-right: 0.5rem;
  width: 1rem;
}

.dropdown-divider {
  height: 1px;
  background: #dee2e6;
  margin: 0.5rem 0;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}

.card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.card-header {
  padding: 0.75rem 1rem;
  font-weight: 500;
}

.card-body {
  padding: 1rem;
}

.btn-close-white {
  filter: brightness(0) invert(1);
}

/* Адаптивность */
@media (max-width: 768px) {
  .modal-container {
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>