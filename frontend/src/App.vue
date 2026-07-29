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
          <div class="flex flex-wrap rounded-2xl border border-white/10 bg-slate-950/70 p-1">
            <button
              v-for="view in views"
              :key="view.key"
              type="button"
              class="rounded-xl px-4 py-2 text-sm font-medium transition"
              :class="activeView === view.key ? 'bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-400/20' : 'text-slate-300 hover:bg-white/5 hover:text-white'"
              @click="activeView = view.key"
            >
              {{ view.label }}
            </button>
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
            {{ staffMode ? t('auth.leave') : t('app.staffMode') }}
          </button>
        </div>
      </header>

      <div v-if="portalState.notice" class="mb-4 rounded-2xl border px-4 py-3 text-sm" :class="portalState.noticeType === 'error' ? 'border-rose-400/20 bg-rose-500/10 text-rose-100' : portalState.noticeType === 'success' ? 'border-emerald-400/20 bg-emerald-500/10 text-emerald-100' : 'border-white/10 bg-white/5 text-slate-100'">
        {{ portalState.notice }}
      </div>

      <div class="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
        <span>{{ staffMode ? t('common.managedHint') : t('common.readOnlyHint') }}</span>
        <span class="rounded-full border border-white/10 bg-slate-950/60 px-3 py-1 text-xs uppercase tracking-[0.24em] text-cyan-200">
          {{ staffModeBadge }}
        </span>
      </div>

      <section v-if="activeView === 'after-sales'" class="flex-1">
        <div class="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-start">
          <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">After-sales Service</p>
            <div class="mt-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">{{ t('fault.section') }}</h2>
                <p class="mt-3 text-sm leading-7 text-slate-300 sm:text-base">{{ t('fault.subtitle') }}</p>
              </div>
              <button v-if="staffMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openFaultEditor()">
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
              {{ t('fault.currentCount') }}：<span class="font-semibold text-white">{{ faultResults.length }}</span>
            </div>
          </aside>
        </div>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-white sm:text-2xl">{{ t('fault.resultTitle') }}</h3>
            <p class="mt-1 text-sm text-slate-400">{{ faultHint }}</p>
          </div>
          <div class="text-sm text-slate-500">{{ faultLoading ? 'Loading...' : `${faultResults.length} item(s)` }}</div>
        </div>

        <div v-if="faultLoading" class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 3" :key="index" class="h-56 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else-if="faultError" class="mt-4 rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100">
          {{ faultError }}
        </div>

        <div v-else-if="faultResults.length > 0" class="mt-4 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article v-for="item in faultResults" :key="item.fault_code" class="group rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:-translate-y-0.5 hover:border-cyan-400/30 hover:bg-white/7">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-medium text-cyan-200">{{ item.fault_code }}</p>
                <h4 class="mt-1 text-lg font-semibold text-white">{{ item.fault_name }}</h4>
              </div>
              <span class="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">Match</span>
            </div>
            <div v-if="staffMode" class="mt-3 flex flex-wrap gap-2">
              <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openFaultEditor(item)">{{ t('common.edit') }}</button>
              <button type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('fault', item.fault_code, item.fault_code, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
            </div>
            <div class="mt-5 space-y-4 text-sm leading-6 text-slate-300">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{{ t('fault.possibleCauses') }}</p>
                <p class="mt-2 whitespace-pre-line">{{ item.possible_causes }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{{ t('fault.solution') }}</p>
                <p class="mt-2 whitespace-pre-line">{{ item.solution }}</p>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-4 rounded-3xl border border-dashed border-white/15 bg-white/5 p-10 text-center text-slate-300">
          <p class="text-lg font-medium text-white">{{ t('fault.noResult') }}</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">{{ t('fault.noResultHint') }}</p>
        </div>

        <div class="mt-8 grid gap-6 xl:grid-cols-2">
          <section class="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div class="flex items-end justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Documents</p>
                <h3 class="mt-2 text-xl font-semibold text-white">技术文档与教学多媒体 / Materials Center</h3>
              </div>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">PDF / Video</span>
            </div>

            <div class="mt-4 grid gap-4 md:grid-cols-3">
              <article v-for="doc in documents" :key="doc.title" class="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div class="flex items-start justify-between gap-3">
                  <div class="flex items-center gap-3">
                    <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-rose-500/15 text-sm font-bold text-rose-200">PDF</div>
                    <div>
                      <p class="text-sm font-semibold text-white">{{ doc.title }}</p>
                      <p class="text-xs text-slate-400">{{ doc.desc }}</p>
                    </div>
                  </div>
                </div>
                <a :href="doc.href" :download="doc.filename" class="mt-4 inline-flex w-full items-center justify-center rounded-xl bg-white/5 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:bg-white/10">
                  下载 / Download
                </a>
              </article>
            </div>
          </section>

          <section class="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div class="flex items-end justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Training Videos</p>
                <h3 class="mt-2 text-xl font-semibold text-white">标准化教学视频</h3>
              </div>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">Play / Download</span>
            </div>

            <div class="mt-4 grid gap-4 md:grid-cols-3">
              <article v-for="video in videos" :key="video.title" class="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/60">
                <div class="flex aspect-video items-center justify-center bg-gradient-to-br from-cyan-400/15 via-slate-950 to-emerald-400/10 text-center">
                  <div>
                    <p class="text-sm font-semibold text-white">{{ video.title }}</p>
                    <p class="mt-1 text-xs text-slate-300">{{ video.subtitle }}</p>
                    <p class="mt-2 text-[11px] tracking-[0.24em] text-cyan-200">{{ video.duration }}</p>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-2 p-3">
                  <button type="button" class="rounded-xl bg-cyan-400 px-3 py-2 text-xs font-semibold text-slate-950 transition hover:brightness-110" @click="openVideo(video.url)">
                    播放 / Play
                  </button>
                  <a :href="video.url" download class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-center text-xs font-semibold text-white transition hover:bg-white/10">
                    下载 / Download
                  </a>
                </div>
              </article>
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
              <button v-if="staffMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openProjectEditor()">
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

            <div v-if="staffMode" class="mt-4 flex flex-wrap gap-2">
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
              <button v-if="staffMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openCiEditor()">
                {{ t('ci.createDealer') }}
              </button>
            </div>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
            {{ t('ci.dealerCount') }}：<span class="font-semibold text-white">{{ ciDeliveries.length }}</span>
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
                  <th class="px-5 py-4 font-medium">{{ t('ci.total') }}</th>
                  <th v-if="staffMode" class="px-5 py-4 font-medium">{{ t('common.actions') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <tr v-for="item in ciDeliveries" :key="item.dealer_name" class="bg-white/[0.02] hover:bg-white/[0.04]">
                  <td class="px-5 py-4">{{ item.region }}</td>
                  <td class="px-5 py-4 font-medium text-white">{{ item.dealer_name }}</td>
                  <td class="px-5 py-4"><span class="rounded-full bg-cyan-400/10 px-3 py-1 font-semibold text-cyan-200">{{ item.delivered_100c }}</span></td>
                  <td class="px-5 py-4"><span class="rounded-full bg-emerald-400/10 px-3 py-1 font-semibold text-emerald-200">{{ item.delivered_250 }}</span></td>
                  <td class="px-5 py-4 font-semibold text-white">{{ item.delivered_100c + item.delivered_250 }}</td>
                  <td v-if="staffMode" class="px-5 py-4">
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
              <button v-if="staffMode" type="button" class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15" @click="openInventoryEditor()">
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
                  <th v-if="staffMode" class="px-5 py-4 font-medium">{{ t('common.actions') }}</th>
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
                  <td v-if="staffMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openInventoryEditor(item)">{{ t('common.edit') }}</button>
                      <button type="button" class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15" @click="openDeleteDialog('inventory', item.item_no, item.item_no, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="inventoryItems.length === 0">
                  <td :colspan="staffMode ? 9 : 8" class="px-4 py-10 text-center text-slate-400">{{ t('common.noData') }}</td>
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
              <h3 class="mt-2 text-2xl font-semibold text-white">{{ crudModal.kind === 'fault' ? t('fault.adminCreate') : crudModal.kind === 'grid' ? t('grid.createTitle') : crudModal.kind === 'ci' ? t('ci.createTitle') : t('inventory.createTitle') }}</h3>
            </div>
            <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="closeCrudModal">{{ t('common.close') }}</button>
          </div>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <template v-if="crudModal.kind === 'fault'">
              <label class="block">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Fault Code</span>
                <input v-model="crudDraft.fault_code" :disabled="crudModal.mode === 'edit'" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:cursor-not-allowed disabled:opacity-60" />
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Fault Name</span>
                <input v-model="crudDraft.fault_name" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Possible Causes</span>
                <textarea v-model="crudDraft.possible_causes" rows="4" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"></textarea>
              </label>
              <label class="block md:col-span-2">
                <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Solution</span>
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
  { key: 'grid-scale', label: t('views.gridScale') },
  { key: 'ci-dashboard', label: t('views.ciDashboard') },
  { key: 'warehouse', label: t('views.warehouse') },
])

const warehouseOptions = [
  { key: 'europe', label: '欧洲仓 / Europe' },
  { key: 'north_america', label: '北美仓 / North America' },
]

const documents = [
  {
    title: '安装手册',
    desc: 'Installation Manual',
    filename: 'installation-manual.pdf',
    href: makeTextDownload('JD Energy 安装手册\n\n此处为演示下载文件，可后续替换为真实 PDF。', 'installation-manual.pdf'),
  },
  {
    title: '调试手册',
    desc: 'Commissioning Manual',
    filename: 'commissioning-manual.pdf',
    href: makeTextDownload('JD Energy 调试手册\n\n此处为演示下载文件，可后续替换为真实 PDF。', 'commissioning-manual.pdf'),
  },
  {
    title: '运维手册',
    desc: 'O&M Manual',
    filename: 'operation-maintenance-manual.pdf',
    href: makeTextDownload('JD Energy 运维手册\n\n此处为演示下载文件，可后续替换为真实 PDF。', 'operation-maintenance-manual.pdf'),
  },
]

const videos = [
  { title: '标准化开箱视频', subtitle: 'Standard Unboxing', duration: '06:28', url: 'https://www.w3schools.com/html/mov_bbb.mp4' },
  { title: '线缆接线教学视频', subtitle: 'Cable Routing Tutorial', duration: '08:14', url: 'https://www.w3schools.com/html/mov_bbb.mp4' },
  { title: 'BMS 软件配置视频', subtitle: 'BMS Software Setup', duration: '10:06', url: 'https://www.w3schools.com/html/mov_bbb.mp4' },
]

const projectStatuses = ['清关中', '设备上岸', '土建施工', '调试中', '正式并网']

const faultKeyword = ref('')
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
const photoInputRef = ref(null)
const photoUploading = ref(false)
const imagePreviewUrl = ref('')

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
const staffMode = computed(() => portalState.staffMode)
const locale = computed(() => portalState.locale)
const isEnglish = computed(() => locale.value === 'en-US')

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

function makeTextDownload(content, filename) {
  return `data:text/plain;charset=utf-8,${encodeURIComponent(content)}#${encodeURIComponent(filename)}`
}

function formatMwh(value) {
  const numericValue = Number(value) || 0
  return Number.isInteger(numericValue) ? String(numericValue) : numericValue.toFixed(1)
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

function handleStaffModeClick() {
  if (staffMode.value) {
    leaveStaffMode(isEnglish.value ? 'Staff mode disabled.' : '已退出内部员工模式')
    return
  }
  requestStaffMode()
}

function confirmPassword() {
  confirmStaffAuth(t('auth.success'), t('auth.error'))
}

function openCrudModal(kind, mode = 'create', record = null) {
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
    fault_code: '',
    fault_name: '',
    possible_causes: '',
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
    remarks: '',
  }
}

function resetCrudDraft(kind, record) {
  const nextDraft = createEmptyCrudDraft()
  if (kind === 'fault' && record) {
    nextDraft.fault_code = record.fault_code
    nextDraft.fault_name = record.fault_name
    nextDraft.possible_causes = record.possible_causes
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
  if (kind === 'fault') return record.fault_code
  if (kind === 'grid') return record.project_name
  if (kind === 'ci') return record.dealer_name
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
  photoInputRef.value?.click()
}

async function handlePhotoFiles(event) {
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
  faultLoading.value = true
  faultError.value = ''
  faultHasSearched.value = true
  try {
    const payload = await portalApi.getFaultCodes(faultKeyword.value.trim())
    faultResults.value = payload.items ?? []
  } catch (error) {
    faultError.value = formatApiError(error, `${t('notices.loadFailed')} / API request failed`)
    faultResults.value = []
  } finally {
    faultLoading.value = false
  }
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
  if (crudModal.kind === 'fault') {
    if (crudModal.mode === 'create') {
      await portalApi.createFaultCode({
        fault_code: crudDraft.fault_code.trim(),
        fault_name: crudDraft.fault_name.trim(),
        possible_causes: crudDraft.possible_causes.trim(),
        solution: crudDraft.solution.trim(),
      })
    } else {
      await portalApi.updateFaultCode(crudModal.originalKey, {
        fault_name: crudDraft.fault_name.trim(),
        possible_causes: crudDraft.possible_causes.trim(),
        solution: crudDraft.solution.trim(),
      })
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
  if (kind === 'fault') {
    await portalApi.deleteFaultCode(key)
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
  setNotice(t('notices.deleted'), 'success')
  closeDeleteDialog()
}

async function applyProjectStatus(projectName) {
  await saveProjectStatus(projectName)
}

async function submitWarehouseTransaction() {
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

onMounted(async () => {
  todayTick.value = Date.now()
  const timerId = window.setInterval(() => {
    todayTick.value = Date.now()
  }, 60000)
  gridDashboardTimerId = timerId
  prefillWarehouseTxNo()
  await Promise.all([handleFaultSearch(), loadLedgerData(), loadWarehouseData(), loadWarehouseInventory()])
})

onUnmounted(() => {
  if (gridDashboardTimerId !== null) {
    window.clearInterval(gridDashboardTimerId)
    gridDashboardTimerId = null
  }
})
</script>