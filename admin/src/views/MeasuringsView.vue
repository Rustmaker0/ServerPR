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
        
        <!-- Компактная панель фильтров -->
        <div v-if="!showMap" class="d-flex align-items-center gap-2">
          <!-- Быстрый поиск -->
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
          
          <!-- Кнопка фильтров -->
          <button 
            class="btn btn-sm" 
            :class="showFilters ? 'btn-primary' : 'btn-outline-primary'"
            @click="showFilters = !showFilters"
          >
            <i class="bi bi-funnel"></i> Фильтры
            <span v-if="hasActiveFilters" class="badge bg-light text-dark ms-1">
              {{ filteredMeasurements.length }}/{{ measurements.length }}
            </span>
          </button>
        </div>
      </div>

      <!-- Блок выбранной области -->
      <div v-if="filters.mapSelection && !showMap" class="mb-3">
        <div class="card border-primary">
          <div class="card-body py-2">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-title mb-1 text-primary">
                  <i class="bi bi-geo-alt-fill"></i> 
                  {{ filters.mapSelection.type === 'circle' ? 'Круглая область' : 'Область из 4 точек' }}
                </h6>
                <div class="small text-muted">
                  <template v-if="filters.mapSelection.type === 'circle'">
                    Центр: [{{ filters.mapSelection.lat.toFixed(6) }}, {{ filters.mapSelection.lng.toFixed(6) }}] 
                    • Радиус: {{ filters.mapSelection.radius }} метров
                  </template>
                  <template v-else>
                    Четырехугольник • {{ filters.mapSelection.points.length }} точек
                  </template>
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
              <span class="badge bg-info ms-2">
                {{ getMeasurementsForMap.length }} записей
              </span>
              <span v-if="tempMapSelection" class="badge bg-warning ms-2">Область выбрана</span>
            </h5>
            <div class="d-flex align-items-center gap-3">
              <!-- Выбор типа области -->
              <div class="selection-type-control">
                <label class="form-label mb-0 me-2">
                  <i class="bi bi-bounding-box"></i> Тип области:
                </label>
                <div class="btn-group btn-group-sm">
                  <button 
                    class="btn" 
                    :class="selectionType === 'circle' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="setSelectionType('circle')"
                  >
                    <i class="bi bi-circle"></i> Круг
                  </button>
                  <button 
                    class="btn" 
                    :class="selectionType === 'polygon' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="setSelectionType('polygon')"
                  >
                    <i class="bi bi-square"></i> 4 точки
                  </button>
                </div>
              </div>

              <!-- Управление радиусом выбора (только для круга) -->
<div class="radius-control" v-if="selectionType === 'circle'">
  <label class="form-label mb-2">
    <i class="bi bi-bullseye"></i> Радиус выбора:
  </label>
  
  <!-- Числовое поле ввода -->
  <div class="input-group input-group-sm mb-2" style="width: 200px;">
    <input 
      type="number" 
      class="form-control" 
      min="10" 
      max="1000" 
      step="10"
      v-model.number="selectionRadius"
      @input="updateTempSelectionRadius"
      placeholder="Введите радиус"
    >
    <span class="input-group-text">м</span>
  </div>
  
  <!-- Ползунок для тонкой настройки -->
  <div class="d-flex align-items-center gap-2">
    <small>10м</small>
    <input 
      type="range" 
      class="form-range flex-grow-1" 
      min="10" 
      max="300" 
      step="10"
      v-model.number="selectionRadius"
      @input="updateTempSelectionRadius"
    >
    <small>300м</small>
    <span class="badge bg-primary ms-2">{{ selectionRadius }}м</span>
  </div>
