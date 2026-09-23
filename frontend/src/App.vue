<template>
  <div class="admin-shell flex min-h-screen bg-hero-grid theme-light text-slate-900">
    <aside
      class="sidebar sticky top-0 hidden h-screen w-64 shrink-0 flex-col overflow-y-auto bg-slate-950 text-slate-200 lg:flex"
    >
      <div class="sidebar-brand border-b border-white/10 px-5 py-5">
        <p
          class="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-[10px] font-semibold tracking-[0.2em] text-cyan-200 uppercase"
        >
          {{ t("app.brand") }}
        </p>
        <h1 class="mt-3 text-base font-bold text-white">
          {{ t("app.title") }}
        </h1>
      </div>
      <nav class="flex-1 space-y-5 overflow-y-auto px-3 py-5">
        <div v-for="group in navGroups" :key="group.key">
          <p
            class="sidebar-group-label mb-2 text-[13px] font-semibold uppercase tracking-wider text-slate-400"
          >
            {{ group.label }}
          </p>
          <div class="space-y-1">
            <button
              v-for="view in group.items"
              :key="view.key"
              type="button"
              class="sidebar-item w-full rounded-lg px-3 py-2 text-left text-sm font-medium transition"
              :class="
                activeView === view.key
                  ? 'sidebar-item-active bg-cyan-400 text-slate-950'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              "
              @click="activeView = view.key"
            >
              {{ view.label }}
            </button>
          </div>
        </div>
      </nav>
      <div class="sidebar-footer flex flex-col gap-2 border-t border-white/10 p-4">
        <button
          type="button"
          class="toolbar-btn rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
          @click="isAuthenticated ? logout() : (loginOpen = true)"
        >
          {{ isAuthenticated ? t("portal.logout") : t("portal.login") }}
        </button>
        <button
          type="button"
          class="toolbar-btn rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
          @click="toggleLocale"
        >
          {{ t("app.languageToggle") }}
        </button>
      </div>
    </aside>
    <main
      class="admin-content flex min-h-screen min-w-0 w-full flex-1 flex-col p-4 sm:p-5"
    >
      <div class="mb-4 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center lg:hidden">
          <select
            v-model="activeView"
            class="toolbar-btn rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100"
          >
            <optgroup
              v-for="group in navGroups"
              :key="group.key"
              :label="group.label"
            >
              <option
                v-for="view in group.items"
                :key="view.key"
                :value="view.key"
              >
                {{ view.label }}
              </option>
            </optgroup>
          </select>

          <button
            type="button"
            class="toolbar-btn rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
            @click="isAuthenticated ? logout() : (loginOpen = true)"
          >
            {{ isAuthenticated ? t("portal.logout") : t("portal.login") }}
          </button>

          <button
            type="button"
            class="toolbar-btn rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
            @click="toggleLocale"
          >
            {{ t("app.languageToggle") }}
          </button>
      </div>

      <div
        v-if="portalState.notice"
        class="mb-4 rounded-2xl border px-4 py-3 text-sm font-semibold"
        :class="
          portalState.noticeType === 'error'
            ? 'border-rose-200 bg-rose-50 text-rose-800'
            : portalState.noticeType === 'success'
              ? 'border-emerald-400/20 bg-emerald-500/10 text-emerald-100'
              : 'border-white/10 bg-white/5 text-slate-100'
        "
      >
        {{ portalState.notice }}
      </div>

      <div
        v-if="timelineOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm"
        @click.self="timelineOpen = false"
      >
        <div
          class="w-full max-w-3xl rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs uppercase tracking-[0.24em] text-cyan-200">
                {{ t("grid.milestoneTitle") }}
              </p>
              <h3 class="mt-2 text-2xl font-semibold text-white">
                {{ selectedProject?.project_name }}
              </h3>
            </div>
            <button
              type="button"
              class="rounded-xl border border-white/10 px-3 py-2 text-sm text-white"
              @click="timelineOpen = false"
            >
              {{ t("portal.close") }}
            </button>
          </div>
          <div class="mt-6 grid gap-3 md:grid-cols-4">
            <article
              v-for="item in milestones"
              :key="item.key"
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <div class="flex items-start justify-between gap-2">
                <span
                  class="h-3 w-3 rounded-full"
                  :class="
                    item.status === '已完成'
                      ? 'bg-emerald-400'
                      : item.status === '进行中'
                        ? 'bg-cyan-400'
                        : 'bg-slate-500'
                  "
                ></span
                >
              </div>
              <h4 class="mt-3 text-sm font-semibold text-white">
                {{ item.label }}
              </h4>
              <p class="mt-1 text-xs text-slate-300">
                {{ t("grid.actual") }}: {{ item.actual_date || "-" }}
              </p>
              <button
                v-if="isInternalMode"
                type="button"
                class="mt-3 text-xs font-semibold text-cyan-200"
                @click="editMilestone(item)"
              >
                {{ t("common.edit") }}
              </button>
            </article>
          </div>
          <div
            v-if="milestoneEditor"
            class="mt-5 grid gap-3 rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-4 md:grid-cols-2"
          >
            <input
              v-model="milestoneDraft.actual_date"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-white"
            /><button
              type="button"
              class="rounded-xl bg-cyan-400 px-3 py-2 text-sm font-semibold text-slate-950"
              @click="saveMilestone"
            >
              保存节点
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="loginOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm"
      >
        <div
          class="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/95 p-6"
        >
          <h3 class="text-2xl font-semibold text-white">
            {{ t("portal.loginTitle") }}
          </h3>
          <input
            v-model="loginDraft.username"
            placeholder="请输入账号 / Username"
            class="mt-5 w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white"
          />
          <input
            v-model="loginDraft.password"
            type="password"
            placeholder="请输入密码 / Password"
            class="mt-3 w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white"
            @keyup.enter="submitLogin"
          />
          <div class="mt-5 flex justify-end gap-2">
            <button
              type="button"
              class="rounded-xl border border-white/10 px-4 py-2 text-white"
              @click="loginOpen = false"
            >
              {{ t("portal.cancel") }}</button
            ><button
              type="button"
              class="rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950"
              @click="submitLogin"
            >
              {{ t("portal.submit") }}
            </button>
          </div>
        </div>
      </div>

      <section v-if="activeView === 'after-sales'" class="flex-1">
        <div class="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-start">
          <div
            class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl sm:p-8"
          >
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              {{ t("views.afterSales") }}
            </p>
            <div
              class="mt-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">
                  {{ t("fault.section") }}
                </h2>
                <p class="mt-3 text-sm leading-7 text-slate-300 sm:text-base">
                  {{ t("fault.subtitle") }}
                </p>
              </div>
              <button
                v-if="isInternalMode"
                type="button"
                class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
                @click="openFaultEditor()"
              >
                {{ t("fault.adminCreate") }}
              </button>
            </div>

            <form
              class="mt-6 flex flex-col gap-3 sm:flex-row"
              @submit.prevent="handleFaultSearch"
            >
              <label class="sr-only" for="fault-search">{{
                t("fault.placeholder")
              }}</label>
              <input
                id="fault-search"
                placeholder="设备序列号 / Serial Number"
                type="text"
              /><input
                v-model="serviceLogDraft.rd_contact"
                placeholder="研发对接人 / R&D Contact"
                class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
              /><select
                :placeholder="t('fault.placeholder')"
              />
              <button
                type="submit"
                class="rounded-2xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-4 text-base font-semibold text-slate-950 transition hover:brightness-110"
              >
                {{ t("fault.searchButton") }}
              </button>
            </form>

            <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
              <label
                class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                >模块</label
              >
              <select
                v-model="faultModule"
                class="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none sm:max-w-xs"
                @change="handleFaultFilterChange"
              >
                <option
                  v-for="module in faultModules"
                  :key="module"
                  :value="module"
                >
                  {{ module }}
                </option>
              </select>
              <label
                class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400 sm:ml-2"
                >每页</label
              >
              <select
                v-model.number="faultPageSize"
                class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none"
                @change="handleFaultPageSizeChange"
              >
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
              </select>
            </div>

            <div class="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
              <span
                v-for="chip in t('fault.chips')"
                :key="chip"
                class="rounded-full border border-white/10 bg-white/5 px-3 py-1"
                >{{ chip }}</span
              >
            </div>
          </div>

          <aside
            class="grid gap-4 rounded-3xl border border-white/10 bg-slate-950/55 p-5"
          >
            <div class="quick-guide-panel">
              <p class="text-xs uppercase tracking-[0.24em] text-cyan-200">
                Quick Guide
              </p>
              <p class="quick-guide-text mt-2 text-sm leading-6 text-slate-300">
                {{ t("fault.quickGuide") }}
              </p>
            </div>
            <div
              class="quick-count rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300"
            >
              {{ t("fault.currentCount") }}：<span
                class="quick-count-number font-semibold text-white"
                >{{ faultTotal }}</span
              >
            </div>
          </aside>
        </div>

        <div
          class="mt-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <h3 class="text-xl font-semibold text-white sm:text-2xl">
              {{ t("fault.resultTitle") }}
            </h3>
            <p class="mt-1 text-sm text-slate-400">{{ faultHint }}</p>
          </div>
          <div class="result-meta text-sm text-slate-500">
            {{
              faultLoading
                ? "Loading..."
                : `${faultResults.length} / ${faultTotal} item(s)`
            }}
          </div>
        </div>

        <div
          v-if="faultLoading"
          class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3"
        >
          <div
            v-for="index in 3"
            :key="index"
            class="h-56 animate-pulse rounded-3xl border border-white/10 bg-white/5"
          ></div>
        </div>

        <div
          v-else-if="faultError"
          class="mt-4 rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100"
        >
          {{ faultError }}
        </div>

        <div
          v-else-if="faultResults.length > 0"
          class="mt-4 overflow-hidden rounded-3xl border border-white/10 bg-white/5"
        >
          <div class="overflow-x-auto">
            <table
              class="min-w-full divide-y divide-white/10 text-left text-sm"
            >
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.module") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.code") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.name") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.level") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.shutdown") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.recovery") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.cause") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("fault.columns.resolution") }}</th>
                  <th v-if="isInternalMode" class="px-5 py-4 font-medium">
                    {{ t("common.actions") }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <tr
                  v-for="item in faultResults"
                  :key="`${item.module}-${item.fault_code}-${item.id}`"
                  class="bg-white/[0.02] hover:bg-white/[0.04]"
                >
                  <td class="px-5 py-4">
                    <span
                      class="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-200"
                      >{{ item.module || "-" }}</span
                    >
                  </td>
                  <td class="px-5 py-4 font-semibold text-white">
                    {{ item.fault_code || "-" }}
                  </td>
                  <td class="px-5 py-4 text-white">
                    {{ item.fault_name || "-" }}
                  </td>
                  <td class="px-5 py-4">{{ item.fault_level || "-" }}</td>
                  <td class="px-5 py-4">{{ item.is_stop || "-" }}</td>
                  <td class="px-5 py-4">{{ item.recovery || "-" }}</td>
                  <td class="max-w-xs px-5 py-4 text-slate-300">
                    {{ item.possible_cause || "-" }}
                  </td>
                  <td class="max-w-xs px-5 py-4 text-slate-300">
                    {{ item.solution || "-" }}
                  </td>
                  <td v-if="isInternalMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button
                        type="button"
                        class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
                        @click="openFaultEditor(item)"
                      >
                        {{ t("common.edit") }}
                      </button>
                      <button
                        type="button"
                        class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15"
                        @click="
                          openDeleteDialog(
                            'fault',
                            String(item.id),
                            `${item.module}-${item.fault_code}`,
                            t('common.deleteConfirm'),
                          )
                        "
                      >
                        {{ t("common.delete") }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            class="flex flex-col items-center justify-between gap-3 border-t border-white/10 px-5 py-4 sm:flex-row"
          >
            <p class="text-xs text-slate-400">
              第 {{ faultPage }} / {{ faultTotalPages }} 页，共
              {{ faultTotal }} 条
            </p>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                :disabled="faultPage <= 1"
                @click="goFaultPage(faultPage - 1)"
              >
                上一页
              </button>
              <button
                type="button"
                class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                :disabled="faultPage >= faultTotalPages"
                @click="goFaultPage(faultPage + 1)"
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <div
          v-else
          class="mt-4 rounded-3xl border border-dashed border-white/15 bg-white/5 p-10 text-center text-slate-300"
        >
          <p class="text-lg font-medium text-white">
            {{ t("fault.noResult") }}
          </p>
          <p class="mt-2 text-sm leading-6 text-slate-400">
            {{ t("fault.noResultHint") }}
          </p>
        </div>
      </section>

      <section v-else-if="activeView === 'materials-center'" class="flex-1">
        <div class="mb-5">
          <p
            class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
          >
            Materials Center
          </p>
          <div
            class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
          >
            <div>
              <h2 class="text-2xl font-semibold text-white sm:text-3xl">
                {{ t("views.materialsCenter") }}
              </h2>
              <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
                {{ t("materials.subtitle") }}
              </p>
            </div>
            <button
              v-if="materialsCanManage"
              type="button"
              class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
              @click="openTechnicalDocEditor()"
            >
              + 上传新资料
            </button>
          </div>
        </div>

        <div
          class="mb-5 flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-white/5 p-2"
        >
          <button
            v-for="series in technicalDocProductSeries"
            :key="series"
            type="button"
            class="rounded-xl px-4 py-2 text-sm font-semibold transition"
            :class="
              materialsProductSeries === series
                ? 'bg-cyan-400 text-slate-950'
                : 'text-slate-300 hover:bg-white/10 hover:text-white'
            "
            @click="changeMaterialsSeries(series)"
          >
            {{ series }}
          </button>
        </div>

        <div
          v-if="materialsLoading"
          class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
        >
          <div
            v-for="index in 5"
            :key="index"
            class="h-56 animate-pulse rounded-3xl border border-white/10 bg-white/5"
          ></div>
        </div>

        <div
          v-else-if="materialsError"
          class="rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100"
        >
          {{ materialsError }}
        </div>

        <div v-else class="grid gap-6 xl:grid-cols-2">
          <section
            v-for="category in technicalDocCategories"
            :key="category"
            class="rounded-3xl border border-white/10 bg-white/5 p-6"
          >
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-xl font-semibold text-white">{{ category }}</h3>
              <span
                class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300"
                >{{ materialsByCategory[category]?.length ?? 0 }}</span
              >
            </div>

            <div class="mt-4 grid gap-3">
              <article
                v-for="item in materialsByCategory[category]"
                :key="item.id"
                class="rounded-2xl border border-white/10 bg-slate-950/60 p-4"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="text-sm font-semibold text-white">
                      {{ item.title }}
                    </p>
                    <p class="doc-meta mt-1 text-xs text-slate-400">
                      {{ item.file_type || "-" }} · {{ item.file_size || "-" }}
                    </p>
                  </div>
                  <span
                    class="doc-series-badge rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 text-[11px] text-cyan-200"
                    >{{ item.product_series }}</span
                  >
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <button
                    type="button"
                    class="rounded-xl bg-cyan-400 px-3 py-2 text-xs font-semibold text-slate-950 transition hover:brightness-110"
                    @click="previewTechnicalDoc(item)"
                  >
                    {{ isVideoFile(item) ? "播放 / Play" : "预览 / Preview" }}
                  </button>
                  <a
                    :href="technicalDocActionUrl(item, true)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
                  >
                    下载 / Download
                  </a>
                  <button
                    v-if="materialsCanManage"
                    type="button"
                    class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
                    @click="openTechnicalDocEditor(item)"
                  >
                    编辑
                  </button>
                  <button
                    v-if="materialsCanManage"
                    type="button"
                    class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15"
                    @click="
                      openDeleteDialog(
                        'technical-doc',
                        String(item.id),
                        item.title,
                        t('common.deleteConfirm'),
                      )
                    "
                  >
                    删除
                  </button>
                </div>
              </article>
              <div
                v-if="(materialsByCategory[category] ?? []).length === 0"
                class="empty-placeholder rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-xs text-slate-400"
              >
                {{ t("common.noData") }}
              </div>
            </div>
          </section>
        </div>
      </section>

      <section v-else-if="activeView === 'overview' && overviewSubTab === 'grid-scale'" class="flex-1">
        <div class="mb-5 inline-flex rounded-full border border-slate-200 bg-white p-1 shadow-sm">
          <button
            type="button"
            class="rounded-full px-4 py-2 text-sm font-semibold transition"
            :class="overviewSubTab === 'grid-scale' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'"
            @click="overviewSubTab = 'grid-scale'"
          >
            {{ t("overviewTabs.gridScale") }}
          </button>
          <button
            type="button"
            class="rounded-full px-4 py-2 text-sm font-semibold transition"
            :class="overviewSubTab === 'ci-dashboard' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'"
            @click="overviewSubTab = 'ci-dashboard'"
          >
            {{ t("overviewTabs.ciDashboard") }}
          </button>
        </div>
        <div
          class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              Grid-Scale Delivery
            </p>
            <div
              class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">
                  {{ t("grid.section") }}
                </h2>
                <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
                  {{ t("grid.subtitle") }}
                </p>
              </div>
              <button
                v-if="isInternalMode"
                type="button"
                class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
                @click="openProjectEditor()"
              >
                {{ t("grid.adminCreate") }}
              </button>
            </div>
          </div>
          <div class="grid w-full gap-3 lg:max-w-3xl sm:grid-cols-2">
            <article
              class="grid-stat-card rounded-3xl border border-emerald-300/30 bg-emerald-400/10 p-4"
            >
              <div class="flex items-center justify-between gap-3">
                <span
                  class="grid-stat-badge rounded-full border border-emerald-300/40 bg-emerald-100/20 px-3 py-1 text-xs font-semibold text-emerald-200"
                  >{{ t("grid.deliveredTag") }}</span
                >
                <span
                  class="grid-stat-percent text-xs font-semibold text-emerald-200"
                  >{{ gridSummary.connectedRatioLabel }}</span
                >
              </div>
              <div class="mt-3 flex items-end gap-2">
                <span
                  class="grid-stat-value text-3xl font-semibold text-white sm:text-4xl"
                  >{{ formatMwh(gridSummary.connectedMwh) }}</span
                >
                <span
                  class="grid-stat-unit pb-1 text-sm font-medium text-slate-300"
                  >MWh</span
                >
              </div>
              <p class="grid-stat-meta mt-1 text-sm text-slate-300">
                {{ t("grid.projectCount") }}：<span
                  class="font-semibold text-white"
                  >{{ gridSummary.connectedCount }}</span
                >
              </p>
              <div
                class="mt-3 h-2 overflow-hidden rounded-full bg-slate-900/80"
              >
                <div
                  class="h-full rounded-full bg-gradient-to-r from-emerald-500 to-green-500 transition-all"
                  :style="{ width: `${gridSummary.connectedRatio}%` }"
                ></div>
              </div>
            </article>

            <article
              class="grid-stat-card rounded-3xl border border-amber-300/35 bg-amber-400/10 p-4"
            >
              <div class="flex items-center justify-between gap-3">
                <span
                  class="grid-stat-badge rounded-full border border-amber-300/40 bg-amber-100/20 px-3 py-1 text-xs font-semibold text-amber-200"
                  >{{ t("grid.inProgressTag") }}</span
                >
                <span
                  class="grid-stat-percent text-xs font-semibold text-amber-200"
                  >{{ gridSummary.pendingRatioLabel }}</span
                >
              </div>
              <div class="mt-3 flex items-end gap-2">
                <span
                  class="grid-stat-value text-3xl font-semibold text-white sm:text-4xl"
                  >{{ formatMwh(gridSummary.pendingMwh) }}</span
                >
                <span
                  class="grid-stat-unit pb-1 text-sm font-medium text-slate-300"
                  >MWh</span
                >
              </div>
              <p class="grid-stat-meta mt-1 text-sm text-slate-300">
                {{ t("grid.projectCount") }}：<span
                  class="font-semibold text-white"
                  >{{ gridSummary.pendingCount }}</span
                >
              </p>
              <div
                class="mt-3 h-2 overflow-hidden rounded-full bg-slate-900/80"
              >
                <div
                  class="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all"
                  :style="{ width: `${gridSummary.pendingRatio}%` }"
                ></div>
              </div>
            </article>

            <p
              class="grid-stat-total text-xs font-semibold text-slate-400 sm:col-span-2"
            >
              {{ t("grid.totalMwh") }}：<span class="font-semibold text-white"
                >{{ formatMwh(gridSummary.totalMwh) }} MWh</span
              >
              · {{ t("grid.projectCount") }}：<span
                class="font-semibold text-white"
                >{{ gridProjects.length }}</span
              >
            </p>
          </div>
        </div>

        <div
          v-if="ledgerLoading"
          class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
        >
          <div
            v-for="index in 3"
            :key="index"
            class="h-72 animate-pulse rounded-3xl border border-white/10 bg-white/5"
          ></div>
        </div>

        <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="project in gridSummary.projects"
            :key="project.project_name"
            class="grid-project-card overflow-hidden rounded-3xl border border-white/10 bg-white/5 transition hover:border-cyan-400/30"
          >
            <div
              class="relative h-44 w-full cursor-pointer overflow-hidden bg-gradient-to-br from-slate-800 to-slate-900"
              @click="
                project.photo_paths && project.photo_paths.length
                  ? openImagePreview(project.photo_paths[0])
                  : openProjectEditor(project)
              "
            >
              <img
                v-if="project.photo_paths && project.photo_paths.length"
                :src="resolvePhotoUrl(project.photo_paths[0])"
                :alt="project.project_name"
                class="h-full w-full object-cover transition duration-300 hover:scale-105"
              />
              <div
                v-else
                class="flex h-full w-full flex-col items-center justify-center gap-2 text-slate-400"
              >
                <span class="text-3xl">🔋</span>
                <span class="text-xs font-semibold uppercase tracking-widest">{{
                  t("grid.noPhotos")
                }}</span>
              </div>
              <span
                class="absolute left-3 top-3 rounded-full bg-slate-900/70 px-3 py-1 text-[10px] font-semibold text-white backdrop-blur"
                >{{ project.product_model || "418" }}</span
              >
            </div>
            <div class="p-5">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h3 class="text-lg font-semibold text-white">
                  {{ project.project_name }}
                </h3>
                <p
                  v-if="project.partner_name"
                  class="mt-1 text-xs font-medium text-cyan-200"
                >
                  {{ project.partner_name }}
                </p>
              </div>
              <div class="flex flex-col items-end gap-1">
                <span
                  class="rounded-full px-3 py-1 text-xs font-semibold"
                  :class="project.deliveryBadgeClass"
                  >{{ project.deliveryState }}</span
                >
                <span
                  v-if="project.daysLabel.includes(t('grid.overdueDays'))"
                  class="rounded-full bg-amber-400/20 px-2 py-1 text-[10px] font-bold text-amber-200"
                  >{{ t("grid.overdue") }}</span
                >
              </div>
            </div>

            <div class="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-300">
              <p>{{ t("grid.codDate") }}: <span class="text-white">{{ project.cod || "-" }}</span></p>
              <p>{{ t("grid.softwareVersion") }}: <span class="text-white">{{ project.software_version || project.cell_version || "-" }}</span></p>
            </div>

            <div
              class="grid-capacity-panel mt-5 rounded-2xl border border-white/10 bg-slate-950/60 p-4"
            >
              <div class="flex items-end justify-between gap-3">
                <p class="grid-ratio text-xs font-semibold text-cyan-200">
                  {{ project.ratioLabel }}
                </p>
              </div>
              <div class="mt-2 flex items-end justify-between gap-3">
                <p class="text-2xl font-semibold text-white">
                  {{ formatMwh(project.capacityMwh) }}
                  <span class="text-base text-slate-300">MWh</span>
                </p>
                <p class="pb-1 text-sm font-medium text-slate-300">
                  {{ project.ratioLabel }}
                </p>
              </div>
              <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-900">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all"
                  :style="{ width: `${project.capacityRatio}%` }"
                ></div>
              </div>
            </div>

            <div
              class="grid-day-block mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3"
            >
              <p class="grid-day-value mt-1 text-sm font-semibold text-white">
                {{ project.daysLabel }}
              </p>
            </div>

            <button
              type="button"
              class="mt-3 w-full rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-semibold text-cyan-100 transition hover:bg-cyan-400/20"
              @click="openMilestoneTimeline(project)"
            >
              查看交付里程碑
            </button>

            <div v-if="isInternalMode" class="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
                @click="openProjectEditor(project)"
              >
                {{ t("common.edit") }}
              </button>
              <button
                type="button"
                class="rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15"
                @click="
                  openDeleteDialog(
                    'grid',
                    project.id,
                    project.project_name,
                    t('common.deleteConfirm'),
                  )
                "
              >
                {{ t("common.delete") }}
              </button>
            </div>
            </div>
          </article>
        </div>
      </section>

      <section v-else-if="activeView === 'overview' && overviewSubTab === 'ci-dashboard'" class="flex-1">
        <div class="mb-5 inline-flex rounded-full border border-slate-200 bg-white p-1 shadow-sm">
          <button
            type="button"
            class="rounded-full px-4 py-2 text-sm font-semibold transition"
            :class="overviewSubTab === 'grid-scale' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'"
            @click="overviewSubTab = 'grid-scale'"
          >
            {{ t("overviewTabs.gridScale") }}
          </button>
          <button
            type="button"
            class="rounded-full px-4 py-2 text-sm font-semibold transition"
            :class="overviewSubTab === 'ci-dashboard' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'"
            @click="overviewSubTab = 'ci-dashboard'"
          >
            {{ t("overviewTabs.ciDashboard") }}
          </button>
        </div>
        <div
          class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              C&I Delivery Dashboard
            </p>
            <div
              class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">
                  {{ t("ci.section") }}
                </h2>
                <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
                  {{ t("ci.subtitle") }}
                </p>
              </div>
              <div class="flex flex-wrap items-center gap-2">
                <button
                  v-if="isAuthenticated"
                  type="button"
                  class="flex items-center gap-1.5 rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
                  @click="exportCiDeliveryDetails"
                >
                  导出交付明细
                </button>
                <button
                  v-if="isInternalMode"
                  type="button"
                  class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
                  @click="openCiEditor()"
                >
                  {{ t("ci.createDealer") }}
                </button>
              </div>
            </div>
          </div>
          <div class="ci-kpi-grid grid gap-3 sm:grid-cols-3">
            <div
              class="ci-kpi-card rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300"
            >
              {{ t("ci.dealerCount") }}：<span
                class="kpi-number font-semibold text-white"
                >{{ ciDeliveries.length }}</span
              >
            </div>
            <div
              class="ci-kpi-card ci-kpi-card-100c rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100"
            >
              <p class="text-xs uppercase tracking-[0.2em] text-cyan-200">
                100C
              </p>
              <p class="kpi-number mt-1 font-semibold text-white">
                {{ ciSummary.total100c }} 台
              </p>
              <p class="kpi-number kpi-number-sub text-xs text-cyan-200">
                {{ formatCiMwh(ciSummary.total100cMwh) }} MWh
              </p>
            </div>
            <div
              class="ci-kpi-card ci-kpi-card-250 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
            >
              <p class="text-xs font-bold uppercase tracking-[0.2em] text-emerald-700">
                250
              </p>
              <p class="kpi-number mt-1 text-base font-bold text-emerald-950">
                {{ ciSummary.total250 }} 台
              </p>
              <p class="kpi-number kpi-number-sub text-xs font-medium text-emerald-600">
                {{ formatCiMwh(ciSummary.total250Mwh) }} MWh
              </p>
            </div>
          </div>
        </div>

        <div
          class="overflow-hidden rounded-3xl border border-white/10 bg-white/5"
        >
          <div class="overflow-x-auto">
            <table
              class="data-table ci-data-table min-w-full divide-y divide-white/10 text-left text-sm"
            >
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">{{ t("ci.region") }}</th>
                  <th class="px-5 py-4 font-medium">{{ t("ci.dealer") }}</th>
                  <th class="px-5 py-4 font-medium">100C 已交付</th>
                  <th class="px-5 py-4 font-medium">250 已交付</th>
                  <th v-if="isInternalMode" class="px-5 py-4 font-medium">
                    {{ t("common.actions") }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <template v-for="item in ciCapacityRows" :key="item.dealer_name">
                <tr class="bg-white/[0.02] hover:bg-white/[0.04]">
                  <td class="key-cell px-5 py-4">{{ item.region }}</td>
                  <td class="key-cell px-5 py-4 font-medium text-white">
                    {{ item.dealer_name }}
                  </td>
                  <td class="cursor-pointer px-5 py-4" @click="toggleCiDeliveryBatches(item)">
                    <span class="mr-2 text-xs text-cyan-200">{{ ciExpandedDealerId === item.id ? '▼' : '▶' }}</span>
                    <p
                      class="delivery-metric delivery-metric-100c font-semibold text-cyan-200"
                    >
                      {{ item.delivered_100c }} 台 ({{
                        formatCiMwh(item.mwh100c)
                      }}
                      MWh)
                    </p>
                    <div
                      class="delivery-track mt-2 h-2 overflow-hidden rounded-full bg-slate-900"
                    >
                      <div
                        class="delivery-fill delivery-fill-100c h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all"
                        :style="{ width: `${item.ratio100c}%` }"
                      ></div>
                    </div>
                  </td>
                  <td class="cursor-pointer px-5 py-4" @click="toggleCiDeliveryBatches(item)">
                    <span class="mr-2 text-xs text-emerald-200">{{ ciExpandedDealerId === item.id ? '▼' : '▶' }}</span>
                    <p
                      class="delivery-metric delivery-metric-250 font-semibold text-emerald-200"
                    >
                      {{ item.delivered_250 }} 台 ({{
                        formatCiMwh(item.mwh250)
                      }}
                      MWh)
                    </p>
                    <div
                      class="delivery-track mt-2 h-2 overflow-hidden rounded-full bg-slate-900"
                    >
                      <div
                        class="delivery-fill delivery-fill-250 h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all"
                        :style="{ width: `${item.ratio250}%` }"
                      ></div>
                    </div>
                  </td>
                  <td v-if="isInternalMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button
                        type="button"
                        class="table-action-btn rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
                        @click="openCiEditor(item)"
                      >
                        {{ t("common.edit") }}
                      </button>
                      <button
                        type="button"
                        class="table-action-btn table-action-danger rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15"
                        @click="
                          openDeleteDialog(
                            'ci',
                            item.dealer_name,
                            item.dealer_name,
                            t('common.deleteConfirm'),
                          )
                        "
                      >
                        {{ t("common.delete") }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="ciExpandedDealerId === item.id" :key="`${item.id}-batches`">
                  <td colspan="5" class="border-y border-slate-200/80 bg-slate-50/70 p-4">
                    <div class="grid gap-5 lg:grid-cols-2">
                      <section v-for="productType in ['100C', '250']" :key="productType" class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                        <div class="mb-3 flex items-center justify-between gap-3">
                          <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-700">{{ productType }} 交付明细</h4>
                          <button v-if="isInternalMode" type="button" class="rounded-lg border border-sky-200 bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-600 transition-colors hover:bg-sky-100" @click="openBatchDeliveryModal(item, productType)">+ 新增交付批次</button>
                        </div>
                        <div v-if="ciBatchesByDealer[item.id]?.filter((batch) => batch.product_type === productType).length" class="divide-y divide-slate-100">
                          <div v-for="batch in ciBatchesByDealer[item.id].filter((entry) => entry.product_type === productType)" :key="batch.id" class="flex items-center justify-between gap-3 py-2 text-sm">
                            <span class="text-sm font-semibold text-slate-800">{{ batch.quantity }} 台</span>
                            <span class="font-mono text-xs text-slate-500">{{ batch.delivery_date }}</span>
                            <div v-if="isInternalMode" class="flex gap-2 text-xs">
                              <button type="button" class="mr-2 text-xs font-medium text-indigo-600 hover:text-indigo-800" @click="openBatchDeliveryModal(item, productType, batch)">{{ t('common.edit') }}</button>
                              <button type="button" class="text-xs font-medium text-rose-500 hover:text-rose-700" @click="openDeleteDialog('ci-batch', `${item.id}:${batch.id}`, `${productType} ${batch.delivery_date}`, t('common.deleteConfirm'))">{{ t('common.delete') }}</button>
                            </div>
                          </div>
                        </div>
                        <p v-else class="text-sm text-slate-500">暂无交付批次</p>
                      </section>
                    </div>
                  </td>
                </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section
        v-else-if="activeView === 'service-logs'"
        class="service-log-view flex-1"
      >
        <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              After-Sales Operations
            </p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">
              {{ t("portal.serviceLogs") }}
            </h2>
          </div>
          <div class="flex gap-2">
            <button
              v-if="isInternalMode"
              type="button"
              class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950"
              @click="serviceLogFormOpen = true"
            >
              {{ t("portal.addLog") }}</button
            ><button
              v-if="isInternalMode"
              type="button"
              class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white"
              @click="downloadServiceLogs"
            >
              {{ t("portal.exportCsv") }}
            </button>
          </div>
        </div>
        <div
          v-if="serviceLogFormOpen"
          class="mb-5 rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-5"
        >
          <div class="grid gap-3 md:grid-cols-3">
            <input
              v-model="serviceLogDraft.event_date"
              type="date"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            /><input
              v-model="serviceLogDraft.country"
              placeholder="国家"
              :disabled="serviceLogCountryLocked"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white disabled:opacity-60"
            /><select
              v-model="serviceLogDraft.customer_company"
              required
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option value="">客户/代理商名称</option>
              <option v-for="company in partnerOptions" :key="company" :value="company">{{ company }}</option>
            </select><select
              v-model="serviceLogDraft.project_name"
              required
              class="service-log-project-select rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option value="">选择项目</option>
              <option v-for="project in serviceLogProjectOptions" :key="project.project_name" :value="project.project_name">{{ project.project_name }}</option>
            </select><select
              v-model="serviceLogDraft.product_model"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option v-for="model in serviceLogProductModelOptions" :key="model" :value="model">{{ model }}</option></select
            ><select
              v-model="serviceLogDraft.support_type"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option>远程 (Remote)</option>
              <option>现场 (On-site)</option></select
            ><select
              v-model="serviceLogDraft.fault_component"
              required
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option value="">Faulty Component</option>
              <option v-for="component in faultyComponentOptions" :key="component" :value="component">{{ component }}</option>
            </select><input
              v-model="serviceLogDraft.serial_number"
              placeholder="设备序列号"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            /><select
              v-model="serviceLogDraft.status"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option>处理中 (Pending)</option>
              <option>已解决 (Resolved)</option></select
            ><input
              v-model="serviceLogDraft.created_by"
              placeholder="登记人"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            /><label class="block"><span class="mb-1 block text-xs text-slate-400">照片 Photos / Attachments</span><input type="file" multiple accept="image/*,.pdf" class="block w-full text-xs text-slate-300" @change="handlePortalAttachments($event, 'log')" /></label><textarea
              v-model="serviceLogDraft.fault_description"
              placeholder="故障描述 Fault Description"
              class="md:col-span-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            ></textarea><textarea
              v-model="serviceLogDraft.onsite_solution"
              placeholder="现场解决方案 On-site Solution"
              class="md:col-span-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            ></textarea><textarea
              v-model="serviceLogDraft.pending_reason"
              placeholder="跟进说明"
              class="md:col-span-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            ></textarea>
          </div>
          <div class="mt-3 flex justify-end gap-2">
            <button
              type="button"
              class="rounded-xl border border-white/10 px-4 py-2 text-white"
              @click="serviceLogFormOpen = false"
            >
              取消</button
            ><button
              type="button"
              class="rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950"
              @click="submitServiceLog"
            >
              保存
            </button>
          </div>
        </div>
        <div
          class="scroll-thin overflow-x-auto rounded-3xl border border-white/10 bg-white/5"
        >
          <table class="min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400">
              <tr>
                <th class="px-4 py-3">日期</th>
                <th class="px-4 py-3">国家 (Country)</th>
                <th class="px-4 py-3">客户 (Customer)</th>
                <th class="px-4 py-3">项目</th>
                <th class="px-4 py-3">型号</th>
                <th class="px-4 py-3">设备序列号 / Serial Number</th>
                <th class="px-4 py-3">远程/现场 (Support Type)</th>
                <th class="px-4 py-3">故障部位</th>
                <th class="px-4 py-3">故障描述 (Fault Description)</th>
                <th class="px-4 py-3">现场解决方案 (On-site Solution)</th>
                <th class="px-4 py-3">照片 (Photos)</th>
                <th class="px-4 py-3">状态</th>
                <th class="px-4 py-3">研发对接人 / R&D Contact</th>
                <th class="px-4 py-3">登记人</th>
                <th v-if="isInternalMode" class="px-4 py-3">
                  {{ t("common.actions") }}
                </th>
              </tr>
              <tr class="ticket-filter-row">
                <th><input v-model="serviceLogDateFilter" type="date" placeholder="筛选日期" /></th>
                <th><select v-model="serviceLogCountryFilter"><option value="">{{ t('common.all') }}</option><option v-for="country in serviceLogCountries" :key="country" :value="country">{{ country }}</option></select></th>
                <th><select v-model="serviceLogCustomerFilter"><option value="">{{ t('common.all') }}</option><option v-for="customer in partnerOptions" :key="customer" :value="customer">{{ customer }}</option></select></th>
                <th><input v-model="serviceLogProjectFilter" placeholder="搜索项目" /></th>
                <th><select v-model="serviceLogModelFilter"><option value="">{{ t('common.all') }}</option><option>418</option><option>250</option><option>100C</option></select></th>
                <th><input v-model="serviceLogSerialFilter" placeholder="搜索序列号" /></th>
                <th><select v-model="serviceLogSupportFilter"><option value="">{{ t('common.all') }}</option><option value="远程 (Remote)">远程 (Remote)</option><option value="现场 (On-site)">现场 (On-site)</option></select></th>
                <th><select v-model="serviceLogComponentFilter"><option value="">{{ t('common.all') }}</option><option v-for="component in faultyComponentOptions" :key="component" :value="component">{{ component }}</option></select></th>
                <th><input v-model="serviceLogDescriptionFilter" placeholder="搜索故障描述" /></th>
                <th></th>
                <th></th>
                <th><select v-model="serviceLogStatusFilter"><option value="">{{ t('common.all') }}</option><option value="处理中 (Pending)">处理中 (Pending)</option><option value="已解决 (Resolved)">已解决 (Resolved)</option></select></th>
                <th><input v-model="serviceLogRdContactFilter" placeholder="搜索研发对接人" /></th>
                <th><input v-model="serviceLogCreatedByFilter" placeholder="搜索登记人" /></th>
                <th v-if="isInternalMode"><button type="button" class="text-xs text-cyan-200" @click="clearAfterSalesFilters">{{ t('common.clearFilters') }}</button></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="item in computedFilteredAfterSalesLogs" :key="item.id">
                <td class="px-4 py-3">{{ item.event_date }}</td>
                <td class="px-4 py-3">{{ item.country || '-' }}</td>
                <td class="px-4 py-3">{{ item.customer_company || item.customer || '-' }}</td>
                <td class="px-4 py-3 font-medium text-white">
                  {{ item.project_name }}
                </td>
                <td class="px-4 py-3">{{ item.product_model }}</td>
                <td class="px-4 py-3">{{ item.serial_number || "-" }}</td>
                <td class="px-4 py-3">{{ item.support_type }}</td>
                <td class="px-4 py-3">{{ item.fault_component || item.faulty_component || "-" }}</td>
                <td class="max-w-xs truncate px-4 py-3" :title="item.fault_description">{{ item.fault_description || "-" }}</td>
                <td class="max-w-xs truncate px-4 py-3" :title="item.onsite_solution">{{ item.onsite_solution || "-" }}</td>
                <td class="px-4 py-3">
                  <div v-if="(item.attachments || []).length" class="flex gap-1">
                    <img
                      v-for="photo in item.attachments.slice(0, 3)"
                      :key="photo"
                      :src="resolvePhotoUrl(photo)"
                      class="h-9 w-9 cursor-pointer rounded-lg border border-white/10 object-cover transition hover:scale-105"
                      @click="openImagePreview(photo)"
                    />
                  </div>
                  <span v-else class="text-slate-500">-</span>
                </td>
                <td class="px-4 py-3">{{ item.status }}</td>
                <td class="px-4 py-3">{{ item.rd_contact || "-" }}</td>
                <td class="px-4 py-3">{{ item.created_by }}</td>
                <td v-if="isInternalMode" class="px-4 py-3">
                  <button
                    type="button"
                    class="mr-2 text-cyan-200"
                    @click="editServiceLog(item)"
                  >
                    {{ t("common.edit") }}</button
                  ><button
                    type="button"
                    class="text-rose-200"
                    @click="
                      openDeleteDialog(
                        'service-log',
                        String(item.id),
                        item.project_name,
                        t('common.deleteConfirm'),
                      )
                    "
                  >
                    {{ t("common.delete") }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else-if="activeView === 'customer-tickets'" class="flex-1">
        <div
          v-if="isInternalMode"
          class="mb-3 flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-white/5 p-3"
        >
          <select
            v-model="ticketUpdate.id"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-white"
          >
            <option value="">{{ t("portal.selectTicket") }}</option>
            <option v-for="item in tickets" :key="item.id" :value="item.id">
              #{{ item.id }} {{ item.project_name || "-" }}
            </option></select
          ><select
            v-model="ticketUpdate.status"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-white"
          >
            <option value="待处理 (Pending)">{{ t("portal.pending") }}</option>
            <option value="处理中 (In Progress)">
              {{ t("portal.inProgress") }}
            </option>
            <option value="已回复/已解决 (Resolved)">
              {{ t("portal.resolved") }}
            </option>
            <option value="已关闭 (Closed)">
              {{ t("portal.closed") }}
            </option></select
          ><input
            v-model="ticketUpdate.resolved_at"
            type="datetime-local"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-white"
          /><input
            v-model="ticketUpdate.staff_reply"
            :placeholder="t('portal.reply')"
            class="min-w-52 flex-1 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-white"
          /><button
            type="button"
            class="rounded-xl bg-cyan-400 px-3 py-2 text-sm font-semibold text-slate-950"
            @click="updateTicketStatus"
          >
            {{ t("portal.update") }}
          </button>
        </div>
        <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              Customer Care
            </p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">
              {{ t("portal.customerTickets") }}
            </h2>
          </div>
          <button
            v-if="isCustomer"
            type="button"
            class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950"
            @click="ticketFormOpen = true"
          >
            {{ t("portal.submitTicket") }}
          </button>
        </div>
        <div
          v-if="ticketFormOpen"
          class="mb-5 rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-5"
        >
          <div class="grid gap-3 md:grid-cols-2">
            <select
              v-if="ticketDraft.product_model === '418'"
              v-model="ticketDraft.project_name"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option value="">{{ t("portal.selectProject") }}</option>
              <option
                v-for="project in gridProjects"
                :key="project.project_name"
                :value="project.project_name"
              >
                {{ project.project_name }}
              </option></select
            ><select
              v-model="ticketDraft.product_model"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option>418</option>
              <option>250</option>
              <option>100C</option></select
            ><label class="block"
              ><span class="mb-2 block text-xs font-semibold text-slate-300">{{
                t("portal.serialNumber")
              }}</span
              ><input
                v-model="ticketDraft.serial_number"
                required
                :placeholder="t('portal.serialNumberRequired')"
                class="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" /></label
            ><select
              v-model="ticketDraft.ticket_type"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option value="产品需求 (Feature Request)">
                {{ t("portal.featureRequest") }}
              </option>
              <option value="故障报修/Bug (Issue Report)">
                {{ t("portal.issueReport") }}
              </option></select
            ><select
              v-model="ticketDraft.suspected_component"
              required
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            >
              <option value="">{{ t("portal.faultyComponent") }}</option>
              <option v-for="component in faultyComponentOptions" :key="component" :value="component">{{ component }}</option>
            </select><textarea
              v-model="ticketDraft.description"
              :placeholder="t('portal.detailedDescription')"
              rows="4"
              class="md:col-span-2 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            ></textarea
            ><input
              v-model="ticketDraft.contact"
              :placeholder="t('portal.contact')"
              class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
            /><label class="block"
              ><span class="mb-2 block text-xs font-semibold text-slate-300">{{
                t("portal.expectedDate")
              }}</span
              ><input
                v-model="ticketDraft.expected_date"
                type="date"
                class="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" /></label
            ><label class="block md:col-span-2"
              ><span class="mb-2 block text-xs font-semibold text-slate-300">{{
                t("portal.upload")
              }}</span
              ><input
                type="file"
                multiple
                class="block w-full text-sm text-slate-300"
                @change="handlePortalAttachments($event, 'ticket')"
            /></label>
          </div>
          <div class="mt-3 flex justify-end gap-2">
            <button
              type="button"
              class="rounded-xl border border-white/10 px-4 py-2 text-white"
              @click="ticketFormOpen = false"
            >
              {{ t("portal.cancel") }}</button
            ><button
              type="button"
              class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950"
              @click="submitTicket"
            >
              {{ t("portal.submitTicket") }}
            </button>
          </div>
        </div>
        <div
          class="scroll-thin overflow-x-auto rounded-3xl border border-white/10 bg-white/5"
        >
          <table class="min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400">
              <tr>
                <th class="px-4 py-3">{{ t("portal.submitTime") }}</th>
                <th class="px-4 py-3">{{ t("common.customerName") }}</th>
                <th class="px-4 py-3">{{ t("portal.project") }}</th>
                <th class="px-4 py-3">{{ t("portal.model") }}</th>
                <th class="px-4 py-3">{{ t("portal.faultyComponent") }}</th>
                <th class="px-4 py-3">{{ t("portal.serialNumber") }}</th>
                <th class="px-4 py-3">{{ t("portal.ticketType") }}</th>
                <th class="px-4 py-3">{{ t("portal.description") }}</th>
                <th class="px-4 py-3">{{ t("portal.ticketStatus") }}</th>
                <th class="px-4 py-3">{{ t("portal.reply") }}</th>
                <th class="px-4 py-3">{{ t("portal.resolvedTime") }}</th>
              </tr>
              <tr class="ticket-filter-row bg-slate-900/40">
                <th></th>
                <th><select v-model="ticketFilters.customer_company"><option value="">{{ t('common.all') }}</option><option v-for="company in customerOptions" :key="company" :value="company">{{ company }}</option></select></th>
                <th><input v-model="ticketFilters.project_name" :placeholder="t('portal.project')" /></th>
                <th><select v-model="ticketFilters.product_model"><option value="">{{ t('common.all') }}</option><option>418</option><option>250</option><option>100C</option></select></th>
                <th><select v-model="ticketFilters.faulty_component"><option value="">{{ t('common.all') }}</option><option v-for="component in faultyComponentOptions" :key="component" :value="component">{{ component }}</option></select></th>
                <th><input v-model="ticketFilters.serial_number" placeholder="SN" /></th>
                <th><select v-model="ticketFilters.ticket_type"><option value="">{{ t('common.all') }}</option><option value="故障报修/Bug (Issue Report)">{{ t('portal.issueReport') }}</option><option value="产品需求 (Feature Request)">{{ t('portal.featureRequest') }}</option></select></th>
                <th></th>
                <th><select v-model="ticketFilters.status"><option value="">{{ t('common.all') }}</option><option value="待处理 (Pending)">{{ t('portal.pending') }}</option><option value="处理中 (In Progress)">{{ t('portal.inProgress') }}</option><option value="已回复/已解决 (Resolved)">{{ t('portal.resolved') }}</option><option value="已关闭 (Closed)">{{ t('portal.closed') }}</option></select></th>
                <th></th><th><button type="button" class="text-xs text-cyan-200" @click="clearTicketFilters">{{ t('common.clearFilters') }}</button></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="item in filteredTickets" :key="item.id">
                <td class="px-4 py-3">
                  {{ formatTicketDate(item.submit_time) }}
                </td>
                <td class="px-4 py-3 font-medium text-white">
                  {{ item.customer_company || item.partner_name || "-" }}
                </td>
                <td class="px-4 py-3 font-medium text-white">
                  {{ item.project_name || "-" }}
                </td>
                <td class="px-4 py-3">{{ item.product_model }}</td>
                <td class="px-4 py-3">{{ item.suspected_component || '-' }}</td>
                <td class="px-4 py-3">{{ item.serial_number || "-" }}</td>
                <td class="px-4 py-3">{{ item.ticket_type }}</td>
                <td class="max-w-sm px-4 py-3">{{ item.description }}</td>
                <td class="px-4 py-3">{{ item.status }}</td>
                <td class="px-4 py-3">{{ item.staff_reply || "-" }}</td>
                <td class="px-4 py-3">
                  {{ formatTicketDate(item.resolved_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else-if="activeView === 'account-management'" class="flex-1">
        <div class="mb-5 flex items-end justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.24em] text-cyan-200">
              Tenant Administration
            </p>
            <h2 class="mt-2 text-2xl font-semibold text-white">
              {{ t("portal.account") }}
            </h2>
          </div>
          <button
            type="button"
            class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950"
            @click="accountFormOpen = !accountFormOpen"
          >
            {{ t("portal.addAccount") }}
          </button>
        </div>
        <div
          v-if="accountFormOpen"
          class="mb-5 grid gap-3 rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-5 md:grid-cols-3"
        >
          <input
            v-model="accountDraft.username"
            :disabled="Boolean(accountEditingId)"
            :placeholder="t('portal.username')"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white disabled:opacity-50"
          /><input
            v-model="accountDraft.password"
            :placeholder="t('portal.password')"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
          /><input
            v-model="accountDraft.customer_company"
            :placeholder="t('portal.customer')"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white md:col-span-2"
          /><input
            v-model="accountDraft.country"
            placeholder="所属国家 (Country)"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"
          />
          <p
            class="rounded-xl border border-white/10 bg-slate-950/50 px-3 py-3 text-sm text-slate-300 md:col-span-3"
          >
            {{ t("portal.automaticHint") }}
          </p>
          <button
            type="button"
            class="rounded-xl bg-cyan-400 px-3 py-2 font-semibold text-slate-950 md:col-span-3"
            @click="createCustomerAccount"
          >
            {{ accountEditingId ? t("common.save") : t("portal.saveAccount") }}
          </button>
        </div>
        <div
          class="scroll-thin overflow-x-auto rounded-3xl border border-white/10 bg-white/5"
        >
          <table class="min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400">
              <tr>
                <th class="px-4 py-3">{{ t("portal.username") }}</th>
                <th class="px-4 py-3">{{ t("portal.customer") }}</th>
                <th class="px-4 py-3">国家 (Country)</th>
                <th class="px-4 py-3">{{ t("portal.projectAccess") }}</th>
                <th class="px-4 py-3">{{ t("portal.ticketStatus") }}</th>
                <th class="px-4 py-3">{{ t("common.actions") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="user in users" :key="user.id">
                <td class="px-4 py-3 font-medium text-white">
                  {{ user.username }}
                </td>
                <td class="px-4 py-3">
                  {{ user.customer_company || user.customer_name || "-" }}
                </td>
                <td class="px-4 py-3">{{ user.country || "-" }}</td>
                <td class="px-4 py-3">
                  <details>
                    <summary class="cursor-pointer text-cyan-200">
                      {{ user.customer_company || user.customer_name }} ({{
                        user.automatic_project_count || 0
                      }})
                    </summary>
                    <p class="mt-2 max-w-md text-xs leading-5 text-slate-400">
                      {{
                        (user.automatic_projects || []).join("、") ||
                        t("portal.noMatches")
                      }}
                    </p>
                  </details>
                </td>
                <td class="px-4 py-3">
                  {{ user.is_active ? "启用" : "停用" }}
                </td>
                <td class="px-4 py-3">
                  <button
                    type="button"
                    class="mr-2 text-cyan-200"
                    @click="editCustomerAccount(user)"
                  >
                    {{ t("common.edit") }}</button
                  ><button
                    type="button"
                    class="text-rose-200"
                    @click="removeCustomerAccount(user.id)"
                  >
                    {{ t("common.delete") }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <VpnDiagnosticView
        v-else-if="activeView === 'vpn-diagnostics'"
        :is-super-admin="isSuperAdmin"
        :locale="locale"
      />

      <section v-else-if="activeView === 'other-settings'" class="flex-1">
        <div class="mb-5 flex gap-2 border-b border-white/10 pb-3">
          <button type="button" class="rounded-lg px-4 py-2 text-sm font-semibold" :class="settingsTab === 'fault-components' ? 'bg-cyan-400 text-slate-950' : 'bg-white/5 text-slate-300'" @click="settingsTab = 'fault-components'">
            {{ t("settings.faultTab") }}
          </button>
          <button type="button" class="rounded-lg px-4 py-2 text-sm font-semibold" :class="settingsTab === 'logistics-statuses' ? 'bg-cyan-400 text-slate-950' : 'bg-white/5 text-slate-300'" @click="settingsTab = 'logistics-statuses'">
            {{ t("settings.logisticsTab") }}
          </button>
          <button v-if="isSuperAdmin" type="button" class="rounded-lg px-4 py-2 text-sm font-semibold" :class="settingsTab === 'empowerment-skills' ? 'bg-cyan-400 text-slate-950' : 'bg-white/5 text-slate-300'" @click="settingsTab = 'empowerment-skills'">
            {{ t("settings.empowermentSkillsTab") }}
          </button>
        </div>

        <div v-if="settingsTab === 'fault-components'" class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">
              Fault Component Dictionary
            </p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">
              {{ t("settings.title") }}
            </h2>
            <p class="mt-2 text-sm text-slate-400">{{ t("settings.subtitle") }}</p>
          </div>
          <button
            v-if="isSuperAdmin"
            type="button"
            class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950"
            @click="openFaultComponentEditor()"
          >
            {{ t("settings.add") }}
          </button>
        </div>

        <div v-else-if="settingsTab === 'logistics-statuses'" class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Logistics Status Dictionary</p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">{{ t("settings.logisticsTitle") }}</h2>
            <p class="mt-2 text-sm text-slate-400">{{ t("settings.logisticsSubtitle") }}</p>
          </div>
          <button v-if="isSuperAdmin" type="button" class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" @click="openLogisticsStatusEditor()">
            {{ t("settings.logisticsAdd") }}
          </button>
        </div>

        <div v-else class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Empowerment After-Sales Skills</p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">{{ t("settings.empowermentSkillsTitle") }}</h2>
            <p class="mt-2 text-sm text-slate-400">{{ t("settings.empowermentSkillsSubtitle") }}</p>
          </div>
          <button type="button" class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" @click="openEmpowermentSkillEditor()">{{ t("settings.empowermentSkillAdd") }}</button>
        </div>

        <div v-if="settingsTab === 'fault-components'" class="mb-4 rounded-xl border border-white/10 bg-white/5 p-4">
          <input
            v-model="faultComponentSearch"
            type="search"
            :placeholder="t('settings.search')"
            class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-4 py-2.5 text-sm text-white outline-none sm:max-w-md"
          />
        </div>

        <div v-if="settingsTab === 'fault-components'" class="scroll-thin overflow-x-auto rounded-xl border border-white/10 bg-white/5">
          <table class="data-table min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400">
              <tr>
                <th class="px-4 py-3">{{ t("settings.id") }}</th>
                <th class="px-4 py-3">{{ t("settings.name") }}</th>
                <th class="px-4 py-3">{{ t("settings.nameEn") }}</th>
                <th class="px-4 py-3">{{ t("settings.sortOrder") }}</th>
                <th class="px-4 py-3">{{ t("settings.status") }}</th>
                <th v-if="isSuperAdmin" class="px-4 py-3">{{ t("common.actions") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="component in filteredFaultComponents" :key="component.id">
                <td class="px-4 py-3">{{ component.id }}</td>
                <td class="px-4 py-3 font-medium text-white">{{ component.name }}</td>
                <td class="px-4 py-3">{{ component.name_en || "-" }}</td>
                <td class="px-4 py-3">{{ component.sort_order }}</td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                    :class="component.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'"
                  >
                    {{ t(component.is_active ? "settings.active" : "settings.inactive") }}
                  </span>
                </td>
                <td v-if="isSuperAdmin" class="px-4 py-3 whitespace-nowrap">
                  <button type="button" class="mr-3 text-cyan-200" @click="openFaultComponentEditor(component)">
                    {{ t("common.edit") }}
                  </button>
                  <button
                    type="button"
                    class="text-rose-200"
                    @click="openDeleteDialog('fault-component', String(component.id), component.name, t('settings.deleteHint'))"
                  >
                    {{ t("common.delete") }}
                  </button>
                </td>
              </tr>
              <tr v-if="filteredFaultComponents.length === 0">
                <td :colspan="isSuperAdmin ? 6 : 5" class="px-4 py-8 text-center text-slate-400">
                  {{ t("common.noData") }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="settingsTab === 'logistics-statuses'" class="scroll-thin overflow-x-auto rounded-xl border border-white/10 bg-white/5">
          <table class="data-table min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400">
              <tr>
                <th class="px-4 py-3">{{ t("settings.stepOrder") }}</th>
                <th class="px-4 py-3">{{ t("settings.statusName") }}</th>
                <th class="px-4 py-3">{{ t("settings.statusNameEn") }}</th>
                <th class="px-4 py-3">{{ t("settings.active") }}</th>
                <th v-if="isSuperAdmin" class="px-4 py-3">{{ t("common.actions") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="status in logisticsStatuses" :key="status.id">
                <td class="px-4 py-3">{{ status.step_order }}</td>
                <td class="px-4 py-3 font-medium text-white">{{ status.name }}</td>
                <td class="px-4 py-3">{{ status.name_en || "-" }}</td>
                <td class="px-4 py-3">{{ t(status.is_active ? "settings.active" : "settings.inactive") }}</td>
                <td v-if="isSuperAdmin" class="px-4 py-3 whitespace-nowrap">
                  <button type="button" class="mr-3 text-cyan-200" @click="openLogisticsStatusEditor(status)">{{ t("common.edit") }}</button>
                  <button type="button" class="text-rose-200" @click="openDeleteDialog('logistics-status', String(status.id), status.name, t('settings.logisticsDeleteHint'))">{{ t("common.delete") }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="scroll-thin overflow-x-auto rounded-xl border border-white/10 bg-white/5">
          <table class="data-table min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400"><tr><th class="px-4 py-3">ID</th><th class="px-4 py-3">{{ t("settings.skillName") }}</th><th class="px-4 py-3">{{ t("settings.skillNameEn") }}</th><th class="px-4 py-3">{{ t("settings.sortOrder") }}</th><th class="px-4 py-3">{{ t("settings.status") }}</th><th class="px-4 py-3">{{ t("common.actions") }}</th></tr></thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="skill in empowermentSkills" :key="skill.id">
                <td class="px-4 py-3">{{ skill.id }}</td><td class="px-4 py-3 font-medium text-white">{{ skill.name }}</td><td class="px-4 py-3">{{ skill.name_en || "-" }}</td><td class="px-4 py-3">{{ skill.sort_order }}</td>
                <td class="px-4 py-3"><span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="skill.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'">{{ t(skill.is_active ? "settings.active" : "settings.inactive") }}</span></td>
                <td class="whitespace-nowrap px-4 py-3"><button type="button" class="mr-3 text-cyan-200" @click="openEmpowermentSkillEditor(skill)">{{ t("common.edit") }}</button><button type="button" class="text-rose-200" @click="openDeleteDialog('empowerment-skill', String(skill.id), skill.name, t('settings.empowermentSkillDeleteHint'))">{{ t("common.delete") }}</button></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="faultComponentFormOpen"
          class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm"
          @click.self="faultComponentFormOpen = false"
        >
          <div class="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">Configuration</p>
                <h3 class="mt-2 text-xl font-semibold text-white">{{ t("settings.editorTitle") }}</h3>
              </div>
              <button type="button" class="rounded-lg border border-white/10 px-3 py-2 text-sm text-white" @click="faultComponentFormOpen = false">
                {{ t("common.close") }}
              </button>
            </div>
            <div class="mt-5 grid gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.name") }} *</span>
                <input v-model="faultComponentDraft.name" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" />
              </label>
              <label class="block">
                <span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.nameEn") }}</span>
                <input v-model="faultComponentDraft.name_en" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" />
              </label>
              <label class="block">
                <span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.sortOrder") }}</span>
                <input v-model.number="faultComponentDraft.sort_order" type="number" min="0" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" />
              </label>
              <label class="flex items-center gap-3 self-end rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white">
                <input v-model="faultComponentDraft.is_active" type="checkbox" class="h-4 w-4 accent-cyan-500" />
                {{ t("settings.active") }}
              </label>
            </div>
            <div class="mt-6 flex justify-end gap-3">
              <button type="button" class="rounded-lg border border-white/10 px-4 py-2 text-sm text-white" @click="faultComponentFormOpen = false">
                {{ t("common.cancel") }}
              </button>
              <button type="button" class="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" @click="saveFaultComponent">
                {{ t("common.save") }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="logisticsStatusFormOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm" @click.self="logisticsStatusFormOpen = false">
          <div class="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl">
            <div class="flex items-start justify-between gap-3">
              <h3 class="text-xl font-semibold text-white">{{ t("settings.logisticsEditorTitle") }}</h3>
              <button type="button" class="rounded-lg border border-white/10 px-3 py-2 text-sm text-white" @click="logisticsStatusFormOpen = false">{{ t("common.close") }}</button>
            </div>
            <div class="mt-5 grid gap-4 sm:grid-cols-2">
              <label class="block"><span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.statusName") }} *</span><input v-model="logisticsStatusDraft.name" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" /></label>
              <label class="block"><span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.statusNameEn") }}</span><input v-model="logisticsStatusDraft.name_en" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" /></label>
              <label class="block"><span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.stepOrder") }}</span><input v-model.number="logisticsStatusDraft.step_order" type="number" min="0" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" /></label>
              <label class="flex items-center gap-3 self-end rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white"><input v-model="logisticsStatusDraft.is_active" type="checkbox" class="h-4 w-4 accent-cyan-500" />{{ t("settings.active") }}</label>
            </div>
            <div class="mt-6 flex justify-end gap-3">
              <button type="button" class="rounded-lg border border-white/10 px-4 py-2 text-sm text-white" @click="logisticsStatusFormOpen = false">{{ t("common.cancel") }}</button>
              <button type="button" class="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" @click="saveLogisticsStatus">{{ t("common.save") }}</button>
            </div>
          </div>
        </div>

        <div v-if="empowermentSkillFormOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm" @click.self="empowermentSkillFormOpen = false">
          <div class="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl">
            <div class="flex items-start justify-between gap-3"><h3 class="text-xl font-semibold text-white">{{ t("settings.empowermentSkillEditorTitle") }}</h3><button type="button" class="rounded-lg border border-white/10 px-3 py-2 text-sm text-white" @click="empowermentSkillFormOpen = false">{{ t("common.close") }}</button></div>
            <div class="mt-5 grid gap-4 sm:grid-cols-2">
              <label class="block"><span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.skillName") }} *</span><input v-model="empowermentSkillDraft.name" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" /></label>
              <label class="block"><span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.skillNameEn") }}</span><input v-model="empowermentSkillDraft.name_en" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" /></label>
              <label class="block"><span class="mb-1.5 block text-xs font-semibold text-slate-300">{{ t("settings.sortOrder") }}</span><input v-model.number="empowermentSkillDraft.sort_order" type="number" min="0" class="w-full rounded-lg border border-white/10 bg-slate-950/70 px-3 py-2.5 text-white" /></label>
              <label class="flex items-center gap-3 self-end rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white"><input v-model="empowermentSkillDraft.is_active" type="checkbox" class="h-4 w-4 accent-cyan-500" />{{ t("settings.active") }}</label>
            </div>
            <div class="mt-6 flex justify-end gap-3"><button type="button" class="rounded-lg border border-white/10 px-4 py-2 text-sm text-white" @click="empowermentSkillFormOpen = false">{{ t("common.cancel") }}</button><button type="button" class="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" @click="saveEmpowermentSkill">{{ t("common.save") }}</button></div>
          </div>
        </div>
      </section>

      <section v-else-if="activeView === 'logistics'" class="flex-1">
        <div
          class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              Logistics Tracking
            </p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">
              {{ t("views.logistics") }}
            </h2>
          </div>
          <button
            v-if="isInternalMode"
            type="button"
            class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
            @click="openLogisticsEditor()"
          >
            {{ t("logistics.add") }}
          </button>
        </div>

        <div class="scroll-thin overflow-x-auto rounded-3xl border border-white/10 bg-white/5 p-5">
          <div class="flex min-w-max items-center gap-2">
            <template v-for="(step, index) in activeLogisticsStatuses" :key="step.id">
              <div class="flex flex-col items-center gap-2">
                <span
                  class="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold"
                  :class="index <= 0 ? 'bg-cyan-400 text-slate-950' : 'bg-slate-800 text-slate-400'"
                  >{{ index + 1 }}</span
                >
                <span class="w-24 text-center text-[11px] text-slate-300">{{ logisticsStatusLabel(step) }}</span>
              </div>
              <div v-if="index < activeLogisticsStatuses.length - 1" class="h-0.5 w-10 flex-1 bg-slate-700"></div>
            </template>
          </div>
        </div>

        <div v-if="logisticsFormOpen" class="mt-5 rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-5">
          <div class="grid gap-3 md:grid-cols-3">
            <label class="block"><span class="mb-1 block text-xs text-slate-400">{{ t("logistics.createdDate") }}</span><input v-model="logisticsDraft.created_date" type="date" class="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" /></label>
            <label class="block">
              <span class="mb-1 block text-xs text-slate-400">{{ t("logistics.stage") }} *</span>
              <select v-model="logisticsDraft.stage" required class="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white">
                <option value="delivery">{{ t("logistics.delivery") }}</option>
                <option value="after_sales">{{ t("logistics.afterSales") }}</option>
              </select>
            </label>
            <select v-model="logisticsDraft.customer_company" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" @change="handleLogisticsCustomerChange">
              <option value="" disabled>客户/代理商名称</option>
              <option v-for="company in partnerOptions" :key="company" :value="company">{{ company }}</option>
            </select>
            <select v-model="logisticsDraft.related_project" :disabled="!logisticsDraft.customer_company" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white disabled:cursor-not-allowed disabled:opacity-50">
              <option value="" disabled>关联项目</option>
              <option v-for="project in logisticsProjectOptions" :key="project.project_name" :value="project.project_name">{{ project.project_name }}</option>
            </select>
            <input v-model="logisticsDraft.destination_country" placeholder="目的国" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" />
            <select v-model="logisticsDraft.equipment_model" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white">
              <option value="" disabled>设备型号</option>
              <option v-for="model in logisticsEquipmentModels" :key="model" :value="model">{{ model }}</option>
            </select>
            <select v-model="logisticsDraft.specific_module" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white">
              <option value="" disabled>{{ t("logistics.module") }}</option>
              <option v-for="component in faultyComponentOptions" :key="component" :value="component">{{ component }}</option>
            </select>
            <label class="block"><span class="mb-1 block text-xs text-slate-400">{{ t("logistics.quantity") }}</span><input v-model.number="logisticsDraft.equipment_qty" type="number" min="0" class="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" /></label>
            <select v-model="logisticsDraft.status" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white">
              <option v-for="option in activeLogisticsStatuses" :key="option.id" :value="option.name">{{ logisticsStatusLabel(option) }}</option>
            </select>
            <label class="block"><span class="mb-1 block text-xs text-slate-400">{{ t("logistics.shipDate") }}</span><input v-model="logisticsDraft.eta" type="date" class="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" /></label>
            <input v-model="logisticsDraft.tracking_url" placeholder="查询链接 URL" class="md:col-span-2 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white" />
            <textarea v-model="logisticsDraft.remarks" rows="4" placeholder="备注 / Remarks" class="md:col-span-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"></textarea>
          </div>
          <div class="mt-3 flex justify-end gap-2">
            <button type="button" class="rounded-xl border border-white/10 px-4 py-2 text-white" @click="logisticsFormOpen = false">取消</button>
            <button type="button" class="rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950" @click="submitLogisticsShipment">保存</button>
          </div>
        </div>

        <div class="mt-5 scroll-thin overflow-x-auto rounded-3xl border border-white/10 bg-white/5">
          <table class="min-w-full text-left text-sm">
            <thead class="bg-slate-950/50 text-slate-400">
              <tr>
                <th class="px-4 py-3">{{ t("logistics.createdDateShort") }}</th>
                <th class="px-4 py-3">{{ t("logistics.stageShort") }}</th>
                <th class="px-4 py-3">{{ t("logistics.customer") }}</th>
                <th class="px-4 py-3">{{ t("logistics.project") }}</th>
                <th class="px-4 py-3">{{ t("logistics.destination") }}</th>
                <th class="px-4 py-3">{{ t("logistics.equipment") }}</th>
                <th class="px-4 py-3">{{ t("logistics.moduleShort") }}</th>
                <th class="px-4 py-3 text-center">{{ t("logistics.quantityShort") }}</th>
                <th class="px-4 py-3">{{ t("logistics.status") }}</th>
                <th class="px-4 py-3">{{ t("logistics.shipDateShort") }}</th>
                <th class="px-4 py-3">{{ t("logistics.remarks") }}</th>
                <th v-if="isInternalMode" class="px-4 py-3">{{ t("common.actions") }}</th>
              </tr>
              <tr class="ticket-filter-row">
                <th></th>
                <th></th>
                <th></th>
                <th></th>
                <th><input v-model="logisticsFilters.destination" placeholder="搜索目的国" /></th>
                <th></th>
                <th></th>
                <th></th>
                <th><select v-model="logisticsFilters.status"><option value="">{{ t('common.all') }}</option><option v-for="option in activeLogisticsStatuses" :key="option.id" :value="option.name">{{ logisticsStatusLabel(option) }}</option></select></th>
                <th></th>
                <th></th>
                <th v-if="isInternalMode"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10 text-slate-200">
              <tr v-for="item in logisticsShipments" :key="item.id">
                <td class="px-4 py-3 font-medium text-white">{{ item.created_date || "-" }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="item.stage === 'after_sales' ? 'bg-amber-50 text-amber-700' : 'bg-sky-50 text-sky-700'">
                    {{ item.stage === "after_sales" ? t("logistics.afterSalesShort") : t("logistics.deliveryShort") }}
                  </span>
                </td>
                <td class="px-4 py-3">{{ item.customer_company || "-" }}</td>
                <td class="px-4 py-3">{{ item.related_project || "-" }}</td>
                <td class="px-4 py-3">{{ item.destination_country || "-" }}</td>
                <td class="px-4 py-3">{{ logisticsEquipmentLabel(item.equipment_model) }}</td>
                <td class="px-4 py-3">{{ item.specific_module || "-" }}</td>
                <td class="px-4 py-3 text-center tabular-nums">{{ item.equipment_qty }}</td>
                <td class="px-4 py-3"><span class="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 text-xs text-cyan-100">{{ item.status }}</span></td>
                <td class="px-4 py-3">{{ item.eta || "-" }}</td>
                <td class="max-w-xs whitespace-pre-wrap px-4 py-3 text-xs text-slate-300">{{ item.remarks || "-" }}</td>
                <td v-if="isInternalMode" class="px-4 py-3">
                  <button type="button" class="mr-2 text-cyan-200" @click="editLogisticsShipment(item)">{{ t("common.edit") }}</button>
                  <button type="button" class="text-rose-200" @click="openDeleteDialog('logistics', String(item.id), item.created_date, t('common.deleteConfirm'))">{{ t("common.delete") }}</button>
                </td>
              </tr>
              <tr v-if="!logisticsShipments.length">
                <td :colspan="isInternalMode ? 12 : 11" class="px-4 py-6 text-center text-slate-400">{{ t("common.noData") }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else-if="activeView === 'empowerment'" class="flex-1">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Empowerment Plan</p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">{{ t("views.empowerment") }}</h2>
          </div>
          <button
            v-if="isInternalMode"
            type="button"
            class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
            @click="openEmpowermentEditor()"
          >
            {{ t("empowerment.add") }}
          </button>
        </div>

        <div v-if="empowermentFormOpen" class="mb-5 rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-5">
          <div class="grid gap-3 md:grid-cols-3">
            <input v-model="empowermentDraft.partner_name" :disabled="Boolean(empowermentEditingId)" :placeholder="t('empowerment.partnerName')" class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white disabled:opacity-50" />
            <div class="md:col-span-3 mt-2 text-xs font-semibold uppercase text-emerald-300">{{ t("empowerment.deliveryMatrix") }}</div>
            <label v-for="field in empowermentDeliveryFields" :key="field.key" class="block">
              <span class="mb-1 block text-xs text-slate-400">{{ t(field.labelKey) }} ({{ empowermentDraft[field.key] }}%)</span>
              <input v-model.number="empowermentDraft[field.key]" type="range" min="0" max="100" class="w-full" />
            </label>
            <div class="md:col-span-3 mt-2 text-xs font-semibold uppercase text-cyan-300">{{ t("empowerment.afterSalesMatrix") }}</div>
            <label v-for="skill in activeEmpowermentSkills" :key="skill.id" class="block">
              <span class="mb-1 block text-xs text-slate-400">{{ empowermentSkillLabel(skill) }} ({{ empowermentDraft.aftersales_scores?.[skill.name] || 0 }}%)</span>
              <input v-model.number="empowermentDraft.aftersales_scores[skill.name]" type="range" min="0" max="100" class="w-full" />
            </label>
            <textarea v-model="empowermentDraft.remarks" :placeholder="t('empowerment.remarks')" class="md:col-span-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-white"></textarea>
          </div>
          <div class="mt-3 flex justify-end gap-2">
            <button type="button" class="rounded-xl border border-white/10 px-4 py-2 text-white" @click="empowermentFormOpen = false">取消</button>
            <button type="button" class="rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950" @click="submitEmpowermentRecord">保存</button>
          </div>
        </div>

        <div class="scroll-thin overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table class="min-w-max border-separate border-spacing-0 text-left text-sm">
            <thead class="bg-slate-50 text-slate-700">
              <tr class="text-xs font-semibold uppercase tracking-wider text-slate-500">
                <th rowspan="2" class="sticky left-0 z-20 min-w-48 border-b border-r border-slate-200 bg-slate-50 px-4 py-3 shadow-[4px_0_8px_-2px_rgba(0,0,0,0.05)]">{{ t("empowerment.partnerName") }}</th>
                <th :colspan="empowermentDeliveryFields.length" class="border-b border-r border-slate-200 px-4 py-3 text-center">{{ t("empowerment.deliveryMatrix") }}</th>
                <th :colspan="Math.max(activeEmpowermentSkills.length, 1)" class="border-b border-r border-slate-200 px-4 py-3 text-center">{{ t("empowerment.afterSalesMatrix") }}</th>
                <th rowspan="2" class="min-w-52 border-b border-slate-200 px-4 py-3">{{ t("empowerment.remarks") }}</th>
                <th v-if="isInternalMode" rowspan="2" class="sticky right-0 z-20 min-w-28 border-b border-l border-slate-200 bg-slate-50 px-4 py-3 text-center shadow-[-4px_0_8px_-2px_rgba(0,0,0,0.05)]">{{ t("common.actions") }}</th>
              </tr>
              <tr class="text-xs font-medium text-slate-700">
                <th v-for="field in empowermentDeliveryFields" :key="field.key" class="min-w-36 border-b border-slate-200 px-3 py-3">{{ t(field.labelKey) }}</th>
                <th v-for="skill in activeEmpowermentSkills" :key="skill.id" class="min-w-36 border-b border-slate-200 px-3 py-3">{{ empowermentSkillLabel(skill) }}</th>
                <th v-if="!activeEmpowermentSkills.length" class="min-w-36 border-b border-slate-200 px-3 py-3">-</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white text-slate-700">
              <tr v-for="item in empowermentRecords" :key="item.id" class="group transition-colors hover:bg-slate-50/80">
                <td class="sticky left-0 z-10 border-r border-slate-200 bg-white px-4 py-3 font-semibold text-slate-900 shadow-[4px_0_8px_-2px_rgba(0,0,0,0.05)] transition-colors group-hover:bg-slate-50">{{ item.partner_name }}</td>
                <td v-for="field in empowermentDeliveryFields" :key="field.key" class="px-3 py-3">
                  <div class="flex w-28 items-center gap-2"><div class="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100"><div class="h-full rounded-full transition-all duration-300" :class="getProgressColor(item[field.key])" :style="{ width: `${item[field.key] || 0}%` }"></div></div><span class="w-8 text-right font-mono text-xs font-medium text-slate-600">{{ item[field.key] || 0 }}%</span></div>
                </td>
                <td v-for="skill in activeEmpowermentSkills" :key="skill.id" class="px-3 py-3">
                  <div class="flex w-28 items-center gap-2"><div class="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100"><div class="h-full rounded-full transition-all duration-300" :class="getProgressColor(item.aftersales_scores?.[skill.name])" :style="{ width: `${item.aftersales_scores?.[skill.name] || 0}%` }"></div></div><span class="w-8 text-right font-mono text-xs font-medium text-slate-600">{{ item.aftersales_scores?.[skill.name] || 0 }}%</span></div>
                </td>
                <td v-if="!activeEmpowermentSkills.length" class="px-4 py-3 text-center text-slate-400">-</td>
                <td class="max-w-xs px-4 py-3 text-xs leading-5 text-slate-600">{{ item.remarks || "-" }}</td>
                <td v-if="isInternalMode" class="sticky right-0 z-10 border-l border-slate-200 bg-white px-4 py-3 text-center shadow-[-4px_0_8px_-2px_rgba(0,0,0,0.05)] transition-colors group-hover:bg-slate-50">
                  <button type="button" class="mr-3 font-medium text-sky-700 hover:text-sky-900" @click="editEmpowermentRecord(item)">{{ t("common.edit") }}</button>
                  <button type="button" class="font-medium text-rose-600 hover:text-rose-800" @click="openDeleteDialog('empowerment', String(item.id), item.partner_name, t('common.deleteConfirm'))">{{ t("common.delete") }}</button>
                </td>
              </tr>
              <tr v-if="!empowermentRecords.length">
                <td :colspan="empowermentDeliveryFields.length + Math.max(activeEmpowermentSkills.length, 1) + (isInternalMode ? 3 : 2)" class="px-4 py-6 text-center text-slate-400">{{ t("common.noData") }}</td>
              </tr>
            </tbody>
            <tfoot class="border-t border-slate-200 bg-slate-50">
              <tr>
                <td :colspan="empowermentDeliveryFields.length + Math.max(activeEmpowermentSkills.length, 1) + (isInternalMode ? 3 : 2)" class="px-4 py-3 text-xs font-semibold text-slate-400">Count: {{ empowermentRecords.length }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </section>

      <section v-else-if="activeView === 'warehouse'" class="flex-1">
        <div
          class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
            >
              Warehouse & Inventory
            </p>
            <div
              class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <h2 class="text-2xl font-semibold text-white sm:text-3xl">
                  {{ t("inventory.section") }}
                </h2>
                <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
                  {{ t("inventory.subtitle") }}
                </p>
              </div>
              <button
                v-if="isInternalMode"
                type="button"
                class="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/15"
                @click="openInventoryEditor()"
              >
                {{ t("inventory.addItem") }}
              </button>
            </div>
          </div>
          <div
            class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300"
          >
            {{ t("inventory.count") }}：<span
              class="font-semibold text-white"
              >{{ filteredInventoryItems.length }}</span
            >
          </div>
        </div>

        <div
          class="mb-4 grid gap-3 rounded-2xl border border-white/10 bg-white/5 p-3 sm:grid-cols-3"
        >
          <input
            v-model="inventorySearchKeyword"
            placeholder="搜索备件名称 / 物料编码 SKU"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-sm text-white"
          /><select
            v-model="inventoryModelFilter"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-sm text-white"
          >
            <option value="">适用机型 (全部)</option>
            <option>418</option>
            <option>250</option>
            <option>100C</option></select
          ><select
            v-model="selectedWarehouse"
            class="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-sm text-white"
          >
            <option v-for="warehouse in warehouseOptions" :key="warehouse.key" :value="warehouse.key">{{ warehouse.label }}</option>
          </select>
        </div>

        <div
          v-if="inventoryLoading"
          class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
        >
          <div
            v-for="index in 6"
            :key="index"
            class="h-64 animate-pulse rounded-3xl border border-white/10 bg-white/5"
          ></div>
        </div>

        <div
          v-else-if="inventoryError"
          class="rounded-3xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100"
        >
          {{ inventoryError }}
        </div>

        <div
          v-else
          class="overflow-hidden rounded-3xl border border-white/10 bg-white/5"
        >
          <div class="scroll-thin overflow-x-auto">
            <table
              class="data-table inventory-data-table min-w-full divide-y divide-white/10 text-left text-sm"
            >
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.itemNo") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.descriptionZh") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.specification") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.totalQuantity") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.damagedQuantity") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.availableQuantity") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.photoPaths") }}
                  </th>
                  <th class="px-5 py-4 font-medium">
                    {{ t("inventory.remarks") }}
                  </th>
                  <th v-if="isInternalMode" class="px-5 py-4 font-medium">
                    {{ t("common.actions") }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/10 text-slate-200">
                <tr
                  v-for="item in filteredInventoryItems"
                  :key="item.item_no"
                  class="bg-white/[0.02] hover:bg-white/[0.04]"
                >
                  <td
                    class="px-5 py-4 whitespace-nowrap font-semibold text-white"
                  >
                    {{ item.item_no }}
                  </td>
                  <td class="px-5 py-4">{{ item.description_zh }}</td>
                  <td class="px-5 py-4">{{ item.specification }}</td>
                  <td class="px-5 py-4">{{ item.total_quantity }}</td>
                  <td class="px-5 py-4">{{ item.damaged_quantity }}</td>
                  <td class="px-5 py-4 font-semibold text-emerald-200">
                    {{ item.available_quantity }}
                  </td>
                  <td class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button
                        v-for="photo in item.photo_paths"
                        :key="photo"
                        type="button"
                        class="overflow-hidden rounded-xl border border-white/10 bg-slate-950/80"
                        @click="openImagePreview(photo)"
                      >
                        <img
                          :src="resolvePhotoUrl(photo)"
                          :alt="item.item_no"
                          class="h-12 w-12 object-cover"
                        />
                      </button>
                      <span
                        v-if="(item.photo_paths || []).length === 0"
                        class="text-xs text-slate-400"
                        >{{ t("common.noData") }}</span
                      >
                    </div>
                  </td>
                  <td class="px-5 py-4 text-slate-300">
                    {{ item.remarks || "-" }}
                  </td>
                  <td v-if="isInternalMode" class="px-5 py-4">
                    <div class="flex flex-wrap gap-2">
                      <button
                        type="button"
                        class="table-action-btn rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
                        @click="openInventoryEditor(item)"
                      >
                        {{ t("common.edit") }}
                      </button>
                      <button
                        type="button"
                        class="table-action-btn table-action-danger rounded-xl border border-rose-400/20 bg-rose-500/10 px-3 py-2 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/15"
                        @click="
                          openDeleteDialog(
                            'inventory',
                            item.item_no,
                            item.item_no,
                            t('common.deleteConfirm'),
                          )
                        "
                      >
                        {{ t("common.delete") }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="filteredInventoryItems.length === 0">
                  <td
                    :colspan="isInternalMode ? 9 : 8"
                    class="px-4 py-10 text-center text-slate-400"
                  >
                    {{ t("common.noData") }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div
        v-if="crudModal.open"
        class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/80 px-4 py-8 backdrop-blur-sm"
      >
        <div
          class="w-full max-w-2xl rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200"
              >
                CRUD
              </p>
              <h3 class="mt-2 text-2xl font-semibold text-white">
                {{
                  crudModal.kind === "fault"
                    ? t("fault.adminCreate")
                    : crudModal.kind === "grid"
                      ? t("grid.createTitle")
                      : crudModal.kind === "ci"
                        ? t("ci.createTitle")
                        : crudModal.kind === "technical-doc"
                          ? t("materials.createTitle")
                          : t("inventory.createTitle")
                }}
              </h3>
            </div>
            <button
              type="button"
              class="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
              @click="closeCrudModal"
            >
              {{ t("common.close") }}
            </button>
          </div>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <template v-if="crudModal.kind === 'fault'">
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >模块</span
                >
                <input
                  v-model="crudDraft.module"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >故障码</span
                >
                <input
                  v-model="crudDraft.fault_code"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >故障名称</span
                >
                <input
                  v-model="crudDraft.fault_name"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >故障等级</span
                >
                <input
                  v-model="crudDraft.fault_level"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >停机</span
                >
                <input
                  v-model="crudDraft.is_stop"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >恢复机制</span
                >
                <input
                  v-model="crudDraft.recovery"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >触发逻辑</span
                >
                <input
                  v-model="crudDraft.trigger_logic"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >检测条件</span
                >
                <textarea
                  v-model="crudDraft.detection_condition"
                  rows="3"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                ></textarea>
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >可能原因</span
                >
                <textarea
                  v-model="crudDraft.possible_cause"
                  rows="4"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                ></textarea>
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >解决措施</span
                >
                <textarea
                  v-model="crudDraft.solution"
                  rows="4"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                ></textarea>
              </label>
            </template>
            <template v-else-if="crudModal.kind === 'grid'">
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >Project Name</span
                >
                <input
                  v-model="crudDraft.project_name"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("portal.customer") }}</span
                >
                <input
                  v-model="crudDraft.customer_company"
                  list="partner-options"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
                <datalist id="partner-options">
                  <option
                    v-for="partner in partnerOptions"
                    :key="partner"
                    :value="partner"
                  />
                </datalist>
              </label>
              <label v-if="crudDraftGridCountry" class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >国家 (Country)</span
                >
                <input
                  :value="crudDraftGridCountry"
                  disabled
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:opacity-60"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("grid.codDate") }}</span
                >
                <input
                  v-model="crudDraft.cod"
                  type="date"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >Capacity (MWh)</span
                >
                <input
                  v-model.number="crudDraft.capacity_mwh"
                  type="number"
                  min="0"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >Software Version</span
                >
                <input
                  v-model="crudDraft.software_version"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >Status</span
                >
                <select
                  v-model="crudDraft.progress_status"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                >
                  <option
                    v-for="status in projectStatuses"
                    :key="status"
                    :value="status"
                  >
                    {{ status }}
                  </option>
                </select>
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("grid.photoUpload") }}</span
                >
                <input
                  ref="photoInputRef"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden"
                  @change="handlePhotoFiles"
                />
                <div class="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
                    @click="openPhotoPicker"
                  >
                    {{ t("grid.chooseImages") }}
                  </button>
                  <span class="text-xs text-slate-400">{{
                    photoUploading ? t("common.loading") : t("grid.photoHint")
                  }}</span>
                </div>
                <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
                  <div
                    v-for="(photo, index) in crudDraft.photo_paths"
                    :key="photo"
                    class="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950/80"
                  >
                    <img
                      :src="resolvePhotoUrl(photo)"
                      :alt="`${crudDraft.project_name} ${index + 1}`"
                      class="h-28 w-full object-cover"
                    />
                    <button
                      type="button"
                      class="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-slate-950/80 text-xs font-bold text-white"
                      @click="removePhotoPath(index)"
                    >
                      ×
                    </button>
                  </div>
                  <div
                    v-if="crudDraft.photo_paths.length === 0"
                    class="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-xs text-slate-400"
                  >
                    {{ t("grid.noPhotos") }}
                  </div>
                </div>
              </label>
            </template>
            <template v-else-if="crudModal.kind === 'ci'">
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >Dealer Name</span
                >
                <input
                  v-model="crudDraft.dealer_name"
                  :disabled="crudModal.mode === 'edit'"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:cursor-not-allowed disabled:opacity-60"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >Region</span
                >
                <input
                  v-model="crudDraft.region"
                  :disabled="crudDraftCiCountryLocked"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:opacity-60"
                />
              </label>
            </template>
            <template v-else-if="crudModal.kind === 'technical-doc'">
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >产品系列</span
                >
                <select
                  v-model="crudDraft.product_series"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                >
                  <option
                    v-for="series in technicalDocProductSeries"
                    :key="series"
                    :value="series"
                  >
                    {{ series }}
                  </option>
                </select>
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >资料分类</span
                >
                <select
                  v-model="crudDraft.category"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                >
                  <option
                    v-for="category in technicalDocCategories"
                    :key="category"
                    :value="category"
                  >
                    {{ category }}
                  </option>
                </select>
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >标题</span
                >
                <input
                  v-model="crudDraft.title"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label
                v-if="crudModal.mode === 'create'"
                class="block md:col-span-2"
              >
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >上传文件</span
                >
                <input
                  ref="technicalDocFileInputRef"
                  type="file"
                  class="hidden"
                  @change="handleTechnicalDocFile"
                />
                <div class="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
                    @click="openTechnicalDocFilePicker"
                  >
                    选择文件
                  </button>
                  <span class="text-xs text-slate-400">{{
                    crudDraft.technical_doc_file
                      ? crudDraft.technical_doc_file.name
                      : "未选择文件"
                  }}</span>
                </div>
              </label>
              <div
                v-else
                class="md:col-span-2 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-xs text-slate-300"
              >
                当前文件：{{ crudDraft.file_url || "-" }}
              </div>
            </template>
            <template v-else>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.itemNo") }}</span
                >
                <input
                  v-model="crudDraft.item_no"
                  :disabled="crudModal.mode === 'edit'"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none disabled:cursor-not-allowed disabled:opacity-60"
                />
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.descriptionZh") }}</span
                >
                <input
                  v-model="crudDraft.description_zh"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.specification") }}</span
                >
                <input
                  v-model="crudDraft.specification"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.totalQuantity") }}</span
                >
                <input
                  v-model.number="crudDraft.total_quantity"
                  type="number"
                  min="0"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                  @input="recomputeAvailableQuantity"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.damagedQuantity") }}</span
                >
                <input
                  v-model.number="crudDraft.damaged_quantity"
                  type="number"
                  min="0"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                  @input="recomputeAvailableQuantity"
                />
              </label>
              <label class="block">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.availableQuantity") }}</span
                >
                <input
                  v-model.number="crudDraft.available_quantity"
                  type="number"
                  min="0"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                />
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.remarks") }}</span
                >
                <textarea
                  v-model="crudDraft.remarks"
                  rows="3"
                  class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none"
                ></textarea>
              </label>
              <label class="block md:col-span-2">
                <span
                  class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >{{ t("inventory.photoPaths") }}</span
                >
                <input
                  ref="photoInputRef"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden"
                  @change="handlePhotoFiles"
                />
                <div class="flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
                    @click="openPhotoPicker"
                  >
                    {{ t("inventory.chooseImages") }}
                  </button>
                  <span class="text-xs text-slate-400">{{
                    photoUploading
                      ? t("common.loading")
                      : t("inventory.photoHint")
                  }}</span>
                </div>
                <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
                  <div
                    v-for="(photo, index) in crudDraft.photo_paths"
                    :key="photo"
                    class="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950/80"
                  >
                    <img
                      :src="resolvePhotoUrl(photo)"
                      :alt="`${crudDraft.item_no} ${index + 1}`"
                      class="h-28 w-full object-cover"
                    />
                    <button
                      type="button"
                      class="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-slate-950/80 text-xs font-bold text-white"
                      @click="removePhotoPath(index)"
                    >
                      ×
                    </button>
                  </div>
                  <div
                    v-if="crudDraft.photo_paths.length === 0"
                    class="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-center text-xs text-slate-400"
                  >
                    {{ t("inventory.noPhotos") }}
                  </div>
                </div>
              </label>
            </template>
          </div>

          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              @click="closeCrudModal"
            >
              {{ t("common.cancel") }}
            </button>
            <button
              type="button"
              class="rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:brightness-110"
              @click="submitCrud"
            >
              {{ t("common.save") }}
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="deleteDialog.open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm"
      >
        <div
          class="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30"
        >
          <p
            class="text-xs font-semibold uppercase tracking-[0.24em] text-rose-200"
          >
            {{ t("common.delete") }}
          </p>
          <h3 class="mt-3 text-2xl font-semibold text-white">
            {{ deleteDialog.title }}
          </h3>
          <p class="mt-2 text-sm leading-6 text-slate-300">
            {{ deleteDialog.message }}
          </p>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              @click="closeDeleteDialog"
            >
              {{ t("common.cancel") }}
            </button>
            <button
              type="button"
              class="rounded-2xl bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110"
              @click="confirmDelete"
            >
              {{ t("common.delete") }}
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="batchDeliveryModal.open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 backdrop-blur-sm"
        @click.self="closeBatchDeliveryModal"
      >
        <div class="w-full max-w-lg rounded-3xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-black/30">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Delivery Batch</p>
              <h3 class="mt-2 text-2xl font-semibold text-white">{{ batchDeliveryModal.mode === 'edit' ? '编辑交付批次' : '新增交付批次' }}</h3>
              <p class="mt-1 text-sm text-slate-400">{{ batchDeliveryModal.dealerName }}</p>
            </div>
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white" @click="closeBatchDeliveryModal">{{ t('common.close') }}</button>
          </div>
          <div class="mt-5 grid gap-4 sm:grid-cols-2">
            <label class="block">
              <span class="mb-2 block text-xs font-semibold text-slate-400">产品类型</span>
              <select v-model="batchDeliveryDraft.product_type" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white">
                <option value="100C">100C</option>
                <option value="250">250</option>
              </select>
            </label>
            <label class="block">
              <span class="mb-2 block text-xs font-semibold text-slate-400">交付台数 *</span>
              <input v-model.number="batchDeliveryDraft.quantity" type="number" min="1" required class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
            </label>
            <label class="block">
              <span class="mb-2 block text-xs font-semibold text-slate-400">交付时间 *</span>
              <input v-model="batchDeliveryDraft.delivery_date" type="date" required class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white" />
            </label>
            <label class="block sm:col-span-2">
              <span class="mb-2 block text-xs font-semibold text-slate-400">设备序列号 SN（选填）</span>
              <textarea v-model="batchDeliveryDraft.serial_numbers" rows="4" placeholder="每行或逗号分隔一个 SN" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white"></textarea>
            </label>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white" @click="closeBatchDeliveryModal">{{ t('common.cancel') }}</button>
            <button type="button" class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950" @click="saveBatchDelivery">{{ t('common.save') }}</button>
          </div>
        </div>
      </div>

      <div
        v-if="imagePreviewUrl"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 px-4 backdrop-blur-sm"
        @click.self="closeImagePreview"
      >
        <div
          class="max-w-5xl overflow-hidden rounded-3xl border border-white/10 bg-slate-900 shadow-2xl shadow-black/30"
        >
          <div
            class="flex items-center justify-between border-b border-white/10 px-5 py-3"
          >
            <p class="text-sm font-semibold text-white">
              {{ t("inventory.photoPreview") }}
            </p>
            <button
              type="button"
              class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10"
              @click="closeImagePreview"
            >
              {{ t("common.close") }}
            </button>
          </div>
          <img
            :src="imagePreviewUrl"
            alt="preview"
            class="max-h-[80vh] w-full object-contain bg-black"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import { messages } from "./locales/messages";
import { portalApi } from "./services/portalApi";
import { usePortalState } from "./composables/usePortalState";

const VpnDiagnosticView = defineAsyncComponent(() =>
  import("./components/VpnDiagnosticView.vue"),
);

const {
  state: portalState,
  setLocale,
  toggleLocale,
  setNotice,
} = usePortalState();

const activeView = ref("overview");

const navGroups = computed(() => [
  {
    key: "overview",
    label: t("nav.overview"),
    items: [
      { key: "overview", label: t("views.overview") },
      { key: "logistics", label: t("views.logistics") },
      ...(!isCustomer.value
        ? [{ key: "warehouse", label: t("views.warehouse") }]
        : []),
      ...(!isCustomer.value
        ? [{ key: "service-logs", label: t("views.serviceLogs") }]
        : []),
    ],
  },
  {
    key: "client-care",
    label: t("nav.clientCare"),
    items: [
      ...(!isCustomer.value
        ? [{ key: "empowerment", label: t("views.empowerment") }]
        : []),
      { key: "customer-tickets", label: t("views.customerTickets") },
      { key: "after-sales", label: t("views.afterSales") },
      { key: "materials-center", label: t("views.materialsCenter") },
    ],
  },
  ...(isSuperAdmin.value || isViewer.value
    ? [
        {
          key: "system",
          label: t("nav.system"),
          items: [
            ...(isSuperAdmin.value
              ? [{ key: "account-management", label: t("views.accounts") }]
              : []),
            { key: "vpn-diagnostics", label: t("views.vpnDiagnostics") },
            { key: "other-settings", label: t("views.otherSettings") },
          ],
        },
      ]
    : []),
]);
const overviewSubTab = ref("grid-scale");

const warehouseOptions = [
  { key: "europe", label: "欧洲仓 / Europe" },
  { key: "north_america", label: "北美仓 / North America" },
];

const technicalDocProductSeries = ["418", "250", "100C"];
const technicalDocCategories = [
  "安装手册",
  "调试手册",
  "运维手册",
  "安装视频",
  "其他手册",
];

const projectStatuses = [
  "待交付",
  "已并网",
  "交付中",
  "清关中",
  "设备上岸",
  "土建施工",
  "调试中",
  "正式并网",
];

const faultKeyword = ref("");
const faultModule = ref("");
const faultModules = ref(["PCS", "BMS", "EMS", "消防", "水机"]);
const faultPage = ref(1);
const faultPageSize = ref(20);
const faultTotal = ref(0);
const faultLoading = ref(false);
const faultError = ref("");
const faultResults = ref([]);
const faultHasSearched = ref(false);

const ledgerLoading = ref(false);
const gridProjects = ref([]);
const ciDeliveries = ref([]);
const ciBatchesByDealer = ref({});
const ciExpandedDealerId = ref(null);
const batchDeliveryModal = reactive({ open: false, mode: "create", dealerId: null, dealerName: "", batchId: null });
const batchDeliveryDraft = reactive({ product_type: "100C", quantity: 1, delivery_date: new Date().toISOString().slice(0, 10), serial_numbers: "" });
const projectDraftStatus = reactive({});

const selectedWarehouse = ref("europe");
const warehouseLoading = ref(false);
const warehouseError = ref("");
const warehouseSummary = ref({
  warehouse_name: "europe",
  inventory: [],
  grouped_inventory: {},
  transactions: [],
});
const warehouseForm = reactive({
  tx_type: "国内到货入库",
  product_model: "100C",
  quantity: 1,
  related_project: "",
  tx_no: "",
});
const inventoryLoading = ref(false);
const inventoryError = ref("");
const inventoryItems = ref([]);
const inventorySearchKeyword = ref("");
const inventoryModelFilter = ref("");
const filteredInventoryItems = computed(() =>
  inventoryItems.value.filter((item) => {
    const keyword = inventorySearchKeyword.value.trim().toLowerCase();
    const matchesKeyword =
      !keyword ||
      (item.item_no || "").toLowerCase().includes(keyword) ||
      (item.description_zh || "").toLowerCase().includes(keyword) ||
      (item.specification || "").toLowerCase().includes(keyword);
    const matchesModel =
      !inventoryModelFilter.value ||
      `${item.description_zh || ""} ${item.specification || ""}`.includes(
        inventoryModelFilter.value,
      );
    return matchesKeyword && matchesModel;
  }),
);
const materialsProductSeries = ref(technicalDocProductSeries[0]);
const materialsLoading = ref(false);
const materialsError = ref("");
const materialsItems = ref([]);
const photoInputRef = ref(null);
const technicalDocFileInputRef = ref(null);
const photoUploading = ref(false);
const imagePreviewUrl = ref("");
const serviceLogs = ref([]);
const serviceLogComponentFilter = ref("");
const serviceLogSupportFilter = ref("");
const serviceLogCountryFilter = ref("");
const serviceLogCustomerFilter = ref("");
const serviceLogDateFilter = ref("");
const serviceLogProjectFilter = ref("");
const serviceLogModelFilter = ref("");
const serviceLogSerialFilter = ref("");
const serviceLogRdContactFilter = ref("");
const serviceLogStatusFilter = ref("");
const serviceLogCreatedByFilter = ref("");
const serviceLogDescriptionFilter = ref("");
const tickets = ref([]);
const users = ref([]);
const faultComponents = ref([]);
const faultComponentSearch = ref("");
const faultComponentFormOpen = ref(false);
const faultComponentEditingId = ref(null);
const faultComponentDraft = reactive({
  name: "",
  name_en: "",
  sort_order: 0,
  is_active: true,
});
const settingsTab = ref("fault-components");
const logisticsStatuses = ref([]);
const logisticsStatusFormOpen = ref(false);
const logisticsStatusEditingId = ref(null);
const logisticsStatusDraft = reactive({
  name: "",
  name_en: "",
  step_order: 0,
  is_active: true,
});
const empowermentSkills = ref([]);
const empowermentSkillFormOpen = ref(false);
const empowermentSkillEditingId = ref(null);
const empowermentSkillDraft = reactive({ name: "", name_en: "", sort_order: 0, is_active: true });
const activeEmpowermentSkills = computed(() => empowermentSkills.value.filter((skill) => skill.is_active));
const logisticsShipments = ref([]);
const activeLogisticsStatuses = computed(() =>
  logisticsStatuses.value.filter((status) => status.is_active),
);
const logisticsStatusOptions = computed(() =>
  activeLogisticsStatuses.value.map((status) => status.name),
);
const logisticsEquipmentModels = ["418", "250", "100C"];
const logisticsFilters = reactive({ destination: "", status: "" });
const logisticsFormOpen = ref(false);
const logisticsEditingId = ref(null);
const logisticsDraft = reactive({
  created_date: new Date().toISOString().slice(0, 10),
  stage: "delivery",
  customer_company: "",
  related_project: "",
  destination_country: "",
  equipment_model: "",
  specific_module: "",
  equipment_qty: 0,
  status: "工厂备货",
  eta: "",
  tracking_url: "",
  remarks: "",
});
const empowermentRecords = ref([]);
const empowermentFormOpen = ref(false);
const empowermentEditingId = ref(null);
const empowermentDeliveryFields = [
  { key: "delivery_418_net", labelKey: "empowerment.delivery418Net" },
  { key: "delivery_418_soft", labelKey: "empowerment.delivery418Soft" },
  { key: "delivery_250_net", labelKey: "empowerment.delivery250Net" },
  { key: "delivery_250_soft", labelKey: "empowerment.delivery250Soft" },
  { key: "delivery_100c_net", labelKey: "empowerment.delivery100cNet" },
  { key: "delivery_100c_soft", labelKey: "empowerment.delivery100cSoft" },
];
const empowermentDraft = reactive({
  partner_name: "",
  delivery_418_net: 0,
  delivery_418_soft: 0,
  delivery_250_net: 0,
  delivery_250_soft: 0,
  delivery_100c_net: 0,
  delivery_100c_soft: 0,
  aftersales_scores: {},
  remarks: "",
});
const loginOpen = ref(false);
const loginDraft = reactive({ username: "", password: "" });
const serviceLogFormOpen = ref(false);
const serviceLogEditingId = ref(null);
const serviceLogDraft = reactive({
  event_date: new Date().toISOString().slice(0, 10),
  country: "",
  customer: "",
  customer_company: "",
  project_name: "",
  product_model: "418",
  support_type: "远程 (Remote)",
  issue_category: "软件 (Software)",
  fault_component: "",
  faulty_component: "",
  fault_description: "",
  onsite_solution: "",
  serial_number: "",
  rd_contact: "",
  status: "处理中 (Pending)",
  pending_reason: "",
  created_by: "",
  attachments: [],
});
const accountFormOpen = ref(false);
const accountEditingId = ref(null);
const accountDraft = reactive({
  username: "",
  password: "",
  customer_company: "",
  country: "",
});
const partnerOptions = computed(() => [
  ...new Set(
    [
      ...ciDeliveries.value.map(
        (item) => item.customer_company || item.dealer_name,
      ),
      ...users.value.map((item) => item.customer_company || item.customer_name),
      ...gridProjects.value.map(
        (item) => item.customer_company || item.partner_name,
      ),
    ].filter(Boolean),
  ),
]);
const customerOptions = computed(() =>
  [...new Set(users.value.map((item) => item.customer_company || item.customer_name).filter(Boolean))].sort(),
);
const serviceLogProjectOptions = computed(() => {
  const company = serviceLogDraft.customer_company.trim().toLowerCase();
  const options = [
    ...gridProjects.value,
    ...ciDeliveries.value.map((item) => ({
      project_name: item.dealer_name,
      customer_company: item.customer_company || item.dealer_name,
      country: item.region,
    })),
  ];
  if (!company) return options;
  return options.filter(
    (project) =>
      (project.customer_company || project.partner_name || "")
        .trim()
        .toLowerCase() === company,
  );
});
const logisticsProjectOptions = computed(() => {
  const company = logisticsDraft.customer_company.trim().toLowerCase();
  if (!company) return [];
  const customer = users.value.find(
    (user) =>
      (user.customer_company || user.customer_name || "")
        .trim()
        .toLowerCase() === company,
  );
  const assignedProjectNames = new Set([
    ...(customer?.project_ids || []),
    ...(customer?.automatic_projects || []),
  ]);
  const candidates = [
    ...gridProjects.value,
    ...ciDeliveries.value.map((item) => ({
      project_name: item.dealer_name,
      customer_company: item.customer_company || item.dealer_name,
    })),
    ...logisticsShipments.value.map((item) => ({
      project_name: item.related_project,
      customer_company: item.customer_company,
    })),
  ].filter((project) => {
    if (!project.project_name) return false;
    return (
      assignedProjectNames.has(project.project_name) ||
      (project.customer_company || project.partner_name || "")
        .trim()
        .toLowerCase() === company
    );
  });
  return [...new Map(candidates.map((project) => [project.project_name, project])).values()];
});
const timelineOpen = ref(false);
const selectedProject = ref(null);
const milestones = ref([]);
const milestoneEditor = ref(null);
const milestoneDraft = reactive({ actual_date: "" });
const ticketFormOpen = ref(false);
const ticketDraft = reactive({
  project_name: "",
  product_model: "418",
  serial_number: "",
  ticket_type: "故障报修/Bug (Issue Report)",
  suspected_scope: "软件",
  suspected_component: "",
  description: "",
  expected_date: "",
  contact: "",
  attachments: [],
});
ticketDraft.attachments = [];
const ticketUpdate = reactive({
  id: "",
  status: "处理中 (In Progress)",
  staff_reply: "",
  resolved_at: "",
});
const ticketFilters = reactive({
  customer_company: "",
  project_name: "",
  serial_number: "",
  status: "",
  product_model: '',
  ticket_type: '',
  faulty_component: '',
});
const faultyComponentOptions = computed(() =>
  faultComponents.value
    .filter((component) => component.is_active)
    .map((component) => component.name),
);
const filteredFaultComponents = computed(() => {
  const keyword = faultComponentSearch.value.trim().toLowerCase();
  if (!keyword) return faultComponents.value;
  return faultComponents.value.filter((component) =>
    `${component.name || ""} ${component.name_en || ""}`
      .toLowerCase()
      .includes(keyword),
  );
});
const filteredServiceLogs = computed(() => serviceLogs.value.filter((item) => (!serviceLogComponentFilter.value || (item.fault_component || item.faulty_component) === serviceLogComponentFilter.value) && (!serviceLogSupportFilter.value || item.support_type === serviceLogSupportFilter.value)));
const serviceLogCountries = computed(() => [...new Set(serviceLogs.value.map((item) => item.country).filter(Boolean))].sort());
const computedFilteredAfterSalesLogs = computed(() => filteredServiceLogs.value.filter((item) => (!serviceLogDateFilter.value || item.event_date === serviceLogDateFilter.value) && (!serviceLogCountryFilter.value || item.country === serviceLogCountryFilter.value) && (!serviceLogCustomerFilter.value || (item.customer_company || item.customer) === serviceLogCustomerFilter.value) && (!serviceLogProjectFilter.value || (item.project_name || '').toLowerCase().includes(serviceLogProjectFilter.value.toLowerCase())) && (!serviceLogModelFilter.value || item.product_model === serviceLogModelFilter.value) && (!serviceLogSerialFilter.value || (item.serial_number || '').toLowerCase().includes(serviceLogSerialFilter.value.toLowerCase())) && (!serviceLogRdContactFilter.value || (item.rd_contact || '').toLowerCase().includes(serviceLogRdContactFilter.value.toLowerCase())) && (!serviceLogStatusFilter.value || item.status === serviceLogStatusFilter.value) && (!serviceLogCreatedByFilter.value || (item.created_by || '').toLowerCase().includes(serviceLogCreatedByFilter.value.toLowerCase())) && (!serviceLogDescriptionFilter.value || (item.fault_description || '').toLowerCase().includes(serviceLogDescriptionFilter.value.toLowerCase()))));
const filteredTickets = computed(() => tickets.value.filter((ticket) => {
  const company = ticket.customer_company || ticket.partner_name || ticket.customer_name || ''
  return (!ticketFilters.customer_company || company.toLowerCase().includes(ticketFilters.customer_company.toLowerCase()))
    && (!ticketFilters.project_name || (ticket.project_name || '').toLowerCase().includes(ticketFilters.project_name.toLowerCase()))
    && (!ticketFilters.serial_number || (ticket.serial_number || '').toLowerCase().includes(ticketFilters.serial_number.toLowerCase()))
    && (!ticketFilters.product_model || ticket.product_model === ticketFilters.product_model)
    && (!ticketFilters.ticket_type || ticket.ticket_type === ticketFilters.ticket_type)
    && (!ticketFilters.status || ticket.status === ticketFilters.status)
    && (!ticketFilters.faulty_component || ticket.suspected_component === ticketFilters.faulty_component)
}))
let gridDashboardTimerId = null;

const crudModal = reactive({
  open: false,
  kind: "",
  mode: "create",
  originalKey: "",
});
const crudDraft = reactive(createEmptyCrudDraft());
function resolveCountryForCompany(company) {
  const normalized = (company || "").trim().toLowerCase();
  if (!normalized) return "";
  const match = users.value.find(
    (user) =>
      (user.customer_company || user.customer_name || "").trim().toLowerCase() ===
      normalized,
  );
  return match?.country || "";
}
const crudDraftGridCountry = computed(() =>
  resolveCountryForCompany(crudDraft.customer_company),
);
watch(
  () => crudDraft.dealer_name,
  (dealerName) => {
    if (crudModal.kind !== "ci") return;
    const country = resolveCountryForCompany(dealerName);
    if (country) {
      crudDraft.region = country;
    }
  },
);
const crudDraftCiCountryLocked = computed(() =>
  Boolean(resolveCountryForCompany(crudDraft.dealer_name)),
);
const deleteDialog = reactive({
  open: false,
  kind: "",
  key: "",
  title: "",
  message: "",
});

watch(
  () => ticketUpdate.status,
  (status) => {
    if (
      ["已回复/已解决 (Resolved)", "已关闭 (Closed)"].includes(status) &&
      !ticketUpdate.resolved_at
    ) {
      const now = new Date();
      const pad = (value) => String(value).padStart(2, "0");
      ticketUpdate.resolved_at = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
    }
    if (!["已回复/已解决 (Resolved)", "已关闭 (Closed)"].includes(status))
      ticketUpdate.resolved_at = "";
  },
);

const selectedWarehouseLabel = computed(
  () =>
    warehouseOptions.find((item) => item.key === selectedWarehouse.value)
      ?.label ?? selectedWarehouse.value,
);
const warehouseProductOptions = computed(() => {
  const inventory = warehouseSummary.value.inventory ?? [];
  return [...new Set(inventory.map((item) => item.product_model))];
});
const warehouseTopCards = computed(() => {
  const inventory = warehouseSummary.value.inventory ?? [];
  const lookup = (productModel) =>
    inventory.find((item) => item.product_model === productModel)?.quantity ??
    0;
  return [
    {
      key: "100C",
      label: "100C 储能柜",
      quantity: lookup("100C"),
      note: "柜体库存",
    },
    {
      key: "250",
      label: "250 储能柜",
      quantity: lookup("250"),
      note: "柜体库存",
    },
    {
      key: "PCS",
      label: "PCS 主机",
      quantity: lookup("PCS"),
      note: "核心配件",
    },
    {
      key: "BMS",
      label: "BMS 主控板",
      quantity: lookup("BMS"),
      note: "核心配件",
    },
    {
      key: "CableKit",
      label: "线缆包",
      quantity: lookup("CableKit"),
      note: "核心配件",
    },
  ];
});
const isSuperAdmin = computed(() => loggedUser.value?.role === "super_admin");
const isViewer = computed(() => loggedUser.value?.role === "viewer");
const isInternalMode = isSuperAdmin;
const loggedUser = computed(() => {
  if (typeof window === "undefined") return null;
  try {
    return JSON.parse(window.localStorage.getItem("portal-user") || "null");
  } catch {
    return null;
  }
});
const isAuthenticated = computed(() =>
  Boolean(
    loggedUser.value &&
    typeof window !== "undefined" &&
    window.localStorage.getItem("token"),
  ),
);
const isCustomer = computed(() => loggedUser.value?.role === "customer");

watch(
  () => serviceLogDraft.customer_company,
  (company) => {
    if (
      serviceLogDraft.project_name &&
      !serviceLogProjectOptions.value.some(
        (project) => project.project_name === serviceLogDraft.project_name,
      )
    ) {
      serviceLogDraft.project_name = "";
    }
  },
);

watch(
  () => serviceLogDraft.project_name,
  (projectName) => {
    const project = serviceLogProjectOptions.value.find(
      (item) => item.project_name === projectName,
    );
    if (project) {
      serviceLogDraft.customer_company =
        project.customer_company || project.partner_name || "";
      const matchedUser = users.value.find(
        (user) =>
          (user.customer_company || user.customer_name || "").toLowerCase() ===
          (serviceLogDraft.customer_company || "").toLowerCase(),
      );
      serviceLogDraft.country =
        matchedUser?.country || project.country || serviceLogDraft.country;
      const isGridScale = gridProjects.value.some(
        (item) => item.project_name === projectName,
      );
      if (isGridScale) {
        serviceLogDraft.product_model = "418";
      } else if (serviceLogDraft.product_model === "418") {
        serviceLogDraft.product_model = "250";
      }
    }
  },
);
const serviceLogProductModelOptions = computed(() => {
  const isGridScale = gridProjects.value.some(
    (item) => item.project_name === serviceLogDraft.project_name,
  );
  return isGridScale ? ["418"] : ["250", "100C"];
});
const serviceLogCountryLocked = computed(() =>
  Boolean(serviceLogDraft.project_name || serviceLogDraft.customer_company),
);
const locale = computed(() => portalState.locale);
const isEnglish = computed(() => locale.value === "en-US");
const materialsCanManage = computed(() => {
  if (isInternalMode.value) {
    return true;
  }
  if (typeof window === "undefined") {
    return false;
  }
  return Boolean(window.localStorage.getItem("token"));
});
const materialsByCategory = computed(() => {
  const grouped = Object.fromEntries(
    technicalDocCategories.map((category) => [category, []]),
  );
  for (const item of materialsItems.value) {
    if (!grouped[item.category]) {
      grouped[item.category] = [];
    }
    grouped[item.category].push(item);
  }
  return grouped;
});

function t(path) {
  return (
    path
      .split(".")
      .reduce(
        (accumulator, key) => accumulator?.[key],
        messages[locale.value],
      ) ?? path
  );
}

const todayTick = ref(Date.now());

const faultHint = computed(() => {
  if (!faultHasSearched.value) {
    return isEnglish.value
      ? "Showing the full simulated fault library by default."
      : "默认展示全部模拟故障库，输入关键字后即可快速筛选。";
  }
  return faultKeyword.value.trim()
    ? `${isEnglish.value ? "Current keyword" : "当前搜索词"}: ${faultKeyword.value.trim()}`
    : isEnglish.value
      ? "Showing all results."
      : "显示全部结果。";
});

const faultTotalPages = computed(() =>
  Math.max(1, Math.ceil((faultTotal.value || 0) / (faultPageSize.value || 1))),
);

const gridSummary = computed(() => {
  const totalMwh = gridProjects.value.reduce(
    (sum, project) => sum + (Number(project.capacity_mwh) || 0),
    0,
  );
  const totalDayValue = getTodayDayValue();
  const palette = [
    "bg-cyan-400/80",
    "bg-emerald-400/80",
    "bg-violet-400/80",
    "bg-amber-400/80",
    "bg-fuchsia-400/80",
    "bg-sky-400/80",
  ];

  const projects = gridProjects.value.map((project, index) => {
    const capacityMwh = Number(project.capacity_mwh) || 0;
    const ratio = totalMwh > 0 ? (capacityMwh / totalMwh) * 100 : 0;
    const codDiff = getCodDayDiff(project.cod, totalDayValue);
    const delivered = isGridProjectDelivered(project);
    const daysLabel =
      codDiff === null
        ? t("common.noData")
        : delivered
          ? `${t("grid.deliveredDays")}: ${Math.max(-codDiff, 0)} ${isEnglish.value ? "days" : "天"}`
          : codDiff >= 0
            ? `${t("grid.remainingDays")}: ${codDiff} ${isEnglish.value ? "days" : "天"}`
            : `${t("grid.overdueDays")}: ${Math.abs(codDiff)} ${isEnglish.value ? "days" : "天"}`;

    return {
      ...project,
      capacityMwh,
      capacityRatio: ratio,
      ratioLabel: `${ratio.toFixed(1)}%`,
      deliveryState: delivered
        ? t("grid.deliveredTag")
        : t("grid.inProgressTag"),
      deliveryBadgeClass: delivered
        ? "border border-emerald-300/20 bg-emerald-400/15 text-emerald-200"
        : "border border-amber-300/20 bg-amber-400/15 text-amber-200",
      ratioBarClass: palette[index % palette.length],
      daysLabel,
    };
  });

  const connectedProjects = projects.filter((project) =>
    isGridProjectConnectedStatus(project.progress_status),
  );
  const pendingProjects = projects.filter((project) =>
    isGridProjectPendingStatus(project.progress_status),
  );
  const connectedMwh = connectedProjects.reduce(
    (sum, project) => sum + project.capacityMwh,
    0,
  );
  const pendingMwh = pendingProjects.reduce(
    (sum, project) => sum + project.capacityMwh,
    0,
  );
  const connectedRatio = totalMwh > 0 ? (connectedMwh / totalMwh) * 100 : 0;
  const pendingRatio = totalMwh > 0 ? (pendingMwh / totalMwh) * 100 : 0;

  return {
    totalMwh,
    projects,
    connectedMwh,
    connectedCount: connectedProjects.length,
    pendingMwh,
    pendingCount: pendingProjects.length,
    connectedRatio,
    pendingRatio,
    connectedRatioLabel: `${connectedRatio.toFixed(1)}%`,
    pendingRatioLabel: `${pendingRatio.toFixed(1)}%`,
  };
});

const CI_100C_MWH_PER_UNIT = 0.1;
const CI_250_MWH_PER_UNIT = 0.25;

const ciCapacityRows = computed(() => {
  const baseRows = ciDeliveries.value.map((item) => {
    const batches = ciBatchesByDealer.value[item.id] || [];
    const delivered100c = batches.filter((batch) => batch.product_type === "100C").reduce((sum, batch) => sum + (Number(batch.quantity) || 0), 0);
    const delivered250 = batches.filter((batch) => batch.product_type === "250").reduce((sum, batch) => sum + (Number(batch.quantity) || 0), 0);
    return {
      ...item,
      delivered_100c: delivered100c,
      delivered_250: delivered250,
      mwh100c: delivered100c * CI_100C_MWH_PER_UNIT,
      mwh250: delivered250 * CI_250_MWH_PER_UNIT,
    };
  });

  const max100cMwh = Math.max(0, ...baseRows.map((item) => item.mwh100c));
  const max250Mwh = Math.max(0, ...baseRows.map((item) => item.mwh250));

  return baseRows.map((item) => ({
    ...item,
    ratio100c: max100cMwh > 0 ? (item.mwh100c / max100cMwh) * 100 : 0,
    ratio250: max250Mwh > 0 ? (item.mwh250 / max250Mwh) * 100 : 0,
  }));
});

const ciSummary = computed(() => {
  const total100c = ciCapacityRows.value.reduce(
    (sum, item) => sum + item.delivered_100c,
    0,
  );
  const total250 = ciCapacityRows.value.reduce(
    (sum, item) => sum + item.delivered_250,
    0,
  );
  return {
    total100c,
    total250,
    total100cMwh: total100c * CI_100C_MWH_PER_UNIT,
    total250Mwh: total250 * CI_250_MWH_PER_UNIT,
  };
});

function makeTextDownload(content, filename) {
  return `data:text/plain;charset=utf-8,${encodeURIComponent(content)}#${encodeURIComponent(filename)}`;
}

function formatMwh(value) {
  const numericValue = Number(value) || 0;
  return Number.isInteger(numericValue)
    ? String(numericValue)
    : numericValue.toFixed(1);
}

function formatCiMwh(value) {
  return (Number(value) || 0).toFixed(2);
}

function currentTimestampStamp() {
  return new Date()
    .toISOString()
    .replaceAll("-", "")
    .replaceAll(":", "")
    .replaceAll("T", "")
    .replaceAll("Z", "")
    .replaceAll(".", "")
    .slice(0, 14);
}

function prefillWarehouseTxNo() {
  warehouseForm.tx_no = `WH-${selectedWarehouse.value.toUpperCase()}-${currentTimestampStamp()}`;
}

function statusClass(status) {
  const map = {
    清关中: "bg-amber-400/15 text-amber-200 border border-amber-300/20",
    设备上岸: "bg-sky-400/15 text-sky-200 border border-sky-300/20",
    土建施工: "bg-violet-400/15 text-violet-200 border border-violet-300/20",
    调试中: "bg-cyan-400/15 text-cyan-200 border border-cyan-300/20",
    正式并网: "bg-emerald-400/15 text-emerald-200 border border-emerald-300/20",
  };
  return map[status] ?? "bg-white/10 text-slate-200 border border-white/10";
}

function getTodayDayValue(epochMs = todayTick.value) {
  const now = new Date(epochMs);
  return Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
}

function getCodDayValue(cod) {
  if (!cod) return null;
  const [year, month, day] = String(cod)
    .split("-")
    .map((part) => Number(part));
  if (!year || !month || !day) return null;
  return Date.UTC(year, month - 1, day);
}

function getCodDayDiff(cod, todayDayValue = getTodayDayValue()) {
  const codDayValue = getCodDayValue(cod);
  if (codDayValue === null) return null;
  return Math.round((codDayValue - todayDayValue) / 86400000);
}

function normalizeGridProjectStatus(status) {
  const normalized = String(status ?? "").trim();
  const lower = normalized.toLowerCase();
  if (
    normalized === "已并网" ||
    normalized === "正式并网" ||
    lower === "connected" ||
    lower === "grid_connected"
  ) {
    return "connected";
  }
  if (
    normalized === "待交付" ||
    normalized === "交付中" ||
    normalized === "清关中" ||
    normalized === "设备上岸" ||
    normalized === "土建施工" ||
    normalized === "调试中" ||
    lower === "pending" ||
    lower === "pending_delivery" ||
    lower === "in_progress" ||
    lower === "in progress"
  ) {
    return "pending";
  }
  return "pending";
}

function isGridProjectConnectedStatus(status) {
  return normalizeGridProjectStatus(status) === "connected";
}

function isGridProjectPendingStatus(status) {
  return normalizeGridProjectStatus(status) === "pending";
}

function isGridProjectDelivered(project) {
  return isGridProjectConnectedStatus(project?.progress_status);
}

function openVideo(url) {
  window.open(url, "_blank", "noopener,noreferrer");
}

function isVideoFile(item) {
  const fileType = String(item?.file_type ?? "").toLowerCase();
  const fileUrl = String(item?.file_url ?? "").toLowerCase();
  return (
    fileType.startsWith("video/") ||
    /\.(mp4|mov|webm|m4v)$/i.test(fileUrl) ||
    item?.category === "安装视频"
  );
}

function previewTechnicalDoc(item) {
  const previewUrl = technicalDocActionUrl(item, false);
  if (!previewUrl) return;
  if (isVideoFile(item)) {
    openVideo(previewUrl);
    return;
  }
  window.open(previewUrl, "_blank", "noopener,noreferrer");
}

function technicalDocActionUrl(item, download = false) {
  const id = item?.id;
  if (!id) {
    return item?.file_url || "";
  }
  return `/api/technical-docs/${encodeURIComponent(String(id))}/file${download ? "?download=1" : ""}`;
}

function changeMaterialsSeries(series) {
  if (materialsProductSeries.value === series) {
    return;
  }
  materialsProductSeries.value = series;
  loadTechnicalDocs();
}

async function loadTechnicalDocs() {
  materialsLoading.value = true;
  materialsError.value = "";
  try {
    const payload = await portalApi.listTechnicalDocs({
      product: materialsProductSeries.value,
    });
    materialsItems.value = payload.items ?? [];
  } catch (error) {
    materialsItems.value = [];
    materialsError.value = formatApiError(
      error,
      `${t("notices.loadFailed")} / Materials load failed`,
    );
  } finally {
    materialsLoading.value = false;
  }
}

function openTechnicalDocEditor(record = null) {
  if (!materialsCanManage.value) {
    setNotice(
      isEnglish.value
        ? "No permission to modify materials."
        : "当前无资料管理权限。",
      "error",
    );
    return;
  }
  openCrudModal("technical-doc", record ? "edit" : "create", record);
}

function openTechnicalDocFilePicker() {
  technicalDocFileInputRef.value?.click();
}

function handleTechnicalDocFile(event) {
  const files = [...(event.target.files ?? [])];
  const file = files[0];
  if (!file) return;
  crudDraft.technical_doc_file = file;
  if (!crudDraft.title.trim()) {
    crudDraft.title = file.name.replace(/\.[^.]+$/, "");
  }
}

function ensureInternalMode() {
  if (isInternalMode.value) {
    return true;
  }
  setNotice(
    isEnglish.value
      ? "Read-only mode: your account does not have write access."
      : "当前为只读模式，您的账号没有写入权限。",
    "error",
  );
  return false;
}

function openCrudModal(kind, mode = "create", record = null) {
  if (kind === "technical-doc") {
    if (!materialsCanManage.value) {
      setNotice(
        isEnglish.value
          ? "No permission to modify materials."
          : "当前无资料管理权限。",
        "error",
      );
      return;
    }
  } else if (!ensureInternalMode()) {
    return;
  }
  crudModal.kind = kind;
  crudModal.mode = mode;
  crudModal.originalKey = getRecordKey(kind, record) ?? "";
  crudModal.open = true;
  resetCrudDraft(kind, record);
}

function closeCrudModal() {
  crudModal.open = false;
  crudModal.kind = "";
  crudModal.mode = "create";
  crudModal.originalKey = "";
}

function openDeleteDialog(kind, key, title, message) {
  if (kind === "technical-doc") {
    if (!materialsCanManage.value) {
      setNotice(
        isEnglish.value
          ? "No permission to modify materials."
          : "当前无资料管理权限。",
        "error",
      );
      return;
    }
  } else if (!ensureInternalMode()) {
    return;
  }
  deleteDialog.kind = kind;
  deleteDialog.key = key;
  deleteDialog.title = title;
  deleteDialog.message = message;
  deleteDialog.open = true;
}

function closeDeleteDialog() {
  deleteDialog.open = false;
  deleteDialog.kind = "";
  deleteDialog.key = "";
  deleteDialog.title = "";
  deleteDialog.message = "";
}

function createEmptyCrudDraft() {
  return {
    id: null,
    module: "",
    fault_code: "",
    fault_name: "",
    fault_level: "",
    is_stop: "",
    recovery: "",
    detection_condition: "",
    trigger_logic: "",
    possible_cause: "",
    solution: "",
    project_name: "",
    customer_company: "",
    cod: "",
    capacity_mwh: 0,
    software_version: "",
    progress_status: projectStatuses[0],
    photo_paths: [],
    region: "",
    dealer_name: "",
    delivered_100c: 0,
    delivered_250: 0,
    warehouse_name: selectedWarehouse.value,
    tx_type: "国内到货入库",
    product_model: "100C",
    quantity: 1,
    related_project: "",
    tx_no: "",
    item_no: "",
    description_zh: "",
    specification: "",
    total_quantity: 0,
    damaged_quantity: 0,
    available_quantity: 0,
    product_series: materialsProductSeries.value,
    category: technicalDocCategories[0],
    title: "",
    file_url: "",
    file_type: "",
    file_size: "",
    technical_doc_file: null,
    remarks: "",
  };
}

function resetCrudDraft(kind, record) {
  const nextDraft = createEmptyCrudDraft();
  if (kind === "fault" && record) {
    nextDraft.id = record.id;
    nextDraft.module = record.module;
    nextDraft.fault_code = record.fault_code;
    nextDraft.fault_name = record.fault_name;
    nextDraft.fault_level = record.fault_level;
    nextDraft.is_stop = record.is_stop;
    nextDraft.recovery = record.recovery;
    nextDraft.detection_condition = record.detection_condition;
    nextDraft.trigger_logic = record.trigger_logic;
    nextDraft.possible_cause = record.possible_cause;
    nextDraft.solution = record.solution;
  }
  if (kind === "grid" && record) {
    nextDraft.project_name = record.project_name;
    nextDraft.customer_company =
      record.customer_company || record.partner_name || "";
    nextDraft.cod = record.cod;
    nextDraft.capacity_mwh = record.capacity_mwh;
    nextDraft.software_version = record.software_version || record.cell_version || "";
    nextDraft.progress_status = record.progress_status;
    nextDraft.photo_paths = [...(record.photo_paths ?? [])];
  }
  if (kind === "ci" && record) {
    nextDraft.region = record.region;
    nextDraft.dealer_name = record.dealer_name;
    nextDraft.delivered_100c = record.delivered_100c;
    nextDraft.delivered_250 = record.delivered_250;
  }
  if (kind === "inventory" && record) {
    nextDraft.item_no = record.item_no;
    nextDraft.description_zh = record.description_zh;
    nextDraft.specification = record.specification;
    nextDraft.total_quantity = record.total_quantity;
    nextDraft.damaged_quantity = record.damaged_quantity;
    nextDraft.available_quantity = record.available_quantity;
    nextDraft.photo_paths = [...(record.photo_paths ?? [])];
    nextDraft.remarks = record.remarks ?? "";
  }
  if (kind === "technical-doc" && record) {
    nextDraft.product_series = record.product_series;
    nextDraft.category = record.category;
    nextDraft.title = record.title;
    nextDraft.file_url = record.file_url;
    nextDraft.file_type = record.file_type;
    nextDraft.file_size = record.file_size;
    nextDraft.technical_doc_file = null;
  }
  Object.assign(crudDraft, nextDraft);
  if (kind === "warehouse" && !crudDraft.tx_no) {
    prefillWarehouseTxNo();
  }
  if (kind === "inventory") {
    crudDraft.available_quantity =
      Number(crudDraft.available_quantity) ||
      Math.max(
        Number(crudDraft.total_quantity) - Number(crudDraft.damaged_quantity),
        0,
      );
  }
}

function getRecordKey(kind, record) {
  if (!record) return "";
  if (kind === "fault") return String(record.id);
  if (kind === "grid") return String(record.id);
  if (kind === "ci") return record.dealer_name;
  if (kind === "technical-doc") return String(record.id);
  if (kind === "inventory") return record.item_no;
  if (kind === "warehouse") return record.tx_no;
  return "";
}

function normalizePhotoPaths(text) {
  return text
    .split(/[\n,;]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function recomputeAvailableQuantity() {
  crudDraft.available_quantity = Math.max(
    Number(crudDraft.total_quantity) - Number(crudDraft.damaged_quantity),
    0,
  );
}

function openPhotoPicker() {
  if (!ensureInternalMode()) return;
  photoInputRef.value?.click();
}

async function handlePhotoFiles(event) {
  if (!ensureInternalMode()) return;
  const files = [...(event.target.files ?? [])];
  if (files.length === 0) return;
  photoUploading.value = true;
  try {
    for (const file of files) {
      const result = await portalApi.uploadImage(file);
      crudDraft.photo_paths.push(result.url);
    }
  } finally {
    photoUploading.value = false;
    event.target.value = "";
  }
}

function removePhotoPath(index) {
  crudDraft.photo_paths.splice(index, 1);
}

function openImagePreview(url) {
  imagePreviewUrl.value = resolvePhotoUrl(url);
}

function resolvePhotoUrl(photo) {
  if (!photo) return "";
  if (
    photo.startsWith("http://") ||
    photo.startsWith("https://") ||
    photo.startsWith("data:")
  ) {
    return photo;
  }
  if (photo.startsWith("/static_uploads/")) {
    return photo;
  }
  return `/static_uploads/${photo.replace(/^\/+/, "")}`;
}

function closeImagePreview() {
  imagePreviewUrl.value = "";
}

function formatApiError(error, fallback) {
  return `${fallback}: ${error instanceof Error ? error.message : "Unknown error"}`;
}

async function openMilestoneTimeline(project) {
  selectedProject.value = project;
  timelineOpen.value = true;
  milestoneEditor.value = null;
  try {
    const payload = await portalApi.listMilestones(project.project_name);
    milestones.value = payload.items ?? [];
  } catch (error) {
    milestones.value = [];
    setNotice(formatApiError(error, "请先登录后查看项目里程碑。"), "error");
  }
}

function editMilestone(item) {
  milestoneEditor.value = item.key;
  milestoneDraft.actual_date = item.actual_date || "";
}

async function saveMilestone() {
  if (!selectedProject.value || !milestoneEditor.value) return;
  await portalApi.updateMilestone(
    selectedProject.value.project_name,
    milestoneEditor.value,
    { actual_date: milestoneDraft.actual_date || null },
  );
  const payload = await portalApi.listMilestones(
    selectedProject.value.project_name,
  );
  milestones.value = payload.items ?? [];
  milestoneEditor.value = null;
  setNotice(t("notices.gridSaved"), "success");
}

async function loadPortalExtras() {
  if (!isAuthenticated.value) return;
  try {
    const [logsPayload, ticketPayload] = await Promise.all([
      portalApi.listAfterSalesLogs(),
      portalApi.listTickets(isInternalMode.value ? ticketFilters : {}),
    ]);
    serviceLogs.value = logsPayload.items ?? [];
    tickets.value = ticketPayload.items ?? [];
  } catch (error) {
    setNotice(formatApiError(error, "客户数据加载失败"), "error");
  }
}

async function fetchUsers() {
  if (!isSuperAdmin.value) {
    users.value = [];
    return;
  }
  try {
    const response = await portalApi.listUsers();
    const payload = Array.isArray(response)
      ? response
      : response?.data?.items ?? response?.data ?? response?.items ?? [];
    users.value = Array.isArray(payload) ? payload : [];
  } catch (error) {
    users.value = [];
    setNotice(formatApiError(error, "客户账号加载失败"), "error");
  }
}

async function fetchFaultComponents() {
  if (!isAuthenticated.value) {
    faultComponents.value = [];
    return;
  }
  try {
    const response = await portalApi.listFaultComponents(!isCustomer.value);
    const payload = Array.isArray(response)
      ? response
      : response?.data?.items ?? response?.data ?? response?.items ?? [];
    faultComponents.value = Array.isArray(payload) ? payload : [];
  } catch (error) {
    faultComponents.value = [];
    setNotice(formatApiError(error, "故障部件加载失败"), "error");
  }
}

async function fetchLogisticsStatuses() {
  if (!isAuthenticated.value) {
    logisticsStatuses.value = [];
    return;
  }
  try {
    const response = await portalApi.listLogisticsStatuses(!isCustomer.value);
    logisticsStatuses.value = response?.items ?? response?.data?.items ?? [];
    if (!logisticsDraft.status && logisticsStatusOptions.value.length) {
      logisticsDraft.status = logisticsStatusOptions.value[0];
    }
  } catch (error) {
    logisticsStatuses.value = [];
    setNotice(formatApiError(error, "物流状态加载失败"), "error");
  }
}

async function fetchEmpowermentSkills() {
  if (!isAuthenticated.value) {
    empowermentSkills.value = [];
    return;
  }
  try {
    const response = await portalApi.listEmpowermentSkills(isSuperAdmin.value);
    empowermentSkills.value = response?.items ?? response?.data?.items ?? [];
  } catch (error) {
    empowermentSkills.value = [];
    setNotice(formatApiError(error, t("settings.empowermentSkillsLoadFailed")), "error");
  }
}

function empowermentSkillLabel(skill) {
  return isEnglish.value && skill.name_en ? skill.name_en : skill.name;
}

function getProgressColor(value) {
  const score = Number(value) || 0;
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-sky-500";
  if (score >= 40) return "bg-amber-500";
  return "bg-rose-400";
}

function resetEmpowermentSkillDraft() {
  Object.assign(empowermentSkillDraft, { name: "", name_en: "", sort_order: empowermentSkills.value.length + 1, is_active: true });
  empowermentSkillEditingId.value = null;
}

function openEmpowermentSkillEditor(skill = null) {
  if (!isSuperAdmin.value) return;
  resetEmpowermentSkillDraft();
  if (skill) {
    empowermentSkillEditingId.value = skill.id;
    Object.assign(empowermentSkillDraft, skill);
  }
  empowermentSkillFormOpen.value = true;
}

async function saveEmpowermentSkill() {
  if (!empowermentSkillDraft.name.trim()) {
    setNotice(t("settings.skillName"), "error");
    return;
  }
  const payload = {
    name: empowermentSkillDraft.name.trim(),
    name_en: empowermentSkillDraft.name_en.trim(),
    sort_order: Number(empowermentSkillDraft.sort_order) || 0,
    is_active: Boolean(empowermentSkillDraft.is_active),
  };
  try {
    if (empowermentSkillEditingId.value) await portalApi.updateEmpowermentSkill(empowermentSkillEditingId.value, payload);
    else await portalApi.createEmpowermentSkill(payload);
    empowermentSkillFormOpen.value = false;
    resetEmpowermentSkillDraft();
    await fetchEmpowermentSkills();
    setNotice(t("settings.empowermentSkillSaved"), "success");
  } catch (error) {
    setNotice(formatApiError(error, t("settings.empowermentSkillSaveFailed")), "error");
  }
}

function logisticsStatusLabel(status) {
  return isEnglish.value && status.name_en ? status.name_en : status.name;
}

function logisticsEquipmentLabel(model) {
  return model ? model.replace(/^eBlock-/i, "") : "-";
}

function resetLogisticsStatusDraft() {
  Object.assign(logisticsStatusDraft, {
    name: "",
    name_en: "",
    step_order: logisticsStatuses.value.length + 1,
    is_active: true,
  });
  logisticsStatusEditingId.value = null;
}

function openLogisticsStatusEditor(status = null) {
  if (!isSuperAdmin.value) return;
  resetLogisticsStatusDraft();
  if (status) {
    logisticsStatusEditingId.value = status.id;
    Object.assign(logisticsStatusDraft, status);
  }
  logisticsStatusFormOpen.value = true;
}

async function saveLogisticsStatus() {
  if (!logisticsStatusDraft.name.trim()) {
    setNotice(t("settings.statusName"), "error");
    return;
  }
  const payload = {
    name: logisticsStatusDraft.name.trim(),
    name_en: logisticsStatusDraft.name_en.trim(),
    step_order: Number(logisticsStatusDraft.step_order) || 0,
    is_active: Boolean(logisticsStatusDraft.is_active),
  };
  try {
    if (logisticsStatusEditingId.value) {
      await portalApi.updateLogisticsStatus(logisticsStatusEditingId.value, payload);
    } else {
      await portalApi.createLogisticsStatus(payload);
    }
    logisticsStatusFormOpen.value = false;
    resetLogisticsStatusDraft();
    await fetchLogisticsStatuses();
    setNotice(t("settings.logisticsSaved"), "success");
  } catch (error) {
    setNotice(formatApiError(error, t("settings.logisticsSaved")), "error");
  }
}

function resetFaultComponentDraft() {
  Object.assign(faultComponentDraft, {
    name: "",
    name_en: "",
    sort_order: faultComponents.value.length + 1,
    is_active: true,
  });
  faultComponentEditingId.value = null;
}

function openFaultComponentEditor(component = null) {
  if (!isSuperAdmin.value) return;
  resetFaultComponentDraft();
  if (component) {
    faultComponentEditingId.value = component.id;
    Object.assign(faultComponentDraft, component);
  }
  faultComponentFormOpen.value = true;
}

async function saveFaultComponent() {
  if (!faultComponentDraft.name.trim()) {
    setNotice(t("settings.name"), "error");
    return;
  }
  try {
    const payload = {
      name: faultComponentDraft.name.trim(),
      name_en: faultComponentDraft.name_en.trim(),
      sort_order: Number(faultComponentDraft.sort_order) || 0,
      is_active: Boolean(faultComponentDraft.is_active),
    };
    if (faultComponentEditingId.value) {
      await portalApi.updateFaultComponent(faultComponentEditingId.value, payload);
    } else {
      await portalApi.createFaultComponent(payload);
    }
    faultComponentFormOpen.value = false;
    resetFaultComponentDraft();
    await fetchFaultComponents();
    setNotice(t("settings.saved"), "success");
  } catch (error) {
    setNotice(formatApiError(error, t("settings.saved")), "error");
  }
}

async function loadLogisticsShipments() {
  if (!isAuthenticated.value) return;
  try {
    const payload = await portalApi.listLogisticsShipments(logisticsFilters);
    logisticsShipments.value = payload.items ?? [];
  } catch (error) {
    setNotice(formatApiError(error, "物流数据加载失败"), "error");
  }
}

async function loadEmpowermentRecords() {
  if (!isAuthenticated.value || isCustomer.value) return;
  try {
    const payload = await portalApi.listEmpowermentRecords();
    empowermentRecords.value = payload.items ?? [];
  } catch (error) {
    setNotice(formatApiError(error, "赋能计划数据加载失败"), "error");
  }
}

function resetLogisticsDraft() {
  Object.assign(logisticsDraft, {
    created_date: new Date().toISOString().slice(0, 10),
    stage: "delivery",
    customer_company: "",
    related_project: "",
    destination_country: "",
    equipment_model: "",
    specific_module: "",
    equipment_qty: 0,
    status: logisticsStatusOptions.value[0] || "",
    eta: "",
    tracking_url: "",
    remarks: "",
  });
  logisticsEditingId.value = null;
}

function handleLogisticsCustomerChange() {
  logisticsDraft.related_project = "";
  const country = resolveCountryForCompany(logisticsDraft.customer_company);
  if (country) logisticsDraft.destination_country = country;
}

function openLogisticsEditor(record = null) {
  if (!ensureInternalMode()) return;
  resetLogisticsDraft();
  if (record) {
    logisticsEditingId.value = record.id;
    Object.assign(logisticsDraft, record);
  }
  logisticsFormOpen.value = true;
}

function editLogisticsShipment(record) {
  openLogisticsEditor(record);
}

async function submitLogisticsShipment() {
  if (!logisticsDraft.created_date) {
    setNotice(t("notices.requiredLog"), "error");
    return;
  }
  try {
    const payload = {
      created_date: logisticsDraft.created_date,
      stage: logisticsDraft.stage,
      customer_company: logisticsDraft.customer_company,
      related_project: logisticsDraft.related_project,
      destination_country: logisticsDraft.destination_country.trim(),
      equipment_model: logisticsDraft.equipment_model,
      specific_module: logisticsDraft.specific_module,
      equipment_qty: Number(logisticsDraft.equipment_qty) || 0,
      status: logisticsDraft.status,
      eta: logisticsDraft.eta || null,
      tracking_url: logisticsDraft.tracking_url.trim(),
      remarks: logisticsDraft.remarks.trim(),
    };
    if (logisticsEditingId.value) {
      await portalApi.updateLogisticsShipment(logisticsEditingId.value, payload);
    } else {
      await portalApi.createLogisticsShipment(payload);
    }
    logisticsFormOpen.value = false;
    resetLogisticsDraft();
    await loadLogisticsShipments();
    setNotice(t("notices.logSaved"), "success");
  } catch (error) {
    setNotice(formatApiError(error, t("notices.logSaveFailed")), "error");
  }
}

function resetEmpowermentDraft() {
  Object.assign(empowermentDraft, {
    partner_name: "",
    delivery_418_net: 0,
    delivery_418_soft: 0,
    delivery_250_net: 0,
    delivery_250_soft: 0,
    delivery_100c_net: 0,
    delivery_100c_soft: 0,
    aftersales_scores: Object.fromEntries(activeEmpowermentSkills.value.map((skill) => [skill.name, 0])),
    remarks: "",
  });
  empowermentEditingId.value = null;
}

function openEmpowermentEditor(record = null) {
  if (!ensureInternalMode()) return;
  resetEmpowermentDraft();
  if (record) {
    empowermentEditingId.value = record.id;
    Object.assign(empowermentDraft, record);
    empowermentDraft.aftersales_scores = Object.fromEntries(activeEmpowermentSkills.value.map((skill) => [skill.name, record.aftersales_scores?.[skill.name] || 0]));
  }
  empowermentFormOpen.value = true;
}

function editEmpowermentRecord(record) {
  openEmpowermentEditor(record);
}

async function submitEmpowermentRecord() {
  if (!empowermentDraft.partner_name) {
    setNotice(t("notices.requiredLog"), "error");
    return;
  }
  try {
    const payload = {
      partner_name: empowermentDraft.partner_name.trim(),
      ...Object.fromEntries(empowermentDeliveryFields.map((field) => [field.key, Number(empowermentDraft[field.key]) || 0])),
      aftersales_scores: Object.fromEntries(activeEmpowermentSkills.value.map((skill) => [skill.name, Number(empowermentDraft.aftersales_scores?.[skill.name]) || 0])),
      remarks: empowermentDraft.remarks.trim(),
    };
    if (empowermentEditingId.value) {
      await portalApi.updateEmpowermentRecord(empowermentEditingId.value, payload);
    } else {
      await portalApi.createEmpowermentRecord(payload);
    }
    empowermentFormOpen.value = false;
    resetEmpowermentDraft();
    await loadEmpowermentRecords();
    setNotice(t("notices.logSaved"), "success");
  } catch (error) {
    setNotice(formatApiError(error, t("notices.logSaveFailed")), "error");
  }
}

async function createCustomerAccount() {
  if (
    !accountDraft.username ||
    (!accountEditingId.value && !accountDraft.password) ||
    !accountDraft.customer_company ||
    !accountDraft.country
  ) {
    setNotice(t("portal.customer"), "error");
    return;
  }
  const editing = Boolean(accountEditingId.value);
  if (editing) {
    await portalApi.updateUser(accountEditingId.value, {
      password: accountDraft.password || null,
      customer_company: accountDraft.customer_company,
      country: accountDraft.country,
    });
  } else {
    await portalApi.createUser({ ...accountDraft });
  }
  accountDraft.username = "";
  accountDraft.password = "";
  accountDraft.customer_company = "";
  accountDraft.country = "";
  accountFormOpen.value = false;
  accountEditingId.value = null;
  await fetchUsers();
  setNotice(
    t(editing ? "notices.accountUpdated" : "notices.accountCreated"),
    "success",
  );
}

function editCustomerAccount(user) {
  accountEditingId.value = user.id;
  accountDraft.username = user.username;
  accountDraft.password = "";
  accountDraft.customer_company =
    user.customer_company || user.customer_name || "";
  accountDraft.country = user.country || "";
  accountFormOpen.value = true;
}

async function removeCustomerAccount(id) {
  await portalApi.deleteUser(id);
  await fetchUsers();
  setNotice(t("notices.accountDeleted"), "success");
}

function formatTicketDate(value) {
  return value ? new Date(value).toLocaleString() : "-";
}

function clearTicketFilters() {
  Object.assign(ticketFilters, {
    customer_company: "",
    project_name: "",
    serial_number: "",
    status: "",
    product_model: "",
    ticket_type: "",
    fault_component: "",
    faulty_component: "",
  });
}

function clearAfterSalesFilters() {
  serviceLogCountryFilter.value = "";
  serviceLogCustomerFilter.value = "";
  serviceLogSupportFilter.value = "";
  serviceLogComponentFilter.value = "";
  serviceLogDateFilter.value = "";
  serviceLogProjectFilter.value = "";
  serviceLogModelFilter.value = "";
  serviceLogSerialFilter.value = "";
  serviceLogRdContactFilter.value = "";
  serviceLogStatusFilter.value = "";
  serviceLogCreatedByFilter.value = "";
  serviceLogDescriptionFilter.value = "";
}

async function submitTicket() {
  if (
    !ticketDraft.project_name ||
    !ticketDraft.description ||
    !ticketDraft.contact
  ) {
    setNotice(t("notices.requiredTicket"), "error");
    return;
  }
  if (ticketDraft.product_model === "418" && !ticketDraft.project_name) {
    setNotice(t("notices.requiredProject418"), "error");
    return;
  }
  if (!ticketDraft.serial_number.trim()) {
    setNotice(t("notices.requiredSerialNumber"), "error");
    return;
  }
  await portalApi.createTicket({
    ...ticketDraft,
    suspected_scope: ticketDraft.suspected_scope,
  });
  ticketFormOpen.value = false;
  Object.assign(ticketDraft, {
    project_name: "",
    serial_number: "",
    suspected_component: "",
    description: "",
    expected_date: "",
    contact: "",
    attachments: [],
  });
  await loadPortalExtras();
  setNotice(t("notices.ticketSubmitted"), "success");
}

async function updateTicketStatus() {
  if (!ticketUpdate.id) return;
  const resolvedAt =
    ticketUpdate.resolved_at ||
    (["已回复/已解决 (Resolved)", "已关闭 (Closed)"].includes(
      ticketUpdate.status,
    )
      ? new Date().toISOString()
      : null);
  await portalApi.updateTicket(ticketUpdate.id, {
    status: ticketUpdate.status,
    staff_reply: ticketUpdate.staff_reply,
    resolved_at: resolvedAt,
  });
  await loadPortalExtras();
  setNotice(t("notices.ticketUpdated"), "success");
}

async function submitLogin() {
  try {
    const result = await portalApi.login(
      loginDraft.username,
      loginDraft.password,
    );
    window.localStorage.setItem("token", result.token);
    window.localStorage.setItem("portal-user", JSON.stringify(result.user));
    loginOpen.value = false;
    loginDraft.password = "";
    window.location.reload();
  } catch (error) {
    setNotice(formatApiError(error, t("notices.loginFailed")), "error");
  }
}

function logout() {
  window.localStorage.removeItem("token");
  window.localStorage.removeItem("portal-user");
  window.localStorage.removeItem("jd-staff-token");
  window.location.reload();
}

async function submitServiceLog() {
  serviceLogDraft.customer = serviceLogDraft.customer_company;
  serviceLogDraft.faulty_component = serviceLogDraft.fault_component;
  serviceLogDraft.project_name = serviceLogDraft.project_name.trim();
  if (
    !serviceLogDraft.project_name ||
    !serviceLogDraft.fault_component ||
    !serviceLogDraft.created_by
  ) {
    setNotice(t("notices.requiredLog"), "error");
    return;
  }
  try {
    if (serviceLogEditingId.value) {
      await portalApi.updateAfterSalesLog(serviceLogEditingId.value, {
        ...serviceLogDraft,
      });
    } else {
      await portalApi.createAfterSalesLog({ ...serviceLogDraft });
    }
    serviceLogFormOpen.value = false;
    serviceLogEditingId.value = null;
    await loadPortalExtras();
    setNotice(t("notices.logSaved"), "success");
  } catch (error) {
    setNotice(formatApiError(error, t("notices.logSaveFailed")), "error");
  }
}

function editServiceLog(item) {
  serviceLogEditingId.value = item.id;
  Object.assign(serviceLogDraft, {
    event_date: item.event_date || "",
    country: item.country || "",
    customer: item.customer || "",
    customer_company: item.customer_company || item.customer || "",
    project_name: item.project_name || "",
    product_model: item.product_model || "418",
    support_type: item.support_type || "远程 (Remote)",
    issue_category: item.issue_category || "软件 (Software)",
    fault_component: item.fault_component || item.faulty_component || "",
    faulty_component: item.fault_component || item.faulty_component || "",
    fault_description: item.fault_description || "",
    onsite_solution: item.onsite_solution || "",
    serial_number: item.serial_number || "",
    rd_contact: item.rd_contact || "",
    status: item.status || "处理中 (Pending)",
    pending_reason: item.pending_reason || "",
    created_by: item.created_by || "",
    attachments: [...(item.attachments || [])],
  });
  serviceLogFormOpen.value = true;
}

async function handlePortalAttachments(event, target) {
  for (const file of [...(event.target.files || [])]) {
    const result = await portalApi.uploadImage(file);
    if (target === "ticket") ticketDraft.attachments.push(result.url);
    if (target === "log") serviceLogDraft.attachments.push(result.url);
  }
  event.target.value = "";
}

async function downloadServiceLogs() {
  const response = await fetch(portalApi.exportAfterSalesLogs(), {
    headers: {
      Authorization: `Bearer ${window.localStorage.getItem("token")}`,
    },
  });
  if (!response.ok) {
    setNotice(t("notices.exportFailed"), "error");
    return;
  }
  const blob = await response.blob();
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "after-sales-logs.csv";
  link.click();
  URL.revokeObjectURL(link.href);
}

async function handleFaultSearch() {
  faultPage.value = 1;
  await loadAfterSalesFaultCodes();
}

async function loadAfterSalesFaultCodes() {
  faultLoading.value = true;
  faultError.value = "";
  faultHasSearched.value = true;
  try {
    const payload = await portalApi.listAfterSalesFaultCodes({
      page: faultPage.value,
      pageSize: faultPageSize.value,
      module: faultModule.value,
      keyword: faultKeyword.value.trim(),
    });
    faultResults.value = payload.items ?? [];
    faultTotal.value = Number(payload.total) || faultResults.value.length;
    const moduleSet = new Set(faultModules.value);
    for (const item of faultResults.value) {
      if (item?.module) {
        moduleSet.add(item.module);
      }
    }
    faultModules.value = [...moduleSet];
  } catch (error) {
    faultError.value = formatApiError(
      error,
      `${t("notices.loadFailed")} / API request failed`,
    );
    faultResults.value = [];
    faultTotal.value = 0;
  } finally {
    faultLoading.value = false;
  }
}

async function handleFaultFilterChange() {
  faultPage.value = 1;
  await loadAfterSalesFaultCodes();
}

async function handleFaultPageSizeChange() {
  faultPage.value = 1;
  await loadAfterSalesFaultCodes();
}

async function goFaultPage(nextPage) {
  const page = Number(nextPage) || 1;
  if (page < 1 || page > faultTotalPages.value || page === faultPage.value) {
    return;
  }
  faultPage.value = page;
  await loadAfterSalesFaultCodes();
}

async function loadLedgerData() {
  ledgerLoading.value = true;
  try {
    const [gridPayload, ciPayload] = await Promise.all([
      isCustomer.value
        ? portalApi.listPortalProjects()
        : portalApi.listGridProjects(),
      isCustomer.value
        ? portalApi.listPortalCiDeliveries()
        : portalApi.listCiDeliveries(),
    ]);
    gridProjects.value = gridPayload.items ?? [];
    ciDeliveries.value = ciPayload.items ?? [];
    const batchEntries = await Promise.all(
      ciDeliveries.value.filter((item) => item.id != null).map(async (item) => [item.id, (await portalApi.listCiDeliveryBatches(item.id)).items ?? []]),
    );
    ciBatchesByDealer.value = Object.fromEntries(batchEntries);
    for (const project of gridProjects.value) {
      projectDraftStatus[project.project_name] = project.progress_status;
    }
  } catch (error) {
    setNotice(
      formatApiError(error, `${t("notices.loadFailed")} / Ledger load failed`),
      "error",
    );
  } finally {
    ledgerLoading.value = false;
  }
}

async function loadCiDeliveryBatches(dealerId) {
  const payload = await portalApi.listCiDeliveryBatches(dealerId);
  ciBatchesByDealer.value = { ...ciBatchesByDealer.value, [dealerId]: payload.items ?? [] };
}

function exportCiDeliveryDetails() {
  const headers = [
    "国家/地区",
    "客户/代理商名称",
    "产品型号",
    "交付台数",
    "交付容量 (MWh)",
    "交付时间",
    "设备序列号",
  ];
  const rows = [];
  for (const dealer of ciDeliveries.value) {
    const batches = ciBatchesByDealer.value[dealer.id] || [];
    const customerName = dealer.customer_company || dealer.dealer_name || "";
    if (batches.length === 0) {
      rows.push([dealer.region || "", customerName, "", "", "", "", ""]);
      continue;
    }
    for (const batch of batches) {
      const quantity = Number(batch.quantity) || 0;
      const unitCapacity = batch.product_type === "100C" ? CI_100C_MWH_PER_UNIT : CI_250_MWH_PER_UNIT;
      rows.push([
        dealer.region || "",
        customerName,
        batch.product_type || "",
        quantity,
        (quantity * unitCapacity).toFixed(2),
        batch.delivery_date || "",
        batch.serial_numbers || "",
      ]);
    }
  }
  const escapeCsv = (value) => {
    const text = String(value ?? "");
    return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  };
  const csv = `\uFEFF${[headers, ...rows].map((row) => row.map(escapeCsv).join(",")).join("\r\n")}`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const dateStamp = new Date().toISOString().slice(0, 10).replaceAll("-", "");
  link.href = url;
  link.download = `工商业交付明细_${dateStamp}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

async function toggleCiDeliveryBatches(item) {
  if (ciExpandedDealerId.value === item.id) {
    ciExpandedDealerId.value = null;
    return;
  }
  ciExpandedDealerId.value = item.id;
  await loadCiDeliveryBatches(item.id);
}

function openBatchDeliveryModal(dealer, productType = "100C", batch = null) {
  batchDeliveryModal.open = true;
  batchDeliveryModal.mode = batch ? "edit" : "create";
  batchDeliveryModal.dealerId = dealer.id;
  batchDeliveryModal.dealerName = dealer.dealer_name;
  batchDeliveryModal.batchId = batch?.id ?? null;
  Object.assign(batchDeliveryDraft, {
    product_type: batch?.product_type || productType,
    quantity: batch?.quantity || 1,
    delivery_date: batch?.delivery_date || new Date().toISOString().slice(0, 10),
    serial_numbers: batch?.serial_numbers || "",
  });
}

function closeBatchDeliveryModal() {
  batchDeliveryModal.open = false;
  batchDeliveryModal.batchId = null;
}

async function saveBatchDelivery() {
  const quantity = Number(batchDeliveryDraft.quantity);
  if (!quantity || quantity <= 0 || !batchDeliveryDraft.delivery_date) {
    setNotice("请输入大于 0 的交付台数和交付日期。", "error");
    return;
  }
  const payload = { ...batchDeliveryDraft, quantity };
  if (batchDeliveryModal.mode === "edit") {
    await portalApi.updateCiDeliveryBatch(batchDeliveryModal.batchId, payload);
  } else {
    await portalApi.createCiDeliveryBatch(batchDeliveryModal.dealerId, payload);
  }
  await loadCiDeliveryBatches(batchDeliveryModal.dealerId);
  closeBatchDeliveryModal();
  setNotice(t("notices.ciSaved"), "success");
}

async function loadWarehouseData() {
  warehouseLoading.value = true;
  warehouseError.value = "";
  try {
    const payload = await portalApi.getWarehouseSummary(
      selectedWarehouse.value,
    );
    warehouseSummary.value = payload;
    if (!warehouseForm.tx_no) {
      prefillWarehouseTxNo();
    }
    if (!warehouseProductOptions.value.includes(warehouseForm.product_model)) {
      warehouseForm.product_model = warehouseProductOptions.value[0] ?? "100C";
    }
  } catch (error) {
    warehouseError.value = formatApiError(
      error,
      `${t("notices.loadFailed")} / Warehouse load failed`,
    );
  } finally {
    warehouseLoading.value = false;
  }
}

async function loadWarehouseInventory() {
  inventoryLoading.value = true;
  inventoryError.value = "";
  try {
    const payload = await portalApi.listWarehouseInventory();
    inventoryItems.value = payload.items ?? [];
  } catch (error) {
    inventoryError.value = formatApiError(
      error,
      `${t("notices.loadFailed")} / Inventory load failed`,
    );
  } finally {
    inventoryLoading.value = false;
  }
}

async function saveProjectStatus(projectName) {
  if (!ensureInternalMode()) return;
  const nextStatus = projectDraftStatus[projectName];
  if (!nextStatus) return;
  await portalApi.updateGridProjectStatus(projectName, nextStatus);
  await loadLedgerData();
  setNotice(t("notices.gridSaved"), "success");
}

function openProjectEditor(record = null) {
  openCrudModal("grid", record ? "edit" : "create", record);
}

function openCiEditor(record = null) {
  openCrudModal("ci", record ? "edit" : "create", record);
}

function openFaultEditor(record = null) {
  openCrudModal("fault", record ? "edit" : "create", record);
}

function openWarehouseEditor(record = null) {
  openCrudModal("warehouse", record ? "edit" : "create", record);
}

function openInventoryEditor(record = null) {
  openCrudModal("inventory", record ? "edit" : "create", record);
}

async function submitCrud() {
  if (!crudModal.kind) return;
  if (crudModal.kind === "technical-doc") {
    if (!materialsCanManage.value) {
      setNotice(
        isEnglish.value
          ? "No permission to modify materials."
          : "当前无资料管理权限。",
        "error",
      );
      return;
    }
  } else if (!ensureInternalMode()) {
    return;
  }
  if (crudModal.kind === "technical-doc") {
    const payload = {
      product_series: crudDraft.product_series,
      category: crudDraft.category,
      title: crudDraft.title.trim(),
    };

    if (!payload.title) {
      setNotice(
        isEnglish.value ? "Title is required." : "标题不能为空。",
        "error",
      );
      return;
    }

    if (crudModal.mode === "create") {
      if (!crudDraft.technical_doc_file) {
        setNotice(
          isEnglish.value
            ? "Please choose a file first."
            : "请先选择上传文件。",
          "error",
        );
        return;
      }
      const formData = new FormData();
      formData.append("product_series", payload.product_series);
      formData.append("category", payload.category);
      formData.append("title", payload.title);
      formData.append("file", crudDraft.technical_doc_file);
      await portalApi.uploadTechnicalDoc(formData);
    } else {
      await portalApi.updateTechnicalDoc(crudModal.originalKey, payload);
    }

    await loadTechnicalDocs();
    setNotice(t("materials.savedNotice"), "success");
  }

  if (crudModal.kind === "fault") {
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
    };

    if (!payload.module || !payload.fault_code) {
      setNotice(
        isEnglish.value
          ? "Module and fault code are required."
          : "模块和故障码不能为空。",
        "error",
      );
      return;
    }

    if (crudModal.mode === "create") {
      await portalApi.createAfterSalesFaultCode(payload);
    } else {
      await portalApi.updateAfterSalesFaultCode(crudModal.originalKey, payload);
    }
    await handleFaultSearch();
    setNotice(t("notices.faultCreated"), "success");
  }

  if (crudModal.kind === "grid") {
    const payload = {
      project_name: crudDraft.project_name.trim(),
      cod: crudDraft.cod.trim(),
      capacity_mwh: Number(crudDraft.capacity_mwh) || 0,
      software_version: crudDraft.software_version.trim(),
      progress_status: crudDraft.progress_status,
      photo_paths: [...crudDraft.photo_paths],
      customer_company: crudDraft.customer_company.trim(),
      partner_name: crudDraft.customer_company.trim(),
    };
    if (!payload.project_name) {
      setNotice(isEnglish.value ? "Project name is required." : "项目名称不能为空。", "error");
      return;
    }
    if (crudModal.mode === "create") {
      await portalApi.createGridProject(payload);
    } else {
      await portalApi.updateGridProject(crudModal.originalKey, payload);
    }
    await loadLedgerData();
    setNotice(t("notices.gridSaved"), "success");
  }

  if (crudModal.kind === "ci") {
    const payload = {
      dealer_name: crudDraft.dealer_name.trim(),
      region: crudDraft.region.trim(),
    };
    if (crudModal.mode === "create") {
      await portalApi.createCiDelivery(payload);
    } else {
      await portalApi.updateCiDelivery(crudModal.originalKey, payload);
    }
    await loadLedgerData();
    setNotice(t("notices.ciSaved"), "success");
  }

  if (crudModal.kind === "warehouse") {
    const payload = {
      warehouse_name: crudDraft.warehouse_name,
      tx_type: crudDraft.tx_type,
      product_model: crudDraft.product_model,
      quantity: Number(crudDraft.quantity) || 0,
      related_project: crudDraft.related_project.trim(),
      tx_no:
        crudDraft.tx_no.trim() ||
        `WH-${crudDraft.warehouse_name.toUpperCase()}-${currentTimestampStamp()}`,
    };
    if (crudModal.mode === "create") {
      await portalApi.createWarehouseTransaction(payload);
    } else {
      await portalApi.updateWarehouseTransaction(
        crudModal.originalKey,
        payload,
      );
    }
    selectedWarehouse.value = payload.warehouse_name;
    await loadWarehouseData();
    setNotice(t("notices.txSaved"), "success");
  }

  if (crudModal.kind === "inventory") {
    const payload = {
      item_no: crudDraft.item_no.trim(),
      description_zh: crudDraft.description_zh.trim(),
      specification: crudDraft.specification.trim(),
      total_quantity: Number(crudDraft.total_quantity) || 0,
      damaged_quantity: Number(crudDraft.damaged_quantity) || 0,
      available_quantity:
        Number(crudDraft.available_quantity) ||
        Math.max(
          Number(crudDraft.total_quantity) - Number(crudDraft.damaged_quantity),
          0,
        ),
      photo_paths: [...crudDraft.photo_paths],
      remarks: crudDraft.remarks.trim(),
    };
    if (crudModal.mode === "create") {
      await portalApi.createWarehouseInventoryItem(payload);
    } else {
      await portalApi.updateWarehouseInventoryItem(
        crudModal.originalKey,
        payload,
      );
    }
    await loadWarehouseInventory();
    setNotice(t("notices.inventorySaved"), "success");
  }

  closeCrudModal();
}

async function confirmDelete() {
  const { kind, key } = deleteDialog;
  if (!kind || !key) return;
  if (kind === "technical-doc") {
    if (!materialsCanManage.value) {
      setNotice(
        isEnglish.value
          ? "No permission to modify materials."
          : "当前无资料管理权限。",
        "error",
      );
      return;
    }
  } else if (!ensureInternalMode()) {
    return;
  }
  if (kind === "service-log") {
    await portalApi.deleteAfterSalesLog(key);
    await loadPortalExtras();
  }
  if (kind === "fault") {
    await portalApi.deleteAfterSalesFaultCode(key);
    await handleFaultSearch();
  }
  if (kind === "grid") {
    await portalApi.deleteGridProject(key);
    await loadLedgerData();
  }
  if (kind === "ci") {
    await portalApi.deleteCiDelivery(key);
    await loadLedgerData();
  }
  if (kind === "ci-batch") {
    const [dealerId, batchId] = String(key).split(":");
    await portalApi.deleteCiDeliveryBatch(batchId);
    await loadCiDeliveryBatches(dealerId);
  }
  if (kind === "warehouse") {
    await portalApi.deleteWarehouseTransaction(key);
    await loadWarehouseData();
  }
  if (kind === "inventory") {
    await portalApi.deleteWarehouseInventoryItem(key);
    await loadWarehouseInventory();
  }
  if (kind === "technical-doc") {
    await portalApi.deleteTechnicalDoc(key);
    await loadTechnicalDocs();
  }
  if (kind === "logistics") {
    await portalApi.deleteLogisticsShipment(key);
    await loadLogisticsShipments();
  }
  if (kind === "empowerment") {
    await portalApi.deleteEmpowermentRecord(key);
    await loadEmpowermentRecords();
  }
  if (kind === "fault-component") {
    await portalApi.deleteFaultComponent(key);
    await fetchFaultComponents();
    setNotice(t("settings.deleted"), "success");
    closeDeleteDialog();
    return;
  }
  if (kind === "logistics-status") {
    await portalApi.deleteLogisticsStatus(key);
    await fetchLogisticsStatuses();
    setNotice(t("settings.logisticsDeleted"), "success");
    closeDeleteDialog();
    return;
  }
  if (kind === "empowerment-skill") {
    await portalApi.deleteEmpowermentSkill(key);
    await fetchEmpowermentSkills();
    setNotice(t("settings.empowermentSkillDeleted"), "success");
    closeDeleteDialog();
    return;
  }
  setNotice(t("notices.deleted"), "success");
  closeDeleteDialog();
}

async function applyProjectStatus(projectName) {
  await saveProjectStatus(projectName);
}

async function submitWarehouseTransaction() {
  if (!ensureInternalMode()) return;
  if (!warehouseForm.tx_no) {
    prefillWarehouseTxNo();
  }
  await portalApi.createWarehouseTransaction({
    warehouse_name: selectedWarehouse.value,
    tx_type: warehouseForm.tx_type,
    product_model: warehouseForm.product_model,
    quantity: Number(warehouseForm.quantity) || 0,
    related_project: warehouseForm.related_project,
    tx_no: warehouseForm.tx_no,
  });
  warehouseForm.quantity = 1;
  warehouseForm.related_project = "";
  prefillWarehouseTxNo();
  await loadWarehouseData();
  setNotice(t("notices.txSaved"), "success");
}

watch(selectedWarehouse, async () => {
  await loadWarehouseData();
});

watch(
  () => ({ ...logisticsFilters }),
  async () => {
    await loadLogisticsShipments();
  },
  { deep: true },
);

watch(isInternalMode, (enabled) => {
  if (enabled) return;
  closeCrudModal();
  closeDeleteDialog();
});

onMounted(async () => {
  if (typeof document !== "undefined") {
    document.documentElement.classList.add("light");
    document.documentElement.setAttribute("data-theme", "light");
  }
  todayTick.value = Date.now();
  const timerId = window.setInterval(() => {
    todayTick.value = Date.now();
  }, 60000);
  gridDashboardTimerId = timerId;
  prefillWarehouseTxNo();
  await Promise.all([
    handleFaultSearch(),
    loadLedgerData(),
    loadWarehouseData(),
    loadWarehouseInventory(),
    loadTechnicalDocs(),
    loadPortalExtras(),
    fetchUsers(),
    fetchFaultComponents(),
    fetchLogisticsStatuses(),
    fetchEmpowermentSkills(),
    loadLogisticsShipments(),
    loadEmpowermentRecords(),
  ]);
});

onUnmounted(() => {
  if (gridDashboardTimerId !== null) {
    window.clearInterval(gridDashboardTimerId);
    gridDashboardTimerId = null;
  }
});
</script>
