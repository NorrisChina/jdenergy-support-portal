import { computed, reactive, ref, watch } from 'vue'
import { supportedLocales } from '../locales/messages'

const STORAGE_KEYS = {
  locale: 'jd-energy.locale',
  staffMode: 'jd-energy.staff-mode',
  internalMode: 'isInternalMode',
}

const STAFF_PASSWORD = 'Jdny!1234'

const state = reactive({
  locale: loadStoredValue(STORAGE_KEYS.locale, 'zh-CN'),
  staffMode: loadStoredValue(STORAGE_KEYS.internalMode, loadStoredValue(STORAGE_KEYS.staffMode, false)),
  staffAuthOpen: false,
  staffPassword: '',
  staffAuthError: '',
  notice: '',
  noticeType: 'info',
})

const noticeTimer = ref(null)

function loadStoredValue(key, fallback) {
  if (typeof window === 'undefined') {
    return fallback
  }
  const raw = window.localStorage.getItem(key)
  if (raw === null) {
    return fallback
  }
  if (raw === 'true') return true
  if (raw === 'false') return false
  if (supportedLocales.includes(raw)) return raw
  return raw || fallback
}

function persistValue(key, value) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(key, String(value))
}

watch(
  () => state.locale,
  (value) => persistValue(STORAGE_KEYS.locale, value),
)

watch(
  () => state.staffMode,
  (value) => {
    persistValue(STORAGE_KEYS.staffMode, value)
    persistValue(STORAGE_KEYS.internalMode, value)
  },
)

function setLocale(locale) {
  if (!supportedLocales.includes(locale)) return
  state.locale = locale
}

function toggleLocale() {
  setLocale(state.locale === 'zh-CN' ? 'en-US' : 'zh-CN')
}

function requestStaffMode() {
  if (state.staffMode) {
    state.staffMode = false
    setNotice('已退出内部员工模式', 'info')
    return
  }
  state.staffAuthOpen = true
  state.staffPassword = ''
  state.staffAuthError = ''
}

function cancelStaffAuth() {
  state.staffAuthOpen = false
  state.staffPassword = ''
  state.staffAuthError = ''
}

function confirmStaffAuth(successMessage, errorMessage) {
  if (state.staffPassword === STAFF_PASSWORD) {
    state.staffMode = true
    state.staffAuthOpen = false
    state.staffPassword = ''
    state.staffAuthError = ''
    setNotice(successMessage, 'success')
    return true
  }
  state.staffPassword = ''
  state.staffAuthError = errorMessage
  setNotice(errorMessage, 'error')
  return false
}

function leaveStaffMode(message) {
  state.staffMode = false
  setNotice(message, 'info')
}

function setNotice(message, type = 'info') {
  state.notice = message
  state.noticeType = type
  if (noticeTimer.value) {
    window.clearTimeout(noticeTimer.value)
  }
  noticeTimer.value = window.setTimeout(() => {
    state.notice = ''
    state.noticeType = 'info'
  }, 2800)
}

export function usePortalState() {
  return {
    state,
    setLocale,
    toggleLocale,
    requestStaffMode,
    cancelStaffAuth,
    confirmStaffAuth,
    leaveStaffMode,
    setNotice,
    computed,
  }
}