</div>

              <!-- Информация о полигоне -->
              <div v-if="selectionType === 'polygon'" class="polygon-info">
                <small class="text-muted">
                  Точек: {{ polygonPoints.length }}/4
                </small>
              </div>
              
              <button 
                v-if="tempMapSelection"
                class="btn btn-sm btn-success"
                @click="applyTempSelection"
                :disabled="selectionType === 'polygon' && polygonPoints.length !== 4"
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

              <!-- Кнопка очистки точек полигона -->
              <button 
                v-if="selectionType === 'polygon' && polygonPoints.length > 0"
                class="btn btn-sm btn-outline-danger"
                @click="clearPolygonPoints"
              >
                <i class="bi bi-trash"></i> Очистить точки
              </button>
            </div>
          </div>
          
          <div class="card-body">
            <div class="alert alert-info mb-3">
              <i class="bi bi-info-circle"></i> 
              <strong>Инструкция:</strong> 
              <template v-if="selectionType === 'circle'">
                Кликните на карте для выбора центра области. Настройте радиус и нажмите "Применить выбор".
              </template>
              <template v-else>
                Кликните на карте чтобы добавить 4 точки для создания четырехугольника. После добавления 4 точек нажмите "Применить выбор".
              </template>
              <div v-if="hasActiveFilters" class="mt-1">
                <small><strong>На карте показаны отфильтрованные записи:</strong> {{ getMeasurementsForMap.length }} из {{ measurements.length }}</small>
              </div>
            </div>

            <!-- Список точек полигона -->
            <div v-if="selectionType === 'polygon' && polygonPoints.length > 0" class="polygon-points-list mb-3">
              <h6 class="section-title">
                <i class="bi bi-geo-alt"></i> Точки четырехугольника:
                <span class="badge" :class="polygonPoints.length === 4 ? 'bg-success' : 'bg-warning'">
                  {{ polygonPoints.length }}/4
                </span>
              </h6>
              <div class="points-grid">
                <div 
                  v-for="(point, index) in polygonPoints" 
                  :key="index"
                  class="point-item"
                  :class="{ 'active': currentPointIndex === index }"
                  @click="focusOnPoint(index)"
                >
                  <div class="point-header">
                    <span class="point-number">Точка {{ index + 1 }}</span>
                    <button 
                      class="btn btn-sm btn-outline-danger"
                      @click.stop="removePolygonPoint(index)"
                      title="Удалить точку"
                    >
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                  <div class="point-coordinates">
                    [{{ point.lat.toFixed(6) }}, {{ point.lng.toFixed(6) }}]
                  </div>
                </div>
              </div>
            </div>
            
            <div id="map" class="map-container"></div>
            
            <div class="mt-3">
              <div class="row">
                <div class="col-md-6">
                  <strong>Статистика:</strong>
                  <div class="small text-muted mt-1">
                    Всего измерений: {{ measurements.length }}<br>
                    Показано на карте: {{ getMeasurementsForMap.length }}<br>
                    <template v-if="tempMapSelection">
                      В выбранной области: {{ getTempSelectionMeasurements().length }}
                    </template>
                    <template v-else-if="filters.mapSelection">
                      В выбранной области: {{ getMeasurementsInSelection().length }}
                    </template>
                  </div>
                </div>
                <div class="col-md-6 text-end">
                  <small class="text-muted">
                    <template v-if="tempMapSelection">
                      <template v-if="tempMapSelection.type === 'circle'">
                        Центр: [{{ tempMapSelection.lat.toFixed(6) }}, {{ tempMapSelection.lng.toFixed(6) }}]<br>
                        Радиус: {{ tempMapSelection.radius }} м
                      </template>
                      <template v-else>
                        Четырехугольник • {{ tempMapSelection.points.length }} точек
                      </template>
                    </template>
                    <template v-else-if="filters.mapSelection">
                      <template v-if="filters.mapSelection.type === 'circle'">
                        Центр: [{{ filters.mapSelection.lat.toFixed(6) }}, {{ filters.mapSelection.lng.toFixed(6) }}]<br>
                        Радиус: {{ filters.mapSelection.radius }} м
                      </template>
                      <template v-else>
                        Четырехугольник • {{ filters.mapSelection.points.length }} точек
                      </template>
                    </template>
                    <template v-else>
                      {{ hasActiveFilters ? 'Показаны отфильтрованные записи' : 'Показаны все записи' }}
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
              <span class="badge bg-primary ms-2">{{ filteredMeasurements.length }}/{{ measurements.length }}</span>
            </h5>
            <div>
              <button class="btn btn-sm btn-outline-secondary me-2" @click="resetAllFilters">
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
                <template v-if="filters.mapSelection.type === 'circle'">
                  радиус {{ filters.mapSelection.radius }}м вокруг 
                  [{{ filters.mapSelection.lat.toFixed(6) }}, {{ filters.mapSelection.lng.toFixed(6) }}]
                </template>
                <template v-else>
                  четырехугольник ({{ filters.mapSelection.points.length }} точек)
                </template>
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

      <!-- Информация о статусе авторизации -->
      <div v-if="!isAuthenticated" class="alert alert-info mb-3">
        <i class="bi bi-info-circle"></i> Вы вошли как гость. Для редактирования данных войдите как администратор.
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
        <button v-if="hasActiveFilters" class="btn btn-sm btn-outline-primary ms-2" @click="resetFilters">
          <i class="bi bi-arrow-counterclockwise"></i> Очистить фильтры
        </button>
      </div>

      <!-- Таблица -->
      <div v-if="!showMap && filteredMeasurements.length > 0" class="table-container">
        <!-- Статистика фильтрации -->
        <div class="alert alert-light d-flex justify-content-between align-items-center mb-3">
          <div>
            <i class="bi bi-filter"></i>
            <strong>Показано записей:</strong> {{ filteredMeasurements.length }} из {{ measurements.length }}
            <span v-if="hasActiveFilters" class="text-success">
              • Применены фильтры
            </span>
          </div>
          <button 
            v-if="hasActiveFilters" 
            class="btn btn-sm btn-outline-secondary"
            @click="resetRegularFilters"
          >
            <i class="bi bi-x-circle"></i> Сбросить фильтры
          </button>
        </div>

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
                  <button v-if="isAdmin" class="btn btn-danger btn-sm" @click="onDelete(measuring.id)">
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
                    <span class="info-value">{{ formatDuration(measuring.measurment_duration) }}</span>
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
                  <div class="intensity-micro">
                    <span class="intensity-micro-value">
                      <i class="bi bi-activity"></i>
                      {{ calculateIntensity(measuring) }}
                    </span>
                    <small class="intensity-micro-label">ед/час</small>
                  </div>
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
                      <button v-if="isAdmin" class="btn btn-sm btn-outline-danger btn-delete-compact" @click="onDeleteSingle(child)" title="Удалить">
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
                            <button v-if="isAdmin" class="btn btn-sm btn-outline-danger btn-delete" @click="onDeleteSingle(child)" >
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
import { ref, onBeforeMount, computed, nextTick, watch } from 'vue';
import axios from 'axios';
import _ from 'lodash';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
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

