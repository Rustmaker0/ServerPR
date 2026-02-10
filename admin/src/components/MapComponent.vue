<template>
  <div class="map-container">
    <div ref="mapContainer" class="map"></div>
    <div v-if="showControls" class="map-controls">
      <div class="control-group">
        <label class="control-label">Радиус выбора:</label>
        <div class="control-inputs">
          <input 
            type="range" 
            class="form-range" 
            min="10" 
            max="300" 
            step="10"
            v-model="radius"
            @input="updateRadius"
          >
          <span class="radius-value">{{ radius }}м</span>
        </div>
      </div>
      <div class="control-group" v-if="selectedLocation">
        <label class="control-label">Выбранная область:</label>
        <div class="location-info">
          [{{ selectedLocation.lat.toFixed(6) }}, {{ selectedLocation.lng.toFixed(6) }}]
        </div>
      </div>
      <div class="control-group" v-if="selectedLocation">
        <button class="btn btn-success btn-sm w-100" @click="applySelection">
          <i class="bi bi-check-lg"></i> Применить выбор
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const props = defineProps({
  coordinates: {
    type: Array,
    default: () => []
  },
  allRoutes: {
    type: Array,
    default: () => []
  },
  center: {
    type: Array,
    default: () => [52.294, 104.268] // Иркутск
  },
  zoom: {
    type: Number,
    default: 13
  },
  showControls: {
    type: Boolean,
    default: false
  },
  selectionMode: {
    type: Boolean,
    default: false
  },
  selectionRadius: {
    type: Number,
    default: 100
  },
  selectedArea: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['location-selected', 'radius-changed', 'apply-selection']);

const mapContainer = ref(null);
const radius = ref(props.selectionRadius);
const selectedLocation = ref(null);
let map = null;
let selectionCircle = null;
let selectionMarker = null;
let routes = [];

// Инициализация карты
const initMap = () => {
  map = L.map(mapContainer.value).setView(props.center, props.zoom);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  
  if (props.selectionMode) {
    setupSelectionMode();
  } else if (props.allRoutes.length > 0) {
    drawAllRoutes();
  } else if (props.selectedArea) {
    drawSelectedArea();
  } else {
    drawRoute();
  }
};

// Режим выбора местоположения
const setupSelectionMode = () => {
  map.on('click', (e) => {
    const { lat, lng } = e.latlng;
    selectedLocation.value = { lat, lng };
    emit('location-selected', { lat, lng, radius: radius.value });
    drawSelectionCircle(lat, lng);
  });
};

// Отрисовка круга выбора
const drawSelectionCircle = (lat, lng) => {
  // Очищаем предыдущие элементы
  if (selectionCircle) {
    map.removeLayer(selectionCircle);
  }
  if (selectionMarker) {
    map.removeLayer(selectionMarker);
  }

  // Рисуем круг
  selectionCircle = L.circle([lat, lng], {
    color: '#dc3545',
    fillColor: '#dc3545',
    fillOpacity: 0.1,
    weight: 2,
    radius: radius.value
  }).addTo(map);

  // Добавляем маркер в центр
  selectionMarker = L.marker([lat, lng]).addTo(map)
    .bindPopup(`
      <strong>Выбранная область</strong><br>
      Широта: ${lat.toFixed(6)}<br>
      Долгота: ${lng.toFixed(6)}<br>
      Радиус: ${radius.value}м
    `);

  // Центрируем карту на выбранной точке
  map.setView([lat, lng], map.getZoom());
};

// Отрисовка выбранной области
const drawSelectedArea = () => {
  if (!props.selectedArea) return;
  
  const { lat, lng, radius: areaRadius } = props.selectedArea;
  drawSelectionCircle(lat, lng);
  selectedLocation.value = { lat, lng };
  radius.value = areaRadius;
};

// Отрисовка всех маршрутов
const drawAllRoutes = () => {
  // Очищаем предыдущие маршруты
  routes.forEach(route => {
    if (route.polyline) {
      map.removeLayer(route.polyline);
    }
    if (route.markers) {
      route.markers.forEach(marker => map.removeLayer(marker));
    }
  });
  routes = [];

  // Рисуем новые маршруты
  props.allRoutes.forEach((route, index) => {
    if (route.coordinates && route.coordinates.length >= 2) {
      const polyline = L.polyline(route.coordinates, {
        color: route.color || '#0066cc',
        weight: route.weight || 4,
        opacity: route.opacity || 0.7,
        lineJoin: 'round',
        lineCap: 'round'
      }).addTo(map);

      const markers = [];

      // Добавляем маркеры для точек
      route.coordinates.forEach((coord, pointIndex) => {
        let markerColor, markerText, markerContent;
        
        if (pointIndex === 0) {
          markerColor = '#28a745'; // зеленый для старта
          markerText = 'Старт';
          markerContent = ''; // Пустое содержимое для зеленой метки
        } else if (pointIndex === 1 && route.coordinates.length === 3) {
          markerColor = '#007bff'; // синий для позиции
          markerText = 'Позиция';
          // Вместо цифры 2 используем ID измерения
          markerContent = route.id ? route.id.toString() : '';
        } else if (pointIndex === route.coordinates.length - 1) {
          markerColor = '#dc3545'; // красный для конца
          markerText = 'Конец';
          markerContent = ''; // Пустое содержимое для красной метки
        } else {
          markerColor = '#007bff'; // синий для промежуточных
          markerText = 'Точка';
          markerContent = route.id ? route.id.toString() : '';
        }

        const customIcon = L.divIcon({
          className: 'custom-marker',
          html: `
            <div style="background-color: ${markerColor}; 
                        width: ${pointIndex === 1 && route.coordinates.length === 3 ? '24px' : '16px'}; 
                        height: ${pointIndex === 1 && route.coordinates.length === 3 ? '24px' : '16px'}; 
                        border-radius: 50%; 
                        border: 2px solid white;
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
                        ${pointIndex === 1 && route.coordinates.length === 3 ? 'font-size: 10px; color: white; font-weight: bold;' : ''}">
              ${markerContent}
            </div>
          `,
          iconSize: pointIndex === 1 && route.coordinates.length === 3 ? [28, 28] : [20, 20],
          iconAnchor: pointIndex === 1 && route.coordinates.length === 3 ? [14, 14] : [10, 10]
        });

        const marker = L.marker(coord, { icon: customIcon })
          .addTo(map)
          .bindPopup(`
            <strong>${markerText}</strong><br>
            ${route.popup || 'Маршрут'}<br>
            ${pointIndex === 1 && route.coordinates.length === 3 ? `ID измерения: ${route.id}<br>` : ''}
            Точка ${pointIndex + 1}<br>
            Ш: ${coord[0].toFixed(6)}<br>
            Д: ${coord[1].toFixed(6)}
          `);

        markers.push(marker);
      });

      // Добавляем всплывающую подсказку
      if (route.popup) {
        polyline.bindPopup(route.popup);
      }

      routes.push({ polyline, markers, ...route });
    }
  });

  // Автоматическое изменение границ карты чтобы показать все маршруты
  if (routes.length > 0) {
    const group = new L.featureGroup(routes.map(r => r.polyline));
    map.fitBounds(group.getBounds());
  }
};

// Отрисовка одного маршрута
const drawRoute = () => {
  if (props.coordinates.length < 2) return;

  const polyline = L.polyline(props.coordinates, {
    color: '#dc3545',
    weight: 6,
    opacity: 0.8,
    lineJoin: 'round',
    lineCap: 'round'
  }).addTo(map);

  // Добавляем маркеры с номерами
  props.coordinates.forEach((coord, index) => {
    let markerColor = '#007bff';
    let markerText = 'Точка';
    let markerContent = '';
    
    if (index === 0) {
      markerColor = '#28a745';
      markerText = 'Старт';
      markerContent = ''; // Зеленая метка без текста
    } else if (index === 1 && props.coordinates.length === 3) {
      markerColor = '#007bff';
      markerText = 'Позиция';
      // Вместо цифры 2 используем ID измерения (если доступен)
      markerContent = props.measuringId ? props.measuringId.toString() : '';
    } else if (index === props.coordinates.length - 1) {
      markerColor = '#dc3545';
      markerText = 'Конец';
      markerContent = ''; // Красная метка без текста
    } else {
      markerColor = '#007bff';
      markerText = 'Точка';
      markerContent = (index + 1).toString();
    }

    const customIcon = L.divIcon({
      className: 'custom-marker',
      html: `
        <div style="background-color: ${markerColor}; 
                    width: ${index === 1 && props.coordinates.length === 3 ? '24px' : '20px'}; 
                    height: ${index === 1 && props.coordinates.length === 3 ? '24px' : '20px'}; 
                    border-radius: 50%; 
                    border: 3px solid white;
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: ${index === 1 && props.coordinates.length === 3 ? '10px' : '10px'};
                    box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
          ${markerContent}
        </div>
      `,
      iconSize: index === 1 && props.coordinates.length === 3 ? [30, 30] : [26, 26],
      iconAnchor: index === 1 && props.coordinates.length === 3 ? [15, 15] : [13, 13]
    });

    L.marker(coord, { icon: customIcon })
      .addTo(map)
      .bindPopup(`
        <strong>${markerText} ${index + 1}</strong><br>
        ${index === 1 && props.coordinates.length === 3 && props.measuringId ? `ID измерения: ${props.measuringId}<br>` : ''}
        Ш: ${coord[0].toFixed(6)}<br>
        Д: ${coord[1].toFixed(6)}
      `);
  });

  // Добавляем стрелку направления
  if (props.coordinates.length >= 2) {
    const startPoint = props.coordinates[props.coordinates.length - 2];
    const endPoint = props.coordinates[props.coordinates.length - 1];
    
    const arrowIcon = L.divIcon({
      className: 'arrow-icon',
      html: '➤',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });

    const arrowMarker = L.marker(endPoint, { 
      icon: arrowIcon,
      rotationAngle: calculateBearing(startPoint, endPoint)
    }).addTo(map);
  }

  map.fitBounds(polyline.getBounds());
};

// Расчет направления для стрелки
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

// Обновление радиуса
const updateRadius = () => {
  emit('radius-changed', radius.value);
  
  if (selectionCircle && selectedLocation.value) {
    const { lat, lng } = selectedLocation.value;
    map.removeLayer(selectionCircle);
    selectionCircle = L.circle([lat, lng], {
      color: '#dc3545',
      fillColor: '#dc3545',
      fillOpacity: 0.1,
      weight: 2,
      radius: radius.value
    }).addTo(map);
    
    // Обновляем popup
    if (selectionMarker) {
      selectionMarker.setPopupContent(`
        <strong>Выбранная область</strong><br>
        Широта: ${lat.toFixed(6)}<br>
        Долгота: ${lng.toFixed(6)}<br>
        Радиус: ${radius.value}м
      `);
    }
  }
};

// Применение выбора
const applySelection = () => {
  if (selectedLocation.value) {
    emit('apply-selection', {
      ...selectedLocation.value,
      radius: radius.value
    });
  }
};

// Очистка выбора
const clearSelection = () => {
  if (selectionCircle) {
    map.removeLayer(selectionCircle);
    selectionCircle = null;
  }
  if (selectionMarker) {
    map.removeLayer(selectionMarker);
    selectionMarker = null;
  }
  selectedLocation.value = null;
};

// Наблюдаем за изменениями пропсов
watch(() => props.coordinates, () => {
  if (map && !props.selectionMode && props.allRoutes.length === 0 && !props.selectedArea) {
    drawRoute();
  }
}, { deep: true });

watch(() => props.allRoutes, () => {
  if (map && props.allRoutes.length > 0) {
    drawAllRoutes();
  }
}, { deep: true });

watch(() => props.selectedArea, () => {
  if (map && props.selectedArea) {
    drawSelectedArea();
  }
}, { deep: true });

watch(() => props.selectionMode, () => {
  if (map) {
    if (props.selectionMode) {
      setupSelectionMode();
    } else {
      map.off('click');
    }
  }
});

// Экспортируем методы для использования извне
defineExpose({
  clearSelection,
  setLocation: (lat, lng) => {
    selectedLocation.value = { lat, lng };
    drawSelectionCircle(lat, lng);
  }
});

onMounted(() => {
  initMap();
});
</script>

<style scoped>
.map-container {
  height: 500px;
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ddd;
  position: relative;
}

.map {
  height: 100%;
  width: 100%;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 1000;
  min-width: 250px;
}

.control-group {
  margin-bottom: 10px;
}

.control-group:last-child {
  margin-bottom: 0;
}

.control-label {
  font-size: 12px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 5px;
  display: block;
}

.control-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-range {
  flex: 1;
}

.radius-value {
  font-size: 12px;
  font-weight: 600;
  color: #0d6efd;
  min-width: 50px;
}

.location-info {
  font-size: 11px;
  font-family: 'Courier New', monospace;
  color: #6c757d;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

:deep(.leaflet-popup-content) {
  margin: 8px 12px;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 8px;
}

:deep(.custom-marker) {
  background: transparent !important;
  border: none !important;
}

:deep(.arrow-icon) {
  color: #dc3545;
  font-size: 18px;
  text-shadow: 1px 1px 2px white;
  font-weight: bold;
}

@media (max-width: 768px) {
  .map-controls {
    position: relative;
    top: auto;
    right: auto;
    margin-bottom: 10px;
    min-width: auto;
  }
  
  .map-container {
    height: 400px;
  }
}
</style>