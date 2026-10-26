<template>
  <section class="flex min-h-0 flex-1 flex-col">
    <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Delivery Schedule Calendar</p>
        <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">{{ copy.title }}</h2>
        <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">{{ copy.subtitle }}</p>
      </div>
      <button type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openCreate(cursor)">
        {{ copy.create }}
      </button>
    </div>

    <div class="mb-4 flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-1 rounded-xl border border-white/10 bg-white/5 p-1">
        <button type="button" class="rounded-lg px-3 py-1.5 text-sm text-slate-200 hover:bg-white/10" @click="shift(-1)">‹</button>
        <button type="button" class="rounded-lg px-3 py-1.5 text-sm font-semibold text-slate-200 hover:bg-white/10" @click="goToday">{{ copy.today }}</button>
        <button type="button" class="rounded-lg px-3 py-1.5 text-sm text-slate-200 hover:bg-white/10" @click="shift(1)">›</button>
      </div>
      <h3 class="min-w-48 text-lg font-semibold text-white">{{ rangeTitle }}</h3>
      <div class="flex items-center gap-3 text-xs text-slate-300">
        <span v-for="stage in STAGES" :key="stage.key" class="flex items-center gap-1.5">
          <span class="h-3 w-3 rounded-sm border-l-4" :style="{ background: stage.background, borderLeftColor: stage.color }"></span>{{ copy.stages[stage.key] }}
        </span>
      </div>
      <div class="ml-auto flex gap-1 rounded-xl border border-white/10 bg-white/5 p-1">
        <button
          v-for="mode in viewModes"
          :key="mode"
          type="button"
          class="rounded-lg px-3 py-1.5 text-sm font-semibold transition"
          :class="view === mode ? 'bg-cyan-400 text-slate-950' : 'text-slate-300 hover:bg-white/10'"
          @click="view = mode"
        >
          {{ copy.views[mode] }}
        </button>
      </div>
    </div>

    <p v-if="error" class="mb-3 rounded-xl border border-rose-400/20 bg-rose-500/10 px-4 py-2 text-sm text-rose-100">{{ error }}</p>

    <!-- Month -->
    <div v-if="view === 'month'" class="overflow-hidden rounded-2xl border border-white/10 bg-white/5">
      <div class="grid grid-cols-7 border-b border-white/10 bg-slate-950/50 text-center text-xs font-semibold text-slate-400">
        <div v-for="day in weekDays" :key="day.key" class="py-2">{{ weekdayLabel(day) }}</div>
      </div>
      <div class="grid grid-cols-7">
        <div
          v-for="day in monthCells"
          :key="day.key"
          class="min-h-28 cursor-pointer border-b border-r border-white/5 p-1.5 transition hover:bg-white/5"
          :class="day.getMonth() !== cursor.getMonth() ? 'opacity-40' : ''"
          @click="openCreate(day)"
        >
          <div class="mb-1 flex justify-end">
            <span class="flex h-6 min-w-6 items-center justify-center rounded-full px-1 text-xs font-semibold" :class="isToday(day) ? 'bg-cyan-400 text-slate-950' : 'text-slate-300'">{{ day.getDate() }}</span>
          </div>
          <button
            v-for="item in itemsOn(day).slice(0, 3)"
            :key="item.id"
            type="button"
            class="mb-1 block w-full truncate rounded-md border-l-4 px-1.5 py-0.5 text-left text-[11px] font-medium"
            :style="chipStyle(item)"
            @click.stop="openEdit(item)"
          >
            {{ item.start_time }} {{ item.customer_name || item.project_name }}
          </button>
          <button v-if="itemsOn(day).length > 3" type="button" class="text-[11px] text-cyan-200" @click.stop="openDay(day)">
            {{ copy.more(itemsOn(day).length - 3) }}
          </button>
        </div>
      </div>
    </div>

    <!-- Week / Day -->
    <div v-else-if="view === 'week' || view === 'day'" class="overflow-auto rounded-2xl border border-white/10 bg-white/5">
      <div class="grid min-w-[640px]" :style="{ gridTemplateColumns: `56px repeat(${timelineDays.length}, minmax(0, 1fr))` }">
        <div class="sticky top-0 z-10 border-b border-white/10 bg-slate-950/90"></div>
        <div v-for="day in timelineDays" :key="day.key" class="sticky top-0 z-10 border-b border-l border-white/10 bg-slate-950/90 py-2 text-center text-xs font-semibold text-slate-300">
          {{ weekdayLabel(day) }}
          <span class="ml-1 inline-flex h-6 min-w-6 items-center justify-center rounded-full px-1" :class="isToday(day) ? 'bg-cyan-400 text-slate-950' : ''">{{ day.getDate() }}</span>
        </div>

        <div class="relative" :style="{ height: `${(HOUR_END - HOUR_START) * HOUR_PX}px` }">
          <div v-for="hour in hours" :key="hour" class="absolute right-2 -translate-y-2 text-[11px] text-slate-500" :style="{ top: `${(hour - HOUR_START) * HOUR_PX}px` }">{{ pad(hour) }}:00</div>
        </div>
        <div
          v-for="day in timelineDays"
          :key="`col-${day.key}`"
          class="relative cursor-pointer border-l border-white/10"
          :style="{ height: `${(HOUR_END - HOUR_START) * HOUR_PX}px` }"
          @click="onSlotClick($event, day)"
        >
          <div v-for="hour in hours" :key="hour" class="absolute inset-x-0 border-t border-white/5" :style="{ top: `${(hour - HOUR_START) * HOUR_PX}px` }"></div>
          <button
            v-for="block in layoutBlocks(day)"
            :key="block.item.id"
            type="button"
            class="absolute overflow-hidden rounded-lg border-l-4 px-1.5 py-1 text-left text-[11px] leading-tight shadow"
            :style="{ ...chipStyle(block.item), top: `${block.top}px`, height: `${block.height}px`, left: `calc(${block.left}% + 2px)`, width: `calc(${block.width}% - 4px)` }"
            @click.stop="openEdit(block.item)"
          >
            <p class="truncate font-bold">{{ block.item.customer_name || '-' }}</p>
            <p class="truncate">{{ block.item.project_name }}</p>
            <p class="truncate font-medium text-slate-900">{{ block.item.start_time }}–{{ block.item.end_time }} · {{ stageLabel(block.item.stage) }}</p>
            <p v-if="block.item.notes && block.height > 80" class="mt-0.5 line-clamp-2 text-slate-800">{{ block.item.notes }}</p>
          </button>
        </div>
      </div>
    </div>

    <!-- List -->
    <div v-else class="overflow-hidden rounded-2xl border border-white/10 bg-white/5">
      <div v-if="!items.length" class="px-4 py-10 text-center text-sm text-slate-400">{{ copy.empty }}</div>
      <div v-for="group in listGroups" :key="group.date" class="border-b border-white/5 last:border-b-0">
        <div class="bg-slate-950/50 px-4 py-2 text-xs font-semibold text-slate-300">{{ longDate(parseDate(group.date)) }}</div>
        <button v-for="item in group.items" :key="item.id" type="button" class="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-white/5" @click="openEdit(item)">
          <span class="mt-1 h-3 w-3 shrink-0 rounded-full" :style="{ background: stageColor(item.stage) }"></span>
          <span class="w-28 shrink-0 font-mono text-xs text-slate-300">{{ item.start_time }} – {{ item.end_time }}</span>
          <span class="min-w-0 flex-1">
            <span class="block text-sm font-semibold text-white">{{ item.customer_name }} <span class="font-normal text-slate-400">· {{ item.project_name }}</span></span>
            <span class="block text-xs text-slate-400">{{ stageLabel(item.stage) }}<template v-if="item.engineer"> · {{ item.engineer }}</template></span>
            <span v-if="item.notes" class="mt-1 block whitespace-pre-line text-xs text-slate-500">{{ item.notes }}</span>
          </span>
        </button>
      </div>
    </div>

    <div v-if="modal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm" @click.self="closeModal">
      <div class="max-h-[92vh] w-full max-w-xl overflow-y-auto rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30">
        <div class="flex items-start justify-between gap-4">
          <h3 class="text-xl font-semibold text-white">{{ modal.id ? copy.edit : copy.create.replace('+ ', '') }}</h3>
          <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white" @click="closeModal">{{ copy.close }}</button>
        </div>
        <div class="mt-5 grid gap-4 sm:grid-cols-2">
          <label class="block">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.customer }} *</span>
            <input v-model="draft.customer_name" type="text" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
          </label>
          <label class="block">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.project }}</span>
            <input v-model="draft.project_name" type="text" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
          </label>
          <label class="block sm:col-span-2">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.date }} *</span>
            <input v-model="draft.schedule_date" type="date" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
          </label>
          <label class="block">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.start }} *</span>
            <input v-model="draft.start_time" type="time" step="900" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
          </label>
          <label class="block">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.end }} *</span>
            <input v-model="draft.end_time" type="time" step="900" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
          </label>
          <label class="block">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.engineer }}</span>
            <input v-model="draft.engineer" type="text" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
          </label>
          <label class="block">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.stage }}</span>
            <select v-model="draft.stage" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white">
              <option v-for="stage in STAGES" :key="stage.key" :value="stage.key">{{ copy.stages[stage.key] }}</option>
            </select>
          </label>
          <label class="block sm:col-span-2">
            <span class="mb-2 block text-xs font-semibold text-slate-400">{{ copy.notes }}</span>
            <textarea v-model="draft.notes" rows="4" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white"></textarea>
          </label>
        </div>
        <p v-if="modal.error" class="mt-3 text-sm text-rose-300">{{ modal.error }}</p>
        <div class="mt-6 flex items-center justify-between gap-3">
          <button v-if="modal.id" type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-4 py-2 text-sm font-semibold text-rose-100" @click="remove">{{ copy.delete }}</button>
          <span v-else></span>
          <div class="flex gap-3">
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white" @click="closeModal">{{ copy.cancel }}</button>
            <button type="button" class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" :disabled="modal.saving" @click="save">{{ copy.save }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { portalApi } from '../services/portalApi'

