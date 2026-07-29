<template>
  <div class="min-h-screen bg-hero-grid text-slate-100">
    <main class="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-4 sm:px-6 lg:px-8">
      <header class="mb-4 flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-4 shadow-glow backdrop-blur-xl sm:p-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-[11px] font-semibold tracking-[0.24em] text-cyan-200 uppercase">
            Overseas Engineering Delivery Portal
          </p>
          <h1 class="mt-3 text-2xl font-semibold text-white sm:text-3xl">
            JD Energy 海外工程部综合交付与服务门户
          </h1>
          <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300 sm:text-base">
            售后服务、源网侧大储成果展、工商业交付看板、海外仓储管理统一入口。保持同一套深色科技感界面，面向本地 SQLite 持久化与后续服务器部署。
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
            class="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm font-semibold text-emerald-200 transition hover:bg-emerald-400/15 hover:text-emerald-100"
            @click="toggleStaffMode"
          >
            {{ staffMode ? '已进入内部员工模式' : '切换至内部员工模式' }}
          </button>
        </div>
      </header>

      <section v-if="activeView === 'after-sales'" class="flex-1">
        <div class="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-start">
          <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-xl sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">After-sales Service</p>
            <h2 class="mt-3 text-2xl font-semibold text-white sm:text-3xl">售后故障代码速查 / Fault Code Lookup</h2>
            <p class="mt-3 text-sm leading-7 text-slate-300 sm:text-base">
              输入故障代码、故障名称或关键词，快速定位可能原因与标准化解决方案。
            </p>

            <form class="mt-6 flex flex-col gap-3 sm:flex-row" @submit.prevent="handleFaultSearch">
              <label class="sr-only" for="fault-search">故障代码或关键词</label>
              <input
                id="fault-search"
                v-model="faultKeyword"
                type="text"
                class="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-5 py-4 text-base text-white placeholder:text-slate-500 outline-none transition focus:border-cyan-400/60 focus:shadow-[0_0_0_4px_rgba(34,211,238,0.12)]"
                placeholder="请输入故障代码 / Enter fault code e.g. E024"
              />
              <button type="submit" class="rounded-2xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-4 text-base font-semibold text-slate-950 transition hover:brightness-110">
                搜索 / Search
              </button>
            </form>

            <div class="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">支持模糊搜索</span>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">Fault Code / Keyword Search</span>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1">Mobile Friendly</span>
            </div>
          </div>

          <aside class="grid gap-4 rounded-3xl border border-white/10 bg-slate-950/55 p-5">
            <div>
              <p class="text-xs uppercase tracking-[0.24em] text-cyan-200">Quick Guide</p>
              <p class="mt-2 text-sm leading-6 text-slate-300">1. 输入代码或关键词 2. 前端请求后端 API 3. 返回故障名称、可能原因和标准化解决方案。</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
              当前结果：<span class="font-semibold text-white">{{ faultResults.length }}</span>
            </div>
          </aside>
        </div>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-white sm:text-2xl">查询结果 / Search Results</h3>
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
            <div class="mt-5 space-y-4 text-sm leading-6 text-slate-300">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Possible Causes / 可能原因（排查步骤）</p>
                <p class="mt-2 whitespace-pre-line">{{ item.possible_causes }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Standard Solution / 标准化解决方案</p>
                <p class="mt-2 whitespace-pre-line">{{ item.solution }}</p>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-4 rounded-3xl border border-dashed border-white/15 bg-white/5 p-10 text-center text-slate-300">
          <p class="text-lg font-medium text-white">未找到匹配结果 / No matches found</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">
            请尝试输入更准确的故障代码，例如 E024，或换成中文/英文关键词如“过温”“通信断开”“inverter fault”。
          </p>
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
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">源网侧储能项目成果展</h2>
            <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">展示大储项目关键里程碑、当前状态与项目照片墙。员工模式下可直接在前端模拟更新项目进度状态。</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
            项目总数：<span class="font-semibold text-white">{{ gridProjects.length }}</span>
          </div>
        </div>

        <div v-if="ledgerLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="index in 3" :key="index" class="h-72 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article v-for="project in gridProjects" :key="project.project_name" class="rounded-3xl border border-white/10 bg-white/5 p-5 transition hover:border-cyan-400/30">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-medium text-cyan-200">{{ project.project_name }}</p>
                <h3 class="mt-1 text-lg font-semibold text-white">COD {{ project.cod }}</h3>
              </div>
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusClass(project.progress_status)">{{ project.progress_status }}</span>
            </div>

            <div class="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
              <div class="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                <p class="text-slate-500">容量 Capacity</p>
                <p class="mt-1 font-semibold text-white">{{ project.capacity_mwh }} MWh</p>
              </div>
              <div class="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                <p class="text-slate-500">PCS</p>
                <p class="mt-1 font-semibold text-white">{{ project.pcs_model }}</p>
              </div>
              <div class="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                <p class="text-slate-500">电芯版本</p>
                <p class="mt-1 font-semibold text-white">{{ project.cell_version }}</p>
              </div>
              <div class="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                <p class="text-slate-500">COD</p>
                <p class="mt-1 font-semibold text-white">{{ project.cod }}</p>
              </div>
            </div>

            <div class="mt-4 rounded-2xl border border-white/10 bg-white/5 p-3">
              <div class="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-500">
                <span>Photo Wall / 照片墙</span>
                <span>{{ project.photo_paths.length }} pics</span>
              </div>
              <div class="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4 xl:grid-cols-2 2xl:grid-cols-4">
                <div v-for="photo in project.photo_paths" :key="photo" class="aspect-square overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-400/15 to-emerald-400/10 p-2">
                  <div class="flex h-full w-full items-center justify-center rounded-xl border border-dashed border-white/10 text-center text-[11px] leading-4 text-slate-300">
                    {{ photo }}
                  </div>
                </div>
              </div>
            </div>

            <div v-if="staffMode" class="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4">
              <p class="text-sm font-semibold text-cyan-100">录入 / 更新项目进度</p>
              <div class="mt-3 flex flex-col gap-3 sm:flex-row">
                <select v-model="projectDraftStatus[project.project_name]" class="w-full rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-white outline-none">
                  <option v-for="status in projectStatuses" :key="status" :value="status">{{ status }}</option>
                </select>
                <button type="button" class="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:brightness-110" @click="applyProjectStatus(project.project_name)">
                  保存更新
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section v-else-if="activeView === 'ci-dashboard'" class="flex-1">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">C&I Delivery Dashboard</p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">工商业交付看板</h2>
            <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">统计代理商与国家/区域的 100C、250 已交付数量。员工模式下可模拟更新交付数量并即时反映在看板中。</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
            代理商数：<span class="font-semibold text-white">{{ ciDeliveries.length }}</span>
          </div>
        </div>

        <div class="overflow-hidden rounded-3xl border border-white/10 bg-white/5">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-white/10 text-left text-sm">
              <thead class="bg-slate-950/50 text-slate-400">
                <tr>
                  <th class="px-5 py-4 font-medium">国家/区域</th>
                  <th class="px-5 py-4 font-medium">代理商名称</th>
                  <th class="px-5 py-4 font-medium">100C 已交付</th>
                  <th class="px-5 py-4 font-medium">250 已交付</th>
                  <th class="px-5 py-4 font-medium">合计</th>
                  <th v-if="staffMode" class="px-5 py-4 font-medium">操作</th>
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
                    <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="openCiEditor(item)">
                      更新代理商交付数量
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="staffMode && ciEditor" class="mt-5 rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-5">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-sm font-semibold text-emerald-100">更新代理商交付数量</p>
              <p class="text-sm text-emerald-50/80">{{ ciEditor.dealer_name }} / {{ ciEditor.region }}</p>
            </div>
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white transition hover:bg-white/10" @click="ciEditor = null">
              关闭
            </button>
          </div>

          <div class="mt-4 grid gap-3 md:grid-cols-3">
            <label class="block">
              <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100/80">100C</span>
              <input v-model.number="ciEditorDraft.delivered_100c" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
            </label>
            <label class="block">
              <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100/80">250</span>
              <input v-model.number="ciEditorDraft.delivered_250" type="number" min="0" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
            </label>
            <div class="flex items-end">
              <button type="button" class="w-full rounded-2xl bg-emerald-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110" @click="saveCiUpdate">
                保存更新
              </button>
            </div>
          </div>
        </div>
      </section>

      <section v-else class="flex-1">
        <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Warehouse & Inventory</p>
            <h2 class="mt-2 text-2xl font-semibold text-white sm:text-3xl">海外仓储管理</h2>
            <p class="mt-2 max-w-4xl text-sm leading-6 text-slate-300">切换欧洲仓或北美仓，查看 100C、250 及核心配件库存。员工模式下可录入出入库流水并同步到后端 SQLite。</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
            当前仓库：<span class="font-semibold text-white">{{ selectedWarehouseLabel }}</span>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <button
            v-for="warehouse in warehouseOptions"
            :key="warehouse.key"
            type="button"
            class="rounded-2xl border px-4 py-3 text-sm font-semibold transition"
            :class="selectedWarehouse === warehouse.key ? 'border-cyan-400/40 bg-cyan-400/15 text-cyan-100' : 'border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'"
            @click="selectedWarehouse = warehouse.key"
          >
            {{ warehouse.label }}
          </button>
        </div>

        <div v-if="warehouseLoading" class="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <div v-for="index in 5" :key="index" class="h-32 animate-pulse rounded-3xl border border-white/10 bg-white/5"></div>
        </div>

        <div v-else class="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <article v-for="item in warehouseTopCards" :key="item.key" class="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p class="text-sm text-slate-400">{{ item.label }}</p>
            <p class="mt-2 text-3xl font-semibold text-white">{{ item.quantity }}</p>
            <p class="mt-2 text-xs uppercase tracking-[0.2em] text-cyan-200">{{ item.note }}</p>
          </article>
        </div>

        <div v-if="warehouseError" class="mt-5 rounded-3xl border border-rose-400/20 bg-rose-500/10 p-5 text-rose-100">
          {{ warehouseError }}
        </div>

        <div class="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <section class="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div class="flex items-end justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Inventory Board</p>
                <h3 class="mt-2 text-xl font-semibold text-white">实时库存看板</h3>
              </div>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{{ warehouseSummary.inventory?.length || 0 }} SKUs</span>
            </div>

            <div class="mt-4 grid gap-4 md:grid-cols-2">
              <article v-for="item in warehouseSummary.inventory || []" :key="`${item.warehouse_name}-${item.product_model}`" class="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="text-sm font-semibold text-white">{{ item.product_name }}</p>
                    <p class="mt-1 text-xs text-slate-400">{{ item.category }} / {{ item.product_model }}</p>
                  </div>
                  <span class="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-200">{{ item.unit }}</span>
                </div>
                <p class="mt-4 text-3xl font-semibold text-white">{{ item.quantity }}</p>
              </article>
            </div>

            <div v-if="staffMode" class="mt-5 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4">
              <p class="text-sm font-semibold text-cyan-100">出入库动态流水录入</p>
              <div class="mt-4 grid gap-3 md:grid-cols-2">
                <label class="block">
                  <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100/80">类型</span>
                  <select v-model="warehouseForm.tx_type" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none">
                    <option value="国内到货入库">国内到货入库</option>
                    <option value="现场客诉领用出库">现场客诉领用出库</option>
                  </select>
                </label>
                <label class="block">
                  <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100/80">产品型号</span>
                  <select v-model="warehouseForm.product_model" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none">
                    <option v-for="item in warehouseProductOptions" :key="item" :value="item">{{ item }}</option>
                  </select>
                </label>
                <label class="block">
                  <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100/80">数量</span>
                  <input v-model.number="warehouseForm.quantity" type="number" min="1" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
                </label>
                <label class="block">
                  <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100/80">流水单号</span>
                  <input v-model="warehouseForm.tx_no" type="text" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" />
                </label>
                <label class="block md:col-span-2">
                  <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100/80">关联项目</span>
                  <input v-model="warehouseForm.related_project" type="text" class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none" placeholder="例如 418 项目" />
                </label>
              </div>
              <div class="mt-4 flex flex-wrap gap-3">
                <button type="button" class="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110" @click="submitWarehouseTransaction">
                  录入 / 保存流水
                </button>
                <button type="button" class="rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10" @click="prefillWarehouseTxNo">
                  生成流水单号
                </button>
              </div>
            </div>
          </section>

          <section class="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div class="flex items-end justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200">Transaction Feed</p>
                <h3 class="mt-2 text-xl font-semibold text-white">最新历史流水</h3>
              </div>
              <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">Recent 20</span>
            </div>

            <div class="mt-4 overflow-hidden rounded-2xl border border-white/10">
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-white/10 text-left text-sm">
                  <thead class="bg-slate-950/50 text-slate-400">
                    <tr>
                      <th class="px-4 py-3 font-medium">单号</th>
                      <th class="px-4 py-3 font-medium">类型</th>
                      <th class="px-4 py-3 font-medium">型号</th>
                      <th class="px-4 py-3 font-medium">数量</th>
                      <th class="px-4 py-3 font-medium">项目</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-white/10 text-slate-200">
                    <tr v-for="tx in warehouseSummary.transactions || []" :key="tx.tx_no" class="bg-white/[0.02] hover:bg-white/[0.04]">
                      <td class="px-4 py-3 whitespace-nowrap text-white">{{ tx.tx_no }}</td>
                      <td class="px-4 py-3">{{ tx.tx_type }}</td>
                      <td class="px-4 py-3">{{ tx.product_model }}</td>
                      <td class="px-4 py-3 font-semibold text-cyan-200">{{ tx.quantity }}</td>
                      <td class="px-4 py-3">{{ tx.related_project }}</td>
                    </tr>
                    <tr v-if="(warehouseSummary.transactions || []).length === 0">
                      <td colspan="5" class="px-4 py-10 text-center text-slate-400">暂无流水记录</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

const views = [
  { key: 'after-sales', label: '售后服务' },
  { key: 'grid-scale', label: '源网侧大储成果展' },
  { key: 'ci-dashboard', label: '工商业交付看板' },
  { key: 'warehouse', label: '海外仓储' },
]

const warehouseOptions = [
  { key: 'europe', label: '欧洲仓' },
  { key: 'north_america', label: '北美仓' },
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
  {
    title: '标准化开箱视频',
    subtitle: 'Standard Unboxing',
    duration: '06:28',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
  },
  {
    title: '线缆接线教学视频',
    subtitle: 'Cable Routing Tutorial',
    duration: '08:14',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
  },
  {
    title: 'BMS 软件配置视频',
    subtitle: 'BMS Software Setup',
    duration: '10:06',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
  },
]

const projectStatuses = ['清关中', '设备上岸', '土建施工', '调试中', '正式并网']

const activeView = ref('after-sales')
const staffMode = ref(false)

const faultKeyword = ref('')
const faultLoading = ref(false)
const faultError = ref('')
const faultResults = ref([])
const faultHasSearched = ref(false)

const ledgerLoading = ref(false)
const gridProjects = ref([])
const ciDeliveries = ref([])
const ciEditor = ref(null)
const ciEditorDraft = reactive({ region: '', delivered_100c: 0, delivered_250: 0 })
const projectDraftStatus = reactive({})

const selectedWarehouse = ref('europe')
const warehouseLoading = ref(false)
const warehouseError = ref('')
const warehouseSummary = ref({ warehouse_name: 'europe', inventory: [], grouped_inventory: {}, transactions: [] })
const warehouseForm = reactive({
  tx_type: '国内到货入库',
  product_model: '100C',
  quantity: 1,
  related_project: '',
  tx_no: '',
})

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

const faultHint = computed(() => {
  if (!faultHasSearched.value) {
    return '默认展示全部模拟故障库，输入关键字后即可快速筛选。'
  }
  return faultKeyword.value.trim() ? `当前搜索词：${faultKeyword.value.trim()}` : '显示全部结果。'
})

function makeTextDownload(content, filename) {
  return `data:text/plain;charset=utf-8,${encodeURIComponent(content)}#${encodeURIComponent(filename)}`
}

function prefillWarehouseTxNo() {
  const stamp = new Date()
    .toISOString()
    .replaceAll('-', '')
    .replaceAll(':', '')
    .replaceAll('T', '')
    .replaceAll('Z', '')
    .replaceAll('.', '')
    .slice(0, 14)
  warehouseForm.tx_no = `WH-${selectedWarehouse.value.toUpperCase()}-${stamp}`
}

function toggleStaffMode() {
  staffMode.value = !staffMode.value
  if (!staffMode.value) {
    ciEditor.value = null
  }
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

function openVideo(url) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

async function handleFaultSearch() {
  faultLoading.value = true
  faultError.value = ''
  faultHasSearched.value = true

  try {
    const response = await fetch(`/api/fault-codes?q=${encodeURIComponent(faultKeyword.value.trim())}`)
    if (!response.ok) {
      throw new Error(`请求失败，状态码 ${response.status}`)
    }
    const payload = await response.json()
    faultResults.value = payload.items ?? []
  } catch (error) {
    faultError.value = `接口请求失败 / API request failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    faultResults.value = []
  } finally {
    faultLoading.value = false
  }
}

async function loadLedgerData() {
  ledgerLoading.value = true
  try {
    const [gridResponse, ciResponse] = await Promise.all([
      fetch('/api/ledger/grid-scale'),
      fetch('/api/ledger/ci-deliveries'),
    ])
    const gridPayload = await gridResponse.json()
    const ciPayload = await ciResponse.json()
    gridProjects.value = gridPayload.items ?? []
    ciDeliveries.value = ciPayload.items ?? []

    for (const project of gridProjects.value) {
      projectDraftStatus[project.project_name] = project.progress_status
    }
  } catch (error) {
    faultError.value = `台账加载失败 / Ledger load failed: ${error instanceof Error ? error.message : 'Unknown error'}`
  } finally {
    ledgerLoading.value = false
  }
}

async function applyProjectStatus(projectName) {
  const nextStatus = projectDraftStatus[projectName]
  if (!nextStatus) return
  await fetch(`/api/ledger/grid-scale/${encodeURIComponent(projectName)}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ progress_status: nextStatus }),
  })
  await loadLedgerData()
}

