/**
 * Main App Component
 *
 * Routing between Home, Chart, and Backtest Dashboard pages.
 */
import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Home } from './pages/Home'
import { HomeLanding } from './pages/HomeLanding'
import { Chart } from './pages/Chart'
import { BacktestDashboard } from './pages/BacktestDashboard'
import { BacktestRunPage } from './pages/BacktestRunPage'
import { BacktestAnalysisPage } from './pages/BacktestAnalysisPage'
import { TraderStrategiesPage } from './pages/TraderStrategiesPage'
import { AppLanguage, setAppLanguage } from './i18n'
import { AppChromeProvider, useAppChrome } from './contexts/AppChromeContext'
import './App.css'

function AppContent() {
  const { t, i18n } = useTranslation()
  const location = useLocation()
  const { chrome } = useAppChrome()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const currentLanguage: AppLanguage = i18n.resolvedLanguage === 'ja' ? 'ja' : 'en'
  const brandLabel = chrome.brandLabel ?? t('nav.brand')
  const brandLink = chrome.brandLabel ? chrome.brandLink : '/'
  const chromeState = chrome.statusLabel ?? null

  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [location.pathname, location.search])

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen((prev) => !prev)
  }

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  const handleLanguageChange = (language: AppLanguage) => {
    if (currentLanguage === language) return
    setAppLanguage(language)
  }

  return (
      <>
        <nav className="app-nav">
        <div className="nav-brand-group">
          <div className="nav-brand">
            <Link to={brandLink} onClick={closeMobileMenu}>{brandLabel}</Link>
          </div>
          {chromeState ? <span className="nav-status-chip">{chromeState}</span> : null}
          {chrome.onReload ? (
            <button
              type="button"
              className="nav-reload-button"
              aria-label={chrome.reloadLabel ?? t('dashboard.reloadLatestAria')}
              title={chrome.reloadLabel ?? t('dashboard.reloadLatestAria')}
              disabled={chrome.reloadDisabled}
              onClick={() => {
                void chrome.onReload?.()
                closeMobileMenu()
              }}
            >
              ↻
            </button>
          ) : null}
        </div>
        <button
          type="button"
          className={`menu-toggle ${isMobileMenuOpen ? 'active' : ''}`}
          aria-label={isMobileMenuOpen ? t('nav.closeMenu') : t('nav.openMenu')}
          aria-controls="app-nav-links"
          aria-expanded={isMobileMenuOpen}
          onClick={handleMobileMenuToggle}
        >
          {isMobileMenuOpen ? t('nav.close') : t('nav.menu')}
        </button>
        <div
          id="app-nav-links"
          data-testid="app-nav-links"
          className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}
        >
          <Link to="/home" className="nav-link" onClick={closeMobileMenu}>{t('nav.home')}</Link>
          <Link to="/dashboard" className="nav-link" onClick={closeMobileMenu}>{t('nav.dashboard')}</Link>
          <div className="lang-toggle" aria-label="language toggle">
            <button
              type="button"
              className={`lang-btn ${currentLanguage === 'en' ? 'active' : ''}`}
              onClick={() => {
                handleLanguageChange('en')
                closeMobileMenu()
              }}
            >
              {t('nav.langEn')}
            </button>
            <button
              type="button"
              className={`lang-btn ${currentLanguage === 'ja' ? 'active' : ''}`}
              onClick={() => {
                handleLanguageChange('ja')
                closeMobileMenu()
              }}
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
          <Route path="/dashboard" element={<BacktestDashboard />}>
            <Route index element={<Navigate to="run" replace />} />
            <Route path="run" element={<BacktestRunPage />} />
            <Route path="analysis" element={<BacktestAnalysisPage />} />
            <Route path="strategies" element={<TraderStrategiesPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}

function App() {
  const { t } = useTranslation()
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AppChromeProvider>
        <React.Suspense fallback={<div>{t('common.loading')}</div>}>
          <AppContent />
        </React.Suspense>
      </AppChromeProvider>
    </BrowserRouter>
  )
}

export default App