const props = defineProps({
  locale: { type: String, default: 'zh-CN' },
})

const HOUR_START = 7
const HOUR_END = 21
const HOUR_PX = 52
const hours = Array.from({ length: HOUR_END - HOUR_START }, (_, index) => HOUR_START + index)
const viewModes = ['month', 'week', 'day', 'list']

const STAGES = [
  { key: 'delivery', color: '#1D4ED8', background: '#93C5FD' },
  { key: 'after_sales', color: '#C2410C', background: '#FDBA74' },
]

const copy = computed(() => props.locale === 'en-US' ? {
  title: 'Delivery Schedule Calendar',
  subtitle: 'Plan on-site delivery work, see engineer time blocks at a glance and keep every stage in one place.',
  create: '+ New delivery plan', edit: 'Edit delivery plan', today: 'Today', close: 'Close', cancel: 'Cancel', save: 'Save', delete: 'Delete',
  views: { month: 'Month', week: 'Week', day: 'Day', list: 'Schedule' },
  customer: 'Customer', project: 'Project', date: 'Delivery date', start: 'Start time', end: 'End time',
  engineer: 'Engineer / Owner', stage: 'Delivery stage', notes: 'Notes',
  stages: { delivery: 'Delivery', after_sales: 'After-sales' },
  empty: 'No delivery plans in this period.',
  more: (count) => `+${count} more`,
  loadFailed: 'Failed to load delivery plans',
  saveFailed: 'Failed to save delivery plan',
  confirmDelete: 'Delete this delivery plan?',
  requiredName: 'Please enter a customer or project name.',
  invalidTime: 'End time must be later than start time.',
} : {
  title: '交付计划日历',
  subtitle: '统筹现场交付工作安排，直观查看工程师时间占用，集中跟踪各交付阶段。',
  create: '+ 新建交付计划', edit: '编辑交付计划', today: '今天', close: '关闭', cancel: '取消', save: '保存', delete: '删除',
  views: { month: '月', week: '周', day: '日', list: '列表' },
  customer: '客户名称', project: '项目名称', date: '交付日期', start: '开始时间', end: '结束时间',
  engineer: '交付工程师 / 负责人', stage: '交付阶段', notes: '备注',
  stages: { delivery: '交付', after_sales: '售后' },
  empty: '该时间段内暂无交付计划。',
  more: (count) => `还有 ${count} 项`,
  loadFailed: '交付计划加载失败',
  saveFailed: '交付计划保存失败',
  confirmDelete: '确定删除该交付计划吗？',
  requiredName: '请填写客户名称或项目名称。',
  invalidTime: '结束时间必须晚于开始时间。',
})