function openCiEditor(item) {
  ciEditor.value = item.dealer_name
  ciEditorDraft.region = item.region
  ciEditorDraft.delivered_100c = item.delivered_100c
  ciEditorDraft.delivered_250 = item.delivered_250
}

async function saveCiUpdate() {
  if (!ciEditor.value) return
  await fetch(`/api/ledger/ci-deliveries/${encodeURIComponent(ciEditor.value)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      region: ciEditorDraft.region,
      delivered_100c: Number(ciEditorDraft.delivered_100c) || 0,
      delivered_250: Number(ciEditorDraft.delivered_250) || 0,
    }),
  })
  ciEditor.value = null
  await loadLedgerData()
}

async function loadWarehouseData() {
  warehouseLoading.value = true
  warehouseError.value = ''
  try {
    const response = await fetch(`/api/warehouse/summary?warehouse_name=${encodeURIComponent(selectedWarehouse.value)}`)
    if (!response.ok) {
      throw new Error(`请求失败，状态码 ${response.status}`)
    }
    warehouseSummary.value = await response.json()
    if (!warehouseForm.tx_no) {
      prefillWarehouseTxNo()
    }
    if (!warehouseProductOptions.value.includes(warehouseForm.product_model)) {
      warehouseForm.product_model = warehouseProductOptions.value[0] ?? '100C'
    }
  } catch (error) {
    warehouseError.value = `仓储数据加载失败 / Warehouse load failed: ${error instanceof Error ? error.message : 'Unknown error'}`
  } finally {
    warehouseLoading.value = false
  }
}

async function submitWarehouseTransaction() {
  if (!warehouseForm.tx_no) {
    prefillWarehouseTxNo()
  }
  await fetch('/api/warehouse/transactions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      warehouse_name: selectedWarehouse.value,
      tx_type: warehouseForm.tx_type,
      product_model: warehouseForm.product_model,
      quantity: Number(warehouseForm.quantity) || 0,
      related_project: warehouseForm.related_project,
      tx_no: warehouseForm.tx_no,
    }),
  })
  warehouseForm.quantity = 1
  warehouseForm.related_project = ''
  prefillWarehouseTxNo()
  await loadWarehouseData()
}

watch(selectedWarehouse, async () => {
  await loadWarehouseData()
})

onMounted(async () => {
  prefillWarehouseTxNo()
  await Promise.all([handleFaultSearch(), loadLedgerData(), loadWarehouseData()])
})
</script>