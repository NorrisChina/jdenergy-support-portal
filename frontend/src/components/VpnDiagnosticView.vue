<template>
  <section class="vpn-diagnostic flex min-h-0 flex-1 flex-col">
    <header class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-wider text-sky-700">Remote Operations</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-950">{{ copy.title }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ copy.subtitle }}</p>
      </div>
      <div class="flex items-center gap-2 text-xs text-slate-500">
        <span class="h-2 w-2 rounded-full" :class="socketState === 'connected' ? 'bg-emerald-500' : socketState === 'connecting' ? 'bg-amber-500' : 'bg-slate-300'"></span>
        {{ terminalStatusLabel }}
      </div>
    </header>

    <div class="grid min-h-[720px] flex-1 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm xl:grid-cols-[35%_65%]">
      <div class="scroll-thin overflow-y-auto border-b border-slate-200 bg-slate-50 p-4 xl:border-b-0 xl:border-r">
        <section class="border-b border-slate-200 pb-5">
          <div class="flex items-center justify-between gap-3">
            <h3 class="text-sm font-semibold text-slate-900">{{ copy.siteManagement }}</h3>
            <button v-if="isSuperAdmin" type="button" class="text-xs font-semibold text-sky-700 hover:text-sky-900" @click="openSiteEditor()">{{ copy.newSite }}</button>
          </div>
          <select v-model="selectedSiteId" class="mt-3 w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-sky-500">
            <option value="">{{ copy.selectSite }}</option>
            <option v-for="site in sites" :key="site.id" :value="String(site.id)">{{ site.name }} · {{ site.vpn_ip }}</option>
          </select>
          <div v-if="selectedSite" class="mt-3 rounded-md border border-slate-200 bg-white p-3 text-xs text-slate-600">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-mono text-slate-800">{{ selectedSite.vpn_ip }}</p>
                <p class="mt-1">{{ selectedSite.customer_company || copy.unbound }}</p>
              </div>
              <button v-if="isSuperAdmin" type="button" class="font-semibold text-sky-700" @click="openSiteEditor(selectedSite)">{{ copy.edit }}</button>
            </div>
          </div>
          <button type="button" :disabled="!selectedSiteId || socketState === 'connecting'" class="mt-3 w-full rounded-md bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40" @click="connectTerminal(Number(selectedSiteId))">{{ copy.connectSite }}</button>
        </section>

        <section class="border-b border-slate-200 py-5">
          <h3 class="text-sm font-semibold text-slate-900">{{ copy.exportPanel }}</h3>
          <label class="mt-3 block text-xs font-medium text-slate-600">eBlock ID
            <input v-model.number="exportDraft.eblock_id" type="number" min="1" class="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-500" />
          </label>
          <div class="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
            <label class="block text-xs font-medium text-slate-600">{{ copy.startTime }}
              <input v-model="exportDraft.start_time" type="datetime-local" step="1" class="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-500" />
            </label>
            <label class="block text-xs font-medium text-slate-600">{{ copy.endTime }}
              <input v-model="exportDraft.end_time" type="datetime-local" step="1" class="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-sky-500" />
            </label>
          </div>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-xs font-medium text-slate-600">{{ copy.tables }}</span>
            <div class="flex items-center gap-3">
              <button v-if="isSuperAdmin" type="button" class="text-xs font-semibold text-slate-600 hover:text-slate-950" @click="openTableManager">⚙ {{ copy.manageTables }}</button>
              <button type="button" class="text-xs font-semibold text-sky-700" @click="toggleAllTables">{{ allTablesSelected ? copy.clearAll : copy.selectAll }}</button>
            </div>
          </div>
          <div class="mt-2 grid grid-cols-2 gap-2">
            <label v-for="table in exportTables" :key="table.id" class="flex min-w-0 items-center gap-2 rounded-md border border-slate-200 bg-white px-2.5 py-2 text-xs text-slate-700">
              <input v-model="exportDraft.tables" type="checkbox" :value="table.table_name" class="h-4 w-4 shrink-0 accent-sky-600" />
              <span class="min-w-0 truncate font-mono" :title="table.table_name">{{ table.table_name }}</span>
              <span v-if="table.extra_where" class="ml-auto shrink-0 rounded bg-amber-50 px-1.5 py-0.5 font-mono text-[10px] text-amber-700">{{ compactWhere(table.extra_where) }}</span>
            </label>
          </div>
          <button type="button" :disabled="submitting || !canSubmitExport" class="mt-4 w-full rounded-md bg-sky-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-sky-800 disabled:cursor-not-allowed disabled:opacity-40" @click="submitExport">{{ submitting ? copy.submitting : copy.runExport }}</button>
        </section>

        <section class="pt-5">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-slate-900">{{ copy.history }}</h3>
            <button type="button" class="text-xs font-semibold text-sky-700" @click="loadTasks">{{ copy.refresh }}</button>
          </div>
          <div class="mt-3 space-y-2">
            <article v-for="task in tasks" :key="task.id" class="rounded-md border border-slate-200 bg-white p-3">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="truncate text-xs font-semibold text-slate-800">{{ task.file_name || `${task.site_name} #${task.id}` }}</p>
                  <p class="mt-1 text-[11px] text-slate-500">{{ formatDate(task.created_at) }}</p>
                </div>
                <span class="rounded-full px-2 py-1 text-[10px] font-semibold" :class="statusClass(task.status)">{{ statusLabel(task.status) }}</span>
              </div>
              <p class="mt-2 text-[11px] leading-5 text-slate-500">{{ formatDate(task.start_time) }}<br />{{ formatDate(task.end_time) }}</p>
              <p v-if="task.error_message" class="mt-2 line-clamp-2 text-[11px] text-rose-600" :title="task.error_message">{{ task.error_message }}</p>
              <button v-if="task.status === 'completed'" type="button" class="mt-2 text-xs font-semibold text-sky-700 hover:text-sky-900" @click="downloadTask(task)">{{ copy.download }}</button>
            </article>
            <p v-if="!tasks.length" class="rounded-md border border-dashed border-slate-300 py-8 text-center text-xs text-slate-400">{{ copy.noHistory }}</p>
          </div>
        </section>
      </div>

      <div class="flex min-h-[560px] min-w-0 flex-col bg-[#101418]">
        <div class="flex items-center justify-between border-b border-white/10 px-4 py-3">
          <div class="flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full bg-rose-400"></span><span class="h-2.5 w-2.5 rounded-full bg-amber-400"></span><span class="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
            <span class="ml-2 font-mono text-xs text-slate-400">{{ terminalTarget }}</span>
          </div>
          <button type="button" class="text-xs font-semibold text-slate-400 hover:text-white" @click="connectTerminal(null)">{{ copy.jumpHost }}</button>
        </div>
        <div ref="terminalElement" class="min-h-0 flex-1 p-2"></div>
      </div>
    </div>

    <div v-if="siteEditorOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4" @click.self="siteEditorOpen = false">
      <form class="w-full max-w-lg rounded-lg bg-white p-6 shadow-2xl" @submit.prevent="saveSite">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-slate-950">{{ copy.siteEditor }}</h3>
          <button type="button" class="text-sm text-slate-500" @click="siteEditorOpen = false">{{ copy.close }}</button>
        </div>
        <label class="mt-5 block text-xs font-medium text-slate-600">{{ copy.siteName }}
          <input v-model="siteDraft.name" required class="mt-1.5 w-full rounded-md border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-sky-500" />
        </label>
        <label class="mt-4 block text-xs font-medium text-slate-600">Station VPN IP
          <input v-model="siteDraft.vpn_ip" required inputmode="decimal" class="mt-1.5 w-full rounded-md border border-slate-300 px-3 py-2.5 font-mono text-sm outline-none focus:border-sky-500" />
        </label>
        <label class="mt-4 block text-xs font-medium text-slate-600">{{ copy.customer }}
          <select v-model="siteDraft.customer_company" class="mt-1.5 w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none focus:border-sky-500">
            <option value="">{{ copy.unbound }}</option>
            <option v-for="customer in customerOptions" :key="customer" :value="customer">{{ customer }}</option>
          </select>
        </label>
        <div class="mt-6 flex justify-end gap-3">
          <button v-if="siteEditingId" type="button" class="mr-auto text-sm font-semibold text-rose-600" @click="removeSite">{{ copy.delete }}</button>
          <button type="button" class="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700" @click="siteEditorOpen = false">{{ copy.cancel }}</button>
          <button type="submit" class="rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white">{{ copy.save }}</button>
        </div>
      </form>
    </div>

    <div v-if="tableManagerOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4" @click.self="tableManagerOpen = false">
      <div class="flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-lg bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h3 class="text-lg font-semibold text-slate-950">{{ copy.tableManager }}</h3>
          <button type="button" class="text-sm text-slate-500 hover:text-slate-900" @click="tableManagerOpen = false">{{ copy.close }}</button>
        </div>
        <div class="grid min-h-0 flex-1 overflow-y-auto lg:grid-cols-[1.15fr_.85fr]">
          <div class="border-b border-slate-200 p-5 lg:border-b-0 lg:border-r">
            <div class="space-y-2">
              <div v-for="table in exportTables" :key="table.id" class="flex items-center gap-3 border-b border-slate-100 py-3">
                <div class="min-w-0 flex-1">
                  <p class="truncate font-mono text-xs font-semibold text-slate-800">{{ table.table_name }}</p>
                  <p class="mt-1 text-[11px] text-slate-500">Sheet: {{ table.sheet_name }} · {{ table.has_eblock_id ? 'eBlock ID' : copy.noEblock }}<span v-if="table.extra_where"> · {{ table.extra_where }}</span></p>
                </div>
                <span class="text-[10px] font-semibold" :class="table.is_enabled ? 'text-emerald-700' : 'text-slate-400'">{{ table.is_enabled ? copy.enabled : copy.disabled }}</span>
                <button type="button" class="text-xs font-semibold text-sky-700" @click="editDiagnosticTable(table)">{{ copy.edit }}</button>
                <button type="button" class="text-xs font-semibold text-rose-600" @click="removeDiagnosticTable(table)">{{ copy.delete }}</button>
              </div>
            </div>
          </div>
          <form class="p-5" @submit.prevent="saveDiagnosticTable">
            <h4 class="text-sm font-semibold text-slate-900">{{ tableEditingId ? copy.editTable : copy.newTable }}</h4>
            <p v-if="tableError" class="mt-3 rounded-md bg-rose-50 px-3 py-2 text-xs text-rose-700">{{ tableError }}</p>
            <label class="mt-4 block text-xs font-medium text-slate-600">{{ copy.tableName }}
              <input v-model="tableDraft.table_name" required placeholder="eblock.pcs_tc" class="mt-1.5 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm outline-none focus:border-sky-500" />
            </label>
            <label class="mt-3 block text-xs font-medium text-slate-600">{{ copy.sheetName }}
              <input v-model="tableDraft.sheet_name" required placeholder="pcs_tc" maxlength="31" class="mt-1.5 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm outline-none focus:border-sky-500" />
            </label>
            <label class="mt-3 block text-xs font-medium text-slate-600">{{ copy.extraWhere }}
              <input v-model="tableDraft.extra_where" placeholder="pcs_id = 1" class="mt-1.5 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm outline-none focus:border-sky-500" />
            </label>
            <label class="mt-3 block text-xs font-medium text-slate-600">{{ copy.sortOrder }}
              <input v-model.number="tableDraft.sort_order" type="number" class="mt-1.5 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500" />
            </label>
            <label class="mt-4 flex items-center gap-2 text-xs text-slate-700"><input v-model="tableDraft.has_eblock_id" type="checkbox" class="h-4 w-4 accent-sky-600" />{{ copy.hasEblock }}</label>
            <label class="mt-3 flex items-center gap-2 text-xs text-slate-700"><input v-model="tableDraft.is_enabled" type="checkbox" class="h-4 w-4 accent-sky-600" />{{ copy.defaultEnabled }}</label>
            <div class="mt-6 flex justify-end gap-3">
              <button v-if="tableEditingId" type="button" class="mr-auto text-sm font-semibold text-slate-600" @click="resetTableDraft">{{ copy.newTable }}</button>
              <button type="button" class="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700" @click="tableManagerOpen = false">{{ copy.cancel }}</button>
              <button type="submit" class="rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white">{{ copy.save }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { WebLinksAddon } from '@xterm/addon-web-links'
import '@xterm/xterm/css/xterm.css'
import { portalApi } from '../services/portalApi'

const props = defineProps({
  isSuperAdmin: { type: Boolean, default: false },
  locale: { type: String, default: 'zh-CN' },
})

const copy = computed(() => props.locale === 'en-US' ? {
  title: 'VPN Remote Diagnostics & Time-Series Export', subtitle: 'Secure dual-hop terminal and automated TDengine exports.', siteManagement: 'Sites', newSite: 'New site', selectSite: 'Select a diagnostic site', unbound: 'Unbound customer', edit: 'Edit', connectSite: 'Connect site', exportPanel: 'TDengine export task', startTime: 'Start time', endTime: 'End time', tables: 'Export tables', selectAll: 'Select all', clearAll: 'Clear', manageTables: 'Manage tables', tableManager: 'Diagnostic export tables', newTable: 'New table', editTable: 'Edit table', tableName: 'Full table name', sheetName: 'Excel Sheet name', extraWhere: 'Extra WHERE condition', sortOrder: 'Sort order', hasEblock: 'Filter by eBlock ID', defaultEnabled: 'Selected by default', enabled: 'Enabled', disabled: 'Disabled', noEblock: 'No eBlock filter', runExport: 'Run and export', submitting: 'Submitting...', history: 'Export history', refresh: 'Refresh', download: 'Download Excel / ZIP', noHistory: 'No export history', jumpHost: 'Jump host', siteEditor: 'Site settings', siteName: 'Site name', customer: 'Customer', close: 'Close', delete: 'Delete', cancel: 'Cancel', save: 'Save', processing: 'Processing', completed: 'Completed', failed: 'Failed', disconnected: 'Disconnected', connecting: 'Connecting', connected: 'Connected', confirmDelete: 'Delete this site?', confirmTableDelete: 'Delete this export table?'
} : {
  title: 'VPN 远程诊断与时序数据导出', subtitle: '双层 SSH 实时终端与 TDengine 无交互自动化取数。', siteManagement: '站点管理', newSite: '新建站点', selectSite: '选择当前调试站点', unbound: '未绑定客户', edit: '编辑', connectSite: '连接站点', exportPanel: 'TDengine 数据导出任务', startTime: '开始时间', endTime: '结束时间', tables: '选择导出表', selectAll: '全选', clearAll: '清空', manageTables: '管理表配置', tableManager: '诊断导出表配置', newTable: '新增表', editTable: '编辑表', tableName: '完整表名', sheetName: 'Excel Sheet 名称', extraWhere: '额外 WHERE 条件', sortOrder: '排序序号', hasEblock: '包含 eBlock ID 过滤', defaultEnabled: '默认勾选', enabled: '已启用', disabled: '未启用', noEblock: '无 eBlock 过滤', runExport: '一键执行并导出数据', submitting: '提交中...', history: '文件下载列表', refresh: '刷新', download: '下载 Excel / ZIP', noHistory: '暂无导出任务', jumpHost: '返回跳板机', siteEditor: '站点配置', siteName: '站点名称', customer: '绑定客户', close: '关闭', delete: '删除', cancel: '取消', save: '保存', processing: '处理中', completed: '已完成', failed: '失败', disconnected: '未连接', connecting: '连接中', connected: '已连接', confirmDelete: '确认删除该站点吗？', confirmTableDelete: '确认删除该导出表吗？'
})

const exportTables = ref([])
const sites = ref([])
const customerOptions = ref([])
const tasks = ref([])
const selectedSiteId = ref('')
const siteEditorOpen = ref(false)
const tableManagerOpen = ref(false)
const tableEditingId = ref(null)
const tableError = ref('')
const siteEditingId = ref(null)
const siteDraft = reactive({ name: '', vpn_ip: '', customer_company: '' })
const tableDraft = reactive({ table_name: '', sheet_name: '', has_eblock_id: true, extra_where: '', sort_order: 0, is_enabled: true })
const submitting = ref(false)
const socketState = ref('disconnected')
const terminalElement = ref(null)
const exportDraft = reactive({ eblock_id: 1, start_time: '', end_time: '', tables: [] })
let terminal = null
let fitAddon = null
let socket = null
let socketReceivedMessage = false
let resizeObserver = null
let taskTimer = null

const selectedSite = computed(() => sites.value.find((site) => String(site.id) === selectedSiteId.value) || null)
const allTablesSelected = computed(() => exportTables.value.length > 0 && exportDraft.tables.length === exportTables.value.length)
const canSubmitExport = computed(() => selectedSiteId.value && exportDraft.start_time && exportDraft.end_time && exportDraft.tables.length)
const terminalStatusLabel = computed(() => copy.value[socketState.value])
const terminalTarget = computed(() => socketState.value === 'connected' && selectedSite.value ? `${selectedSite.value.name} · ${selectedSite.value.vpn_ip}` : 'jump-host')

function initializeDateRange() {
  const end = new Date()
  const start = new Date(end.getTime() - 60 * 60 * 1000)
  const localValue = (value) => new Date(value.getTime() - value.getTimezoneOffset() * 60000).toISOString().slice(0, 19)
  exportDraft.start_time = localValue(start)
  exportDraft.end_time = localValue(end)
}

async function loadSites() {
  const [sitePayload, customerPayload] = await Promise.all([portalApi.listVpnSites(), portalApi.listVpnCustomerOptions()])
  sites.value = sitePayload.items || []
  customerOptions.value = customerPayload.items || []
  if (selectedSiteId.value && !sites.value.some((site) => String(site.id) === selectedSiteId.value)) selectedSiteId.value = ''
}

async function loadDiagnosticTables(resetSelection = false) {
  const payload = await portalApi.listDiagnosticTables()
  exportTables.value = payload.items || []
  const available = new Set(exportTables.value.map((table) => table.table_name))
  exportDraft.tables = resetSelection
    ? exportTables.value.filter((table) => table.is_enabled).map((table) => table.table_name)
    : exportDraft.tables.filter((tableName) => available.has(tableName))
}

async function loadTasks() {
  const payload = await portalApi.listVpnExportTasks(selectedSiteId.value || null)
  tasks.value = payload.items || []
}

function openSiteEditor(site = null) {
  siteEditingId.value = site?.id || null
  Object.assign(siteDraft, { name: site?.name || '', vpn_ip: site?.vpn_ip || '', customer_company: site?.customer_company || '' })
  siteEditorOpen.value = true
}

async function saveSite() {
  const payload = { name: siteDraft.name.trim(), vpn_ip: siteDraft.vpn_ip.trim(), customer_company: siteDraft.customer_company }
  if (siteEditingId.value) await portalApi.updateVpnSite(siteEditingId.value, payload)
  else await portalApi.createVpnSite(payload)
  siteEditorOpen.value = false
  await loadSites()
}

async function removeSite() {
  if (!window.confirm(copy.value.confirmDelete)) return
  await portalApi.deleteVpnSite(siteEditingId.value)
  siteEditorOpen.value = false
  selectedSiteId.value = ''
  await loadSites()
}

function toggleAllTables() {
  exportDraft.tables = allTablesSelected.value ? [] : exportTables.value.map((table) => table.table_name)
}

function compactWhere(value) {
  return value.replace(/\s+/g, '')
}

function resetTableDraft() {
  tableEditingId.value = null
  tableError.value = ''
  Object.assign(tableDraft, { table_name: '', sheet_name: '', has_eblock_id: true, extra_where: '', sort_order: exportTables.value.length * 10 + 10, is_enabled: true })
}

function openTableManager() {
  resetTableDraft()
  tableManagerOpen.value = true
}

function editDiagnosticTable(table) {
  tableEditingId.value = table.id
  tableError.value = ''
  Object.assign(tableDraft, { table_name: table.table_name, sheet_name: table.sheet_name, has_eblock_id: table.has_eblock_id, extra_where: table.extra_where, sort_order: table.sort_order, is_enabled: table.is_enabled })
}

async function saveDiagnosticTable() {
  tableError.value = ''
  try {
    const payload = { ...tableDraft, table_name: tableDraft.table_name.trim(), sheet_name: tableDraft.sheet_name.trim(), extra_where: tableDraft.extra_where.trim() }
    if (tableEditingId.value) await portalApi.updateDiagnosticTable(tableEditingId.value, payload)
    else await portalApi.createDiagnosticTable(payload)
    await loadDiagnosticTables(false)
    resetTableDraft()
  } catch (error) {
    tableError.value = error.message
  }
}

async function removeDiagnosticTable(table) {
  if (!window.confirm(copy.value.confirmTableDelete)) return
  try {
    await portalApi.deleteDiagnosticTable(table.id)
    await loadDiagnosticTables(false)
    if (tableEditingId.value === table.id) resetTableDraft()
  } catch (error) {
    tableError.value = error.message
  }
}

async function submitExport() {
  submitting.value = true
  try {
    await portalApi.createVpnExportTask({ site_id: Number(selectedSiteId.value), eblock_id: Number(exportDraft.eblock_id), start_time: exportDraft.start_time, end_time: exportDraft.end_time, tables: [...exportDraft.tables] })
    await loadTasks()
  } finally {
    submitting.value = false
  }
}

async function downloadTask(task) {
  await portalApi.downloadVpnExport(task.id, task.file_name)
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString(props.locale) : '-'
}

function statusLabel(status) {
  return copy.value[status] || status
}

function statusClass(status) {
  if (status === 'completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'failed') return 'bg-rose-50 text-rose-700'
  return 'bg-amber-50 text-amber-700'
}

async function connectTerminal(siteId) {
  socket?.close()
  socketReceivedMessage = false
  socketState.value = 'connecting'
  terminal?.reset()
  terminal?.writeln(`\x1b[90m${siteId ? 'Connecting to station through jump host...' : 'Connecting to jump host...'}\x1b[0m`)
  try {
    const { ticket } = await portalApi.createVpnTerminalTicket(siteId)
    socket = new WebSocket(portalApi.vpnTerminalWebSocketUrl(ticket))
    socket.addEventListener('open', () => {
      socketState.value = 'connected'
      fitAddon?.fit()
      sendResize()
      terminal?.focus()
    })
    socket.addEventListener('message', (event) => {
      socketReceivedMessage = true
      terminal?.write(event.data)
    })
    socket.addEventListener('close', (event) => {
      socketState.value = 'disconnected'
      const reason = event.reason ? `: ${event.reason}` : ''
      const hint = !socketReceivedMessage && event.code === 1006 ? '\r\nCheck whether the backend is running with VPN_* and TDENGINE_* environment variables.' : ''
      terminal?.writeln(`\r\n\x1b[33mTerminal disconnected (${event.code})${reason}${hint}\x1b[0m`)
    })
    socket.addEventListener('error', () => terminal?.writeln('\r\n\x1b[31mTerminal WebSocket connection failed; check backend and proxy logs.\x1b[0m'))
  } catch (error) {
    socketState.value = 'disconnected'
    terminal?.writeln(`\r\n\x1b[31m${error.message}\x1b[0m`)
  }
}

function sendResize() {
  if (socket?.readyState === WebSocket.OPEN && terminal) socket.send(JSON.stringify({ type: 'resize', cols: terminal.cols, rows: terminal.rows }))
}

watch(selectedSiteId, async (siteId) => {
  await loadTasks()
  if (siteId) await connectTerminal(Number(siteId))
})

onMounted(async () => {
  initializeDateRange()
  terminal = new Terminal({ cursorBlink: true, convertEol: true, fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", monospace', fontSize: 13, theme: { background: '#101418', foreground: '#d7dde5', cursor: '#38bdf8', selectionBackground: '#334155' } })
  fitAddon = new FitAddon()
  terminal.loadAddon(fitAddon)
  terminal.loadAddon(new WebLinksAddon())
  terminal.open(terminalElement.value)
  terminal.onData((data) => { if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: 'input', data })) })
  resizeObserver = new ResizeObserver(() => { nextTick(() => { fitAddon?.fit(); sendResize() }) })
  resizeObserver.observe(terminalElement.value)
  await Promise.all([loadSites(), loadTasks(), loadDiagnosticTables(true)])
  await connectTerminal(null)
  taskTimer = window.setInterval(() => { if (tasks.value.some((task) => task.status === 'processing')) loadTasks() }, 4000)
})

onUnmounted(() => {
  window.clearInterval(taskTimer)
  resizeObserver?.disconnect()
  socket?.close()
  terminal?.dispose()
})
</script>
