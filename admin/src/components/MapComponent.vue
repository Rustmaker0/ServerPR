<template>
  <div class="map-container">
    <div ref="mapContainer" class="map"></div>
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
  center: {
    type: Array,
    default: () => [55.7558, 37.6173] // [lat, lng]
  },
  zoom: {
    type: Number,
    default: 13
  }
});

const mapContainer = ref(null);
let map = null;
let polyline = null;
let markers = [];

// Инициализация карты
const initMap = () => {
  map = L.map(mapContainer.value).setView(props.center, props.zoom);
  
  // Добавляем слой OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  
  drawRoute();
};

// Отрисовка маршрута со стрелкой
const drawRoute = () => {
  // Очищаем предыдущие элементы
  if (polyline) map.removeLayer(polyline);
  markers.forEach(marker => map.removeLayer(marker));
  markers = [];

  if (props.coordinates.length < 2) return;

  // Создаем полилинию
  polyline = L.polyline(props.coordinates, {
    color: 'red',
    weight: 4,
    opacity: 0.7,
    lineJoin: 'round'
  }).addTo(map);

  // Добавляем маркеры с номерами
  props.coordinates.forEach((coord, index) => {
    const marker = L.marker(coord)
      .addTo(map)
      .bindPopup(`Точка ${index + 1}<br>Ш: ${coord[0].toFixed(6)}<br>Д: ${coord[1].toFixed(6)}`);
    
    markers.push(marker);
  });

  // Добавляем стрелку направления
  addDirectionArrow();
  
  // Автоматическое изменение границ карты
  map.fitBounds(polyline.getBounds());
};

// Функция для добавления стрелки направления
const addDirectionArrow = () => {
  if (props.coordinates.length < 2) return;

  // Берем последний сегмент пути
  const startPoint = props.coordinates[props.coordinates.length - 2];
  const endPoint = props.coordinates[props.coordinates.length - 1];

  // Создаем полилинию со стрелкой (используем plugin или кастомный маркер)
  const arrowHead = L.polyline([startPoint, endPoint], {
    color: 'blue',
    weight: 3,
    opacity: 0.8
  }).addTo(map);

  // Добавляем маркер-стрелку в конечной точке
  const arrowIcon = L.divIcon({
    className: 'arrow-icon',
    html: '➤',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });

  const arrowMarker = L.marker(endPoint, { icon: arrowIcon }).addTo(map);
  markers.push(arrowMarker);
};

// Наблюдаем за изменениями координат
watch(() => props.coordinates, () => {
  if (map) drawRoute();
}, { deep: true });

onMounted(() => {
  initMap();
});
</script>

<style scoped>
.map-container {
  height: 400px;
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.map {
  height: 100%;
  width: 100%;
}

:deep(.arrow-icon) {
  color: blue;
  font-size: 20px;
  transform: rotate(45deg);
  text-shadow: 1px 1px 2px white;
}
</style>