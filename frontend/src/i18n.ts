import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import ja from './locales/ja.json'

const LANG_STORAGE_KEY = 'app_lang'

export type AppLanguage = 'en' | 'ja'

function normalizeLanguage(value: string | null | undefined): AppLanguage | null {
  if (value === 'en' || value === 'ja') return value
  return null
}

function updateLangQuery(language: AppLanguage) {
  if (typeof window === 'undefined') return
  const url = new URL(window.location.href)
  url.searchParams.set('lang', language)
  window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`)
}

function detectInitialLanguage(): AppLanguage {
  if (typeof window === 'undefined') return 'en'

  const fromQuery = normalizeLanguage(new URLSearchParams(window.location.search).get('lang'))
  if (fromQuery) return fromQuery

  const fromStorage = normalizeLanguage(window.localStorage.getItem(LANG_STORAGE_KEY))
  if (fromStorage) return fromStorage

  return 'en'
}

export function setAppLanguage(language: AppLanguage) {
  void i18n.changeLanguage(language)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(LANG_STORAGE_KEY, language)
    updateLangQuery(language)
  }
}

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ja: { translation: ja },
  },
  lng: detectInitialLanguage(),
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
})

export default i18n
