import { createI18n } from 'vue-i18n'
import ru from './locales/ru.json'
import en from './locales/en.json'
import ar from './locales/ar.json'

// Get saved language from localStorage or use browser language
const getSavedLanguage = () => {
  const saved = localStorage.getItem('gantt-language')
  if (saved && ['ru', 'en', 'ar'].includes(saved)) {
    return saved
  }
  // Try to detect from browser
  const browserLang = navigator.language.split('-')[0]
  if (['ru', 'en', 'ar'].includes(browserLang)) {
    return browserLang
  }
  return 'ru' // Default to Russian
}

const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: getSavedLanguage(),
  fallbackLocale: 'en',
  messages: {
    ru,
    en,
    ar
  }
})

// Helper to change language and save preference
export const setLanguage = (lang) => {
  i18n.global.locale.value = lang
  localStorage.setItem('gantt-language', lang)
  document.documentElement.lang = lang
}

// Initialize language on load
document.documentElement.lang = getSavedLanguage()

export default i18n

