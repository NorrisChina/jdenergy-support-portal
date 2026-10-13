<template>
  <section class="flex-1 space-y-5">
    <header class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">DELIVERY & AFTER-SALES</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">交付与售后成本管理</h2>
      </div>
      <div class="flex flex-wrap gap-2">
        <button v-if="canManage && activeType === 'fixed-costs'" type="button" class="rounded-lg border border-cyan-700 bg-white px-3 py-2 text-sm font-semibold text-cyan-800 hover:bg-cyan-50" @click="openFixedCost()">添加固定成本</button>
        <button type="button" class="rounded-lg border border-emerald-700 bg-white px-3 py-2 text-sm font-semibold text-emerald-800 hover:bg-emerald-50 disabled:opacity-50" :disabled="exporting" @click="exportWorkbook">{{ exporting ? '导出中…' : '导出 Excel' }}</button>
        <button v-if="canManage" type="button" class="rounded-lg bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800" @click="openAssumptions">成本假设</button>
        <button type="button" class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" :disabled="loading" @click="loadProjects">
          刷新
        </button>
      </div>
    </header>

    <div v-if="notice" class="rounded-lg border px-4 py-3 text-sm" :class="noticeType === 'error' ? 'border-rose-200 bg-rose-50 text-rose-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800'">
      {{ notice }}
    </div>

    <div class="flex flex-wrap items-center gap-3">
      <label for="delivery-cost-customer-filter" class="text-sm font-semibold text-slate-700">客户名称</label>
      <select id="delivery-cost-customer-filter" v-model="selectedCustomer" class="min-w-56 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800">
        <option value="">全部客户</option>
        <option v-for="name in customerOptions" :key="name" :value="name">{{ name }}</option>
      </select>
    </div>

    <div class="grid gap-3 md:grid-cols-2">
      <article class="relative overflow-hidden border-l-4 border-cyan-700 bg-white px-5 py-5 shadow-sm"><p class="text-xs font-semibold uppercase tracking-wider text-slate-500">总交付成本</p><p class="mt-2 text-3xl font-bold tabular-nums text-slate-900">¥ {{ money(totalDeliveryCost) }}</p></article>
      <article class="relative overflow-hidden border-l-4 border-amber-500 bg-white px-5 py-5 shadow-sm"><p class="text-xs font-semibold uppercase tracking-wider text-slate-500">总售后成本</p><p class="mt-2 text-3xl font-bold tabular-nums text-slate-900">¥ {{ money(totalAfterSalesCost) }}</p></article>
    </div>
    <div class="grid gap-3 sm:grid-cols-3">
      <div class="bg-slate-100 px-4 py-3"><p class="text-xs text-slate-500">项目 / 客户数</p><p class="mt-1 text-lg font-semibold tabular-nums text-slate-800">{{ globalVisibleProjects.length }}</p></div>
      <div class="bg-slate-100 px-4 py-3"><p class="text-xs text-slate-500">售后出差次数</p><p class="mt-1 text-lg font-semibold tabular-nums text-slate-800">{{ totalTripCount }}</p></div>
      <div class="bg-slate-100 px-4 py-3"><p class="text-xs text-slate-500">固定成本记录</p><p class="mt-1 text-lg font-semibold tabular-nums text-slate-800">{{ fixedCostRows.length }}</p></div>
    </div>

    <nav class="flex gap-1 border-b border-slate-200" aria-label="成本类别">
      <button v-for="item in projectTypes" :key="item.key" type="button" class="border-b-2 px-4 py-3 text-sm font-semibold transition" :class="activeType === item.key ? 'border-cyan-700 text-cyan-800' : 'border-transparent text-slate-500 hover:text-slate-900'" @click="activeType = item.key">
        {{ item.label }} <span v-if="item.key !== 'fixed-costs'" class="ml-1 text-xs font-normal text-slate-400">{{ countByType(item.key) }}</span>
      </button>
    </nav>

    <section v-if="activeType === 'fixed-costs'" class="space-y-4">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div><p class="text-xs font-semibold uppercase tracking-wider text-cyan-700">CUSTOMER FIXED COSTS</p><h3 class="mt-1 text-xl font-semibold text-slate-900">客户固定成本记录</h3></div>
      </div>
      <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div v-if="loading" class="px-5 py-12 text-center text-sm text-slate-500">正在加载固定成本…</div>
        <div v-else-if="!fixedCostRows.length" class="px-5 py-12 text-center text-sm text-slate-500">暂无固定成本记录。</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-[980px] w-full text-left text-sm">
            <thead class="bg-slate-50 text-xs font-semibold text-slate-500"><tr><th class="px-4 py-3">客户名称</th><th class="px-4 py-3">费用名称</th><th class="px-4 py-3">每日单价</th><th class="px-4 py-3">开始时间</th><th class="px-4 py-3">结束时间</th><th class="px-4 py-3">总天数</th><th class="px-4 py-3">总金额</th><th class="px-4 py-3">备注</th><th v-if="canManage" class="px-4 py-3">操作</th></tr></thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in fixedCostRows" :key="item.id" class="hover:bg-slate-50/70">
                <td class="whitespace-nowrap px-4 py-3 font-semibold text-slate-900">{{ item.customer_name }}</td><td class="px-4 py-3">{{ item.name }}</td><td class="px-4 py-3 tabular-nums">{{ money(item.daily_price) }}</td><td class="px-4 py-3">{{ item.start_date }}</td><td class="px-4 py-3">{{ item.end_date }}</td><td class="px-4 py-3 tabular-nums">{{ item.total_days }}</td><td class="px-4 py-3 font-semibold tabular-nums">{{ money(item.total_price) }}</td><td class="max-w-56 truncate px-4 py-3" :title="item.note">{{ item.note || '—' }}</td><td v-if="canManage" class="whitespace-nowrap px-4 py-3"><button type="button" class="mr-3 text-xs font-semibold text-cyan-800" @click="openFixedCost(item)">编辑</button><button type="button" class="text-xs font-semibold text-rose-600" @click="deleteFixedCost(item)">删除</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <div v-if="activeType !== 'fixed-costs'" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
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
              <th class="px-4 py-3">交付人天</th><th class="px-4 py-3">售后出差</th>
              <th class="px-4 py-3">总交付成本</th><th class="px-4 py-3">总售后成本</th><th class="px-4 py-3">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <template v-for="project in visibleProjects" :key="project.id">
              <tr class="hover:bg-slate-50/70">
                <td class="whitespace-nowrap px-4 py-3 font-semibold text-slate-900">{{ project.project_name || project.customer_name }}</td>
                <td v-if="activeType === '418'" class="whitespace-nowrap px-4 py-3 text-slate-600">{{ project.customer_name || '—' }}</td>
                <td class="px-4 py-3 tabular-nums">{{ project.delivery?.total_man_days ?? 0 }}</td>
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
                    <table class="w-full min-w-[880px] text-left text-xs">
                      <thead class="text-slate-500"><tr><th class="pb-2 pr-4">记录</th><th class="pb-2 pr-4">总人天</th><th class="pb-2 pr-4">每人天成本</th><th class="pb-2 pr-4">一次性成本</th><th class="pb-2 pr-4">硬件更换</th><th class="pb-2 pr-4">本行总成本</th><th v-if="canManage" class="pb-2">操作</th></tr></thead>
                      <tbody class="divide-y divide-slate-200">
                        <template v-for="line in costLines(project)" :key="`${line.kind}-${line.id}`">
                          <tr class="font-medium text-slate-700">
                            <td class="py-2 pr-4">{{ line.label }}</td>
                            <td class="py-2 pr-4"><div class="flex items-center gap-2"><span>{{ line.item.total_man_days.toLocaleString('zh-CN') }} 天</span><button v-if="canManage" type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleBreakdown(line, 'people')">{{ isBreakdownOpen(line, 'people') ? '收起' : '编辑' }}</button><button v-else type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleBreakdown(line, 'people')">人员</button><button type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleNoteEditor(line.kind, line.id, noteFields.totalManDays, line.item.total_man_days_note)">备注</button></div></td>
                            <td class="py-2 pr-4"><div class="flex items-center gap-2"><span>{{ money(line.item.per_day_cost) }}</span><button type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleBreakdown(line, 'per-day')">{{ isBreakdownOpen(line, 'per-day') ? '收起' : canManage ? '编辑' : '分项' }}</button><button type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleNoteEditor(line.kind, line.id, noteFields.perDay, line.item.per_day_cost_note)">备注</button></div></td>
                            <td class="py-2 pr-4"><div class="flex items-center gap-2"><span>{{ money(line.item.one_time_cost) }}</span><button type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleBreakdown(line, 'one-time')">{{ isBreakdownOpen(line, 'one-time') ? '收起' : canManage ? '编辑' : '分项' }}</button><button type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleNoteEditor(line.kind, line.id, noteFields.oneTime, line.item.one_time_cost_note)">备注</button></div></td>
                            <td class="py-2 pr-4"><div class="flex items-center gap-2"><template v-if="isInlineCostOpen(line, 'hardware_replacement_cost')"><input v-model.number="inlineCostEditor.value" type="number" min="0" step="0.01" class="w-24 rounded border border-slate-300 px-2 py-1 text-xs tabular-nums"/><button type="button" class="text-[10px] font-semibold text-cyan-800" @click="saveInlineCost(line)">保存</button><button type="button" class="text-[10px] text-slate-500" @click="closeInlineCostEditor">取消</button></template><template v-else><span>{{ money(line.item.hardware_replacement_cost) }}</span><button v-if="canManage" type="button" class="text-[10px] font-semibold text-cyan-700" @click="openInlineCostEditor(line, 'hardware_replacement_cost')">编辑</button></template><button type="button" class="text-[10px] font-semibold text-cyan-700" @click="toggleNoteEditor(line.kind, line.id, noteFields.hardware, line.item.hardware_replacement_cost_note)">备注</button></div></td>
                            <td class="py-2 pr-4"><div class="flex items-center gap-2 font-semibold tabular-nums"><span>{{ money(line.item.total_cost) }}</span><button type="button" class="text-[10px] font-medium text-cyan-700" @click="toggleNoteEditor(line.kind, line.id, noteFields.totalCost, line.item.total_cost_note)">备注</button></div></td>
                            <td v-if="canManage" class="py-2"><button v-if="line.kind === 'after-sales' && !line.item.after_sales_log_id" type="button" class="font-semibold text-rose-600" @click="removeEntry(line.id)">删除</button></td>
                          </tr>
                          <tr v-if="isNoteEditorOpen(line.kind, line.id)"><td :colspan="canManage ? 7 : 6" class="pb-3"><div class="rounded-lg border border-cyan-200 bg-white p-3"><label class="block text-xs font-semibold text-slate-600">{{ noteEditor.field?.label }}备注<textarea v-model="noteEditor.text" rows="2" maxlength="2000" :readonly="!canManage" class="mt-2 w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-800 read-only:bg-slate-50" placeholder="填写这项费用的说明" /></label><div class="mt-2 flex justify-end gap-2"><button type="button" class="rounded-md px-3 py-1.5 text-xs font-semibold text-slate-500 hover:bg-slate-100" @click="closeNoteEditor">关闭</button><button v-if="canManage" type="button" class="rounded-md bg-cyan-700 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50" :disabled="saving" @click="saveNote">{{ saving ? '保存中…' : '保存备注' }}</button></div></div></td></tr>
                          <tr v-if="isBreakdownOpen(line, 'people')"><td :colspan="canManage ? 7 : 6" class="bg-white px-3 py-3"><div class="space-y-2"><div v-for="person in line.item.person_days" :key="person.id" class="grid items-center gap-2 rounded-md bg-slate-50 p-2 sm:grid-cols-[1fr_120px_auto_auto]">
                            <input v-model.trim="person.person_name" :disabled="!canManage" class="rounded border border-slate-300 px-2 py-1.5 text-xs disabled:bg-slate-100" aria-label="人名" />
                            <label class="flex items-center gap-2 text-xs text-slate-500"><input v-model.number="person.days" :disabled="!canManage" type="number" min="0" step="0.25" class="w-full rounded border border-slate-300 px-2 py-1.5 text-right tabular-nums disabled:bg-slate-100" />天</label>
                            <button type="button" class="text-xs font-semibold text-cyan-700" @click="togglePersonNote(person)">备注</button>
                            <div v-if="canManage" class="flex gap-2"><button type="button" class="text-xs font-semibold text-cyan-800" :disabled="saving" @click="savePerson(line, person)">保存</button><button type="button" class="text-xs font-semibold text-rose-600" @click="deletePerson(person)">删除</button></div>
                            <div v-if="personNoteEditorId === person.id" class="col-span-full rounded border border-cyan-200 bg-white p-2"><textarea v-model="personNoteDraft" rows="2" maxlength="2000" :readonly="!canManage" class="w-full rounded border border-slate-300 px-2 py-1.5 text-xs read-only:bg-slate-50" placeholder="人天备注"/><div v-if="canManage" class="mt-1 text-right"><button type="button" class="text-xs font-semibold text-cyan-800" @click="savePersonNote(person)">保存备注</button></div></div>
                          </div>
                          <form v-if="canManage" class="grid gap-2 rounded-md border border-dashed border-slate-300 p-2 sm:grid-cols-[1fr_120px_auto]" @submit.prevent="addPerson(line)"><input v-model.trim="personDraft.person_name" required maxlength="120" class="rounded border border-slate-300 px-2 py-1.5 text-xs" placeholder="人名"/><label class="flex items-center gap-2 text-xs text-slate-500"><input v-model.number="personDraft.days" required min="0" step="0.25" type="number" class="w-full rounded border border-slate-300 px-2 py-1.5 text-right"/>天</label><button type="submit" class="rounded bg-cyan-700 px-3 py-1.5 text-xs font-semibold text-white" :disabled="saving">添加人员</button></form>
                          <p v-if="!line.item.person_days.length" class="text-xs text-slate-500">暂无人员人天明细</p></div></td></tr>
                          <template v-for="group in ['per-day', 'one-time']" :key="`${line.kind}-${line.id}-${group}`"><tr v-if="isBreakdownOpen(line, group)"><td :colspan="canManage ? 7 : 6" class="bg-white px-3 py-3"><div class="space-y-1"><template v-for="field in groupFields(group)" :key="field.key"><div class="grid items-center gap-3 border-b border-slate-100 py-2 sm:grid-cols-[180px_1fr_auto]"><span class="text-xs font-medium text-slate-600">{{ field.label }}</span><div class="flex items-center gap-2"><template v-if="isInlineCostOpen(line, field.key)"><input v-model.number="inlineCostEditor.value" type="number" min="0" step="0.01" class="w-28 rounded border border-slate-300 px-2 py-1 text-xs tabular-nums"/><button type="button" class="text-xs font-semibold text-cyan-800" @click="saveInlineCost(line)">保存</button><button type="button" class="text-xs text-slate-500" @click="closeInlineCostEditor">取消</button></template><template v-else><span class="text-xs font-semibold tabular-nums text-slate-800">{{ money(line.item[field.key]) }}</span><button v-if="canManage" type="button" class="text-[10px] font-semibold text-cyan-700" @click="openInlineCostEditor(line, field.key)">编辑</button></template></div><button type="button" class="text-xs font-semibold text-cyan-700" @click="toggleNoteEditor(line.kind, line.id, field, line.item[`${field.key}_note`])">备注</button></div><div v-if="isCostNoteOpen(line.kind, line.id, field.key)" class="rounded-md border border-cyan-200 bg-slate-50 p-2"><textarea v-model="noteEditor.text" rows="2" maxlength="2000" :readonly="!canManage" class="w-full rounded border border-slate-300 px-2 py-1.5 text-xs read-only:bg-white"/><div class="mt-1 flex justify-end gap-2"><button type="button" class="text-xs text-slate-500" @click="closeNoteEditor">关闭</button><button v-if="canManage" type="button" class="text-xs font-semibold text-cyan-800" @click="saveNote">保存备注</button></div></div></template></div></td></tr></template>
                        </template>
                        <tr v-if="!costLines(project).length"><td :colspan="canManage ? 7 : 6" class="py-3 text-slate-500">暂无成本明细</td></tr>
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

    <div v-if="fixedCostModal.open" class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/60 px-4 py-6" @click.self="fixedCostModal.open = false">
      <form class="w-full max-w-xl rounded-xl bg-white p-5 shadow-2xl" @submit.prevent="saveFixedCost">
        <header class="flex items-start justify-between gap-3"><div><p class="text-xs font-semibold uppercase tracking-wider text-cyan-700">FIXED COST</p><h3 class="mt-1 text-lg font-semibold text-slate-900">{{ fixedCostModal.id ? '编辑固定成本' : '添加固定成本' }}</h3></div><button type="button" class="rounded-md px-2 py-1 text-lg text-slate-500 hover:bg-slate-100" aria-label="关闭" @click="fixedCostModal.open = false">×</button></header>
        <div class="mt-5 grid gap-4 sm:grid-cols-2">
          <label class="text-sm font-medium text-slate-700 sm:col-span-2">客户名称<select v-model="fixedCostDraft.customer_name" required class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"><option disabled value="">选择客户账号</option><option v-for="customer in customerOptions" :key="customer" :value="customer">{{ customer }}</option></select></label>
          <label class="text-sm font-medium text-slate-700 sm:col-span-2">固定成本项目<input v-model.trim="fixedCostDraft.name" required maxlength="160" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="如：租车、租房、临时薪资" /></label>
          <label class="text-sm font-medium text-slate-700 sm:col-span-2">每日价格<input v-model.number="fixedCostDraft.daily_price" required type="number" min="0" step="0.01" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 tabular-nums" /></label>
          <label class="text-sm font-medium text-slate-700">开始时间<input v-model="fixedCostDraft.start_date" required type="date" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
          <label class="text-sm font-medium text-slate-700">结束时间<input v-model="fixedCostDraft.end_date" required type="date" :min="fixedCostDraft.start_date" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
          <div class="rounded-lg bg-slate-50 px-3 py-3"><p class="text-xs text-slate-500">总天数（含起止日期）</p><p class="mt-1 font-semibold tabular-nums text-slate-900">{{ fixedCostDays }} 天</p></div>
          <div class="rounded-lg bg-cyan-50 px-3 py-3"><p class="text-xs text-cyan-800">自动计算总价格</p><p class="mt-1 font-semibold tabular-nums text-cyan-950">¥ {{ money(fixedCostTotal) }}</p></div>
          <label class="text-sm font-medium text-slate-700 sm:col-span-2">备注<textarea v-model.trim="fixedCostDraft.note" maxlength="2000" rows="3" class="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="说明该固定成本的用途" /></label>
        </div>
        <p v-if="fixedCostError" class="mt-3 text-sm text-rose-700">{{ fixedCostError }}</p>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600" @click="fixedCostModal.open = false">取消</button><button type="submit" class="rounded-lg bg-cyan-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50" :disabled="saving || fixedCostDays < 1">{{ saving ? '保存中…' : '保存固定成本' }}</button></div>
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
  { key: 'fixed-costs', label: '固定成本' },
]
const activeType = ref('418')
const selectedCustomer = ref('')
const projects = ref([])
const fixedCosts = ref([])
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const expandedId = ref(null)
const notice = ref('')
const noticeType = ref('success')
const costAmountFields = [
  { key: 'meal_allowance', label: '餐补', group: 'per-day' },
  { key: 'local_transport_cost', label: '交通', group: 'per-day' },
  { key: 'salary_cost', label: '薪资', group: 'per-day' },
  { key: 'accommodation_cost', label: '住宿', group: 'per-day' },
  { key: 'long_distance_cost', label: '大交通', group: 'one-time' },
  { key: 'visa_cost', label: '签证', group: 'one-time' },
  { key: 'tool_cost', label: '工具', group: 'one-time' },
  { key: 'hardware_replacement_cost', label: '硬件更换', group: 'hardware' },
]
const costGroups = [
  { key: 'per-day', label: '每人天成本', fields: costAmountFields.filter((field) => field.group === 'per-day') },
  { key: 'one-time', label: '一次性成本', fields: costAmountFields.filter((field) => field.group === 'one-time') },
]
const noteFields = {
  totalManDays: { key: 'total_man_days', label: '总人天' },
  perDay: { key: 'per_day_cost', label: '每人天成本合计' },
  oneTime: { key: 'one_time_cost', label: '一次性成本合计' },
  totalCost: { key: 'total_cost', label: '本行总成本' },
  hardware: { key: 'hardware_replacement_cost', label: '硬件更换' },
}
const noteEditor = reactive({ open: false, kind: '', id: null, field: null, text: '' })
const inlineCostEditor = reactive({ open: false, kind: '', id: null, field_key: '', value: 0 })
const expandedBreakdown = reactive({ kind: '', id: null, group: '' })
const personDraft = reactive({ person_name: '', days: 0 })
const personNoteEditorId = ref(null)
const personNoteDraft = ref('')
const assumptionsOpen = ref(false)
const assumptions = ref([])
const assumptionNotice = ref('')
const assumptionNoticeType = ref('success')
const assumptionEditingId = ref(null)
const assumptionDraft = reactive({ name: '', default_amount: 0, description: '' })
const fixedCostModal = reactive({ open: false, id: null })
const fixedCostDraft = reactive({ customer_name: '', name: '', daily_price: 0, start_date: localToday(), end_date: localToday(), note: '' })
const fixedCostError = ref('')
const fixedCostDays = computed(() => {
  if (!fixedCostDraft.start_date || !fixedCostDraft.end_date) return 0
  const start = dateToUtcDay(fixedCostDraft.start_date)
  const end = dateToUtcDay(fixedCostDraft.end_date)
  return end < start ? 0 : end - start + 1
})
const fixedCostTotal = computed(() => fixedCostDays.value * Math.max(Number(fixedCostDraft.daily_price) || 0, 0))
const customerOptions = computed(() => [...new Set([
  ...projects.value.map((item) => item.customer_name),
  ...fixedCosts.value.map((item) => item.customer_name),
].filter(Boolean))].sort((a, b) => a.localeCompare(b, 'zh-CN')))
const globalVisibleProjects = computed(() => projects.value.filter((item) => !selectedCustomer.value || item.customer_name === selectedCustomer.value))
const fixedCostRows = computed(() => [...fixedCosts.value]
  .filter((item) => !selectedCustomer.value || item.customer_name === selectedCustomer.value)
  .sort((left, right) => left.customer_name.localeCompare(right.customer_name, 'zh-CN') || left.start_date.localeCompare(right.start_date) || left.name.localeCompare(right.name, 'zh-CN')))
