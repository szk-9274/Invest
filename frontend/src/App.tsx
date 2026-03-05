/**
 * Main App Component
 *
 * Routing between Home, Chart, and Backtest Dashboard pages.
 */
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { Home } from './pages/Home'
import { HomeLanding } from './pages/HomeLanding'
import { Chart } from './pages/Chart'
import { BacktestDashboard } from './pages/BacktestDashboard'
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
  return (
    <>
      <nav className="app-nav">
        <div className="nav-brand">
          <Link to="/">Stock Screening</Link>
        </div>
        <div className="nav-links">
          <Link to="/home" className="nav-link">Home</Link>
          <Link to="/" className="nav-link">Backtest</Link>
          <Link to="/dashboard" className="nav-link">Backtest Dashboard</Link>
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
  return (
    <BrowserRouter>
      <React.Suspense fallback={<div>Loading...</div>}>
        <AppContent />
      </React.Suspense>
    </BrowserRouter>
  )
}

export default App