// Fix for default markers in leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Новые переменные для полигона
const selectionType = ref('circle'); // 'circle' или 'polygon'
const polygonPoints = ref([]);
const currentPointIndex = ref(null);
const polygonLayer = ref(null);
const pointMarkers = ref([]);

// Существующие переменные
const measurements = ref([]);
const filteredMeasurements = ref([]);
const loading = ref(false);
const transports = ref([]);
const publicTransports = ref([]);
const publicTransportsNumbers = ref([]);
const users = ref([]);
const showMap = ref(false);
const mapMode = ref('allRoutes');
const selectedMeasuring = ref(null);
const routeCoordinates = ref([]);
const map = ref(null);
const scrollToMeasuringId = ref(null);
const showFilters = ref(false);
const selectionRadius = ref(100);
const tempMapSelection = ref(null);
const selectionCircle = ref(null);
const selectionMarker = ref(null);
const routePolylines = ref([]);
const routeMarkers = ref([]);

// Координаты Иркутска
const IRKUTSK_CENTER = [52.294, 104.268];

// Фильтры
const filters = ref({
  search: '', // Добавлен быстрый поиск
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
  mapSelection: null,
  isDeleted: 'all'
});

const transportsById = computed(() => _.keyBy(transports.value, x => x.id));
const publicTransportsById = computed(() => _.keyBy(publicTransports.value, x => x.id));
const publicTransportsNumbersById = computed(() => _.keyBy(publicTransportsNumbers.value, x => x.id));
const usersById = computed(() => _.keyBy(users.value, x => x.id));

// Проверка активных фильтров
const hasActiveFilters = computed(() => {
  return filters.value.search !== '' ||
         filters.value.measuringId !== '' ||
         filters.value.user !== '' ||
         filters.value.type !== 'all' ||
         filters.value.dateRange.start !== '' ||
         filters.value.dateRange.end !== '' ||
         filters.value.timeRange.start !== '' ||
         filters.value.timeRange.end !== '' ||
         filters.value.daysOfWeek.length > 0 ||
         filters.value.streetName !== '' ||
         filters.value.transportTypes.length > 0 ||
         filters.value.passengerTransportTypes.length > 0 ||
         filters.value.isDeleted !== 'all';
});

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
  const localDate = convertToLocalTime(dateString);
  if (!localDate) return '0';
  
  return localDate.getDay().toString();
};

// Функция для конвертации UTC времени в местное время (+8 UTC)
const convertToLocalTime = (dateString) => {
  if (!dateString) return null;
  
  try {
    const date = new Date(dateString);
    // Добавляем 8 часов к UTC времени
    const localTime = new Date(date.getTime() + (8 * 60 * 60 * 1000));
    return localTime;
  } catch (error) {
    console.error('Error converting to local time:', error);
    return null;
  }
};

// Обновленные функции форматирования
const formatDateTime = (dateString) => {
  const localDate = convertToLocalTime(dateString);
  if (!localDate) return 'Не указано';
  
  return `${localDate.getFullYear()}-${String(localDate.getMonth() + 1).padStart(2, '0')}-${String(localDate.getDate()).padStart(2, '0')} ${String(localDate.getHours()).padStart(2, '0')}:${String(localDate.getMinutes()).padStart(2, '0')}:${String(localDate.getSeconds()).padStart(2, '0')}`;
};

