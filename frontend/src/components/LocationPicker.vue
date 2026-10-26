<template>
  <div>
    <div ref="mapEl" class="h-56 w-full overflow-hidden rounded-2xl border border-white/10"></div>
    <p class="mt-1 text-xs text-slate-400">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM, MAP_TILE_ATTRIBUTION, MAP_TILE_SUBDOMAINS, MAP_TILE_URL } from '../services/mapConfig'

const props = defineProps({
  latitude: { type: [Number, String, null], default: null },
  longitude: { type: [Number, String, null], default: null },
  locale: { type: String, default: 'zh-CN' },
})
const emit = defineEmits(['pick'])

const hint = computed(() => props.locale === 'en-US' ? 'Click the map to pick coordinates.' : '点击地图即可拾取坐标。')
const mapEl = ref(null)
let map = null
let marker = null

function current() {
  const lat = props.latitude === null || props.latitude === '' ? NaN : Number(props.latitude)
  const lng = props.longitude === null || props.longitude === '' ? NaN : Number(props.longitude)
  return Number.isFinite(lat) && Number.isFinite(lng) ? [lat, lng] : null
}

function sync(recenter) {
  if (!map) return
  const point = current()
  if (!point) {
    marker?.remove()
    marker = null
    return
  }
  if (!marker) marker = L.circleMarker(point, { radius: 8, color: '#22d3ee', fillColor: '#22d3ee', fillOpacity: 0.7 }).addTo(map)
  else marker.setLatLng(point)
  if (recenter) map.setView(point, Math.max(map.getZoom(), 5))
}

onMounted(() => {
  map = L.map(mapEl.value, { center: MAP_DEFAULT_CENTER, zoom: MAP_DEFAULT_ZOOM, minZoom: 1, worldCopyJump: true })
  L.tileLayer(MAP_TILE_URL, { attribution: MAP_TILE_ATTRIBUTION, subdomains: MAP_TILE_SUBDOMAINS, maxZoom: 19 }).addTo(map)
  map.on('click', (event) => {
    const { lat, lng } = event.latlng.wrap()
    emit('pick', { latitude: Number(lat.toFixed(6)), longitude: Number(lng.toFixed(6)) })
  })
  sync(true)
  setTimeout(() => map?.invalidateSize(), 0)
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

watch(() => [props.latitude, props.longitude], () => sync(false))
</script>