const view = ref('month')
const cursor = ref(startOfDay(new Date()))
const items = ref([])
const error = ref('')
const modal = reactive({ open: false, id: null, saving: false, error: '' })
const draft = reactive({ customer_name: '', project_name: '', schedule_date: '', start_time: '09:00', end_time: '13:00', engineer: '', stage: 'delivery', notes: '' })

function pad(value) { return String(value).padStart(2, '0') }
function startOfDay(date) { return new Date(date.getFullYear(), date.getMonth(), date.getDate()) }
function addDays(date, amount) { return new Date(date.getFullYear(), date.getMonth(), date.getDate() + amount) }
function fmt(date) { return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` }
function parseDate(value) { const [y, m, d] = value.split('-').map(Number); return new Date(y, m - 1, d) }
function mondayOf(date) { return addDays(date, -((date.getDay() + 6) % 7)) }
function minutes(time) { const [h, m] = (time || '0:0').split(':').map(Number); return h * 60 + m }
function isToday(date) { return fmt(date) === fmt(new Date()) }
function withKey(date) { const copyDate = new Date(date); copyDate.key = fmt(date); return copyDate }

const weekDays = computed(() => Array.from({ length: 7 }, (_, index) => withKey(addDays(mondayOf(cursor.value), index))))
const timelineDays = computed(() => view.value === 'day' ? [withKey(cursor.value)] : weekDays.value)
const monthCells = computed(() => {
  const first = new Date(cursor.value.getFullYear(), cursor.value.getMonth(), 1)
  const start = mondayOf(first)
  return Array.from({ length: 42 }, (_, index) => withKey(addDays(start, index)))
})

const range = computed(() => {
  if (view.value === 'day') return [fmt(cursor.value), fmt(cursor.value)]
  if (view.value === 'week') return [fmt(weekDays.value[0]), fmt(weekDays.value[6])]
  if (view.value === 'month') return [fmt(monthCells.value[0]), fmt(monthCells.value[41])]
  const first = new Date(cursor.value.getFullYear(), cursor.value.getMonth(), 1)
  const last = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + 1, 0)
  return [fmt(first), fmt(last)]
})

const rangeTitle = computed(() => {
  const loc = props.locale
  if (view.value === 'day') return cursor.value.toLocaleDateString(loc, { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
  if (view.value === 'week') {
    const [a, b] = [weekDays.value[0], weekDays.value[6]]
    return `${a.toLocaleDateString(loc, { month: 'short', day: 'numeric' })} – ${b.toLocaleDateString(loc, { year: 'numeric', month: 'short', day: 'numeric' })}`
  }
  return cursor.value.toLocaleDateString(loc, { year: 'numeric', month: 'long' })
})

function weekdayLabel(date) { return date.toLocaleDateString(props.locale, { weekday: 'short' }) }
function longDate(date) { return date.toLocaleDateString(props.locale, { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' }) }
// Records saved with the former four-stage values are shown as Delivery.
function stageKey(stage) { return stage === 'after_sales' ? 'after_sales' : 'delivery' }
function stageDef(stage) { return STAGES.find((entry) => entry.key === stageKey(stage)) }
function stageColor(stage) { return stageDef(stage).color }
function stageLabel(stage) { return copy.value.stages[stageKey(stage)] }
function chipStyle(item) {
  const def = stageDef(item.stage)
  return { background: def.background, borderLeftColor: def.color, color: '#0F172A' }
}

function itemsOn(day) { return items.value.filter((item) => item.schedule_date === day.key) }

const listGroups = computed(() => {
  const groups = new Map()
  for (const item of items.value) {
    if (!groups.has(item.schedule_date)) groups.set(item.schedule_date, [])
    groups.get(item.schedule_date).push(item)
  }
  return [...groups.entries()].map(([date, entries]) => ({ date, items: entries }))
})

function layoutBlocks(day) {
  const dayItems = itemsOn(day).map((item) => ({ item, start: minutes(item.start_time), end: minutes(item.end_time) })).sort((a, b) => a.start - b.start || a.end - b.end)
  const blocks = []
  let cluster = []
  let clusterEnd = -1
  const flush = () => {
    const columnEnds = []
    for (const entry of cluster) {
      let column = columnEnds.findIndex((end) => end <= entry.start)
      if (column === -1) { column = columnEnds.length; columnEnds.push(entry.end) } else columnEnds[column] = entry.end
      entry.column = column
    }
    for (const entry of cluster) {
      const top = Math.max(0, (entry.start - HOUR_START * 60) / 60 * HOUR_PX)
      const bottom = Math.min((HOUR_END - HOUR_START) * HOUR_PX, (entry.end - HOUR_START * 60) / 60 * HOUR_PX)
      blocks.push({ item: entry.item, top, height: Math.max(22, bottom - top), left: entry.column / columnEnds.length * 100, width: 100 / columnEnds.length })
    }
    cluster = []
  }
  for (const entry of dayItems) {
    if (cluster.length && entry.start >= clusterEnd) { flush(); clusterEnd = -1 }
    cluster.push(entry)
    clusterEnd = Math.max(clusterEnd, entry.end)
  }
  if (cluster.length) flush()
  return blocks
}

async function load() {
  error.value = ''
  try {
    const payload = await portalApi.listDeliverySchedules(range.value[0], range.value[1])
    items.value = payload.items ?? []
  } catch (err) {
    items.value = []
    error.value = `${copy.value.loadFailed}: ${err?.message || ''}`
  }
}

function shift(direction) {
  const date = cursor.value
  if (view.value === 'day') cursor.value = addDays(date, direction)
  else if (view.value === 'week') cursor.value = addDays(date, 7 * direction)
  else cursor.value = new Date(date.getFullYear(), date.getMonth() + direction, 1)
}
function goToday() { cursor.value = startOfDay(new Date()) }
function openDay(day) { cursor.value = startOfDay(day); view.value = 'day' }

function resetDraft(date, startTime = '09:00', endTime = '13:00') {
  Object.assign(draft, { customer_name: '', project_name: '', schedule_date: fmt(date), start_time: startTime, end_time: endTime, engineer: '', stage: 'delivery', notes: '' })
}
function openCreate(date, startTime, endTime) {
  modal.id = null; modal.error = ''; modal.open = true
  resetDraft(date, startTime, endTime)
}
function openEdit(item) {
  modal.id = item.id; modal.error = ''; modal.open = true
  Object.assign(draft, {
    customer_name: item.customer_name || '', project_name: item.project_name || '', schedule_date: item.schedule_date,
    start_time: item.start_time, end_time: item.end_time, engineer: item.engineer || '', stage: stageKey(item.stage), notes: item.notes || '',
  })
}
function closeModal() { modal.open = false; modal.id = null }

function onSlotClick(event, day) {
  const rect = event.currentTarget.getBoundingClientRect()
  const hour = Math.min(HOUR_END - 1, HOUR_START + Math.floor((event.clientY - rect.top) / HOUR_PX))
  openCreate(day, `${pad(hour)}:00`, `${pad(Math.min(hour + 1, 23))}:00`)
}

async function save() {
  modal.error = ''
  if (!draft.customer_name.trim() && !draft.project_name.trim()) { modal.error = copy.value.requiredName; return }
  if (!draft.schedule_date || minutes(draft.end_time) <= minutes(draft.start_time)) { modal.error = copy.value.invalidTime; return }
  modal.saving = true
  try {
    if (modal.id) await portalApi.updateDeliverySchedule(modal.id, { ...draft })
    else await portalApi.createDeliverySchedule({ ...draft })
    closeModal()
    await load()
  } catch (err) {
    modal.error = `${copy.value.saveFailed}: ${err?.message || ''}`
  } finally {
    modal.saving = false
  }
}

async function remove() {
  if (!window.confirm(copy.value.confirmDelete)) return
  try {
    await portalApi.deleteDeliverySchedule(modal.id)
    closeModal()
    await load()
  } catch (err) {
    modal.error = `${copy.value.saveFailed}: ${err?.message || ''}`
  }
}

watch(range, load)
onMounted(load)
</script>
