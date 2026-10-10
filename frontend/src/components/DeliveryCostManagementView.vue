<template>
  <section class="flex-1 space-y-5">
    <header class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">DELIVERY & AFTER-SALES</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">交付与售后成本管理</h2>
      </div>
      <div class="flex flex-wrap gap-2">
        <button v-if="canManage" type="button" class="rounded-lg bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800" @click="openAssumptions">成本假设</button>
        <button type="button" class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" :disabled="loading" @click="loadProjects">
          刷新
        </button>
      </div>
    </header>

    <div v-if="notice" class="rounded-lg border px-4 py-3 text-sm" :class="noticeType === 'error' ? 'border-rose-200 bg-rose-50 text-rose-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800'">
      {{ notice }}
    </div>

    <nav class="flex gap-1 border-b border-slate-200" aria-label="项目类型">
      <button v-for="item in projectTypes" :key="item.key" type="button" class="border-b-2 px-4 py-3 text-sm font-semibold transition" :class="activeType === item.key ? 'border-cyan-700 text-cyan-800' : 'border-transparent text-slate-500 hover:text-slate-900'" @click="activeType = item.key">
        {{ item.label }} <span class="ml-1 text-xs font-normal text-slate-400">{{ countByType(item.key) }}</span>
      </button>
    </nav>

    <div v-if="activeType === '418'" class="flex flex-wrap items-center gap-3">
      <label for="delivery-cost-customer-filter" class="text-sm font-semibold text-slate-700">客户筛选</label>
      <select id="delivery-cost-customer-filter" v-model="selectedCustomer" class="min-w-56 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800">
        <option value="">全部客户</option>
        <option v-for="name in gridScaleCustomers" :key="name" :value="name">{{ name }}</option>
      </select>
    </div>

    <div class="grid gap-3 md:grid-cols-2">
      <article class="relative overflow-hidden border-l-4 border-cyan-700 bg-white px-5 py-5 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">总交付成本</p>
        <p class="mt-2 text-3xl font-bold tabular-nums text-slate-900">¥ {{ money(totalDeliveryCost) }}</p>
      </article>
      <article class="relative overflow-hidden border-l-4 border-amber-500 bg-white px-5 py-5 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">总售后成本</p>
        <p class="mt-2 text-3xl font-bold tabular-nums text-slate-900">¥ {{ money(totalAfterSalesCost) }}</p>
      </article>
    </div>
    <div class="grid gap-3 sm:grid-cols-2">
      <div class="bg-slate-100 px-4 py-3"><p class="text-xs text-slate-500">{{ activeType === '418' ? '项目数' : '客户数' }}</p><p class="mt-1 text-lg font-semibold tabular-nums text-slate-800">{{ visibleProjects.length }}</p></div>
      <div class="bg-slate-100 px-4 py-3"><p class="text-xs text-slate-500">售后出差次数</p><p class="mt-1 text-lg font-semibold tabular-nums text-slate-800">{{ totalTripCount }}</p></div>
    </div>

    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h3 class="text-sm font-semibold text-slate-800">{{ activeType }} 项目成本明细</h3>
        <span class="text-xs text-slate-500">金额：元</span>
      </div>
      <div v-if="loading" class="px-5 py-12 text-center text-sm text-slate-500">正在加载成本记录…</div>
      <div v-else-if="!visibleProjects.length" class="px-5 py-12 text-center text-sm text-slate-500">暂无匹配的项目成本记录。</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-[820px] w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs font-semibold text-slate-500">
            <tr>
              <th class="px-4 py-3">{{ activeType === '418' ? '项目名称' : '客户名称' }}</th>
              <th v-if="activeType === '418'" class="px-4 py-3">客户名称</th>
              <th class="px-4 py-3">交付人数</th><th class="px-4 py-3">售后出差</th>
              <th class="px-4 py-3">总交付成本</th><th class="px-4 py-3">总售后成本</th><th class="px-4 py-3">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <template v-for="project in visibleProjects" :key="project.id">
              <tr class="hover:bg-slate-50/70">
                <td class="whitespace-nowrap px-4 py-3 font-semibold text-slate-900">{{ project.project_name || project.customer_name }}</td>
                <td v-if="activeType === '418'" class="whitespace-nowrap px-4 py-3 text-slate-600">{{ project.customer_name || '—' }}</td>
                <td class="px-4 py-3 tabular-nums">{{ project.delivery?.delivery_headcount ?? '—' }}</td>
                <td class="px-4 py-3 tabular-nums">{{ project.after_sales.trip_count }}</td>
                <td class="px-4 py-3 font-semibold tabular-nums">{{ money(deliveryTotal(project)) }}</td>
                <td class="px-4 py-3 font-semibold tabular-nums">{{ money(afterSalesTotal(project)) }}</td>
                <td class="whitespace-nowrap px-4 py-3">
                  <button type="button" class="mr-3 text-xs font-semibold text-cyan-800 hover:text-cyan-950" @click="toggleEntries(project.id)">{{ expandedId === project.id ? '收起明细' : '展开明细' }}</button>
                </td>
              </tr>
              <tr v-if="expandedId === project.id">
                <td :colspan="activeType === '418' ? 7 : 6" class="bg-slate-50 px-4 py-4">
                  <div class="overflow-x-auto">
                    <table class="w-full min-w-[760px] text-left text-xs">
                      <thead class="text-slate-500"><tr><th class="pb-2 pr-4">类型 / 日期</th><th class="pb-2 pr-4">记录 / 人数</th><th class="pb-2 pr-4">差旅</th><th class="pb-2 pr-4">用工</th><th class="pb-2 pr-4">工具</th><th class="pb-2 pr-4">硬件</th><th v-if="canManage" class="pb-2">操作</th></tr></thead>
                      <tbody class="divide-y divide-slate-200">
                        <tr v-if="project.delivery" class="font-medium text-slate-700">
                          <td class="py-2 pr-4">交付成本</td><td class="py-2 pr-4">{{ project.delivery.delivery_headcount }} 人</td>
                          <td v-for="field in costFields" :key="field.key" class="py-2 pr-4"><div class="flex items-center gap-2"><span>{{ money(project.delivery[field.key]) }}</span><button type="button" class="text-[10px] font-semibold text-cyan-700 hover:text-cyan-950" :title="project.delivery[`${field.key}_note`] || '添加备注'" :aria-label="project.delivery[`${field.key}_note`] ? '查看或编辑备注' : '添加备注'" @click="toggleNoteEditor('delivery', project.delivery.id, field, project.delivery[`${field.key}_note`])">备注</button></div></td>
                          <td v-if="canManage" class="py-2"><button type="button" class="font-semibold text-cyan-800 hover:text-cyan-950" @click="openEdit(project)">编辑</button></td>
                        </tr>
                        <tr v-if="noteEditor.open && noteEditor.kind === 'delivery' && noteEditor.id === project.delivery?.id">
                          <td :colspan="canManage ? 7 : 6" class="pb-3"><div class="rounded-lg border border-cyan-200 bg-white p-3"><label class="block text-xs font-semibold text-slate-600">{{ noteEditor.field?.label }}备注<textarea v-model="noteEditor.text" rows="2" maxlength="2000" :readonly="!canManage" class="mt-2 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-800 read-only:bg-slate-50" placeholder="填写这项费用的说明" /></label><div class="mt-2 flex justify-end gap-2"><button type="button" class="rounded-md px-3 py-1.5 text-xs font-semibold text-slate-500 hover:bg-slate-100" @click="closeNoteEditor">关闭</button><button v-if="canManage" type="button" class="rounded-md bg-cyan-700 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50" :disabled="saving" @click="saveNote">{{ saving ? '保存中…' : '保存备注' }}</button></div></div></td>
                        </tr>
                        <tr v-for="entry in project.entries" :key="entry.id">
                          <td class="py-2 pr-4">现场售后 · {{ entry.event_date || '—' }}</td><td class="py-2 pr-4">{{ entry.after_sales_log_id ? `售后记录 #${entry.after_sales_log_id}` : entry.reference || `导入批次 ${entry.import_batch_id.slice(0, 8)}` }}</td>
                          <td v-for="field in costFields" :key="field.key" class="py-2 pr-4"><div class="flex items-center gap-2"><span>{{ money(entry[field.key]) }}</span><button type="button" class="text-[10px] font-semibold text-cyan-700 hover:text-cyan-950" :title="entry[`${field.key}_note`] || '添加备注'" :aria-label="entry[`${field.key}_note`] ? '查看或编辑备注' : '添加备注'" @click="toggleNoteEditor('after-sales', entry.id, field, entry[`${field.key}_note`])">备注</button></div></td>
                          <td v-if="canManage" class="py-2"><button type="button" class="mr-3 font-semibold text-cyan-800 hover:text-cyan-950" @click="openAfterSalesEdit(entry)">编辑</button><button v-if="!entry.after_sales_log_id" type="button" class="font-semibold text-rose-600" @click="removeEntry(entry.id)">删除</button><span v-else class="text-slate-400">源记录联动</span></td>
                        </tr>
                        <tr v-for="entry in project.entries" :key="`note-${entry.id}`" v-if="noteEditor.open && noteEditor.kind === 'after-sales' && noteEditor.id === entry.id">
                          <td :colspan="canManage ? 7 : 6" class="pb-3"><div class="rounded-lg border border-cyan-200 bg-white p-3"><label class="block text-xs font-semibold text-slate-600">{{ noteEditor.field?.label }}备注<textarea v-model="noteEditor.text" rows="2" maxlength="2000" :readonly="!canManage" class="mt-2 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-800 read-only:bg-slate-50" placeholder="填写这项费用的说明" /></label><div class="mt-2 flex justify-end gap-2"><button type="button" class="rounded-md px-3 py-1.5 text-xs font-semibold text-slate-500 hover:bg-slate-100" @click="closeNoteEditor">关闭</button><button v-if="canManage" type="button" class="rounded-md bg-cyan-700 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50" :disabled="saving" @click="saveNote">{{ saving ? '保存中…' : '保存备注' }}</button></div></div></td>
                        </tr>
                        <tr v-if="!project.delivery && !project.entries.length"><td :colspan="canManage ? 7 : 6" class="py-3 text-slate-500">暂无成本明细</td></tr>
                      </tbody>
                    </table>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="modalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 py-6" @click.self="modalOpen = false">
      <form class="max-h-full w-full max-w-xl overflow-y-auto rounded-xl bg-white p-5 shadow-2xl" @submit.prevent="saveDelivery">
        <div class="flex items-start justify-between gap-3"><div><p class="text-xs font-semibold uppercase tracking-wider text-cyan-700">DELIVERY COST</p><h3 class="mt-1 text-lg font-semibold text-slate-900">编辑交付成本</h3><p class="mt-1 text-sm text-slate-500">{{ draft.project_name || draft.customer_name }}</p></div><button type="button" class="rounded-md px-2 py-1 text-lg text-slate-500 hover:bg-slate-100" aria-label="关闭" @click="modalOpen = false">×</button></div>
        <div class="mt-5 grid gap-4 sm:grid-cols-2">
          <label class="text-sm font-medium text-slate-700">交付人数<input v-model.number="draft.delivery_headcount" type="number" min="0" step="1" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
          <label class="text-sm font-medium text-slate-700">总差旅成本<input v-model.number="draft.travel_cost" type="number" min="0" step="0.01" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
          <label class="text-sm font-medium text-slate-700">总用工成本<input v-model.number="draft.labor_cost" type="number" min="0" step="0.01" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
          <label class="text-sm font-medium text-slate-700">现场工具成本<input v-model.number="draft.tool_cost" type="number" min="0" step="0.01" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
          <label class="text-sm font-medium text-slate-700">现场硬件成本<input v-model.number="draft.hardware_cost" type="number" min="0" step="0.01" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
        </div>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600" @click="modalOpen = false">取消</button><button type="submit" class="rounded-lg bg-cyan-700 px-4 py-2 text-sm font-semibold text-white" :disabled="saving">{{ saving ? '保存中…' : '保存' }}</button></div>
      </form>
    </div>

    <div v-if="detailEdit.open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 py-6" @click.self="detailEdit.open = false">
      <form class="w-full max-w-lg rounded-xl bg-white p-5 shadow-2xl" @submit.prevent="saveDetailEdit">
        <h3 class="text-lg font-semibold text-slate-900">编辑售后成本</h3>
        <div class="mt-4 grid gap-4 sm:grid-cols-2">
          <label v-for="field in costFields" :key="field.key" class="text-sm font-medium text-slate-700">{{ field.label }}<input v-model.number="detailDraft[field.key]" type="number" min="0" step="0.01" required class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
        </div>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600" @click="detailEdit.open = false">取消</button><button type="submit" class="rounded-lg bg-cyan-700 px-4 py-2 text-sm font-semibold text-white" :disabled="saving">{{ saving ? '保存中…' : '保存' }}</button></div>
      </form>
    </div>

    <div v-if="assumptionsOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 py-6" @click.self="assumptionsOpen = false">
      <section class="max-h-full w-full max-w-3xl overflow-y-auto rounded-xl bg-white p-5 shadow-2xl">
        <header class="flex items-start justify-between gap-3"><div><p class="text-xs font-semibold uppercase tracking-wider text-cyan-700">COST ASSUMPTIONS</p><h3 class="mt-1 text-lg font-semibold text-slate-900">成本假设</h3></div><button type="button" class="rounded-md px-2 py-1 text-lg text-slate-500 hover:bg-slate-100" aria-label="关闭" @click="assumptionsOpen = false">×</button></header>
        <p v-if="assumptionNotice" class="mt-3 rounded-md border px-3 py-2 text-sm" :class="assumptionNoticeType === 'error' ? 'border-rose-200 bg-rose-50 text-rose-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800'">{{ assumptionNotice }}</p>
        <form v-if="canManage" class="mt-4 grid gap-3 rounded-lg bg-slate-50 p-3 sm:grid-cols-[1fr_150px_1.5fr_auto]" @submit.prevent="saveAssumption">
          <input v-model.trim="assumptionDraft.name" required maxlength="120" class="rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="假设名称" />
          <input v-model.number="assumptionDraft.default_amount" required min="0" step="0.01" type="number" class="rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="默认金额" />
          <input v-model.trim="assumptionDraft.description" maxlength="500" class="rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="说明（可选）" />
          <button type="submit" class="rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold text-white" :disabled="saving">{{ assumptionEditingId ? '保存修改' : '添加' }}</button>
        </form>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full min-w-[560px] text-left text-sm"><thead class="border-b border-slate-200 text-xs text-slate-500"><tr><th class="px-3 py-2">假设名称</th><th class="px-3 py-2">默认金额</th><th class="px-3 py-2">说明</th><th class="px-3 py-2">操作</th></tr></thead><tbody class="divide-y divide-slate-100"><tr v-for="item in assumptions" :key="item.id"><td class="px-3 py-3 font-medium text-slate-800">{{ item.name }}</td><td class="px-3 py-3 tabular-nums">{{ money(item.default_amount) }}</td><td class="px-3 py-3 text-slate-600">{{ item.description || '—' }}</td><td class="whitespace-nowrap px-3 py-3"><button v-if="canManage" type="button" class="mr-3 text-xs font-semibold text-cyan-800" @click="editAssumption(item)">编辑</button><button v-if="canManage" type="button" class="text-xs font-semibold text-rose-600" @click="deleteAssumption(item)">删除</button></td></tr><tr v-if="!assumptions.length"><td colspan="4" class="px-3 py-8 text-center text-sm text-slate-500">暂无成本假设</td></tr></tbody></table>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { portalApi } from '../services/portalApi'

