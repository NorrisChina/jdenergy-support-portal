<template>
  <div class="min-h-screen bg-hero-grid text-slate-100">
    <main class="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-4 sm:px-6 lg:px-8">
      <header class="mb-4 flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl sm:p-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-[11px] font-semibold tracking-[0.24em] text-cyan-200 uppercase">
            {{ t('app.brand') }}
          </p>
          <h1 class="mt-3 text-2xl font-semibold text-white sm:text-3xl">
            {{ t('app.title') }}
          </h1>
          <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300 sm:text-base">
            {{ t('app.description') }}
          </p>
        </div>

        <div class="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
          <div class="rounded-2xl border border-white/10 bg-slate-950/70 p-1">
            <div v-for="(row, rowIndex) in viewRows" :key="`view-row-${rowIndex}`" class="flex flex-wrap gap-1" :class="rowIndex > 0 ? 'mt-1' : ''">
              <button
                v-for="view in row"
                :key="view.key"
                type="button"
                class="rounded-xl px-4 py-2 text-sm font-medium transition"
                :class="activeView === view.key ? 'bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-400/20' : 'text-slate-300 hover:bg-white/5 hover:text-white'"
                @click="activeView = view.key"
              >
                {{ view.label }}
              </button>
            </div>
          </div>

          <button
            type="button"
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
            @click="toggleLocale"
          >
            {{ t('app.languageToggle') }}
          </button>

          <button
            type="button"
            class="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm font-semibold text-emerald-200 transition hover:bg-emerald-400/15 hover:text-emerald-100"
            @click="handleStaffModeClick"
          >
            {{ isInternalMode ? t('auth.leave') : t('app.staffMode') }}
          </button>
        </div>
      </header>

      <div v-if="portalState.notice" class="mb-4 rounded-2xl border px-4 py-3 text-sm" :class="portalState.noticeType === 'error' ? 'border-rose-400/20 bg-rose-500/10 text-rose-100' : portalState.noticeType === 'success' ? 'border-emerald-400/20 bg-emerald-500/10 text-emerald-100' : 'border-white/10 bg-white/5 text-slate-100'">
        {{ portalState.notice }}
      </div>

      <div class="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
        <span>{{ isInternalMode ? t('common.managedHint') : t('common.readOnlyHint') }}</span>
        <span class="rounded-full border border-white/10 bg-slate-950/60 px-3 py-1 text-xs uppercase tracking-[0.24em] text-cyan-200">
          {{ staffModeBadge }}
        </span>
      </div>

      <section v-if="activeView === 'after-sales'" class="flex-1">
        <div class="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-start">
          <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">{{ t('views.afterSales') }}</p>
            <div class="mt-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">{{ t('fault.section') }}</h2>
                <p class="mt-3 text-sm leading-7 text-slate-300 sm:text-base">{{ t('fault.subtitle') }}</p>
              </div>
              <button v-if="isInternalMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openFaultEditor()">
                {{ t('fault.adminCreate') }}
              </button>
            </div>

            <form class="mt-6 flex flex-col gap-3 sm:flex-row" @submit.prevent="handleFaultSearch">
              <label class="sr-only" for="fault-search">{{ t('fault.placeholder') }}</label>
              <input
                id="fault-search"
                v-model="faultKeyword"
                type="text"
                class="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-5 py-4 text-base text-white placeholder:text-slate-500 outline-none transition focus:border-cyan-400/60 focus:shadow-[0_0_0_4px_rgba(34,211,238,0.12)]"
                :placeholder="t('fault.placeholder')"
              />
              <button type="submit" class="rounded-2xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-4 text-base font-semibold text-slate-950 transition hover:brightness-110">
                {{ t('fault.searchButton') }}
              </button>
            </form>

            <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
              <label class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">模块</label>
              <select v-model="faultModule" class="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none sm:max-w-xs" @change="handleFaultFilterChange">
                <option value="">全部模块</option>
                <option v-for="module in faultModules" :key="module" :value="module">{{ module }}</option>
              </select>
              <label class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400 sm:ml-2">每页</label>
              <select v-model.number="faultPageSize" class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none" @change="handleFaultPageSizeChange">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
              </select>
            </div>

            <div class="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
              <span v-for="chip in t('fault.chips')" :key="chip" class="rounded-full border border-white/10 bg-white/5 px-3 py-1">{{ chip }}</span>
            </div>
          </div>

          <aside class="grid gap-4 rounded-3xl border border-white/10 bg-slate-950/55 p-5">
            <div>
              <p class="text-xs uppercase tracking-[0.24em] text-cyan-200">Quick Guide</p>
              <p class="mt-2 text-sm leading-6 text-slate-300">{{ t('fault.quickGuide') }}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
              {{ t('fault.currentCount') }}：<span class="font-semibold text-white">{{ faultTotal }}</span>
            </div>
          </aside>
        </div>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-white sm:text-2xl">{{ t('fault.resultTitle') }}</h3>
            <p class="mt-1 text-sm text-slate-400">{{ faultHint }}</p>
          </div>
          <div class="text-sm text-slate-500">{{ faultLoading ? 'Loading...' : `${faultResults.length} / ${faultTotal} item(s)` }}</div>
        </div>

        <div v-if="faultLoading" class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 3" :key="index" class="h-56 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else-if="faultError" class="mt-4 rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100">
          {{ faultError }}
        </div>

        <div v-else-if="faultResults.length > 0" class="mt-4 overflow-hidden rounded-3xl border border-white/10 bg-white/5">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-white/10 text-left text-sm">
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">模块</th>
                  <th class="px-5 py-4 font-medium">故障码</th>
                  <th class="px-5 py-4 font-medium">故障名称</th>
                  <th class="px-5 py-4 font-medium">等级</th>
                  <th class="px-5 py-4 font-medium">停机</th>
                  <th class="px-5 py-4 font-medium">恢复机制</th>
                  <th class="px-5 py-4 font-medium">可能原因</th>
                  <th class="px-5 py-4 font-medium">解决措施</th>
                  <th v-if="isInternalMode" class="px-5 py-4 font-medium">{{ t('common.actions') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <tr v-for="item in faultResults" :key="`${item.module}-${item.fault_code}-${item.id}`" class="bg-white/[0.02] hover:bg-white/[0.04]">
                  <td class="px-5 py-4"><span class="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-200">{{ item.module || '-' }}</span></td>
                  <td class="px-5 py-4 font-semibold text-white">{{ item.fault_code || '-' }}</td>
                  <td class="px-5 py-4 text-white">{{ item.fault_name || '-' }}</td>
                  <td class="px-5 py-4">{{ item.fault_level || '-' }}</td>
                  <td class="px-5 py-4">{{ item.is_stop || '-' }}</td>
                  <td class="px-5 py-4">{{ item.recovery || '-' }}</td>
                  <td class="max-w-xs px-5 py-4 text-slate-300">{{ item.possible_cause || '-' }}</td>
                  <td class="max-w-xs px-5 py-4 text-slate-300">{{ item.solution || '-' }}</td>
                  <td v-if="isInternalMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openFaultEditor(item)">{{ t('common.edit') }}</button>
                      <button type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('fault', String(item.id), `${item.module}-${item.fault_code}`, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="flex flex-col items-center justify-between gap-3 border-t border-white/10 px-5 py-4 sm:flex-row">
            <p class="text-xs text-slate-400">第 {{ faultPage }} / {{ faultTotalPages }} 页，共 {{ faultTotal }} 条</p>
            <div class="flex items-center gap-2">
              <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40" :disabled="faultPage <= 1" @click="goFaultPage(faultPage - 1)">上一页</button>
              <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40" :disabled="faultPage >= faultTotalPages" @click="goFaultPage(faultPage + 1)">下一页</button>
            </div>
          </div>
        </div>

        <div v-else class="mt-4 rounded-3xl border border-dashed border-white/15 bg-white/5 p-10 text-center text-slate-300">
          <p class="text-lg font-medium text-white">{{ t('fault.noResult') }}</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">{{ t('fault.noResultHint') }}</p>
        </div>

      </section>

      <section v-else-if="activeView === 'materials-center'" class="flex-1">
        <div class="mb-5">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Materials Center</p>
          <div class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 class="text-2xl font-semibold text-white sm:text-3xl">{{ t('views.materialsCenter') }}</h2>
              <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">{{ t('materials.subtitle') }}</p>
            </div>
            <button v-if="materialsCanManage" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openTechnicalDocEditor()">
              + 上传新资料
            </button>
          </div>
        </div>

        <div class="mb-5 flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-white/5 p-2">
          <button
            v-for="series in technicalDocProductSeries"
            :key="series"
            type="button"
            class="rounded-xl px-4 py-2 text-sm font-semibold transition"
            :class="materialsProductSeries === series ? 'bg-cyan-400 text-slate-950' : 'text-slate-300 hover:bg-white/10 hover:text-white'"
            @click="changeMaterialsSeries(series)"
          >
            {{ series }}
          </button>
        </div>

        <div v-if="materialsLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 5" :key="index" class="h-56 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else-if="materialsError" class="rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100">
          {{ materialsError }}
        </div>

        <div v-else class="grid gap-6 xl:grid-cols-2">
          <section v-for="category in technicalDocCategories" :key="category" class="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-xl font-semibold text-white">{{ category }}</h3>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{{ materialsByCategory[category]?.length ?? 0 }}</span>
            </div>

            <div class="mt-4 grid gap-3">
              <article v-for="item in materialsByCategory[category]" :key="item.id" class="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="text-sm font-semibold text-white">{{ item.title }}</p>
                    <p class="mt-1 text-xs text-slate-400">{{ item.file_type || '-' }} · {{ item.file_size || '-' }}</p>
                  </div>
                  <span class="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 text-[11px] text-cyan-200">{{ item.product_series }}</span>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <button type="button" class="rounded-xl bg-cyan-400 px-3 py-2 text-xs font-semibold text-slate-950 transition hover:brightness-110" @click="previewTechnicalDoc(item)">
                    {{ isVideoFile(item) ? '播放 / Play' : '预览 / Preview' }}
                  </button>
                  <a :href="technicalDocActionUrl(item, true)" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10">
                    下载 / Download
                  </a>
                  <button v-if="materialsCanManage" type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openTechnicalDocEditor(item)">编辑</button>
                  <button v-if="materialsCanManage" type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('technical-doc', String(item.id), item.title, t('common.deleteConfirm'))">删除</button>
                </div>
              </article>
              <div v-if="(materialsByCategory[category] ?? []).length === 0" class="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-xs text-slate-400">
                {{ t('common.noData') }}
              </div>
            </div>
          </section>
        </div>
      </section>

      <section v-else-if="activeView === 'grid-scale'" class="flex-1">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Grid-Scale Delivery</p>
            <div class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">{{ t('grid.section') }}</h2>
                <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">{{ t('grid.subtitle') }}</p>
              </div>
              <button v-if="isInternalMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openProjectEditor()">
                {{ t('grid.adminCreate') }}
              </button>
            </div>
          </div>
          <div class="rounded-3xl border border-cyan-400/20 bg-gradient-to-r from-cyan-400/10 via-white/5 to-emerald-400/10 p-4 shadow-glow">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">{{ t('grid.totalMwh') }}</p>
                <div class="mt-2 flex items-end gap-3">
                  <span class="text-3xl font-semibold text-white sm:text-4xl">{{ formatMwh(gridSummary.totalMwh) }}</span>
                  <span class="pb-1 text-sm font-medium text-slate-300">MWh</span>
                </div>
              </div>
              <div class="text-sm text-slate-300">
                <p>{{ t('grid.projectCount') }}：<span class="font-semibold text-white">{{ gridProjects.length }}</span></p>
                <p class="mt-1 max-w-md leading-6 text-slate-400">{{ t('grid.ratioHint') }}</p>
              </div>
            </div>
            <div class="mt-4 h-3 overflow-hidden rounded-full bg-slate-950/70">
              <div class="flex h-full w-full overflow-hidden rounded-full">
                <div
                  v-for="project in gridSummary.projects"
                  :key="project.project_name"
                  class="h-full transition-all"
                  :class="project.ratioBarClass"
                  :style="{ width: `${project.capacityRatio}%` }"
                  :title="`${project.project_name} · ${project.capacityMwh} MWh · ${project.ratioLabel}`"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="ledgerLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 3" :key="index" class="h-72 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article v-for="project in gridSummary.projects" :key="project.project_name" class="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:border-cyan-400/30">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{{ t('grid.location') }}</p>
                <h3 class="mt-1 text-lg font-semibold text-white">{{ project.project_name }}</h3>
              </div>
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="project.deliveryBadgeClass">{{ project.deliveryState }}</span>
            </div>

            <div class="mt-5 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              <div class="flex items-end justify-between gap-3">
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{{ t('grid.capacity') }}</p>
                <p class="text-xs font-semibold text-cyan-200">{{ project.ratioLabel }}</p>
              </div>
              <div class="mt-2 flex items-end justify-between gap-3">
                <p class="text-2xl font-semibold text-white">{{ formatMwh(project.capacityMwh) }} <span class="text-base text-slate-300">MWh</span></p>
                <p class="pb-1 text-sm font-medium text-slate-300">{{ project.ratioLabel }}</p>
              </div>
              <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-900">
                <div class="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all" :style="{ width: `${project.capacityRatio}%` }"></div>
              </div>
            </div>

            <div class="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">{{ t('grid.daySummary') }}</p>
              <p class="mt-1 text-sm font-semibold text-white">{{ project.daysLabel }}</p>
            </div>

            <div v-if="isInternalMode" class="mt-4 flex flex-wrap gap-2">
              <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openProjectEditor(project)">{{ t('common.edit') }}</button>
              <button type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('grid', project.project_name, project.project_name, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
            </div>
          </article>
        </div>
      </section>

      <section v-else-if="activeView === 'ci-dashboard'" class="flex-1">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">C&I Delivery Dashboard</p>
            <div class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">{{ t('ci.section') }}</h2>
                <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">{{ t('ci.subtitle') }}</p>
              </div>
              <button v-if="isInternalMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openCiEditor()">
                {{ t('ci.createDealer') }}
              </button>
            </div>
          </div>
          <div class="grid gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
              {{ t('ci.dealerCount') }}：<span class="font-semibold text-white">{{ ciDeliveries.length }}</span>
            </div>
            <div class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">
              <p class="text-xs uppercase tracking-[0.2em] text-cyan-200">100C</p>
              <p class="mt-1 font-semibold text-white">{{ ciSummary.total100c }} 台</p>
              <p class="text-xs text-cyan-200">{{ formatCiMwh(ciSummary.total100cMwh) }} MWh</p>
            </div>
            <div class="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
              <p class="text-xs uppercase tracking-[0.2em] text-emerald-200">250</p>
              <p class="mt-1 font-semibold text-white">{{ ciSummary.total250 }} 台</p>
              <p class="text-xs text-emerald-200">{{ formatCiMwh(ciSummary.total250Mwh) }} MWh</p>
            </div>
          </div>
        </div>

        <div class="overflow-hidden rounded-3xl border border-white/10 bg-white/5">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-white/10 text-left text-sm">
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">{{ t('ci.region') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('ci.dealer') }}</th>
                  <th class="px-5 py-4 font-medium">100C 已交付</th>
                  <th class="px-5 py-4 font-medium">250 已交付</th>
                  <th v-if="isInternalMode" class="px-5 py-4 font-medium">{{ t('common.actions') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <tr v-for="item in ciCapacityRows" :key="item.dealer_name" class="bg-white/[0.02] hover:bg-white/[0.04]">
                  <td class="px-5 py-4">{{ item.region }}</td>
                  <td class="px-5 py-4 font-medium text-white">{{ item.dealer_name }}</td>
                  <td class="px-5 py-4">
                    <p class="font-semibold text-cyan-200">{{ item.delivered_100c }} 台 ({{ formatCiMwh(item.mwh100c) }} MWh)</p>
                    <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-900">
                      <div class="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all" :style="{ width: `${item.ratio100c}%` }"></div>
                    </div>
                  </td>
                  <td class="px-5 py-4">
                    <p class="font-semibold text-emerald-200">{{ item.delivered_250 }} 台 ({{ formatCiMwh(item.mwh250) }} MWh)</p>
                    <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-900">
                      <div class="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all" :style="{ width: `${item.ratio250}%` }"></div>
                    </div>
                  </td>
                  <td v-if="isInternalMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openCiEditor(item)">{{ t('common.edit') }}</button>
                      <button type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('ci', item.dealer_name, item.dealer_name, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section v-else class="flex-1">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Warehouse & Inventory</p>
            <div class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">{{ t('inventory.section') }}</h2>
                <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">{{ t('inventory.subtitle') }}</p>
              </div>
              <button v-if="isInternalMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openInventoryEditor()">
                {{ t('inventory.addItem') }}
              </button>
            </div>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
            {{ t('inventory.count') }}：<span class="font-semibold text-white">{{ inventoryItems.length }}</span>
          </div>
        </div>

        <div v-if="inventoryLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 6" :key="index" class="h-64 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else-if="inventoryError" class="rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100">
          {{ inventoryError }}
        </div>

        <div v-else class="overflow-hidden rounded-3xl border border-white/10 bg-white/5">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-white/10 text-left text-sm">
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.itemNo') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.descriptionZh') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.specification') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.totalQuantity') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.damagedQuantity') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.availableQuantity') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.photoPaths') }}</th>
                  <th class="px-5 py-4 font-medium">{{ t('inventory.remarks') }}</th>
                  <th v-if="isInternalMode" class="px-5 py-4 font-medium">{{ t('common.actions') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <tr v-for="item in inventoryItems" :key="item.item_no" class="bg-white/[0.02] hover:bg-white/[0.04]">
                  <td class="px-5 py-4 whitespace-nowrap font-semibold text-white">{{ item.item_no }}</td>
                  <td class="px-5 py-4">{{ item.description_zh }}</td>
                  <td class="px-5 py-4">{{ item.specification }}</td>
                  <td class="px-5 py-4">{{ item.total_quantity }}</td>
                  <td class="px-5 py-4">{{ item.damaged_quantity }}</td>
                  <td class="px-5 py-4 font-semibold text-emerald-200">{{ item.available_quantity }}</td>
                  <td class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button v-for="photo in item.photo_paths" :key="photo" type="button" class="overflow-hidden rounded-xl border border-white/10 bg-slate-950/80" @click="openImagePreview(photo)">
                        <img :src="resolvePhotoUrl(photo)" :alt="item.item_no" class="h-12 w-12 object-cover" />
                      </button>
                      <span v-if="(item.photo_paths || []).length === 0" class="text-xs text-slate-400">{{ t('common.noData') }}</span>
                    </div>
                  </td>
                  <td class="px-5 py-4 text-slate-300">{{ item.remarks || '-' }}</td>
                  <td v-if="isInternalMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openInventoryEditor(item)">{{ t('common.edit') }}</button>
                      <button type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('inventory', item.item_no, item.item_no, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="inventoryItems.length === 0">
                  <td :colspan="isInternalMode ? 9 : 8" class="px-4 py-10 text-center text-slate-400">{{ t('common.noData') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
      <div v-if="portalState.staffAuthOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm">
        <div class="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">{{ t('auth.title') }}</p>
          <h3 class="mt-3 text-2xl font-semibold text-white">{{ t('auth.title') }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-300">{{ t('auth.description') }}</p>
          <input v-model="portalState.staffPassword" type="password" class="mt-5 w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-cyan-400/60" :placeholder="t('auth.placeholder')" @keyup.enter="confirmPassword" />
          <p v-if="portalState.staffAuthError" class="mt-3 text-sm text-rose-200">{{ portalState.staffAuthError }}</p>
          <div class="mt-6 flex justify-end gap-3">
            <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10" @click="cancelStaffAuth">{{ t('auth.cancel') }}</button>
            <button type="button" class="rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:brightness-110" @click="confirmPassword">{{ t('auth.confirm') }}</button>
          </div>
        </div>
      </div>

      <div v-if="crudModal.open" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/80 px-4 py-8 backdrop-blur-sm">
        <div class="w-full max-w-2xl rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">CRUD</p>
              <h3 class="mt-2 text-2xl font-semibold text-white">{{ crudModal.kind === 'fault' ? t('fault.adminCreate') : crudModal.kind === 'grid' ? t('grid.createTitle') : crudModal.kind === 'ci' ? t('ci.createTitle') : crudModal.kind === 'technical-doc' ? t('materials.createTitle') : t('inventory.createTitle') }}</h3>
            </div>
            <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="closeCrudModal">{{ t('common.close') }}</button>
          </div>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <template v-if="crudModal.kind === 'fault'">
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">模块</span>
                <input v-model="crudDraft.module" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">故障码</span>
                <input v-model="crudDraft.fault_code" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">故障名称</span>
                <input v-model="crudDraft.fault_name" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">故障等级</span>
                <input v-model="crudDraft.fault_level" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">停机</span>
                <input v-model="crudDraft.is_stop" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">恢复机制</span>
                <input v-model="crudDraft.recovery" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">触发逻辑</span>
                <input v-model="crudDraft.trigger_logic" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">检测条件</span>
                <textarea v-model="crudDraft.detection_condition" rows="3" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"></textarea>
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">可能原因</span>
                <textarea v-model="crudDraft.possible_cause" rows="4" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"></textarea>
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">解决措施</span>
                <textarea v-model="crudDraft.solution" rows="4" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"></textarea>
              </label>
            </template>
            <template v-else-if="crudModal.kind === 'grid'">
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Project Name</span>
                <input v-model="crudDraft.project_name" :disabled="crudModal.mode === 'edit'" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:cursor-not-allowed disabled:opacity-60" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('grid.codDate') }}</span>
                <input v-model="crudDraft.cod" type="date" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Capacity (MWh)</span>
                <input v-model.number="crudDraft.capacity_mwh" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">PCS Model</span>
                <input v-model="crudDraft.pcs_model" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Cell Version</span>
                <input v-model="crudDraft.cell_version" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Status</span>
                <select v-model="crudDraft.progress_status" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none">
                  <option v-for="status in projectStatuses" :key="status" :value="status">{{ status }}</option>
                </select>
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('grid.photoUpload') }}</span>
                <input ref="photoInputRef" type="file" accept="image/*" multiple class="hidden" @change="handlePhotoFiles" />
                <div class="flex flex-wrap items-center gap-3">
                  <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10" @click="openPhotoPicker">
                    {{ t('grid.chooseImages') }}
                  </button>
                  <span class="text-xs text-slate-400">{{ photoUploading ? t('common.loading') : t('grid.photoHint') }}</span>
                </div>
                <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
                  <div v-for="(photo, index) in crudDraft.photo_paths" :key="photo" class="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950/80">
                    <img :src="resolvePhotoUrl(photo)" :alt="`${crudDraft.project_name} ${index + 1}`" class="h-28 w-full object-cover" />
                    <button type="button" class="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-slate-950/80 text-xs font-bold text-white" @click="removePhotoPath(index)">×</button>
                  </div>
                  <div v-if="crudDraft.photo_paths.length === 0" class="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-xs text-slate-400">{{ t('grid.noPhotos') }}</div>
                </div>
              </label>
            </template>
            <template v-else-if="crudModal.kind === 'ci'">
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Dealer Name</span>
                <input v-model="crudDraft.dealer_name" :disabled="crudModal.mode === 'edit'" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:cursor-not-allowed disabled:opacity-60" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Region</span>
                <input v-model="crudDraft.region" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">100C</span>
                <input v-model.number="crudDraft.delivered_100c" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">250</span>
                <input v-model.number="crudDraft.delivered_250" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
            </template>
            <template v-else-if="crudModal.kind === 'technical-doc'">
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">产品系列</span>
                <select v-model="crudDraft.product_series" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none">
                  <option v-for="series in technicalDocProductSeries" :key="series" :value="series">{{ series }}</option>
                </select>
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">资料分类</span>
                <select v-model="crudDraft.category" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none">
                  <option v-for="category in technicalDocCategories" :key="category" :value="category">{{ category }}</option>
                </select>
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">标题</span>
                <input v-model="crudDraft.title" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label v-if="crudModal.mode === 'create'" class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">上传文件</span>
                <input ref="technicalDocFileInputRef" type="file" class="hidden" @change="handleTechnicalDocFile" />
                <div class="flex flex-wrap items-center gap-3">
                  <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10" @click="openTechnicalDocFilePicker">
                    选择文件
                  </button>
                  <span class="text-xs text-slate-400">{{ crudDraft.technical_doc_file ? crudDraft.technical_doc_file.name : '未选择文件' }}</span>
                </div>
              </label>
              <div v-else class="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-xs text-slate-300">
                当前文件：{{ crudDraft.file_url || '-' }}
              </div>
            </template>
            <template v-else>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.itemNo') }}</span>
                <input v-model="crudDraft.item_no" :disabled="crudModal.mode === 'edit'" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:cursor-not-allowed disabled:opacity-60" />
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.descriptionZh') }}</span>
                <input v-model="crudDraft.description_zh" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.specification') }}</span>
                <input v-model="crudDraft.specification" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.totalQuantity') }}</span>
                <input v-model.number="crudDraft.total_quantity" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" @input="recomputeAvailableQuantity" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.damagedQuantity') }}</span>
                <input v-model.number="crudDraft.damaged_quantity" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" @input="recomputeAvailableQuantity" />
              </label>
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.availableQuantity') }}</span>
                <input v-model.number="crudDraft.available_quantity" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.remarks') }}</span>
                <textarea v-model="crudDraft.remarks" rows="3" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"></textarea>
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ t('inventory.photoPaths') }}</span>
                <input ref="photoInputRef" type="file" accept="image/*" multiple class="hidden" @change="handlePhotoFiles" />
                <div class="flex flex-wrap items-center gap-3">
                  <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10" @click="openPhotoPicker">
                    {{ t('inventory.chooseImages') }}
                  </button>
                  <span class="text-xs text-slate-400">{{ photoUploading ? t('common.loading') : t('inventory.photoHint') }}</span>
                </div>
                <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
                  <div v-for="(photo, index) in crudDraft.photo_paths" :key="photo" class="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950/80">
                    <img :src="resolvePhotoUrl(photo)" :alt="`${crudDraft.item_no} ${index + 1}`" class="h-28 w-full object-cover" />
                    <button type="button" class="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-slate-950/80 text-xs font-bold text-white" @click="removePhotoPath(index)">×</button>
                  </div>
                  <div v-if="crudDraft.photo_paths.length === 0" class="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-xs text-slate-400">{{ t('inventory.noPhotos') }}</div>
                </div>
              </label>
            </template>
          </div>

          <div class="mt-6 flex justify-end gap-3">
            <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10" @click="closeCrudModal">{{ t('common.cancel') }}</button>
            <button type="button" class="rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:brightness-110" @click="submitCrud">{{ t('common.save') }}</button>
          </div>
        </div>
      </div>

      <div v-if="deleteDialog.open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm">
        <div class="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-rose-200">{{ t('common.delete') }}</p>
          <h3 class="mt-3 text-2xl font-semibold text-white">{{ deleteDialog.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-300">{{ deleteDialog.message }}</p>
          <div class="mt-6 flex justify-end gap-3">
            <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10" @click="closeDeleteDialog">{{ t('common.cancel') }}</button>
            <button type="button" class="rounded-2xl bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110" @click="confirmDelete">{{ t('common.delete') }}</button>
          </div>
        </div>
      </div>

      <div v-if="imagePreviewUrl" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 px-4 backdrop-blur-sm" @click.self="closeImagePreview">
        <div class="max-w-5xl overflow-hidden rounded-3xl border border-white/10 bg-slate-900 shadow-2xl shadow-black/30">
          <div class="flex items-center justify-between border-b border-white/10 px-5 py-3">
            <p class="text-sm font-semibold text-white">{{ t('inventory.photoPreview') }}</p>
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="closeImagePreview">{{ t('common.close') }}</button>
          </div>
          <img :src="imagePreviewUrl" alt="preview" class="max-h-[80vh] w-full object-contain bg-black" />
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { messages } from './locales/messages'
import { portalApi } from './services/portalApi'
import { usePortalState } from './composables/usePortalState'

const { state: portalState, setLocale, toggleLocale, requestStaffMode, cancelStaffAuth, confirmStaffAuth, leaveStaffMode, setNotice } = usePortalState()

const activeView = ref('after-sales')

const views = computed(() => [
  { key: 'after-sales', label: t('views.afterSales') },
  { key: 'materials-center', label: t('views.materialsCenter') },
  { key: 'warehouse', label: t('views.warehouse') },
  { key: 'grid-scale', label: t('views.gridScale') },
  { key: 'ci-dashboard', label: t('views.ciDashboard') },
])
const viewRows = computed(() => [
  [views.value[0], views.value[1], views.value[2]],
  [views.value[3], views.value[4]],
])

const warehouseOptions = [
  { key: 'europe', label: '欧洲仓 / Europe' },
  { key: 'north_america', label: '北美仓 / North America' },
]

const technicalDocProductSeries = ['418', '250', '100C']
const technicalDocCategories = ['安装手册', '调试手册', '运维手册', '安装视频', '其他手册']

const projectStatuses = ['清关中', '设备上岸', '土建施工', '调试中', '正式并网']

const faultKeyword = ref('')
const faultModule = ref('')
const faultModules = ref(['PCS', 'BMS', 'EMS', '消防', '水机'])
const faultPage = ref(1)
const faultPageSize = ref(20)
const faultTotal = ref(0)
const faultLoading = ref(false)
const faultError = ref('')
const faultResults = ref([])
const faultHasSearched = ref(false)

const ledgerLoading = ref(false)
const gridProjects = ref([])
const ciDeliveries = ref([])
const projectDraftStatus = reactive({})

const selectedWarehouse = ref('europe')
const warehouseLoading = ref(false)
const warehouseError = ref('')
const warehouseSummary = ref({ warehouse_name: 'europe', inventory: [], grouped_inventory: {}, transactions: [] })
const warehouseForm = reactive({ tx_type: '国内到货入库', product_model: '100C', quantity: 1, related_project: '', tx_no: '' })
const inventoryLoading = ref(false)
const inventoryError = ref('')
const inventoryItems = ref([])
const materialsProductSeries = ref(technicalDocProductSeries[0])
const materialsLoading = ref(false)
const materialsError = ref('')
const materialsItems = ref([])
const photoInputRef = ref(null)
const technicalDocFileInputRef = ref(null)
const photoUploading = ref(false)
const imagePreviewUrl = ref('')
let gridDashboardTimerId = null

const crudModal = reactive({ open: false, kind: '', mode: 'create', originalKey: '' })
const crudDraft = reactive(createEmptyCrudDraft())
const deleteDialog = reactive({ open: false, kind: '', key: '', title: '', message: '' })

const selectedWarehouseLabel = computed(() => warehouseOptions.find((item) => item.key === selectedWarehouse.value)?.label ?? selectedWarehouse.value)
const warehouseProductOptions = computed(() => {
  const inventory = warehouseSummary.value.inventory ?? []
  return [...new Set(inventory.map((item) => item.product_model))]
})
const warehouseTopCards = computed(() => {
  const inventory = warehouseSummary.value.inventory ?? []
  const lookup = (productModel) => inventory.find((item) => item.product_model === productModel)?.quantity ?? 0
  return [
    { key: '100C', label: '100C 储能柜', quantity: lookup('100C'), note: '柜体库存' },
    { key: '250', label: '250 储能柜', quantity: lookup('250'), note: '柜体库存' },
    { key: 'PCS', label: 'PCS 主机', quantity: lookup('PCS'), note: '核心配件' },
    { key: 'BMS', label: 'BMS 主控板', quantity: lookup('BMS'), note: '核心配件' },
    { key: 'CableKit', label: '线缆包', quantity: lookup('CableKit'), note: '核心配件' },
  ]
})
const isInternalMode = computed(() => portalState.staffMode)
const staffMode = isInternalMode
const locale = computed(() => portalState.locale)
const isEnglish = computed(() => locale.value === 'en-US')
const materialsCanManage = computed(() => {
  if (isInternalMode.value) {
    return true
  }
  if (typeof window === 'undefined') {
    return false
  }
  return Boolean(window.localStorage.getItem('token'))
})
const materialsByCategory = computed(() => {
  const grouped = Object.fromEntries(technicalDocCategories.map((category) => [category, []]))
  for (const item of materialsItems.value) {
    if (!grouped[item.category]) {
      grouped[item.category] = []
    }
    grouped[item.category].push(item)
  }
  return grouped
})

function t(path) {
  return path.split('.').reduce((accumulator, key) => accumulator?.[key], messages[locale.value]) ?? path
}

const todayTick = ref(Date.now())

const faultHint = computed(() => {
  if (!faultHasSearched.value) {
    return isEnglish.value ? 'Showing the full simulated fault library by default.' : '默认展示全部模拟故障库，输入关键字后即可快速筛选。'
  }
  return faultKeyword.value.trim() ? `${isEnglish.value ? 'Current keyword' : '当前搜索词'}: ${faultKeyword.value.trim()}` : (isEnglish.value ? 'Showing all results.' : '显示全部结果。')
})

const faultTotalPages = computed(() => Math.max(1, Math.ceil((faultTotal.value || 0) / (faultPageSize.value || 1))))

const gridSummary = computed(() => {
  const totalMwh = gridProjects.value.reduce((sum, project) => sum + (Number(project.capacity_mwh) || 0), 0)
  const totalDayValue = getTodayDayValue()
  const palette = [
    'bg-cyan-400/80',
    'bg-emerald-400/80',
    'bg-violet-400/80',
    'bg-amber-400/80',
    'bg-fuchsia-400/80',
    'bg-sky-400/80',
  ]

  const projects = gridProjects.value.map((project, index) => {
    const capacityMwh = Number(project.capacity_mwh) || 0
    const ratio = totalMwh > 0 ? (capacityMwh / totalMwh) * 100 : 0
    const codDiff = getCodDayDiff(project.cod, totalDayValue)
    const delivered = isGridProjectDelivered(project)
    const daysLabel = codDiff === null
      ? t('common.noData')
      : delivered
        ? `${t('grid.deliveredDays')}: ${Math.max(-codDiff, 0)} ${isEnglish.value ? 'days' : '天'}`
        : codDiff >= 0
          ? `${t('grid.remainingDays')}: ${codDiff} ${isEnglish.value ? 'days' : '天'}`
          : `${t('grid.overdueDays')}: ${Math.abs(codDiff)} ${isEnglish.value ? 'days' : '天'}`

    return {
      ...project,
      capacityMwh,
      capacityRatio: ratio,
      ratioLabel: `${ratio.toFixed(1)}%`,
      deliveryState: delivered ? t('grid.deliveredTag') : t('grid.inProgressTag'),
      deliveryBadgeClass: delivered
        ? 'border border-emerald-300/20 bg-emerald-400/15 text-emerald-200'
        : 'border border-amber-300/20 bg-amber-400/15 text-amber-200',
      ratioBarClass: palette[index % palette.length],
      daysLabel,
    }
  })

  return { totalMwh, projects }
})

const staffModeBadge = computed(() => (staffMode.value ? t('app.staffBadge') : t('app.customerBadge')))

const CI_100C_MWH_PER_UNIT = 0.12
const CI_250_MWH_PER_UNIT = 0.25

const ciCapacityRows = computed(() => {
  const baseRows = ciDeliveries.value.map((item) => {
    const delivered100c = Number(item.delivered_100c) || 0
    const delivered250 = Number(item.delivered_250) || 0
    return {
      ...item,
      delivered_100c: delivered100c,
      delivered_250: delivered250,
      mwh100c: delivered100c * CI_100C_MWH_PER_UNIT,
      mwh250: delivered250 * CI_250_MWH_PER_UNIT,
    }
  })

  const max100cMwh = Math.max(0, ...baseRows.map((item) => item.mwh100c))
  const max250Mwh = Math.max(0, ...baseRows.map((item) => item.mwh250))

  return baseRows.map((item) => ({
    ...item,
    ratio100c: max100cMwh > 0 ? (item.mwh100c / max100cMwh) * 100 : 0,
    ratio250: max250Mwh > 0 ? (item.mwh250 / max250Mwh) * 100 : 0,
  }))
})

const ciSummary = computed(() => {
  const total100c = ciCapacityRows.value.reduce((sum, item) => sum + item.delivered_100c, 0)
  const total250 = ciCapacityRows.value.reduce((sum, item) => sum + item.delivered_250, 0)
  return {
    total100c,
    total250,
    total100cMwh: total100c * CI_100C_MWH_PER_UNIT,
    total250Mwh: total250 * CI_250_MWH_PER_UNIT,
  }
})

function makeTextDownload(content, filename) {
  return `data:text/plain;charset=utf-8,${encodeURIComponent(content)}#${encodeURIComponent(filename)}`
}

function formatMwh(value) {
  const numericValue = Number(value) || 0
  return Number.isInteger(numericValue) ? String(numericValue) : numericValue.toFixed(1)
}

function formatCiMwh(value) {
  return (Number(value) || 0).toFixed(2)
}

function currentTimestampStamp() {
  return new Date().toISOString().replaceAll('-', '').replaceAll(':', '').replaceAll('T', '').replaceAll('Z', '').replaceAll('.', '').slice(0, 14)
}

function prefillWarehouseTxNo() {
  warehouseForm.tx_no = `WH-${selectedWarehouse.value.toUpperCase()}-${currentTimestampStamp()}`
}

function statusClass(status) {
  const map = {
    '清关中': 'bg-amber-400/15 text-amber-200 border border-amber-300/20',
    '设备上岸': 'bg-sky-400/15 text-sky-200 border border-sky-300/20',
    '土建施工': 'bg-violet-400/15 text-violet-200 border border-violet-300/20',
    '调试中': 'bg-cyan-400/15 text-cyan-200 border border-cyan-300/20',
    '正式并网': 'bg-emerald-400/15 text-emerald-200 border border-emerald-300/20',
  }
  return map[status] ?? 'bg-white/10 text-slate-200 border border-white/10'
}

function getTodayDayValue(epochMs = todayTick.value) {
  const now = new Date(epochMs)
  return Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())
}

function getCodDayValue(cod) {
  if (!cod) return null
  const [year, month, day] = String(cod).split('-').map((part) => Number(part))
  if (!year || !month || !day) return null
  return Date.UTC(year, month - 1, day)
}

function getCodDayDiff(cod, todayDayValue = getTodayDayValue()) {
  const codDayValue = getCodDayValue(cod)
  if (codDayValue === null) return null
  return Math.round((codDayValue - todayDayValue) / 86400000)
}

function isGridProjectDelivered(project) {
  return project.progress_status === '正式并网'
}

function openVideo(url) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

function isVideoFile(item) {
  const fileType = String(item?.file_type ?? '').toLowerCase()
  const fileUrl = String(item?.file_url ?? '').toLowerCase()
  return fileType.startsWith('video/') || /\.(mp4|mov|webm|m4v)$/i.test(fileUrl) || item?.category === '安装视频'
}

function previewTechnicalDoc(item) {
  const previewUrl = technicalDocActionUrl(item, false)
  if (!previewUrl) return
  if (isVideoFile(item)) {
    openVideo(previewUrl)
    return
  }
  window.open(previewUrl, '_blank', 'noopener,noreferrer')
}

function technicalDocActionUrl(item, download = false) {
  const id = item?.id
  if (!id) {
    return item?.file_url || ''
  }
  return `/api/technical-docs/${encodeURIComponent(String(id))}/file${download ? '?download=1' : ''}`
}

function changeMaterialsSeries(series) {
  if (materialsProductSeries.value === series) {
    return
  }
  materialsProductSeries.value = series
  loadTechnicalDocs()
}

async function loadTechnicalDocs() {
  materialsLoading.value = true
  materialsError.value = ''
  try {
    const payload = await portalApi.listTechnicalDocs({ product: materialsProductSeries.value })
    materialsItems.value = payload.items ?? []
  } catch (error) {
    materialsItems.value = []
    materialsError.value = formatApiError(error, `${t('notices.loadFailed')} / Materials load failed`)
  } finally {
    materialsLoading.value = false
  }
}

function openTechnicalDocEditor(record = null) {
  if (!materialsCanManage.value) {
    setNotice(isEnglish.value ? 'No permission to modify materials.' : '当前无资料管理权限。', 'error')
    return
  }
  openCrudModal('technical-doc', record ? 'edit' : 'create', record)
}

function openTechnicalDocFilePicker() {
  technicalDocFileInputRef.value?.click()
}

function handleTechnicalDocFile(event) {
  const files = [...(event.target.files ?? [])]
  const file = files[0]
  if (!file) return
  crudDraft.technical_doc_file = file
  if (!crudDraft.title.trim()) {
    crudDraft.title = file.name.replace(/\.[^.]+$/, '')
  }
}

function handleStaffModeClick() {
  if (isInternalMode.value) {
    leaveStaffMode(isEnglish.value ? 'Staff mode disabled.' : '已退出内部员工模式')
    return
  }
  requestStaffMode()
}

function ensureInternalMode() {
  if (isInternalMode.value) {
    return true
  }
  setNotice(isEnglish.value ? 'Read-only mode: switch to Staff Mode to modify data.' : '当前为只读模式，请切换到内部员工模式后再执行修改。', 'error')
  return false
}

function confirmPassword() {
  confirmStaffAuth(t('auth.success'), t('auth.error'))
}

function openCrudModal(kind, mode = 'create', record = null) {
  if (kind === 'technical-doc') {
    if (!materialsCanManage.value) {
      setNotice(isEnglish.value ? 'No permission to modify materials.' : '当前无资料管理权限。', 'error')
      return
    }
  } else if (!ensureInternalMode()) {
    return
  }
  crudModal.kind = kind
  crudModal.mode = mode
  crudModal.originalKey = getRecordKey(kind, record) ?? ''
  crudModal.open = true
  resetCrudDraft(kind, record)
}

function closeCrudModal() {
  crudModal.open = false
  crudModal.kind = ''
  crudModal.mode = 'create'
  crudModal.originalKey = ''
}

function openDeleteDialog(kind, key, title, message) {
  if (kind === 'technical-doc') {
    if (!materialsCanManage.value) {
      setNotice(isEnglish.value ? 'No permission to modify materials.' : '当前无资料管理权限。', 'error')
      return
    }
  } else if (!ensureInternalMode()) {
    return
  }
  deleteDialog.kind = kind
  deleteDialog.key = key
  deleteDialog.title = title
  deleteDialog.message = message
  deleteDialog.open = true
}

function closeDeleteDialog() {
  deleteDialog.open = false
  deleteDialog.kind = ''
  deleteDialog.key = ''
  deleteDialog.title = ''
  deleteDialog.message = ''
}

function createEmptyCrudDraft() {
  return {
    id: null,
    module: '',
    fault_code: '',
    fault_name: '',
    fault_level: '',
    is_stop: '',
    recovery: '',
    detection_condition: '',
    trigger_logic: '',
    possible_cause: '',
    solution: '',
    project_name: '',
    cod: '',
    capacity_mwh: 0,
    cell_version: '',
    pcs_model: '',
    progress_status: projectStatuses[0],
    photo_paths: [],
    region: '',
    dealer_name: '',
    delivered_100c: 0,
    delivered_250: 0,
    warehouse_name: selectedWarehouse.value,
    tx_type: '国内到货入库',
    product_model: '100C',
    quantity: 1,
    related_project: '',
    tx_no: '',
    item_no: '',
    description_zh: '',
    specification: '',
    total_quantity: 0,
    damaged_quantity: 0,
    available_quantity: 0,
    product_series: materialsProductSeries.value,
    category: technicalDocCategories[0],
    title: '',
    file_url: '',
    file_type: '',
    file_size: '',
    technical_doc_file: null,
    remarks: '',
  }
}

function resetCrudDraft(kind, record) {
  const nextDraft = createEmptyCrudDraft()
  if (kind === 'fault' && record) {
    nextDraft.id = record.id
    nextDraft.module = record.module
    nextDraft.fault_code = record.fault_code
    nextDraft.fault_name = record.fault_name
    nextDraft.fault_level = record.fault_level
    nextDraft.is_stop = record.is_stop
    nextDraft.recovery = record.recovery
    nextDraft.detection_condition = record.detection_condition
    nextDraft.trigger_logic = record.trigger_logic
    nextDraft.possible_cause = record.possible_cause
    nextDraft.solution = record.solution
  }
  if (kind === 'grid' && record) {
    nextDraft.project_name = record.project_name
    nextDraft.cod = record.cod
    nextDraft.capacity_mwh = record.capacity_mwh
    nextDraft.cell_version = record.cell_version
    nextDraft.pcs_model = record.pcs_model
    nextDraft.progress_status = record.progress_status
    nextDraft.photo_paths = [...(record.photo_paths ?? [])]
  }
  if (kind === 'ci' && record) {
    nextDraft.region = record.region
    nextDraft.dealer_name = record.dealer_name
    nextDraft.delivered_100c = record.delivered_100c
    nextDraft.delivered_250 = record.delivered_250
  }
  if (kind === 'inventory' && record) {
    nextDraft.item_no = record.item_no
    nextDraft.description_zh = record.description_zh
    nextDraft.specification = record.specification
    nextDraft.total_quantity = record.total_quantity
    nextDraft.damaged_quantity = record.damaged_quantity
    nextDraft.available_quantity = record.available_quantity
    nextDraft.photo_paths = [...(record.photo_paths ?? [])]
    nextDraft.remarks = record.remarks ?? ''
  }
  if (kind === 'technical-doc' && record) {
    nextDraft.product_series = record.product_series
    nextDraft.category = record.category
    nextDraft.title = record.title
    nextDraft.file_url = record.file_url
    nextDraft.file_type = record.file_type
    nextDraft.file_size = record.file_size
    nextDraft.technical_doc_file = null
  }
  Object.assign(crudDraft, nextDraft)
  if (kind === 'warehouse' && !crudDraft.tx_no) {
    prefillWarehouseTxNo()
  }
  if (kind === 'inventory') {
    crudDraft.available_quantity = Number(crudDraft.available_quantity) || Math.max(Number(crudDraft.total_quantity) - Number(crudDraft.damaged_quantity), 0)
  }
}

function getRecordKey(kind, record) {
  if (!record) return ''
  if (kind === 'fault') return String(record.id)
  if (kind === 'grid') return record.project_name
  if (kind === 'ci') return record.dealer_name
  if (kind === 'technical-doc') return String(record.id)
  if (kind === 'inventory') return record.item_no
  if (kind === 'warehouse') return record.tx_no
  return ''
}

function normalizePhotoPaths(text) {
  return text.split(/[\n,;]/).map((item) => item.trim()).filter(Boolean)
}

function recomputeAvailableQuantity() {
  crudDraft.available_quantity = Math.max(Number(crudDraft.total_quantity) - Number(crudDraft.damaged_quantity), 0)
}

function openPhotoPicker() {
  if (!ensureInternalMode()) return
  photoInputRef.value?.click()
}

async function handlePhotoFiles(event) {
  if (!ensureInternalMode()) return
  const files = [...(event.target.files ?? [])]
  if (files.length === 0) return
  photoUploading.value = true
  try {
    for (const file of files) {
      const result = await portalApi.uploadImage(file)
      crudDraft.photo_paths.push(result.url)
    }
  } finally {
    photoUploading.value = false
    event.target.value = ''
  }
}

function removePhotoPath(index) {
  crudDraft.photo_paths.splice(index, 1)
}

function openImagePreview(url) {
  imagePreviewUrl.value = resolvePhotoUrl(url)
}

function resolvePhotoUrl(photo) {
  if (!photo) return ''
  if (photo.startsWith('http://') || photo.startsWith('https://') || photo.startsWith('data:')) {
    return photo
  }
  if (photo.startsWith('/static_uploads/')) {
    return photo
  }
  return `/static_uploads/${photo.replace(/^\/+/, '')}`
}

function closeImagePreview() {
  imagePreviewUrl.value = ''
}

function formatApiError(error, fallback) {
  return `${fallback}: ${error instanceof Error ? error.message : 'Unknown error'}`
}

async function handleFaultSearch() {
  faultPage.value = 1
  await loadAfterSalesFaultCodes()
}

async function loadAfterSalesFaultCodes() {
  faultLoading.value = true
  faultError.value = ''
  faultHasSearched.value = true
  try {
    const payload = await portalApi.listAfterSalesFaultCodes({
      page: faultPage.value,
      pageSize: faultPageSize.value,
      module: faultModule.value,
      keyword: faultKeyword.value.trim(),
    })
    faultResults.value = payload.items ?? []
    faultTotal.value = Number(payload.total) || faultResults.value.length
    const moduleSet = new Set(faultModules.value)
    for (const item of faultResults.value) {
      if (item?.module) {
        moduleSet.add(item.module)
      }
    }
    faultModules.value = [...moduleSet]
  } catch (error) {
    faultError.value = formatApiError(error, `${t('notices.loadFailed')} / API request failed`)
    faultResults.value = []
    faultTotal.value = 0
  } finally {
    faultLoading.value = false
  }
}

async function handleFaultFilterChange() {
  faultPage.value = 1
  await loadAfterSalesFaultCodes()
}

async function handleFaultPageSizeChange() {
  faultPage.value = 1
  await loadAfterSalesFaultCodes()
}

async function goFaultPage(nextPage) {
  const page = Number(nextPage) || 1
  if (page < 1 || page > faultTotalPages.value || page === faultPage.value) {
    return
  }
  faultPage.value = page
  await loadAfterSalesFaultCodes()
}

async function loadLedgerData() {
  ledgerLoading.value = true
  try {
    const [gridPayload, ciPayload] = await Promise.all([portalApi.listGridProjects(), portalApi.listCiDeliveries()])
    gridProjects.value = gridPayload.items ?? []
    ciDeliveries.value = ciPayload.items ?? []
    for (const project of gridProjects.value) {
      projectDraftStatus[project.project_name] = project.progress_status
    }
  } catch (error) {
    setNotice(formatApiError(error, `${t('notices.loadFailed')} / Ledger load failed`), 'error')
  } finally {
    ledgerLoading.value = false
  }
}

async function loadWarehouseData() {
  warehouseLoading.value = true
  warehouseError.value = ''
  try {
    const payload = await portalApi.getWarehouseSummary(selectedWarehouse.value)
    warehouseSummary.value = payload
    if (!warehouseForm.tx_no) {
      prefillWarehouseTxNo()
    }
    if (!warehouseProductOptions.value.includes(warehouseForm.product_model)) {
      warehouseForm.product_model = warehouseProductOptions.value[0] ?? '100C'
    }
  } catch (error) {
    warehouseError.value = formatApiError(error, `${t('notices.loadFailed')} / Warehouse load failed`)
  } finally {
    warehouseLoading.value = false
  }
}

async function loadWarehouseInventory() {
  inventoryLoading.value = true
  inventoryError.value = ''
  try {
    const payload = await portalApi.listWarehouseInventory()
    inventoryItems.value = payload.items ?? []
  } catch (error) {
    inventoryError.value = formatApiError(error, `${t('notices.loadFailed')} / Inventory load failed`)
  } finally {
    inventoryLoading.value = false
  }
}

async function saveProjectStatus(projectName) {
  if (!ensureInternalMode()) return
  const nextStatus = projectDraftStatus[projectName]
  if (!nextStatus) return
  await portalApi.updateGridProjectStatus(projectName, nextStatus)
  await loadLedgerData()
  setNotice(t('notices.gridSaved'), 'success')
}

function openProjectEditor(record = null) {
  openCrudModal('grid', record ? 'edit' : 'create', record)
}

function openCiEditor(record = null) {
  openCrudModal('ci', record ? 'edit' : 'create', record)
}

function openFaultEditor(record = null) {
  openCrudModal('fault', record ? 'edit' : 'create', record)
}

function openWarehouseEditor(record = null) {
  openCrudModal('warehouse', record ? 'edit' : 'create', record)
}

function openInventoryEditor(record = null) {
  openCrudModal('inventory', record ? 'edit' : 'create', record)
}

async function submitCrud() {
  if (!crudModal.kind) return
  if (crudModal.kind === 'technical-doc') {
    if (!materialsCanManage.value) {
      setNotice(isEnglish.value ? 'No permission to modify materials.' : '当前无资料管理权限。', 'error')
      return
    }
  } else if (!ensureInternalMode()) {
    return
  }
  if (crudModal.kind === 'technical-doc') {
    const payload = {
      product_series: crudDraft.product_series,
      category: crudDraft.category,
      title: crudDraft.title.trim(),
    }

    if (!payload.title) {
      setNotice(isEnglish.value ? 'Title is required.' : '标题不能为空。', 'error')
      return
    }

    if (crudModal.mode === 'create') {
      if (!crudDraft.technical_doc_file) {
        setNotice(isEnglish.value ? 'Please choose a file first.' : '请先选择上传文件。', 'error')
        return
      }
      const formData = new FormData()
      formData.append('product_series', payload.product_series)
      formData.append('category', payload.category)
      formData.append('title', payload.title)
      formData.append('file', crudDraft.technical_doc_file)
      await portalApi.uploadTechnicalDoc(formData)
    } else {
      await portalApi.updateTechnicalDoc(crudModal.originalKey, payload)
    }

    await loadTechnicalDocs()
    setNotice(t('materials.savedNotice'), 'success')
  }

  if (crudModal.kind === 'fault') {
    const payload = {
      module: crudDraft.module.trim(),
      fault_code: crudDraft.fault_code.trim(),
      fault_name: crudDraft.fault_name.trim(),
      fault_level: crudDraft.fault_level.trim(),
      is_stop: crudDraft.is_stop.trim(),
      recovery: crudDraft.recovery.trim(),
      detection_condition: crudDraft.detection_condition.trim(),
      trigger_logic: crudDraft.trigger_logic.trim(),
      possible_cause: crudDraft.possible_cause.trim(),
      solution: crudDraft.solution.trim(),
    }

    if (!payload.module || !payload.fault_code) {
      setNotice(isEnglish.value ? 'Module and fault code are required.' : '模块和故障码不能为空。', 'error')
      return
    }

    if (crudModal.mode === 'create') {
      await portalApi.createAfterSalesFaultCode(payload)
    } else {
      await portalApi.updateAfterSalesFaultCode(crudModal.originalKey, payload)
    }
    await handleFaultSearch()
    setNotice(t('notices.faultCreated'), 'success')
  }

  if (crudModal.kind === 'grid') {
    const payload = {
      project_name: crudDraft.project_name.trim(),
      cod: crudDraft.cod.trim(),
      capacity_mwh: Number(crudDraft.capacity_mwh) || 0,
      cell_version: crudDraft.cell_version.trim(),
      pcs_model: crudDraft.pcs_model.trim(),
      progress_status: crudDraft.progress_status,
      photo_paths: [...crudDraft.photo_paths],
    }
    if (crudModal.mode === 'create') {
      await portalApi.createGridProject(payload)
    } else {
      await portalApi.updateGridProject(crudModal.originalKey, payload)
    }
    await loadLedgerData()
    setNotice(t('notices.gridSaved'), 'success')
  }

  if (crudModal.kind === 'ci') {
    const payload = {
      dealer_name: crudDraft.dealer_name.trim(),
      region: crudDraft.region.trim(),
      delivered_100c: Number(crudDraft.delivered_100c) || 0,
      delivered_250: Number(crudDraft.delivered_250) || 0,
    }
    if (crudModal.mode === 'create') {
      await portalApi.createCiDelivery(payload)
    } else {
      await portalApi.updateCiDelivery(crudModal.originalKey, payload)
    }
    await loadLedgerData()
    setNotice(t('notices.ciSaved'), 'success')
  }

  if (crudModal.kind === 'warehouse') {
    const payload = {
      warehouse_name: crudDraft.warehouse_name,
      tx_type: crudDraft.tx_type,
      product_model: crudDraft.product_model,
      quantity: Number(crudDraft.quantity) || 0,
      related_project: crudDraft.related_project.trim(),
      tx_no: crudDraft.tx_no.trim() || `WH-${crudDraft.warehouse_name.toUpperCase()}-${currentTimestampStamp()}`,
    }
    if (crudModal.mode === 'create') {
      await portalApi.createWarehouseTransaction(payload)
    } else {
      await portalApi.updateWarehouseTransaction(crudModal.originalKey, payload)
    }
    selectedWarehouse.value = payload.warehouse_name
    await loadWarehouseData()
    setNotice(t('notices.txSaved'), 'success')
  }

  if (crudModal.kind === 'inventory') {
    const payload = {
      item_no: crudDraft.item_no.trim(),
      description_zh: crudDraft.description_zh.trim(),
      specification: crudDraft.specification.trim(),
      total_quantity: Number(crudDraft.total_quantity) || 0,
      damaged_quantity: Number(crudDraft.damaged_quantity) || 0,
      available_quantity: Number(crudDraft.available_quantity) || Math.max(Number(crudDraft.total_quantity) - Number(crudDraft.damaged_quantity), 0),
      photo_paths: [...crudDraft.photo_paths],
      remarks: crudDraft.remarks.trim(),
    }
    if (crudModal.mode === 'create') {
      await portalApi.createWarehouseInventoryItem(payload)
    } else {
      await portalApi.updateWarehouseInventoryItem(crudModal.originalKey, payload)
    }
    await loadWarehouseInventory()
    setNotice(t('notices.inventorySaved'), 'success')
  }

  closeCrudModal()
}

async function confirmDelete() {
  const { kind, key } = deleteDialog
  if (!kind || !key) return
  if (kind === 'technical-doc') {
    if (!materialsCanManage.value) {
      setNotice(isEnglish.value ? 'No permission to modify materials.' : '当前无资料管理权限。', 'error')
      return
    }
  } else if (!ensureInternalMode()) {
    return
  }
  if (kind === 'fault') {
    await portalApi.deleteAfterSalesFaultCode(key)
    await handleFaultSearch()
  }
  if (kind === 'grid') {
    await portalApi.deleteGridProject(key)
    await loadLedgerData()
  }
  if (kind === 'ci') {
    await portalApi.deleteCiDelivery(key)
    await loadLedgerData()
  }
  if (kind === 'warehouse') {
    await portalApi.deleteWarehouseTransaction(key)
    await loadWarehouseData()
  }
  if (kind === 'inventory') {
    await portalApi.deleteWarehouseInventoryItem(key)
    await loadWarehouseInventory()
  }
  if (kind === 'technical-doc') {
    await portalApi.deleteTechnicalDoc(key)
    await loadTechnicalDocs()
  }
  setNotice(t('notices.deleted'), 'success')
  closeDeleteDialog()
}

async function applyProjectStatus(projectName) {
  await saveProjectStatus(projectName)
}

async function submitWarehouseTransaction() {
  if (!ensureInternalMode()) return
  if (!warehouseForm.tx_no) {
    prefillWarehouseTxNo()
  }
  await portalApi.createWarehouseTransaction({
    warehouse_name: selectedWarehouse.value,
    tx_type: warehouseForm.tx_type,
    product_model: warehouseForm.product_model,
    quantity: Number(warehouseForm.quantity) || 0,
    related_project: warehouseForm.related_project,
    tx_no: warehouseForm.tx_no,
  })
  warehouseForm.quantity = 1
  warehouseForm.related_project = ''
  prefillWarehouseTxNo()
  await loadWarehouseData()
  setNotice(t('notices.txSaved'), 'success')
}

watch(selectedWarehouse, async () => {
  await loadWarehouseData()
})

watch(isInternalMode, (enabled) => {
  if (enabled) return
  closeCrudModal()
  closeDeleteDialog()
})

onMounted(async () => {
  todayTick.value = Date.now()
  const timerId = window.setInterval(() => {
    todayTick.value = Date.now()
  }, 60000)
  gridDashboardTimerId = timerId
  prefillWarehouseTxNo()
  await Promise.all([handleFaultSearch(), loadLedgerData(), loadWarehouseData(), loadWarehouseInventory(), loadTechnicalDocs()])
})

onUnmounted(() => {
  if (gridDashboardTimerId !== null) {
    window.clearInterval(gridDashboardTimerId)
    gridDashboardTimerId = null
  }
})
</script>