const formatTime = (dateString) => {
  const localDate = convertToLocalTime(dateString);
  if (!localDate) return 'Не указано';
  
  return `${String(localDate.getHours()).padStart(2, '0')}:${String(localDate.getMinutes()).padStart(2, '0')}:${String(localDate.getSeconds()).padStart(2, '0')}`;
};

const hasCoordinates = (measuring) => {
  return (measuring.latitude_start && measuring.longtiude_start) ||
         (measuring.latitude_position && measuring.longtiude_position) ||
         (measuring.latitude_end && measuring.longtiude_end);
};

// Функция для расчета расстояния между двумя точками в метрах (формула гаверсинусов)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371000;
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

// Функция для проверки нахождения в полигоне
const isMeasuringInPolygon = (measuring, polygonPoints) => {
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
    isPointInPolygon(point, polygonPoints)
  );
};

// Алгоритм проверки точки в полигоне (ray casting)
const isPointInPolygon = (point, polygon) => {
  const x = point.lat;
  const y = point.lng;
  let inside = false;
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].lat, yi = polygon[i].lng;
    const xj = polygon[j].lat, yj = polygon[j].lng;
    
    const intersect = ((yi > y) !== (yj > y))
        && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    
    if (intersect) inside = !inside;
  }
  
  return inside;
};

// Общая функция проверки нахождения в области
const isMeasuringInArea = (measuring, area) => {
  if (!area) return false;
  
  if (area.type === 'circle') {
    return isMeasuringInRadius(measuring, area.lat, area.lng, area.radius);
  } else if (area.type === 'polygon' && area.points.length === 4) {
    return isMeasuringInPolygon(measuring, area.points);
  }
  
  return false;
};

// Получение измерений для отображения на карте
const getMeasurementsForMap = computed(() => {
  // Если есть активные фильтры (кроме карты), используем отфильтрованные измерения
  if (hasActiveFilters.value && !filters.value.mapSelection) {
    return filteredMeasurements.value;
  }
  // Если выбран фильтр по карте, используем измерения из выбранной области
  else if (filters.value.mapSelection) {
    return measurements.value.filter(measuring => 
      isMeasuringInArea(measuring, filters.value.mapSelection)
    );
  }
  // Если нет фильтров, используем все измерения
  else {
    return measurements.value;
  }
});

// Получение измерений во временной выбранной области
const getTempSelectionMeasurements = () => {
  if (!tempMapSelection.value) {
    return [];
  }
  
  // Применяем текущие фильтры к выбранной области
  let filtered = measurements.value.filter(measuring => 
    isMeasuringInArea(measuring, tempMapSelection.value)
  );
  
  // Применяем остальные фильтры
  return applyOtherFilters(filtered);
};

const getMeasurementsInSelection = () => {
  if (!filters.value.mapSelection) {
    return [];
  }
  
  return measurements.value.filter(measuring => 
    isMeasuringInArea(measuring, filters.value.mapSelection)
  );
};

// Вспомогательная функция для преобразования времени в минуты
const timeToMinutes = (timeStr) => {
  if (!timeStr) return 0;
  
  try {
    const [hours, minutes] = timeStr.split(':').map(Number);
    
    // Проверяем валидность времени
    if (isNaN(hours) || isNaN(minutes) || hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
      console.warn(`Invalid time format: ${timeStr}`);
      return 0;
    }
    
    return hours * 60 + minutes;
  } catch (error) {
    console.error('Error converting time to minutes:', error, 'Time string:', timeStr);
    return 0;
  }
};