const props = defineProps({
  canManage: { type: Boolean, default: false },
})
const projectTypes = [
  { key: '418', label: '418 项目' },
  { key: '250', label: '250 项目' },
  { key: '100C', label: '100C 项目' },
]
const activeType = ref('418')
const selectedCustomer = ref('')
const projects = ref([])
const loading = ref(false)
const saving = ref(false)
const modalOpen = ref(false)
const editingId = ref(null)
const expandedId = ref(null)
const notice = ref('')
const noticeType = ref('success')
const draft = reactive({ project_type: '418', project_name: '', customer_name: '', delivery_headcount: 0, travel_cost: 0, labor_cost: 0, tool_cost: 0, hardware_cost: 0 })
const detailEdit = reactive({ open: false, kind: '', id: null })
const noteEditor = reactive({ open: false, kind: '', id: null, field: null, text: '' })
const detailDraft = reactive({ travel_cost: 0, labor_cost: 0, tool_cost: 0, hardware_cost: 0 })
const assumptionsOpen = ref(false)
const assumptions = ref([])
const assumptionNotice = ref('')
const assumptionNoticeType = ref('success')
const assumptionEditingId = ref(null)
const assumptionDraft = reactive({ name: '', default_amount: 0, description: '' })
const costFields = [
  { key: 'travel_cost', label: '差旅' },
  { key: 'labor_cost', label: '用工' },
  { key: 'tool_cost', label: '工具' },
  { key: 'hardware_cost', label: '硬件' },
]

