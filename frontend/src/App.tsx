/**
 * Main App Component
 *
 * Routing between Home, Chart, and Backtest Dashboard pages.
 */
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { Home } from './pages/Home'
import { Chart } from './pages/Chart'
import { BacktestDashboard } from './pages/BacktestDashboard'

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
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <nav className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 md:px-6">
          <Link
            to="/"
            className="bg-gradient-to-r from-cyan-300 via-sky-400 to-indigo-400 bg-clip-text text-lg font-bold text-transparent"
          >
            Invest Platform
          </Link>
          <div className="flex items-center gap-2 md:gap-3">
            <Link
              to="/"
              className="rounded-md px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              Home
            </Link>
            <Link
              to="/dashboard"
              className="rounded-md bg-sky-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-sky-500"
            >
              Backtest Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <main className="min-h-[calc(100vh-4rem)]">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chart/:ticker" element={<Chart />} />
          <Route path="/dashboard" element={<BacktestDashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
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

