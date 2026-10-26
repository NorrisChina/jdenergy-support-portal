<template>
  <div class="relative overflow-hidden rounded-3xl border border-white/10 bg-slate-950">
    <div ref="mapEl" class="bg-slate-950 h-[calc(100vh-290px)] min-h-[460px] w-full"></div>

    <div class="pointer-events-none absolute inset-x-0 top-0 z-[1000] p-3">
      <div class="pointer-events-auto grid grid-cols-2 gap-2 rounded-2xl border border-white/10 bg-slate-950/60 p-2 backdrop-blur-md lg:grid-cols-4">
        <div v-for="stat in stats" :key="stat.key" class="rounded-xl border border-white/5 bg-white/5 px-3 py-2">
          <p class="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            <span v-if="stat.dot" class="h-2 w-2 rounded-full" :style="{ background: stat.dot, boxShadow: `0 0 8px ${stat.dot}` }"></span>{{ stat.label }}
          </p>
          <p class="mt-0.5 text-xl font-semibold text-white">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <div class="pointer-events-none absolute bottom-3 left-3 z-[1000] flex items-center gap-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-xs text-slate-300 backdrop-blur-md">
      <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>{{ copy.connected }}</span>
      <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-amber-400"></span>{{ copy.pending }}</span>
      <span v-if="missingCount" class="text-slate-400">· {{ copy.missing(missingCount) }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM, MAP_TILE_ATTRIBUTION, MAP_TILE_SUBDOMAINS, MAP_TILE_URL } from '../services/mapConfig'

const props = defineProps({
  // Each project: project_name, customer_company, capacity_mwh, cod, software_version, status ('connected' | 'pending'), latitude, longitude
  projects: { type: Array, default: () => [] },
  locale: { type: String, default: 'zh-CN' },
})
const emit = defineEmits(['view-details'])

const COLORS = { connected: '#34d399', pending: '#fbbf24' }

const copy = computed(() => props.locale === 'en-US' ? {
  totalProjects: 'Total projects', totalMwh: 'Total capacity (MWh)', connectedMwh: 'Grid-connected (MWh)', pendingMwh: 'Pending delivery (MWh)',
  connected: 'Connected', pending: 'Pending', missing: (n) => `${n} without coordinates`,
  customer: 'Customer', capacity: 'Capacity', cod: 'COD / Delivery date', software: 'Software version', status: 'Status', details: 'View details',
} : {
  totalProjects: '全球总项目数', totalMwh: '全球总容量 (MWh)', connectedMwh: '已并网容量 (MWh)', pendingMwh: '待交付容量 (MWh)',
  connected: '已并网', pending: '待交付', missing: (n) => `${n} 个项目未设置坐标`,
  customer: '客户名称', capacity: '容量', cod: 'COD / 交付日期', software: '软件版本', status: '并网状态', details: '查看详情',
})

const mapEl = ref(null)
let map = null
let layer = null

const mwhOf = (project) => Number(project.capacity_mwh) || 0
const round = (value) => Math.round(value * 100) / 100
const sumBy = (predicate) => round(props.projects.filter(predicate).reduce((sum, project) => sum + mwhOf(project), 0))

const stats = computed(() => [
  { key: 'count', label: copy.value.totalProjects, value: props.projects.length },
  { key: 'total', label: copy.value.totalMwh, value: sumBy(() => true) },
  { key: 'connected', label: copy.value.connectedMwh, value: sumBy((p) => p.status === 'connected'), dot: COLORS.connected },
  { key: 'pending', label: copy.value.pendingMwh, value: sumBy((p) => p.status !== 'connected'), dot: COLORS.pending },
])

const located = computed(() => props.projects.filter((p) => Number.isFinite(Number(p.latitude)) && Number.isFinite(Number(p.longitude)) && p.latitude !== null && p.longitude !== null && p.latitude !== ''))
const missingCount = computed(() => props.projects.length - located.value.length)

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch])
}

function markerSize(mwh, maxMwh) {
  if (maxMwh <= 0) return 22
  return Math.round(18 + 38 * Math.sqrt(mwh / maxMwh))
}

function buildIcon(project, maxMwh) {
  const size = markerSize(mwhOf(project), maxMwh)
  const color = COLORS[project.status === 'connected' ? 'connected' : 'pending']
  const html = `<span class="jd-map-pulse" style="--c:${color};width:${size}px;height:${size}px"></span><span class="jd-map-core" style="--c:${color}"></span>`
  return L.divIcon({ className: 'jd-map-marker', html, iconSize: [size, size], iconAnchor: [size / 2, size / 2], popupAnchor: [0, -size / 2] })
}

