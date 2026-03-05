/**
 * Main App Component
 *
 * Routing between Home, Chart, and Backtest Dashboard pages.
 */
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Home } from './pages/Home'
import { HomeLanding } from './pages/HomeLanding'
import { Chart } from './pages/Chart'
import { BacktestDashboard } from './pages/BacktestDashboard'
import { AppLanguage, setAppLanguage } from './i18n'
import './App.css'

function ErrorFallback({ error }: { error: Error | null }) {
  if (!error) return null
  return (
    <div style={{ padding: 20, color: '#800' }}>
      <h3>Application Error</h3>
      <pre style={{ whiteSpace: 'pre-wrap', background: '#fff', padding: 10, borderRadius: 6 }}>{String(error && error.stack)}</pre>
    </div>
  )
}

function AppContent() {
  const { t, i18n } = useTranslation()
  const currentLanguage: AppLanguage = i18n.resolvedLanguage === 'ja' ? 'ja' : 'en'
  const handleLanguageChange = (language: AppLanguage) => {
    if (currentLanguage === language) return
    setAppLanguage(language)
  }

  return (
    <>
      <nav className="app-nav">
        <div className="nav-brand">
          <Link to="/">{t('nav.brand')}</Link>
        </div>
        <div className="nav-links">
          <Link to="/home" className="nav-link">{t('nav.home')}</Link>
          <Link to="/" className="nav-link">{t('nav.backtest')}</Link>
          <Link to="/dashboard" className="nav-link">{t('nav.dashboard')}</Link>
          <div className="lang-toggle" aria-label="language toggle">
            <button
              type="button"
              className={`lang-btn ${currentLanguage === 'en' ? 'active' : ''}`}
              onClick={() => handleLanguageChange('en')}
            >
              {t('nav.langEn')}
            </button>
            <button
              type="button"
              className={`lang-btn ${currentLanguage === 'ja' ? 'active' : ''}`}
              onClick={() => handleLanguageChange('ja')}
            >
              {t('nav.langJa')}
            </button>
          </div>
        </div>
      </nav>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<HomeLanding />} />
          <Route path="/chart/:ticker" element={<Chart />} />
          <Route path="/dashboard" element={<BacktestDashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}

function App() {
  const { t } = useTranslation()
  return (
    <BrowserRouter>
      <React.Suspense fallback={<div>{t('common.loading')}</div>}>
        <AppContent />
      </React.Suspense>
    </BrowserRouter>
  )
}

export default App