// Функция для применения всех фильтров кроме карты
const applyOtherFilters = (data) => {
  console.log('Applying filters:', {
    timeRange: filters.value.timeRange,
    dateRange: filters.value.dateRange,
    search: filters.value.search,
    measuringId: filters.value.measuringId
  });
  
  return data.filter(measuring => {
    console.log(`Checking measurement ${measuring.id} at ${measuring.measurment_time}`);
    
    // Быстрый поиск по всем полям
    if (filters.value.search) {
      const searchTerm = filters.value.search.toLowerCase();
      const id = measuring.id?.toString() || '';
      const userName = getUserDisplayName(measuring.user)?.toLowerCase() || '';
      const streetName = measuring.street_name?.toLowerCase() || '';
      const roadWidth = measuring.road_width?.toString() || '';
      const duration = measuring.measurment_duration?.toString() || '';
      
      const hasMatch = id.includes(searchTerm) ||
                      userName.includes(searchTerm) ||
                      streetName.includes(searchTerm) ||
                      roadWidth.includes(searchTerm) ||
                      duration.includes(searchTerm);
      
      if (!hasMatch) return false;
    }

    // Фильтр по статусу удаления
    if (filters.value.isDeleted !== 'all') {
      if (filters.value.isDeleted === 'deleted') {
        if (measuring.is_deleated != 1) return false;
      } else if (filters.value.isDeleted === 'active') {
        if (measuring.is_deleated == 1) return false;
      }
    }

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
    
    // ФИЛЬТРЫ ПО ДАТЕ - используем UTC время для фильтрации
    if (filters.value.dateRange.start || filters.value.dateRange.end) {
      const measuringDate = new Date(measuring.measurment_time);
      
      // Получаем компоненты даты в UTC времени
      const measuringYear = measuringDate.getUTCFullYear();
      const measuringMonth = measuringDate.getUTCMonth();
      const measuringDay = measuringDate.getUTCDate();
      
      // Создаем дату измерения без времени для сравнения в UTC
      const measuringDateOnly = new Date(Date.UTC(measuringYear, measuringMonth, measuringDay));
      
      // Обрабатываем фильтры дат в UTC
      let startDate = null;
      let endDate = null;
      
      if (filters.value.dateRange.start) {
        const [startYear, startMonth, startDay] = filters.value.dateRange.start.split('-').map(Number);
        startDate = new Date(Date.UTC(startYear, startMonth - 1, startDay));
      }
      
      if (filters.value.dateRange.end) {
        const [endYear, endMonth, endDay] = filters.value.dateRange.end.split('-').map(Number);
        endDate = new Date(Date.UTC(endYear, endMonth - 1, endDay, 23, 59, 59, 999)); // Конец дня в UTC
      }
      
      console.log(`Date filter: Measuring ${measuringDateOnly.toISOString()}, Range: ${startDate?.toISOString()} - ${endDate?.toISOString()}`);
      
      if (startDate && measuringDateOnly < startDate) return false;
      if (endDate && measuringDateOnly > endDate) return false;
    }
    
    // ФИЛЬТРЫ ПО ДАТЕ - используем местное время для фильтрации
    if (filters.value.dateRange.start || filters.value.dateRange.end) {
      const localDate = convertToLocalTime(measuring.measurment_time);
      if (!localDate) return false;
      
      // Получаем компоненты даты в местном времени
      const measuringYear = localDate.getFullYear();
      const measuringMonth = localDate.getMonth();
      const measuringDay = localDate.getDate();
      
      // Создаем дату измерения без времени для сравнения
      const measuringDateOnly = new Date(measuringYear, measuringMonth, measuringDay);
      
      // Обрабатываем фильтры дат
      let startDate = null;
      let endDate = null;
      
      if (filters.value.dateRange.start) {
        const [startYear, startMonth, startDay] = filters.value.dateRange.start.split('-').map(Number);
        startDate = new Date(startYear, startMonth - 1, startDay);
      }
      
      if (filters.value.dateRange.end) {
        const [endYear, endMonth, endDay] = filters.value.dateRange.end.split('-').map(Number);
        endDate = new Date(endYear, endMonth - 1, endDay, 23, 59, 59, 999); // Конец дня
      }
      
      console.log(`Date filter: Measuring ${measuringDateOnly.toISOString()}, Range: ${startDate?.toISOString()} - ${endDate?.toISOString()}`);
      
      if (startDate && measuringDateOnly < startDate) return false;
      if (endDate && measuringDateOnly > endDate) return false;
    }

    // ФИЛЬТРЫ ПО ВРЕМЕНИ - используем местное время для фильтрации
    if (filters.value.timeRange.start || filters.value.timeRange.end) {
      const localDate = convertToLocalTime(measuring.measurment_time);
      if (!localDate) return false;
      
      // Получаем местное время
      const localHours = localDate.getHours();
      const localMinutes = localDate.getMinutes();
      const measuringTotalMinutes = localHours * 60 + localMinutes;
      
      // Преобразуем фильтры времени в минуты
      const startTimeMinutes = filters.value.timeRange.start ? timeToMinutes(filters.value.timeRange.start) : 0;
      const endTimeMinutes = filters.value.timeRange.end ? timeToMinutes(filters.value.timeRange.end) : 1439; // 23:59
      
      console.log(`Time filter: Local ${localHours}:${localMinutes} (${measuringTotalMinutes}min), Range: ${startTimeMinutes}-${endTimeMinutes}min`);
      
      if (measuringTotalMinutes < startTimeMinutes || measuringTotalMinutes > endTimeMinutes) {
        console.log(`Skipping measurement ${measuring.id} - time out of range`);
        return false;
      }
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
};

// Основная функция применения фильтров
const applyFilters = () => {
  let filtered = measurements.value;

  // Сначала применяем фильтр по карте (если есть)
  if (filters.value.mapSelection) {
    filtered = filtered.filter(measuring => 
      isMeasuringInArea(measuring, filters.value.mapSelection)
    );
  }

  // Затем применяем остальные фильтры
  filtered = applyOtherFilters(filtered);

  filteredMeasurements.value = filtered;
};

const resetFilters = () => {
  console.log('Resetting filters...');
  
  filters.value = {
    search: '',
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
  
  // Безопасная очистка временного выбора
  tempMapSelection.value = null;
  polygonPoints.value = [];
  
  // Применяем фильтры (покажет все записи)
  filteredMeasurements.value = [...measurements.value];
  
  console.log('Filters reset successfully');
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

// Функции для работы с полигоном
const setSelectionType = (type) => {
  selectionType.value = type;
  clearTempSelection();
  polygonPoints.value = [];
};

const addPolygonPoint = (lat, lng) => {
  if (polygonPoints.value.length < 4) {
    polygonPoints.value.push({ lat, lng });
    updatePolygonOnMap();
    
    if (polygonPoints.value.length === 4) {
      // Автоматически создаем временный выбор когда есть 4 точки
      tempMapSelection.value = {
        type: 'polygon',
        points: [...polygonPoints.value]
      };
    }
  }
};

const removePolygonPoint = (index) => {
  polygonPoints.value.splice(index, 1);
  updatePolygonOnMap();
  currentPointIndex.value = null;
  
  // Сбрасываем временный выбор если точек меньше 4
  if (polygonPoints.value.length < 4) {
    tempMapSelection.value = null;
  }
};

const clearPolygonPoints = () => {
  polygonPoints.value = [];
  currentPointIndex.value = null;
  tempMapSelection.value = null;
  updatePolygonOnMap();
};

const focusOnPoint = (index) => {
  currentPointIndex.value = index;
  const point = polygonPoints.value[index];
  map.value.setView([point.lat, point.lng], map.value.getZoom());
};

const updatePolygonOnMap = () => {
  // Удаляем старый полигон
  if (polygonLayer.value) {
    map.value.removeLayer(polygonLayer.value);
    polygonLayer.value = null;
  }
  
  // Удаляем старые маркеры точек
  pointMarkers.value.forEach(marker => {
    if (map.value && marker) {
      map.value.removeLayer(marker);
    }
  });
  pointMarkers.value = [];
  
  // Рисуем новый полигон если есть достаточно точек
  if (polygonPoints.value.length >= 2) {
    const latLngs = polygonPoints.value.map(point => [point.lat, point.lng]);
    
    // Замыкаем полигон если есть 4 точки
    if (polygonPoints.value.length === 4) {
      latLngs.push([polygonPoints.value[0].lat, polygonPoints.value[0].lng]);
    }
    
    polygonLayer.value = L.polygon(latLngs, {
      color: '#0d6efd',
      fillColor: '#0d6efd',
      fillOpacity: 0.1,
      weight: 2
    }).addTo(map.value);
  }
  
  // Рисуем маркеры точек
  polygonPoints.value.forEach((point, index) => {
    const customIcon = L.divIcon({
      className: 'custom-marker',
      html: `
        <div style="background-color: #0d6efd; 
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
      `,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });

    const marker = L.marker([point.lat, point.lng], { icon: customIcon })
      .addTo(map.value)
      .bindPopup(`
        <strong>Точка ${index + 1}</strong><br>
        Ш: ${point.lat.toFixed(6)}<br>
        Д: ${point.lng.toFixed(6)}<br>
        <button onclick="window.vm.removePolygonPoint(${index})" class="btn btn-sm btn-outline-danger mt-1">
          <i class="bi bi-trash"></i> Удалить
        </button>
      `);

    pointMarkers.value.push(marker);
  });
};

// Функции для работы с картой
const initMap = () => {
  const mapContainer = document.getElementById('map');
  if (!mapContainer) return;

  if (map.value) {
    map.value.remove();
    map.value = null;
  }

  map.value = L.map(mapContainer).setView(IRKUTSK_CENTER, 13);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: ''
  }).addTo(map.value);

  if (mapMode.value === 'allRoutes') {
    drawAllRoutes();
    map.value.on('click', onMapClick);
    
    // Восстанавливаем выбранную область если есть
    if (filters.value.mapSelection) {
      if (filters.value.mapSelection.type === 'circle') {
        selectionType.value = 'circle';
        drawSelectionCircle(
          filters.value.mapSelection.lat,
          filters.value.mapSelection.lng,
          filters.value.mapSelection.radius
        );
      } else {
        selectionType.value = 'polygon';
        polygonPoints.value = [...filters.value.mapSelection.points];
        updatePolygonOnMap();
      }
    }
  } else if (mapMode.value === 'singleRoute') {
    drawSingleRoute(routeCoordinates.value, selectedMeasuring.value);
  }
};

// Обработчик клика по карте
const onMapClick = (e) => {
  const { lat, lng } = e.latlng;
  
  if (selectionType.value === 'circle') {
    tempMapSelection.value = {
      type: 'circle',
      lat,
      lng,
      radius: selectionRadius.value
    };
    drawSelectionCircle(lat, lng, selectionRadius.value);
  } else {
    addPolygonPoint(lat, lng);
  }
  
  redrawRoutesWithSelection();
};

// Отрисовка всех путей измерений
const drawAllRoutes = () => {
  if (!map.value) return;

  clearRoutesAndMarkers();

  // Используем измерения для карты (учитывая фильтры)
  const measurementsToDraw = getMeasurementsForMap.value;

  measurementsToDraw.forEach(measuring => {
    if (hasCoordinates(measuring)) {
      const coordinates = getCoordinatesFromMeasuring(measuring);
      if (coordinates.length >= 2) {
        const isInSelection = tempMapSelection.value ? 
          isMeasuringInArea(measuring, tempMapSelection.value) :
          false;
        
        const polyline = L.polyline(coordinates, {
          color: isInSelection ? '#ff4444' : '#0066cc',
          weight: isInSelection ? 6 : 4,
          opacity: isInSelection ? 0.9 : 0.7,
          lineJoin: 'round',
          lineCap: 'round'
        }).addTo(map.value);

        routePolylines.value.push(polyline);

        // Добавляем маркеры
        coordinates.forEach((coord, index) => {
          let markerColor, markerText;
          
          if (index === 0) {
            markerColor = '#28a745';
            markerText = 'Старт';
          } else if (index === 1 && coordinates.length === 3) {
            markerColor = '#fd7e14';
            markerText = 'Позиция';
          } else if (index === coordinates.length - 1) {
            markerColor = '#dc3545';
            markerText = 'Конец';
          } else {
            markerColor = '#007bff';
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

  // Восстанавливаем временный выбор если есть
  if (tempMapSelection.value) {
    if (tempMapSelection.value.type === 'circle') {
      const { lat, lng, radius } = tempMapSelection.value;
      drawSelectionCircle(lat, lng, radius);
    } else if (tempMapSelection.value.type === 'polygon') {
      updatePolygonOnMap();
    }
  } else if (filters.value.mapSelection) {
    if (filters.value.mapSelection.type === 'circle') {
      const { lat, lng, radius } = filters.value.mapSelection;
      drawSelectionCircle(lat, lng, radius);
    }
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

// Перерисовка маршрутов с учетом выбора
const redrawRoutesWithSelection = () => {
  if (mapMode.value === 'allRoutes') {
    drawAllRoutes();
  }
};

// Отрисовка круга выбора
const drawSelectionCircle = (lat, lng, radius) => {
  if (selectionCircle.value) {
    map.value.removeLayer(selectionCircle.value);
  }
  if (selectionMarker.value) {
    map.value.removeLayer(selectionMarker.value);
  }

  selectionCircle.value = L.circle([lat, lng], {
    color: '#dc3545',
    fillColor: '#dc3545',
    fillOpacity: 0.1,
    weight: 2,
    radius: radius
  }).addTo(map.value);

  selectionMarker.value = L.marker([lat, lng]).addTo(map.value)
    .bindPopup(`
      <strong>Центр выбора</strong><br>
      Широта: ${lat.toFixed(6)}<br>
      Долгота: ${lng.toFixed(6)}<br>
      Радиус: ${radius} м<br>
      Измерений в области: ${tempMapSelection.value ? getTempSelectionMeasurements().length : getMeasurementsForMap.value.length}
    `);

  map.value.setView([lat, lng], map.value.getZoom());
};

// Обновление радиуса временного выбора
const updateTempSelectionRadius = () => {
  if (tempMapSelection.value && tempMapSelection.value.type === 'circle') {
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
    polygonPoints.value = [];
    applyFilters();
    hideMap();
  }
};

// Очистка временного выбора
const clearTempSelection = () => {
  tempMapSelection.value = null;
  polygonPoints.value = [];
  currentPointIndex.value = null;
  
  if (map.value) {
    if (selectionCircle.value) {
      map.value.removeLayer(selectionCircle.value);
      selectionCircle.value = null;
    }
    if (selectionMarker.value) {
      map.value.removeLayer(selectionMarker.value);
      selectionMarker.value = null;
    }
    if (polygonLayer.value) {
      map.value.removeLayer(polygonLayer.value);
      polygonLayer.value = null;
    }
  }
  
  pointMarkers.value.forEach(marker => {
    if (map.value && marker) {
      map.value.removeLayer(marker);
    }
  });
  pointMarkers.value = [];
  
  redrawRoutesWithSelection();
};

// Очистка выбора на карте
const clearMapSelection = () => {
  filters.value.mapSelection = null;
  clearTempSelection();
  applyFilters();
};

const resetAllFilters = () => {
  console.log('Resetting all filters...');
  
  filters.value = {
    search: '',
    measuringId: '',
    user: '',
    type: 'all',
    dateRange: { start: '', end: '' },
    timeRange: { start: '', end: '' },
    daysOfWeek: [],
    streetName: '',
    transportTypes: [],
    passengerTransportTypes: [],
    mapSelection: null, // очищаем и фильтр карты
    isDeleted: 'all'
  };
  
  // Безопасная очистка временного выбора
  tempMapSelection.value = null;
  polygonPoints.value = [];
  
  // Применяем фильтры (покажет все записи)
  filteredMeasurements.value = [...measurements.value];
  
  console.log('All filters reset successfully');
};

const resetRegularFilters = () => {
  console.log('Resetting regular filters...');
  
  filters.value = {
    ...filters.value, // сохраняем текущий фильтр карты
    search: '',
    measuringId: '',
    user: '',
    type: 'all',
    dateRange: { start: '', end: '' },
    timeRange: { start: '', end: '' },
    daysOfWeek: [],
    streetName: '',
    transportTypes: [],
    passengerTransportTypes: [],
    isDeleted: 'all'
  };
  
  // Применяем фильтры
  applyFilters();
  
  console.log('Regular filters reset successfully');
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
  // Сбрасываем выбранную область на карте
  filters.value.mapSelection = null;
  tempMapSelection.value = null;
  polygonPoints.value = [];
  
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

// Отрисовка одного маршрута
const drawSingleRoute = (coordinates, measuring) => {
  if (!map.value) return;

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
// Новая функция для форматирования длительности
const formatDuration = (durationInSeconds) => {
  if (!durationInSeconds || durationInSeconds <= 0) return '0 сек';
  
  const minutes = Math.floor(durationInSeconds / 60);
  const seconds = Math.round(durationInSeconds % 60);
  
  if (minutes === 0) {
    return `${seconds} сек`;
  } else if (seconds === 0) {
    return `${minutes} мин`;
  } else {
    return `${minutes} мин ${seconds} сек`;
  }
};

// Обновленная функция расчета интенсивности (для секунд)
const calculateIntensity = (measuring) => {
  if (!measuring.children || measuring.children.length === 0) return 0;
  
  const transportChildren = measuring.children.filter(child => child.transport);
  if (transportChildren.length === 0) return 0;
  
  let totalWeightedCount = 0;
  
  transportChildren.forEach(child => {
    const transport = transportsById.value[child.transport];
    if (transport && transport.weight) {
      // Используем вес из БД
      const weight = parseFloat(transport.weight) || 1;
      totalWeightedCount += child.quanity * weight;
    } else {
      totalWeightedCount += child.quanity;
    }
  });
  
  // РАСЧЕТ ИНТЕНСИВНОСТИ В СЕКУНДАХ
  const durationInHours = measuring.measurment_duration / 3600; // переводим секунды в часы
  const intensityPerHour = durationInHours > 0 ? totalWeightedCount / durationInHours : totalWeightedCount;
  
  return Math.round(intensityPerHour * 100) / 100; // округляем до 2 знаков
};
  

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
    },
    removePolygonPoint: (index) => {
      removePolygonPoint(index);
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

/* Новые стили для управления полигоном */
.selection-type-control {
  display: flex;
  align-items: center;
}

.polygon-info {
  padding: 4px 8px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.polygon-points-list {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.points-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.point-item {
  background: white;
  padding: 10px;
  border-radius: 6px;
  border: 2px solid #e9ecef;
  cursor: pointer;
  transition: all 0.2s ease;
}

.point-item:hover {
  border-color: #0d6efd;
  transform: translateY(-1px);
}

.point-item.active {
  border-color: #0d6efd;
  background: #e7f1ff;
}

.point-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.point-number {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.point-coordinates {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #6c757d;
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

/* Адаптивность */
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

  .card-header .d-flex {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .selection-type-control,
  .radius-control {
    width: 100%;
    justify-content: space-between;
  }
  
  .points-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.leaflet-control-attribution) {
  display: none !important;
}
.intensity-micro {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  padding: 2px 6px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.intensity-micro-value {
  font-size: 0.8rem;
  font-weight: 600;
  color: #198754;
  display: flex;
  align-items: center;
  gap: 2px;
}

.intensity-micro-label {
  font-size: 0.6rem;
  color: #6c757d;
}
</style>