function popupHtml(project) {
  const connected = project.status === 'connected'
  const color = COLORS[connected ? 'connected' : 'pending']
  const row = (label, value) => `<div class="jd-pop-row"><span>${label}</span><b>${escapeHtml(value || '-')}</b></div>`
  return `<div class="jd-pop">
    <div class="jd-pop-title">${escapeHtml(project.project_name)}</div>
    ${row(copy.value.customer, project.customer_company)}
    ${row(copy.value.capacity, `${round(mwhOf(project))} MWh`)}
    ${row(copy.value.cod, project.cod)}
    ${row(copy.value.software, project.software_version)}
    <div class="jd-pop-row"><span>${copy.value.status}</span><b style="color:${color}">${connected ? copy.value.connected : copy.value.pending}</b></div>
    <button type="button" class="jd-pop-btn">${copy.value.details}</button>
  </div>`
}

function render() {
  if (!map) return
  layer.clearLayers()
  const maxMwh = Math.max(0, ...located.value.map(mwhOf))
  const points = []
  for (const project of located.value) {
    const latlng = [Number(project.latitude), Number(project.longitude)]
    points.push(latlng)
    const marker = L.marker(latlng, { icon: buildIcon(project, maxMwh), title: project.project_name })
    marker.bindPopup(popupHtml(project), { className: 'jd-map-popup', minWidth: 230 })
    marker.on('popupopen', (event) => {
      event.popup.getElement()?.querySelector('.jd-pop-btn')?.addEventListener('click', () => {
        map.closePopup()
        emit('view-details', project)
      })
    })
    marker.addTo(layer)
  }
  if (points.length) map.fitBounds(points, { padding: [70, 70], maxZoom: 6 })
}

onMounted(() => {
  map = L.map(mapEl.value, { center: MAP_DEFAULT_CENTER, zoom: MAP_DEFAULT_ZOOM, minZoom: 2, worldCopyJump: true, zoomControl: false })
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  L.tileLayer(MAP_TILE_URL, { attribution: MAP_TILE_ATTRIBUTION, subdomains: MAP_TILE_SUBDOMAINS, maxZoom: 19, className: 'jd-dark-tiles' }).addTo(map)
  layer = L.layerGroup().addTo(map)
  render()
  setTimeout(() => map?.invalidateSize(), 0)
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

watch(() => [props.projects, props.locale], render, { deep: true })
</script>

<style>
/* Darken the free OSM tiles to match the portal theme. */
.jd-dark-tiles { filter: invert(1) hue-rotate(180deg) brightness(0.95) contrast(0.9) saturate(0.6); }
.jd-map-marker { background: transparent; border: 0; }
.jd-map-marker { position: relative; }
.jd-map-pulse {
  position: absolute; inset: 0; border-radius: 9999px;
  background: color-mix(in srgb, var(--c) 35%, transparent);
  border: 2px solid var(--c);
  box-shadow: 0 0 14px var(--c);
  animation: jd-map-pulse 2.2s ease-out infinite;
}
.jd-map-core {
  position: absolute; left: 50%; top: 50%; width: 10px; height: 10px; margin: -5px 0 0 -5px;
  border-radius: 9999px; background: var(--c); box-shadow: 0 0 8px var(--c);
}
@keyframes jd-map-pulse {
  0% { transform: scale(0.75); opacity: 0.95; }
  70% { transform: scale(1.12); opacity: 0.45; }
  100% { transform: scale(0.75); opacity: 0.95; }
}
.jd-map-popup .leaflet-popup-content-wrapper { background: #0f172a; color: #e2e8f0; border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; }
.jd-map-popup .leaflet-popup-tip { background: #0f172a; }
.jd-map-popup .leaflet-popup-content { margin: 14px 16px; }
.jd-pop-title { font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 8px; }
.jd-pop-row { display: flex; justify-content: space-between; gap: 16px; font-size: 12px; padding: 3px 0; }
.jd-pop-row span { color: #94a3b8; }
.jd-pop-row b { font-weight: 600; text-align: right; }
.jd-pop-btn { margin-top: 10px; width: 100%; border: 0; border-radius: 10px; background: #22d3ee; color: #0f172a; font-weight: 700; font-size: 12px; padding: 7px 0; cursor: pointer; }
.jd-pop-btn:hover { filter: brightness(1.08); }
</style>
