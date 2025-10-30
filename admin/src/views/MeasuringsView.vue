<template>
  <div class="container-fluid">
    <div class="p-2">
      <!-- Переключение между таблицей и картой -->
      <div class="mb-3 d-flex justify-content-between align-items-center">
        <div>
          <button 
            v-if="!showMap"
            class="btn btn-info"
            @click="showAllRoutesMap"
          >
            <i class="bi bi-map"></i> Показать карту всех путей
          </button>
          <button 
            v-else
            class="btn btn-secondary"
            @click="hideMap"
          >
            <i class="bi bi-list"></i> Показать таблицу
          </button>
        </div>
        
        <!-- Кнопка фильтров -->
        <button 
          v-if="!showMap"
          class="btn btn-primary"
          @click="showFilters = !showFilters"
        >
          <i class="bi bi-funnel"></i> Фильтры
          <span v-if="filteredMeasurements.length !== measurements.length" class="badge bg-light text-dark ms-1">
            {{ filteredMeasurements.length }}/{{ measurements.length }}
          </span>
        </button>
      </div>

      <!-- Блок выбранной области -->
      <div v-if="filters.mapSelection && !showMap" class="mb-3">
        <div class="card border-primary">
          <div class="card-body py-2">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-title mb-1 text-primary">
                  <i class="bi bi-geo-alt-fill"></i> Выбранная область на карте
                </h6>
                <div class="small text-muted">
                  Центр: [{{ filters.mapSelection.lat.toFixed(6) }}, {{ filters.mapSelection.lng.toFixed(6) }}] 
                  • Радиус: {{ filters.mapSelection.radius }} метров
                  • Измерений в области: {{ getMeasurementsInSelection().length }}
                </div>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-outline-danger btn-sm" @click="clearMapSelection">
                  <i class="bi bi-x-circle"></i> Сбросить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Карта всех путей -->
      <div v-if="showMap && mapMode === 'allRoutes'" class="mb-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi bi-geo-alt"></i> Карта всех путей измерений
              <span v-if="tempMapSelection" class="badge bg-warning ms-2">Область выбрана</span>
            </h5>
            <div class="d-flex align-items-center gap-3">
              <!-- Управление радиусом выбора -->
              <div class="radius-control">
                <label class="form-label mb-0 me-2">
                  <i class="bi bi-bullseye"></i> Радиус:
                </label>
                <div class="input-group input-group-sm" style="width: 200px;">
                  <input 
                    type="range" 
                    class="form-range" 
                    min="10" 
                    max="300" 
                    step="10"
                    v-model="selectionRadius"
                    @change="updateTempSelectionRadius"
                  >
                  <span class="input-group-text">{{ selectionRadius }} м</span>
                </div>
              </div>
              
              <button 
                v-if="tempMapSelection"
                class="btn btn-sm btn-success"
                @click="applyTempSelection"
              >
                <i class="bi bi-check-lg"></i> Применить выбор
              </button>
              
              <button 
                v-if="tempMapSelection"
                class="btn btn-sm btn-outline-secondary"
                @click="clearTempSelection"
              >
                <i class="bi bi-x-circle"></i> Отмена
              </button>
            </div>
          </div>
          
          <div class="card-body">
            <div class="alert alert-info mb-3">
              <i class="bi bi-info-circle"></i> 
              <strong>Инструкция:</strong> Кликните на карте для выбора области. Настройте радиус и нажмите "Применить выбор".
            </div>
            
            <div id="map" class="map-container"></div>
            
            <div class="mt-3">
              <div class="row">
                <div class="col-md-6">
                  <strong>Статистика:</strong>
                  <div class="small text-muted mt-1">
                    Всего измерений: {{ measurements.length }}<br>
                    С координатами: {{ measurements.filter(m => hasCoordinates(m)).length }}<br>
                    <template v-if="tempMapSelection">
                      В выбранной области: {{ getTempSelectionMeasurements().length }}
                    </template>
                    <template v-else>
                      В выбранной области: {{ getMeasurementsInSelection().length }}
                    </template>
                  </div>
                </div>
                <div class="col-md-6 text-end">
                  <small class="text-muted">
                    <template v-if="tempMapSelection">
                      Центр: [{{ tempMapSelection.lat.toFixed(6) }}, {{ tempMapSelection.lng.toFixed(6) }}]<br>
                      Радиус: {{ tempMapSelection.radius }} м
                    </template>
                    <template v-else-if="filters.mapSelection">
                      Центр: [{{ filters.mapSelection.lat.toFixed(6) }}, {{ filters.mapSelection.lng.toFixed(6) }}]<br>
                      Радиус: {{ filters.mapSelection.radius }} м
                    </template>
                    <template v-else>
                      Выберите область на карте
                    </template>
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Карта одного маршрута -->
      <div v-if="showMap && mapMode === 'singleRoute'" class="mb-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi bi-geo-alt"></i> Маршрут движения
              <span class="text-muted">
                - Измерение {{ selectedMeasuring?.id }}
              </span>
            </h5>
            <div class="route-stats">
              <span class="badge bg-success me-2">Старт</span>
              <span class="badge bg-warning me-2">Позиция</span>
              <span class="badge bg-danger">Конец</span>
            </div>
          </div>
          <div class="card-body p-0">
            <div id="map" class="map-container"></div>
          </div>
          <div class="card-footer">
            <div class="row">
              <div class="col-md-6">
                <strong>Координаты маршрута:</strong>
                <div class="small text-muted mt-1">
                  <div v-if="routeCoordinates.length > 0">
                    <strong>Старт:</strong> [{{ routeCoordinates[0][0].toFixed(6) }}, {{ routeCoordinates[0][1].toFixed(6) }}]
                  </div>
                  <div v-if="routeCoordinates.length > 1">
                    <strong>Позиция:</strong> [{{ routeCoordinates[1][0].toFixed(6) }}, {{ routeCoordinates[1][1].toFixed(6) }}]
                  </div>
                  <div v-if="routeCoordinates.length > 2">
                    <strong>Конец:</strong> [{{ routeCoordinates[2][0].toFixed(6) }}, {{ routeCoordinates[2][1].toFixed(6) }}]
                  </div>
                </div>
              </div>
              <div class="col-md-6 text-end">
                <small class="text-muted">
                  Всего точек: {{ routeCoordinates.length }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Панель фильтров -->
      <div v-if="showFilters && !showMap" class="mb-3">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi bi-funnel"></i> Фильтры данных
            </h5>
            <div>
              <button class="btn btn-sm btn-outline-secondary me-2" @click="resetFilters">
                <i class="bi bi-arrow-counterclockwise"></i> Сбросить все
              </button>
              <button class="btn btn-sm btn-primary" @click="applyFilters">
                <i class="bi bi-check-circle"></i> Применить
              </button>
            </div>
          </div>
          <div class="card-body">
            <!-- Уведомление о фильтре по карте -->
            <div v-if="filters.mapSelection" class="alert alert-warning d-flex justify-content-between align-items-center mb-3">
              <div>
                <i class="bi bi-geo-alt"></i> Активен фильтр по карте: 
                радиус {{ filters.mapSelection.radius }}м вокруг 
                [{{ filters.mapSelection.lat.toFixed(6) }}, {{ filters.mapSelection.lng.toFixed(6) }}]
              </div>
              <button class="btn btn-sm btn-outline-danger" @click="clearMapSelection">
                <i class="bi bi-x-circle"></i> Очистить
              </button>
            </div>

            <div class="row g-3">
              <!-- Базовые фильтры -->
              <div class="col-md-4">
                <h6 class="border-bottom pb-2"><i class="bi bi-search"></i> Основные фильтры</h6>
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small">ID измерения</label>
                    <input
                      type="text"
                      class="form-control"
                      placeholder="Начните вводить ID..."
                      v-model="filters.measuringId"
                    >
                  </div>
                  <div class="col-12">
                    <label class="form-label small">Пользователь</label>
                    <select class="form-select" v-model="filters.user">
                      <option value="">Все пользователи</option>
                      <option value="is:null">Без пользователя</option>
                      <option v-for="user in uniqueUsers" :key="user.id" :value="user.displayName">
                        {{ user.displayName }}
                      </option>
                    </select>
                  </div>
                  <div class="col-12">
                    <label class="form-label small">Тип данных</label>
                    <select class="form-select" v-model="filters.type">
                      <option value="all">Все типы</option>
                      <option value="intensivity">Интенсивность</option>
                      <option value="passengers">Пассажиры</option>
                    </select>
                  </div>
                  <div class="col-12">
                    <label class="form-label small">Адрес</label>
                    <select class="form-select" v-model="filters.streetName">
                      <option value="">Все адреса</option>
                      <option v-for="street in uniqueStreets" :key="street" :value="street">{{ street }}</option>
                    </select>
                  </div>
                  <!-- ФИЛЬТР УДАЛЕНИЯ -->
                  <div class="col-12">
                    <label class="form-label small">Статус удаления</label>
                    <select class="form-select" v-model="filters.isDeleted">
                      <option value="all">Все записи</option>
                      <option value="deleted">Только удаленные</option>
                      <option value="active">Только активные</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Фильтры по времени -->
              <div class="col-md-4">
                <h6 class="border-bottom pb-2"><i class="bi bi-clock"></i> Время измерения</h6>
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small">Дата от</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      v-model="filters.dateRange.start"
                    >
                  </div>
                  <div class="col-12">
                    <label class="form-label small">Дата до</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      v-model="filters.dateRange.end"
                    >
                  </div>
                  <div class="col-12">
                    <label class="form-label small">Время от</label>
                    <input 
                      type="time" 
                      class="form-control" 
                      v-model="filters.timeRange.start"
                    >
                  </div>
                  <div class="col-12">
                    <label class="form-label small">Время до</label>
                    <input 
                      type="time" 
                      class="form-control" 
                      v-model="filters.timeRange.end"
                    >
                  </div>
                </div>
              </div>

              <!-- Фильтры по типам транспорта -->
              <div class="col-md-4">
                <h6 class="border-bottom pb-2"><i class="bi bi-bus-front"></i> Типы транспорта</h6>
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small">Дни недели</label>
                    <div class="checkbox-group">
                      <div v-for="day in daysOfWeekOptions" :key="day.value" class="form-check">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          :value="day.value"
                          :id="`day-${day.value}`"
                          :checked="filters.daysOfWeek.includes(day.value)"
                          @change="toggleDayOfWeek(day.value)"
                        >
                        <label class="form-check-label small" :for="`day-${day.value}`">
                          {{ day.label }}
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-12" v-if="filters.type !== 'passengers'">
                    <label class="form-label small">Интенсивность движения</label>
                    <div class="checkbox-group">
                      <div v-for="transport in uniqueTransportTypes" :key="transport.id" class="form-check">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          :value="transport.id"
                          :id="`transport-${transport.id}`"
                          :checked="filters.transportTypes.includes(transport.id.toString())"
                          @change="toggleTransportType(transport.id)"
                        >
                        <label class="form-check-label small" :for="`transport-${transport.id}`">
                          {{ transport.name }}
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-12" v-if="filters.type !== 'intensivity'">
                    <label class="form-label small">Пассажиропоток</label>
                    <div class="checkbox-group">
                      <div v-for="transport in uniquePassengerTransportTypes" :key="transport.id" class="form-check">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          :value="transport.id"
                          :id="`passenger-${transport.id}`"
                          :checked="filters.passengerTransportTypes.includes(transport.id.toString())"
                          @change="togglePassengerTransportType(transport.id)"
                        >
                        <label class="form-check-label small" :for="`passenger-${transport.id}`">
                          {{ transport.name }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Состояния загрузки -->
      <div v-if="loading" class="text-center py-3">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <div class="mt-2">Загрузка данных...</div>
      </div>
      <div v-else-if="filteredMeasurements.length === 0 && !showMap" class="alert alert-info text-center">
        <i class="bi bi-info-circle"></i> Ничего не найдено
      </div>

      <!-- Таблица -->
      <div v-if="!showMap && filteredMeasurements.length > 0" class="table-container">
        <!-- Группы измерений -->
        <div v-for="(measuring, index) in filteredMeasurements" 
            :key="measuring.id" 
            class="measuring-card mb-4"
            :id="`measuring-${measuring.id}`">
          <!-- Карточка измерения -->
          <div class="card measuring-main-card">
            <div class="card-header bg-primary text-white">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h5 class="card-title mb-0">
                    <i class="bi bi-clipboard-data"></i> Измерение №{{ measuring.id }}
                    <!-- ЗНАЧОК УДАЛЕНИЯ -->
                    <span v-if="measuring.is_deleated == 1" class="ms-2 text-warning" title="Удалено">
                      <i class="bi bi-trash-fill"></i>
                    </span>
                  </h5>
                </div>
                <div class="d-flex gap-2">
                  <button 
                    class="btn btn-light btn-sm"
                    @click="showSingleRouteMap(measuring)"
                    :disabled="!hasCoordinates(measuring)"
                    :title="hasCoordinates(measuring) ? 'Показать маршрут на карте' : 'Нет координат для отображения'"
                  >
                    <i class="bi bi-map"></i> Карта
                  </button>
                  <button class="btn btn-danger btn-sm" @click="onDelete(measuring.id)">
                    <i class="bi bi-trash"></i> Удалить все
                  </button>
                </div>
              </div>
            </div>
            
            <div class="card-body">
              <!-- Основная информация -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <div class="info-item">
                    <span class="info-label"><i class="bi bi-person"></i> Пользователь:</span>
                    <span class="info-value">{{ getUserDisplayName(measuring.user) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label"><i class="bi bi-arrows-h"></i> Ширина дороги:</span>
                    <span class="info-value">{{ measuring.road_width }} м</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label"><i class="bi bi-geo-alt"></i> Адрес:</span>
                    <span class="info-value">{{ measuring.street_name || 'Не указан' }}</span>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="info-item">
                    <span class="info-label"><i class="bi bi-clock"></i> Время измерения:</span>
                    <span class="info-value">{{ formatDateTime(measuring.measurment_time) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label"><i class="bi bi-stopwatch"></i> Длительность:</span>
                    <span class="info-value">{{ measuring.measurment_duration }} мин</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label"><i class="bi bi-geo"></i> Координаты:</span>
                    <span class="info-value" :class="hasCoordinates(measuring) ? 'text-success' : 'text-warning'">
                      {{ hasCoordinates(measuring) ? '✓ Доступны' : '✗ Отсутствуют' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Координаты -->
              <div v-if="hasCoordinates(measuring)" class="coordinates-section-compact mb-3">
                <h6 class="section-title"><i class="bi bi-signpost"></i> Координаты маршрута</h6>
                <div class="compact-coordinates-row">
                  <div v-if="measuring.latitude_start && measuring.longtiude_start" class="compact-coordinate-item start">
                    <span class="compact-coordinate-label">Старт:</span>
                    <span class="compact-coordinate-value">{{ parseFloat(measuring.latitude_start).toFixed(6) }}, {{ parseFloat(measuring.longtiude_start).toFixed(6) }}</span>
                  </div>
                  <div v-if="measuring.latitude_position && measuring.longtiude_position" class="compact-coordinate-item position">
                    <span class="compact-coordinate-label">Позиция:</span>
                    <span class="compact-coordinate-value">{{ parseFloat(measuring.latitude_position).toFixed(6) }}, {{ parseFloat(measuring.longtiude_position).toFixed(6) }}</span>
                  </div>
                  <div v-if="measuring.latitude_end && measuring.longtiude_end" class="compact-coordinate-item end">
                    <span class="compact-coordinate-label">Конец:</span>
                    <span class="compact-coordinate-value">{{ parseFloat(measuring.latitude_end).toFixed(6) }}, {{ parseFloat(measuring.longtiude_end).toFixed(6) }}</span>
                  </div>
                </div>
              </div>

              <!-- Фото дороги -->
              <div v-if="measuring.road_photo" class="photo-section mb-3">
                <h6 class="section-title"><i class="bi bi-camera"></i> Фото дороги</h6>
                <img :src="measuring.road_photo" class="road-photo img-thumbnail" alt="Фото дороги">
              </div>

              <!-- Дочерние записи -->
              <div class="children-section">
                <!-- Интенсивность движения -->
                <div v-if="measuring.children.filter(c => c.transport).length > 0" class="intensivity-section mb-3">
                  <h6 class="section-title intensivity-title">
                    <i class="bi bi-car-front"></i> Интенсивность движения
                    <span class="badge bg-success ms-2">{{ measuring.children.filter(c => c.transport).length }}</span>
                  </h6>
                  <div class="compact-intensivity-grid">
                    <div v-for="child in measuring.children.filter(c => c.transport)" :key="child.id" class="compact-intensivity-item">
                      <div class="intensivity-transport">
                        <i class="bi bi-bus-front"></i>
                        {{ transportsById[child.transport]?.name }}
                      </div>
                      <div class="intensivity-quantity">
                        <span class="quantity-number">{{ child.quanity }}</span>
                        <small class="quantity-label">шт.</small>
                      </div>
                      <button class="btn btn-sm btn-outline-danger btn-delete-compact" @click="onDeleteSingle(child)" title="Удалить">
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Пассажиропоток -->
                <div v-if="measuring.children.filter(c => !c.transport).length > 0" class="passengers-section">
                  <h6 class="section-title passengers-title">
                    <i class="bi bi-people"></i> Пассажиропоток
                    <span class="badge bg-primary ms-2">{{ measuring.children.filter(c => !c.transport).length }}</span>
                  </h6>
                  <div class="row g-2">
                    <div v-for="child in measuring.children.filter(c => !c.transport)" :key="child.id" class="col-md-6 col-lg-4">
                      <div class="child-card passenger-card">
                        <div class="child-content">
                          <div class="transport-info-compact">
                            <i class="bi bi-bus-front"></i>
                            {{ publicTransportsById[publicTransportsNumbersById[child.public_transport_number]?.public_transport]?.name }} 
                            {{ publicTransportsNumbersById[child.public_transport_number]?.number }}
                            <button class="btn btn-sm btn-outline-danger btn-delete" @click="onDeleteSingle(child)" >
                              <i class="bi bi-trash"></i>
                            </button>
                          </div>
                          <div class="time-info-compact">
                            <i class="bi bi-clock"></i>
                            {{ formatTime(child.time) }}
                          </div>
                          <div class="intensivity-data-column">
                            <div class="data-row">
                              <span class="data-label">Сидячих:</span>
                              <span class="data-value">{{ child.sitting_place }}</span>
                            </div>
                            <div class="data-row">
                              <span class="data-label">Стоячих:</span>
                              <span class="data-value">{{ child.standing_place }}</span>
                            </div>
                            <div class="data-row text-success">
                              <span class="data-label"><i class="bi bi-box-arrow-in-down"></i> Вошло:</span>
                              <span class="data-value">{{ child.entering_people }}</span>
                            </div>
                            <div class="data-row text-danger">
                              <span class="data-label"><i class="bi bi-box-arrow-up"></i> Вышло:</span>
                              <span class="data-value">{{ child.leaving_people }}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeMount, computed, nextTick } from 'vue';
import axios from 'axios';
import _ from 'lodash';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const measurements = ref([]);
const filteredMeasurements = ref([]);
const loading = ref(false);
const transports = ref([]);
const publicTransports = ref([]);
const publicTransportsNumbers = ref([]);
const users = ref([]);
const showMap = ref(false);
const mapMode = ref('allRoutes'); // 'allRoutes' или 'singleRoute'
const selectedMeasuring = ref(null);
const routeCoordinates = ref([]);
const map = ref(null);
const scrollToMeasuringId = ref(null);
const showFilters = ref(false);
const selectionRadius = ref(100); // радиус выбора в метрах (10-300)
const tempMapSelection = ref(null); // временный выбор на карте
const selectionCircle = ref(null);
const selectionMarker = ref(null);
const routePolylines = ref([]);
const routeMarkers = ref([]);

// Координаты Иркутска
const IRKUTSK_CENTER = [52.294, 104.268];

// Фильтры
const filters = ref({
  measuringId: '',
  user: '',
  type: 'all',
  dateRange: {
    start: '',
    end: ''
  },
  timeRange: {
    start: '',
    end: ''
  },
  daysOfWeek: [],
  streetName: '',
  transportTypes: [],
  passengerTransportTypes: [],
  mapSelection: null, // { lat, lng, radius }
  isDeleted: 'all' // 'all', 'deleted', 'active'
});

const transportsById = computed(() => _.keyBy(transports.value, x => x.id));
const publicTransportsById = computed(() => _.keyBy(publicTransports.value, x => x.id));
const publicTransportsNumbersById = computed(() => _.keyBy(publicTransportsNumbers.value, x => x.id));
const usersById = computed(() => _.keyBy(users.value, x => x.id));

// Функция для получения имени пользователя по ID
const getUserDisplayName = (userId) => {
  if (!userId && userId !== 0) return 'Не указан';
  
  const user = usersById.value[userId];
  
  if (user) {
    return user.username || 
           user.name || 
           user.email || 
           user.full_name || 
           user.display_name || 
           `Пользователь ${userId}`;
  }
  
  return `Пользователь ${userId}`;
};

// Уникальные значения для фильтров
const uniqueUsers = computed(() => {
  const userMap = new Map();
  
  measurements.value.forEach(measuring => {
    if (measuring.user !== null && measuring.user !== undefined) {
      const user = usersById.value[measuring.user];
      const displayName = getUserDisplayName(measuring.user);
      
      if (!userMap.has(measuring.user)) {
        userMap.set(measuring.user, {
          id: measuring.user,
          displayName: displayName,
          searchText: displayName.toLowerCase()
        });
      }
    }
  });
  
  const userList = Array.from(userMap.values());
  return userList.sort((a, b) => a.displayName.localeCompare(b.displayName));
});

const uniqueStreets = computed(() => {
  return _.uniq(measurements.value.map(m => m.street_name).filter(Boolean));
});

const uniqueTransportTypes = computed(() => {
  return transports.value.map(t => ({ id: t.id, name: t.name }));
});

const uniquePassengerTransportTypes = computed(() => {
  return publicTransports.value.map(t => ({ id: t.id, name: t.name }));
});

// Дни недели
const daysOfWeekOptions = [
  { value: '0', label: 'Воскресенье' },
  { value: '1', label: 'Понедельник' },
  { value: '2', label: 'Вторник' },
  { value: '3', label: 'Среда' },
  { value: '4', label: 'Четверг' },
  { value: '5', label: 'Пятница' },
  { value: '6', label: 'Суббота' }
];

// Функция для получения дня недели из даты
const getDayOfWeek = (dateString) => {
  const date = new Date(dateString);
  return date.getDay().toString();
};

const formatDateTime = (dateString) => {
  if (!dateString) return 'Не указано';
  try {
    const date = new Date(dateString);
    // Используем UTC компоненты для избежания автоматической корректировки
    return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')} ${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}:${String(date.getUTCSeconds()).padStart(2, '0')}`;
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Ошибка даты';
  }
};

const formatTime = (dateString) => {
  if (!dateString) return 'Не указано';
  try {
    const date = new Date(dateString);
    return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}:${String(date.getUTCSeconds()).padStart(2, '0')}`;
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'Ошибка времени';
  }
};

const hasCoordinates = (measuring) => {
  return (measuring.latitude_start && measuring.longtiude_start) ||
         (measuring.latitude_position && measuring.longtiude_position) ||
         (measuring.latitude_end && measuring.longtiude_end);
};

// Функция для расчета расстояния между двумя точками в метрах (формула гаверсинусов)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371000; // радиус Земли в метрах
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

// Функция для проверки, находится ли измерение в радиусе выбора
const isMeasuringInRadius = (measuring, centerLat, centerLng, radius) => {
  const points = [];
  
  if (measuring.latitude_start && measuring.longtiude_start) {
    points.push({
      lat: parseFloat(measuring.latitude_start),
      lng: parseFloat(measuring.longtiude_start)
    });
  }
  
  if (measuring.latitude_position && measuring.longtiude_position) {
    points.push({
      lat: parseFloat(measuring.latitude_position),
      lng: parseFloat(measuring.longtiude_position)
    });
  }
  
  if (measuring.latitude_end && measuring.longtiude_end) {
    points.push({
      lat: parseFloat(measuring.latitude_end),
      lng: parseFloat(measuring.longtiude_end)
    });
  }
  
  return points.some(point => 
    calculateDistance(centerLat, centerLng, point.lat, point.lng) <= radius
  );
};

// Получение измерений в выбранной области
const getMeasurementsInSelection = () => {
  if (!filters.value.mapSelection) {
    return measurements.value;
  }
  
  const { lat, lng, radius } = filters.value.mapSelection;
  return measurements.value.filter(measuring => 
    isMeasuringInRadius(measuring, lat, lng, radius)
  );
};

// Получение измерений во временной выбранной области
const getTempSelectionMeasurements = () => {
  if (!tempMapSelection.value) {
    return [];
  }
  
  const { lat, lng, radius } = tempMapSelection.value;
  return measurements.value.filter(measuring => 
    isMeasuringInRadius(measuring, lat, lng, radius)
  );
};

// Основная функция применения фильтров
const applyFilters = () => {
  let filtered = measurements.value;

  // Фильтр по статусу удаления
  if (filters.value.isDeleted !== 'all') {
    filtered = filtered.filter(measuring => {
      if (filters.value.isDeleted === 'deleted') {
        return measuring.is_deleated == 1;
      } else if (filters.value.isDeleted === 'active') {
        return measuring.is_deleated != 1;
      }
      return true;
    });
  }

  // Фильтр по карте
  if (filters.value.mapSelection) {
    filtered = getMeasurementsInSelection();
  }

  // Остальные фильтры
  filtered = filtered.filter(measuring => {
    // Фильтр по ID измерения
    if (filters.value.measuringId && !measuring.id.toString().includes(filters.value.measuringId)) {
      return false;
    }
    
    // Фильтр по пользователю
    if (filters.value.user) {
      const userFilter = filters.value.user.toLowerCase().trim();
      
      if (userFilter === 'is:null') {
        if (measuring.user !== null) return false;
      } else {
        const userDisplayName = getUserDisplayName(measuring.user);
        if (!userDisplayName.toLowerCase().includes(userFilter)) {
          return false;
        }
      }
    }
    
    // Остальные фильтры
    if (filters.value.dateRange.start || filters.value.dateRange.end) {
      const measuringDate = new Date(measuring.measurment_time);
      const startDate = filters.value.dateRange.start ? new Date(filters.value.dateRange.start) : null;
      const endDate = filters.value.dateRange.end ? new Date(filters.value.dateRange.end + 'T23:59:59') : null;
      
      if (startDate && measuringDate < startDate) return false;
      if (endDate && measuringDate > endDate) return false;
    }
    
    if (filters.value.timeRange.start || filters.value.timeRange.end) {
      const measuringTime = new Date(measuring.measurment_time);
      const hours = measuringTime.getHours();
      const minutes = measuringTime.getMinutes();
      const totalMinutes = hours * 60 + minutes;
      
      const startTime = filters.value.timeRange.start ? timeToMinutes(filters.value.timeRange.start) : 0;
      const endTime = filters.value.timeRange.end ? timeToMinutes(filters.value.timeRange.end) : 1439;
      
      if (totalMinutes < startTime || totalMinutes > endTime) return false;
    }
    
    if (filters.value.daysOfWeek.length > 0) {
      const dayOfWeek = getDayOfWeek(measuring.measurment_time);
      if (!filters.value.daysOfWeek.includes(dayOfWeek)) {
        return false;
      }
    }
    
    if (filters.value.streetName && measuring.street_name) {
      if (!measuring.street_name.toLowerCase().includes(filters.value.streetName.toLowerCase())) {
        return false;
      }
    }
    
    if (filters.value.type !== 'all') {
      const hasRequestedChildren = measuring.children.some(child => 
        filters.value.type === 'intensivity' ? child.transport : !child.transport
      );
      if (!hasRequestedChildren) return false;
    }
    
    const children = measuring.children || [];
    
    if (filters.value.transportTypes.length > 0 && filters.value.type !== 'passengers') {
      const hasMatchingTransport = children.some(child => 
        child.transport && filters.value.transportTypes.includes(child.transport.toString())
      );
      if (!hasMatchingTransport) return false;
    }
    
    if (filters.value.passengerTransportTypes.length > 0 && filters.value.type !== 'intensivity') {
      const hasMatchingPassengerTransport = children.some(child => {
        if (!child.transport) {
          const ptNumber = publicTransportsNumbersById.value[child.public_transport_number];
          if (ptNumber && ptNumber.public_transport) {
            return filters.value.passengerTransportTypes.includes(ptNumber.public_transport.toString());
          }
        }
        return false;
      });
      if (!hasMatchingPassengerTransport) return false;
    }
    
    return true;
  });

  filteredMeasurements.value = filtered;
};

// Вспомогательная функция для преобразования времени в минуты
const timeToMinutes = (timeStr) => {
  const [hours, minutes] = timeStr.split(':').map(Number);
  return hours * 60 + minutes;
};

const resetFilters = () => {
  filters.value = {
    measuringId: '',
    user: '',
    type: 'all',
    dateRange: { start: '', end: '' },
    timeRange: { start: '', end: '' },
    daysOfWeek: [],
    streetName: '',
    transportTypes: [],
    passengerTransportTypes: [],
    mapSelection: null,
    isDeleted: 'all'
  };
  clearMapSelection();
  filteredMeasurements.value = [...measurements.value];
};

// Функции для работы с чекбоксами
const toggleDayOfWeek = (dayValue) => {
  const index = filters.value.daysOfWeek.indexOf(dayValue);
  if (index > -1) {
    filters.value.daysOfWeek.splice(index, 1);
  } else {
    filters.value.daysOfWeek.push(dayValue);
  }
};

const toggleTransportType = (transportId) => {
  const idStr = transportId.toString();
  const index = filters.value.transportTypes.indexOf(idStr);
  if (index > -1) {
    filters.value.transportTypes.splice(index, 1);
  } else {
    filters.value.transportTypes.push(idStr);
  }
};

const togglePassengerTransportType = (transportId) => {
  const idStr = transportId.toString();
  const index = filters.value.passengerTransportTypes.indexOf(idStr);
  if (index > -1) {
    filters.value.passengerTransportTypes.splice(index, 1);
  } else {
    filters.value.passengerTransportTypes.push(idStr);
  }
};

// Получение статистики по отфильтрованным данным
const filteredStats = computed(() => {
  const stats = {
    totalMeasurements: filteredMeasurements.value.length,
    totalIntensivity: 0,
    totalPassengers: 0,
    withCoordinates: 0
  };
  
  filteredMeasurements.value.forEach(measuring => {
    stats.totalIntensivity += measuring.children.filter(c => c.transport).length;
    stats.totalPassengers += measuring.children.filter(c => !c.transport).length;
    
    if (hasCoordinates(measuring)) {
      stats.withCoordinates++;
    }
  });
  
  return stats;
});

// Функции для работы с картой
const initMap = () => {
  const mapContainer = document.getElementById('map');
  if (!mapContainer) return;

  if (map.value) {
    map.value.remove();
    map.value = null;
  }

  // Устанавливаем центр на Иркутск
  map.value = L.map(mapContainer).setView(IRKUTSK_CENTER, 13);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: ''
  }).addTo(map.value);

  if (mapMode.value === 'allRoutes') {
    drawAllRoutes();
    // Добавляем обработчик клика по карте
    map.value.on('click', onMapClick);
  } else if (mapMode.value === 'singleRoute') {
    drawSingleRoute(routeCoordinates.value, selectedMeasuring.value);
  }
};

// Отрисовка всех путей измерений
const drawAllRoutes = () => {
  if (!map.value) return;

  // Очищаем предыдущие маршруты и маркеры
  clearRoutesAndMarkers();

  // Отрисовываем пути для всех измерений с координатами
  measurements.value.forEach(measuring => {
    if (hasCoordinates(measuring)) {
      const coordinates = getCoordinatesFromMeasuring(measuring);
      if (coordinates.length >= 2) {
        const isInSelection = tempMapSelection.value ? 
          isMeasuringInRadius(measuring, tempMapSelection.value.lat, tempMapSelection.value.lng, tempMapSelection.value.radius) :
          (filters.value.mapSelection ? 
            isMeasuringInRadius(measuring, filters.value.mapSelection.lat, filters.value.mapSelection.lng, filters.value.mapSelection.radius) : 
            false);
        
        // Создаем полилинию с более заметными параметрами
        const polyline = L.polyline(coordinates, {
          color: isInSelection ? '#ff4444' : '#0066cc',
          weight: isInSelection ? 6 : 4,
          opacity: isInSelection ? 0.9 : 0.7,
          lineJoin: 'round',
          lineCap: 'round'
        }).addTo(map.value);

        routePolylines.value.push(polyline);

        // Добавляем маркеры для точек начала, позиции и конца
        coordinates.forEach((coord, index) => {
          let markerColor, markerText;
          
          if (index === 0) {
            markerColor = '#28a745'; // зеленый для старта
            markerText = 'Старт';
          } else if (index === 1 && coordinates.length === 3) {
            markerColor = '#fd7e14'; // оранжевый для позиции
            markerText = 'Позиция';
          } else if (index === coordinates.length - 1) {
            markerColor = '#dc3545'; // красный для конца
            markerText = 'Конец';
          } else {
            markerColor = '#007bff'; // синий для промежуточных
            markerText = 'Точка';
          }

          const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `
              <div style="background-color: ${markerColor}; 
                          width: 20px; 
                          height: 20px; 
                          border-radius: 50%; 
                          border: 3px solid white;
                          display: flex; 
                          align-items: center; 
                          justify-content: center;
                          color: white;
                          font-weight: bold;
                          font-size: 10px;
                          box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                ${index + 1}
              </div>
              <div style="position: absolute; top: 100%; left: 50%; transform: translateX(-50%); 
                          white-space: nowrap; background: white; padding: 2px 6px; 
                          border-radius: 3px; font-size: 10px; margin-top: 4px; 
                          box-shadow: 0 1px 3px rgba(0,0,0,0.3); color: #333; font-weight: 500;">
                ${markerText}
              </div>
            `,
            iconSize: [30, 40],
            iconAnchor: [15, 40]
          });

          const marker = L.marker(coord, { icon: customIcon })
            .addTo(map.value)
            .bindPopup(`
              <strong>${markerText}</strong><br>
              Измерение ${measuring.id}<br>
              Точка ${index + 1}<br>
              Ш: ${coord[0].toFixed(6)}<br>
              Д: ${coord[1].toFixed(6)}<br>
              <button onclick="window.vm.showSingleRouteMapById(${measuring.id})" class="btn btn-sm btn-primary mt-1">
                Показать детально
              </button>
            `);

          routeMarkers.value.push(marker);
        });

        // Добавляем всплывающую подсказку на линию
        polyline.bindPopup(`
          <strong>Измерение ${measuring.id}</strong><br>
          Пользователь: ${getUserDisplayName(measuring.user)}<br>
          Время: ${formatDateTime(measuring.measurment_time)}<br>
          Точек: ${coordinates.length}<br>
          <button onclick="window.vm.showSingleRouteMapById(${measuring.id})" class="btn btn-sm btn-primary mt-1">
            Показать детально
          </button>
        `);
      }
    }
  });

  // Если есть выделение на карте, рисуем круг
  if (tempMapSelection.value) {
    const { lat, lng, radius } = tempMapSelection.value;
    drawSelectionCircle(lat, lng, radius);
  } else if (filters.value.mapSelection) {
    const { lat, lng, radius } = filters.value.mapSelection;
    drawSelectionCircle(lat, lng, radius);
  }
};

// Очистка маршрутов и маркеров
const clearRoutesAndMarkers = () => {
  routePolylines.value.forEach(polyline => {
    if (map.value && polyline) {
      map.value.removeLayer(polyline);
    }
  });
  routePolylines.value = [];

  routeMarkers.value.forEach(marker => {
    if (map.value && marker) {
      map.value.removeLayer(marker);
    }
  });
  routeMarkers.value = [];
};

// Обработчик клика по карте
const onMapClick = (e) => {
  const { lat, lng } = e.latlng;
  
  // Устанавливаем временный выбор
  tempMapSelection.value = {
    lat,
    lng,
    radius: selectionRadius.value
  };
  
  // Рисуем круг выбора
  drawSelectionCircle(lat, lng, selectionRadius.value);
  
  // Перерисовываем маршруты с новыми цветами
  redrawRoutesWithSelection();
};

// Перерисовка маршрутов с учетом выбора
const redrawRoutesWithSelection = () => {
  if (mapMode.value === 'allRoutes') {
    drawAllRoutes();
  }
};

// Отрисовка круга выбора
const drawSelectionCircle = (lat, lng, radius) => {
  // Удаляем предыдущий круг и маркер
  if (selectionCircle.value) {
    map.value.removeLayer(selectionCircle.value);
  }
  if (selectionMarker.value) {
    map.value.removeLayer(selectionMarker.value);
  }

  // Рисуем круг
  selectionCircle.value = L.circle([lat, lng], {
    color: '#dc3545',
    fillColor: '#dc3545',
    fillOpacity: 0.1,
    weight: 2,
    radius: radius
  }).addTo(map.value);

  // Добавляем маркер в центр
  selectionMarker.value = L.marker([lat, lng]).addTo(map.value)
    .bindPopup(`
      <strong>Центр выбора</strong><br>
      Широта: ${lat.toFixed(6)}<br>
      Долгота: ${lng.toFixed(6)}<br>
      Радиус: ${radius} м<br>
      Измерений в области: ${tempMapSelection.value ? getTempSelectionMeasurements().length : getMeasurementsInSelection().length}
    `);

  // Центрируем карту на выбранной точке
  map.value.setView([lat, lng], map.value.getZoom());
};

// Обновление радиуса временного выбора
const updateTempSelectionRadius = () => {
  if (tempMapSelection.value) {
    tempMapSelection.value.radius = selectionRadius.value;
    drawSelectionCircle(
      tempMapSelection.value.lat,
      tempMapSelection.value.lng,
      selectionRadius.value
    );
    redrawRoutesWithSelection();
  }
};

// Применение временного выбора
const applyTempSelection = () => {
  if (tempMapSelection.value) {
    filters.value.mapSelection = { ...tempMapSelection.value };
    tempMapSelection.value = null;
    applyFilters();
    hideMap();
  }
};

// Очистка временного выбора
const clearTempSelection = () => {
  tempMapSelection.value = null;
  if (selectionCircle.value) {
    map.value.removeLayer(selectionCircle.value);
    selectionCircle.value = null;
  }
  if (selectionMarker.value) {
    map.value.removeLayer(selectionMarker.value);
    selectionMarker.value = null;
  }
  redrawRoutesWithSelection();
};

// Очистка выбора на карте
const clearMapSelection = () => {
  filters.value.mapSelection = null;
  tempMapSelection.value = null;
  
  if (selectionCircle.value) {
    map.value.removeLayer(selectionCircle.value);
    selectionCircle.value = null;
  }
  if (selectionMarker.value) {
    map.value.removeLayer(selectionMarker.value);
    selectionMarker.value = null;
  }
  
  applyFilters();
  if (map.value && mapMode.value === 'allRoutes') {
    redrawRoutesWithSelection();
  }
};

const calculateBearing = (start, end) => {
  const startLat = start[0] * Math.PI / 180;
  const startLng = start[1] * Math.PI / 180;
  const endLat = end[0] * Math.PI / 180;
  const endLng = end[1] * Math.PI / 180;

  const y = Math.sin(endLng - startLng) * Math.cos(endLat);
  const x = Math.cos(startLat) * Math.sin(endLat) -
          Math.sin(startLat) * Math.cos(endLat) * Math.cos(endLng - startLng);
  
  const bearing = Math.atan2(y, x) * 180 / Math.PI;
  return (bearing + 360) % 360;
};

const getCoordinatesFromMeasuring = (measuring) => {
  const coordinates = [];

  if (measuring.latitude_start && measuring.longtiude_start) {
    coordinates.push([
      parseFloat(measuring.latitude_start),
      parseFloat(measuring.longtiude_start)
    ]);
  }

  if (measuring.latitude_position && measuring.longtiude_position) {
    coordinates.push([
      parseFloat(measuring.latitude_position),
      parseFloat(measuring.longtiude_position)
    ]);
  }

  if (measuring.latitude_end && measuring.longtiude_end) {
    coordinates.push([
      parseFloat(measuring.latitude_end),
      parseFloat(measuring.longtiude_end)
    ]);
  }

  return coordinates;
};

// Показать карту всех путей
const showAllRoutesMap = () => {
  showMap.value = true;
  mapMode.value = 'allRoutes';
  selectedMeasuring.value = null;
  
  nextTick(() => {
    setTimeout(() => {
      initMap();
    }, 50);
  });
};

// Показать карту одного маршрута
const showSingleRouteMap = (measuring) => {
  selectedMeasuring.value = measuring;
  scrollToMeasuringId.value = measuring.id;
  mapMode.value = 'singleRoute';
  
  const coordinates = getCoordinatesFromMeasuring(measuring);
  
  if (coordinates.length === 0) {
    alert('Нет координат для отображения на карте');
    return;
  }

  routeCoordinates.value = coordinates;
  showMap.value = true;
  
  nextTick(() => {
    setTimeout(() => {
      initMap();
    }, 50);
  });
};

// Отрисовка одного маршрута (для детального просмотра)
const drawSingleRoute = (coordinates, measuring) => {
  if (!map.value) return;

  // Очищаем карту
  map.value.eachLayer((layer) => {
    if (layer instanceof L.Polyline || layer instanceof L.Marker || (layer instanceof L.Control && !(layer instanceof L.TileLayer))) {
      map.value.removeLayer(layer);
    }
  });

  if (coordinates.length < 2) return;

  const polyline = L.polyline(coordinates, {
    color: 'red',
    weight: 6,
    opacity: 0.8,
    lineJoin: 'round'
  }).addTo(map.value);

  coordinates.forEach((coord, index) => {
    let markerColor = 'blue';
    let markerText = '';
    
    if (index === 0) {
      markerColor = 'green';
      markerText = 'Старт';
    } else if (index === 1 && coordinates.length === 3) {
      markerColor = 'orange';
      markerText = 'Позиция';
    } else if (index === coordinates.length - 1) {
      markerColor = 'red';
      markerText = 'Конец';
    }

    const customIcon = L.divIcon({
      className: 'custom-marker',
      html: `
        <div style="background-color: ${markerColor}; 
                    width: 24px; 
                    height: 24px; 
                    border-radius: 50%; 
                    border: 3px solid white;
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
          ${index + 1}
        </div>
        <div style="position: absolute; top: 100%; left: 50%; transform: translateX(-50%); 
                    white-space: nowrap; background: white; padding: 2px 6px; 
                    border-radius: 3px; font-size: 11px; margin-top: 4px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.3);">
          ${markerText}
        </div>
      `,
      iconSize: [30, 40],
      iconAnchor: [15, 40]
    });

    L.marker(coord, { icon: customIcon })
      .addTo(map.value)
      .bindPopup(`
        <strong>${markerText}</strong><br>
        Точка ${index + 1}<br>
        Ш: ${coord[0].toFixed(6)}<br>
        Д: ${coord[1].toFixed(6)}
      `);
  });

  if (coordinates.length >= 2) {
    const startPoint = coordinates[coordinates.length - 2];
    const endPoint = coordinates[coordinates.length - 1];
    
    const arrowIcon = L.divIcon({
      className: 'arrow-icon',
      html: '➤',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });

    L.marker(endPoint, { 
      icon: arrowIcon,
      rotationAngle: calculateBearing(startPoint, endPoint)
    }).addTo(map.value);
  }

  map.value.fitBounds(polyline.getBounds());

  const routeInfo = L.control({ position: 'bottomleft' });
  routeInfo.onAdd = function() {
    const div = L.DomUtil.create('div', 'route-info');
    div.innerHTML = `
      <div style="background: white; padding: 8px; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
        <strong>Маршрут измерения ${measuring.id}</strong><br>
        <small>Точек: ${coordinates.length}</small>
      </div>
    `;
    return div;
  };
  routeInfo.addTo(map.value);
};

const hideMap = () => {
  showMap.value = false;
  mapMode.value = 'allRoutes';
  
  if (map.value) {
    map.value.remove();
    map.value = null;
  }
  
  if (scrollToMeasuringId.value) {
    nextTick(() => {
      setTimeout(() => {
        scrollToMeasuring(scrollToMeasuringId.value);
      }, 100);
    });
  }
  
  selectedMeasuring.value = null;
  routeCoordinates.value = [];
  clearTempSelection();
};

const scrollToMeasuring = (measuringId) => {
  const element = document.getElementById(`measuring-${measuringId}`);
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start'
    });
    
    element.classList.add('highlighted');
    setTimeout(() => {
      element.classList.remove('highlighted');
    }, 2000);
  }
};

// Упрощенные функции загрузки данных
async function fetchUsers() {
  try {
    const response = await axios.get('/api/auth_user/');
    
    if (response.data) {
      if (Array.isArray(response.data)) {
        users.value = response.data;
      } else if (response.data.results) {
        users.value = response.data.results;
      } else if (response.data.users) {
        users.value = response.data.users;
      } else {
        users.value = [];
      }
      return;
    }
  } catch (error) {
    users.value = [];
  }
}

async function fetchTransports(){
  const r = await axios.get("/api/transports/");
  transports.value = r.data;
}

async function fetchPublicTransports(){
  const r = await axios.get("/api/publicTransports/");
  publicTransports.value = r.data;
}

async function fetchPublicTransportsNumbers(){
  const r = await axios.get("/api/publicTransportsNumbers/");
  publicTransportsNumbers.value = r.data;
}

async function fetchData() {
  loading.value = true;
  try {
    const [measuringsRes, intensivitysRes, peoplesRes] = await Promise.all([
      axios.get("/api/measurings/"),
      axios.get("/api/intensivitys/"),
      axios.get("/api/peoplesInPublicsTransport/")
    ]);

    const grouped = _.chain(measuringsRes.data)
      .map(m => ({
        ...m,
        type: 'measuring',
        children: [
          ...intensivitysRes.data.filter(i => i.measuring === m.id),
          ...peoplesRes.data.filter(p => p.measuring === m.id)
        ]
      }))
      .orderBy('id')
      .value();

    measurements.value = grouped;
    filteredMeasurements.value = grouped;
    
  } catch (error) {
    console.error('Error fetching data:', error);
  }
  loading.value = false;
}

async function onDelete(measuringId) {
  if (!confirm('Удалить все данные измерения?')) return;
  
  try {
    const intensivitys = measurements.value
      .find(m => m.id === measuringId)
      ?.children
      ?.filter(c => c.transport)
      || [];

    for (const item of intensivitys) {
      await axios.delete(`/api/intensivitys/${item.id}/`);
    }

    const peoples = measurements.value
      .find(m => m.id === measuringId)
      ?.children
      ?.filter(c => !c.transport)
      || [];

    for (const item of peoples) {
      await axios.delete(`/api/peoplesInPublicsTransport/${item.id}/`);
    }
    
    await axios.delete(`/api/measurings/${measuringId}/`);
    
    await fetchData();
    await fetchTransports();
    await fetchPublicTransports();
    await fetchPublicTransportsNumbers();
  } catch (error) {
    console.error('Error deleting:', error);
  }
}

async function onDeleteSingle(item) {
  if (!confirm('Удалить эту запись?')) return;

  try {
    const isIntensivity = !!item.transport;
    const endpoint = isIntensivity 
      ? `/api/intensivitys/${item.id}/`
      : `/api/peoplesInPublicsTransport/${item.id}/`;

    await axios.delete(endpoint);
    
    await fetchData();
    await fetchTransports();
    await fetchPublicTransports();
    await fetchPublicTransportsNumbers();
  } catch (error) {
    console.error('Error deleting:', error);
  }
}

// Добавляем vm в глобальную область видимости для использования в popup
const setupGlobalVM = () => {
  window.vm = {
    showSingleRouteMapById: (id) => {
      const measuring = measurements.value.find(m => m.id === id);
      if (measuring) {
        showSingleRouteMap(measuring);
      }
    },
    clearMapSelection: () => {
      clearMapSelection();
    }
  };
};

onBeforeMount(async() => {
  await fetchUsers();
  await fetchTransports();
  await fetchPublicTransports();
  await fetchPublicTransportsNumbers();
  await fetchData();
  setupGlobalVM();
});
</script>

<style scoped>
/* Стили для фильтров */
.card-header h5 {
  font-size: 1.1rem;
}

.form-label.small {
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

/* Стили для групп чекбоксов */
.checkbox-group {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 0.5rem;
  background: #f8f9fa;
}

.form-check {
  margin-bottom: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.15s ease;
}

.form-check:hover {
  background-color: #e9ecef;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.form-check-label {
  font-size: 0.8rem;
  cursor: pointer;
}

/* Статистика */
.badge.fs-6 {
  font-size: 1.1rem !important;
  padding: 0.5rem 0.75rem;
}

/* Управление радиусом */
.radius-control {
  display: flex;
  align-items: center;
}

.radius-control .form-range {
  width: 120px;
}

.map-container {
  height: 500px;
  width: 100%;
  border-radius: 4px;
}

.arrow-icon {
  color: blue;
  font-size: 20px;
  text-shadow: 1px 1px 2px white;
  font-weight: bold;
}

.custom-marker {
  background: transparent !important;
  border: none !important;
}

.route-info {
  font-size: 12px;
}

/* Остальные стили остаются без изменений */
.measuring-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.measuring-card.highlighted {
  box-shadow: 0 0 0 3px #007bff, 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.measuring-main-card {
  border: none;
  border-radius: 12px;
  overflow: hidden;
}

.card-header.bg-primary {
  background: linear-gradient(135deg, #007bff, #0056b3) !important;
  border-bottom: none;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  padding: 6px 0;
}

.info-label {
  font-weight: 600;
  color: #495057;
  min-width: 160px;
  margin-right: 10px;
}

.info-value {
  color: #212529;
  font-weight: 500;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.intensivity-title {
  color: #198754;
  border-bottom-color: #198754;
}

.passengers-title {
  color: #0d6efd;
  border-bottom-color: #0d6efd;
}

.road-photo {
  max-width: 200px;
  border-radius: 8px;
  border: 2px solid #dee2e6;
}

.compact-intensivity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}

.compact-intensivity-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid #198754;
  transition: all 0.2s ease;
}

.compact-intensivity-item:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.intensivity-transport {
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.intensivity-quantity {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.quantity-number {
  font-size: 1.1rem;
  font-weight: 700;
  color: #198754;
}

.quantity-label {
  color: #6c757d;
  font-size: 0.75rem;
}

.btn-delete-compact {
  padding: 2px 6px;
  font-size: 0.7rem;
  opacity: 0.7;
}

.btn-delete-compact:hover {
  opacity: 1;
}

.child-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
  max-width: 280px;
}

.child-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.passenger-card {
  border-left: 4px solid #0d6efd;
}

.btn-delete {
  padding: 2px 6px;
  font-size: 0.7rem;
}

.child-content {
  font-size: 0.9rem;
}

.transport-info-compact {
  font-weight: 600;
  color: #495057;
  margin-bottom: 6px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.time-info-compact {
  color: #6c757d;
  margin-bottom: 8px;
  font-size: 0.85rem;
}

.intensivity-data-column {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-top: 8px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid #e9ecef;
}

.data-row:last-child {
  border-bottom: none;
}

.data-label {
  font-weight: 500;
  color: #495057;
  font-size: 0.85rem;
  min-width: 80px;
}

.data-value {
  font-weight: 700;
  color: #212529;
  font-size: 0.9rem;
  text-align: right;
  min-width: 30px;
}

.data-row.text-success .data-value {
  color: #198754;
}

.data-row.text-danger .data-value {
  color: #dc3545;
}

.coordinates-section-compact {
  background: #f8f9fa;
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 3px solid #6c757d;
}

.compact-coordinates-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.compact-coordinate-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 4px;
  background: white;
  border-left: 3px solid transparent;
}

.compact-coordinate-item.start {
  border-left-color: #198754;
}

.compact-coordinate-item.position {
  border-left-color: #fd7e14;
}

.compact-coordinate-item.end {
  border-left-color: #dc3545;
}

.compact-coordinate-label {
  font-weight: 600;
  color: #495057;
  font-size: 0.8rem;
  white-space: nowrap;
}

.compact-coordinate-value {
  color: #6c757d;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .info-item {
    flex-direction: column;
  }
  
  .info-label {
    min-width: auto;
    margin-bottom: 4px;
  }
  
  .compact-intensivity-grid {
    grid-template-columns: 1fr;
  }
  
  .compact-coordinates-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
  
  .compact-coordinate-item {
    width: 100%;
  }
  
  .child-card {
    max-width: 100%;
  }
  
  /* Адаптивность для фильтров */
  .card-body .row > .col-md-4 {
    margin-bottom: 1rem;
  }
  
  .checkbox-group {
    max-height: 120px;
  }

  .radius-control {
    flex-direction: column;
    align-items: flex-start;
  }
}

:deep(.leaflet-control-attribution) {
  display: none !important;
}
</style>