const typeProjects = computed(() => projects.value.filter((item) => item.project_type === activeType.value))
const gridScaleCustomers = computed(() => [...new Set(projects.value.filter((item) => item.project_type === '418').map((item) => item.customer_name).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'zh-CN')))
const visibleProjects = computed(() => typeProjects.value.filter((item) => activeType.value !== '418' || !selectedCustomer.value || item.customer_name === selectedCustomer.value))
const totalDeliveryCost = computed(() => visibleProjects.value.reduce((sum, item) => sum + deliveryTotal(item), 0))
const totalAfterSalesCost = computed(() => visibleProjects.value.reduce((sum, item) => sum + afterSalesTotal(item), 0))
const totalTripCount = computed(() => visibleProjects.value.reduce((sum, item) => sum + item.after_sales.trip_count, 0))

function deliveryTotal(item) {
  return ['travel_cost', 'labor_cost', 'tool_cost', 'hardware_cost'].reduce((sum, key) => sum + Number(item.delivery?.[key] || 0), 0)
}

function afterSalesTotal(item) {
  return ['travel_cost', 'labor_cost', 'tool_cost', 'hardware_cost'].reduce((sum, key) => sum + Number(item.after_sales?.[key] || 0), 0)
}

function money(value) {
  return Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function countByType(type) {
  return projects.value.filter((item) => item.project_type === type).length
}

function noteKey(kind, id, fieldKey) {
  return `${kind}:${id}:${fieldKey}`
}

function showNotice(message, type = 'success') {
  notice.value = message
  noticeType.value = type
}

async function loadProjects() {
  loading.value = true
  try {
    const response = await portalApi.listDeliveryCostProjects()
    projects.value = response.items || []
  } catch (error) {
    showNotice(error.message || '成本记录加载失败', 'error')
  } finally {
    loading.value = false
  }
}

function openEdit(project) {
  editingId.value = project.delivery.id
  Object.assign(draft, {
    project_type: project.project_type,
    project_name: project.project_name,
    customer_name: project.customer_name,
    delivery_headcount: project.delivery.delivery_headcount,
    travel_cost: project.delivery.travel_cost,
    labor_cost: project.delivery.labor_cost,
    tool_cost: project.delivery.tool_cost,
    hardware_cost: project.delivery.hardware_cost || 0,
  })
  modalOpen.value = true
}

function openAfterSalesEdit(entry) {
  detailEdit.open = true
  detailEdit.kind = 'after-sales'
  detailEdit.id = entry.id
  for (const field of costFields) detailDraft[field.key] = Number(entry[field.key] || 0)
}

function toggleNoteEditor(kind, id, field, note) {
  const key = noteKey(kind, id, field.key)
  if (noteEditor.open && noteKey(noteEditor.kind, noteEditor.id, noteEditor.field?.key) === key) {
    closeNoteEditor()
    return
  }
  noteEditor.open = true
  noteEditor.kind = kind
  noteEditor.id = id
  noteEditor.field = field
  noteEditor.text = note || ''
}

function closeNoteEditor() {
  noteEditor.open = false
  noteEditor.kind = ''
  noteEditor.id = null
  noteEditor.field = null
  noteEditor.text = ''
}

async function saveDetailEdit() {
  saving.value = true
  try {
    const payload = Object.fromEntries(costFields.map(({ key }) => [key, Number(detailDraft[key]) || 0]))
    await portalApi.updateAfterSalesCostEntry(detailEdit.id, payload)
    detailEdit.open = false
    showNotice('成本明细已保存')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '成本明细保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function saveNote() {
  saving.value = true
  try {
    const update = noteEditor.kind === 'delivery' ? portalApi.updateDeliveryCostNote : portalApi.updateAfterSalesCostNote
    await update(noteEditor.id, { field: `${noteEditor.field.key}_note`, note: noteEditor.text })
    closeNoteEditor()
    showNotice('备注已保存')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '备注保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function saveDelivery() {
  saving.value = true
  try {
    const payload = { ...draft }
    await portalApi.updateDeliveryCost(editingId.value, payload)
    modalOpen.value = false
    showNotice('交付成本已保存')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

function resetAssumptionDraft() {
  assumptionEditingId.value = null
  Object.assign(assumptionDraft, { name: '', default_amount: 0, description: '' })
}

async function openAssumptions() {
  assumptionsOpen.value = true
  assumptionNotice.value = ''
  resetAssumptionDraft()
  await loadAssumptions()
}

async function loadAssumptions() {
  try {
    const response = await portalApi.listCostAssumptions()
    assumptions.value = response.items || []
  } catch (error) {
    assumptionNotice.value = error.message || '成本假设加载失败'
    assumptionNoticeType.value = 'error'
  }
}

function editAssumption(item) {
  assumptionEditingId.value = item.id
  Object.assign(assumptionDraft, { name: item.name, default_amount: item.default_amount, description: item.description || '' })
}

async function saveAssumption() {
  saving.value = true
  try {
    if (assumptionEditingId.value) await portalApi.updateCostAssumption(assumptionEditingId.value, { ...assumptionDraft })
    else await portalApi.createCostAssumption({ ...assumptionDraft })
    resetAssumptionDraft()
    await loadAssumptions()
    assumptionNotice.value = '成本假设已保存'
    assumptionNoticeType.value = 'success'
  } catch (error) {
    assumptionNotice.value = error.message || '成本假设保存失败'
    assumptionNoticeType.value = 'error'
  } finally {
    saving.value = false
  }
}

async function deleteAssumption(item) {
  if (!window.confirm(`确认删除成本假设“${item.name}”？`)) return
  try {
    await portalApi.deleteCostAssumption(item.id)
    if (assumptionEditingId.value === item.id) resetAssumptionDraft()
    await loadAssumptions()
    assumptionNotice.value = '成本假设已删除'
    assumptionNoticeType.value = 'success'
  } catch (error) {
    assumptionNotice.value = error.message || '成本假设删除失败'
    assumptionNoticeType.value = 'error'
  }
}

async function removeEntry(entryId) {
  if (!window.confirm('确认删除这条售后成本明细？')) return
  try {
    await portalApi.deleteAfterSalesCostEntry(entryId)
    showNotice('售后成本明细已删除')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '删除失败', 'error')
  }
}

function toggleEntries(projectId) {
  expandedId.value = expandedId.value === projectId ? null : projectId
}

onMounted(loadProjects)
</script>