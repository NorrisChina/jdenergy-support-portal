import { computed, reactive, ref, watch } from 'vue'
import { supportedLocales } from '../locales/messages'

const STORAGE_KEYS = {
  locale: 'jd-energy.locale',
}

const state = reactive({
  locale: loadStoredValue(STORAGE_KEYS.locale, 'zh-CN'),
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

function setLocale(locale) {
  if (!supportedLocales.includes(locale)) return
  state.locale = locale
}

function toggleLocale() {
  setLocale(state.locale === 'zh-CN' ? 'en-US' : 'zh-CN')
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
    setNotice,
    computed,
  }
}