const visibleProjects = computed(() => globalVisibleProjects.value.filter((item) => item.project_type === activeType.value))
const totalDeliveryCost = computed(() => globalVisibleProjects.value.reduce((sum, item) => sum + deliveryTotal(item), 0))
const totalAfterSalesCost = computed(() => globalVisibleProjects.value.reduce((sum, item) => sum + afterSalesTotal(item), 0) + fixedCostRows.value.reduce((sum, item) => sum + Number(item.total_price || 0), 0))
const totalTripCount = computed(() => globalVisibleProjects.value.reduce((sum, item) => sum + item.after_sales.trip_count, 0))

function deliveryTotal(item) {
  return Number(item.delivery?.total_cost || 0)
}

function afterSalesTotal(item) {
  return Number(item.after_sales?.total_cost || 0)
}

function costLines(project) {
  const lines = []
  if (project.delivery) lines.push({ kind: 'delivery', id: project.delivery.id, item: project.delivery, project_type: project.project_type, project_name: project.project_name, customer_name: project.customer_name, label: '交付成本' })
  for (const entry of project.entries) {
    lines.push({ kind: 'after-sales', id: entry.id, item: entry, project_type: project.project_type, project_name: project.project_name, customer_name: project.customer_name, label: `现场售后 · ${entry.event_date || '—'} · ${entry.after_sales_log_id ? `记录 #${entry.after_sales_log_id}` : entry.reference || ''}` })
  }
  return lines
}

function groupFields(group) {
  return costAmountFields.filter((field) => field.group === group)
}

function toggleBreakdown(line, group) {
  if (expandedBreakdown.kind === line.kind && expandedBreakdown.id === line.id && expandedBreakdown.group === group) {
    expandedBreakdown.kind = ''
    expandedBreakdown.id = null
    expandedBreakdown.group = ''
  } else {
    expandedBreakdown.kind = line.kind
    expandedBreakdown.id = line.id
    expandedBreakdown.group = group
  }
}

function isBreakdownOpen(line, group) {
  return expandedBreakdown.kind === line.kind && expandedBreakdown.id === line.id && expandedBreakdown.group === group
}

function isNoteEditorOpen(kind, id) {
  return noteEditor.open && noteEditor.kind === kind && noteEditor.id === id && ['total_man_days', 'per_day_cost', 'one_time_cost', 'total_cost', 'hardware_replacement_cost'].includes(noteEditor.field?.key)
}

function isCostNoteOpen(kind, id, fieldKey) {
  return noteEditor.open && noteEditor.kind === kind && noteEditor.id === id && noteEditor.field?.key === fieldKey
}

function isInlineCostOpen(line, fieldKey) {
  return inlineCostEditor.open && inlineCostEditor.kind === line.kind && inlineCostEditor.id === line.id && inlineCostEditor.field_key === fieldKey
}

function openInlineCostEditor(line, fieldKey) {
  inlineCostEditor.open = true
  inlineCostEditor.kind = line.kind
  inlineCostEditor.id = line.id
  inlineCostEditor.field_key = fieldKey
  inlineCostEditor.value = Number(line.item[fieldKey] || 0)
}

function closeInlineCostEditor() {
  inlineCostEditor.open = false
  inlineCostEditor.kind = ''
  inlineCostEditor.id = null
  inlineCostEditor.field_key = ''
  inlineCostEditor.value = 0
}

function money(value) {
  return Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function localToday() {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
}

function dateToUtcDay(value) {
  const [year, month, day] = value.split('-').map(Number)
  return Date.UTC(year, month - 1, day) / 86400000
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
    fixedCosts.value = response.fixed_costs || []
  } catch (error) {
    showNotice(error.message || '成本记录加载失败', 'error')
  } finally {
    loading.value = false
  }
}

async function exportWorkbook() {
  exporting.value = true
  try {
    await portalApi.downloadDeliveryCostExcel(selectedCustomer.value)
    showNotice('Excel 文件已导出')
  } catch (error) {
    showNotice(error.message || 'Excel 导出失败', 'error')
  } finally {
    exporting.value = false
  }
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

async function saveInlineCost(line) {
  const amount = Number(inlineCostEditor.value)
  if (!Number.isFinite(amount) || amount < 0) {
    showNotice('成本金额必须是大于等于0的有效数字。', 'error')
    return
  }
  saving.value = true
  try {
    if (line.kind === 'delivery') {
      const payload = {
        project_type: line.project_type,
        project_name: line.project_name,
        customer_name: line.customer_name,
        ...Object.fromEntries(costAmountFields.map(({ key }) => [key, Number(line.item[key] || 0)])),
        [inlineCostEditor.field_key]: amount,
      }
      await portalApi.updateDeliveryCost(line.item.id, payload)
    } else {
      await portalApi.updateAfterSalesCostEntry(line.item.id, { [inlineCostEditor.field_key]: amount })
    }
    closeInlineCostEditor()
    showNotice('成本金额已保存')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '成本金额保存失败', 'error')
  } finally {
    saving.value = false
  }
}

function openFixedCost(item = null) {
  fixedCostModal.open = true
  fixedCostModal.id = item?.id ?? null
  fixedCostError.value = ''
  Object.assign(fixedCostDraft, {
    customer_name: item?.customer_name || '',
    name: item?.name || '',
    daily_price: Number(item?.daily_price || 0),
    start_date: item?.start_date || localToday(),
    end_date: item?.end_date || localToday(),
    note: item?.note || '',
  })
}

async function saveFixedCost() {
  fixedCostError.value = ''
  if (!fixedCostDraft.start_date || !fixedCostDraft.end_date || fixedCostDays.value < 1) {
    fixedCostError.value = '结束日期不能早于开始日期，请检查日期范围。'
    return
  }
  saving.value = true
  try {
    const payload = {
      customer_name: fixedCostDraft.customer_name,
      name: fixedCostDraft.name.trim(),
      daily_price: Number(fixedCostDraft.daily_price) || 0,
      start_date: fixedCostDraft.start_date,
      end_date: fixedCostDraft.end_date,
      note: fixedCostDraft.note.trim(),
    }
    if (fixedCostModal.id) await portalApi.updateFixedCost(fixedCostModal.id, payload)
    else await portalApi.createFixedCost(payload)
    fixedCostModal.open = false
    showNotice('固定成本已保存')
    await loadProjects()
  } catch (error) {
    fixedCostError.value = error.message || '固定成本保存失败'
  } finally {
    saving.value = false
  }
}

async function deleteFixedCost(item) {
  if (!window.confirm(`确认删除固定成本“${item.name}”？`)) return
  try {
    await portalApi.deleteFixedCost(item.id)
    showNotice('固定成本已删除')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '固定成本删除失败', 'error')
  }
}

function togglePersonNote(person) {
  if (personNoteEditorId.value === person.id) {
    personNoteEditorId.value = null
    personNoteDraft.value = ''
  } else {
    personNoteEditorId.value = person.id
    personNoteDraft.value = person.note || ''
  }
}

async function savePerson(line, person) {
  saving.value = true
  try {
    await portalApi.updateCostPersonDay(person.id, {
      person_name: person.person_name,
      days: Number(person.days) || 0,
      note: person.note || '',
    })
    showNotice('人员人天已保存')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '人员人天保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function savePersonNote(person) {
  saving.value = true
  try {
    await portalApi.updateCostPersonDay(person.id, { note: personNoteDraft.value })
    personNoteEditorId.value = null
    personNoteDraft.value = ''
    showNotice('人天备注已保存')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '备注保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function addPerson(line) {
  if (!personDraft.person_name.trim()) return
  saving.value = true
  try {
    await portalApi.createCostPersonDay(line.kind, line.id, {
      person_name: personDraft.person_name,
      days: Number(personDraft.days) || 0,
    })
    Object.assign(personDraft, { person_name: '', days: 0 })
    showNotice('人员人天已添加')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '人员人天添加失败', 'error')
  } finally {
    saving.value = false
  }
}

async function deletePerson(person) {
  if (!window.confirm(`确认删除${person.person_name}的人天明细？`)) return
  try {
    await portalApi.deleteCostPersonDay(person.id)
    showNotice('人员人天已删除')
    await loadProjects()
  } catch (error) {
    showNotice(error.message || '人员人天删除失败', 'error')
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