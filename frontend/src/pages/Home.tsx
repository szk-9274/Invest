/**
 * Home Page
 *
 * Main page with backtest form and top/bottom ticker lists.
 */
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BacktestForm } from '../components/BacktestForm'
import { TickerList, TickerItem } from '../components/TickerList'
import { runBacktest, getTopBottomTickers } from '../api/client'

interface HomeProps {
  onNavigateToChart?: (ticker: string) => void
}

export function Home({ onNavigateToChart }: HomeProps) {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [topTickers, setTopTickers] = useState<TickerItem[]>([])
  const [bottomTickers, setBottomTickers] = useState<TickerItem[]>([])

  useEffect(() => {
    loadTickers()
  }, [])

  const loadTickers = async () => {
    try {
      const data = await getTopBottomTickers()
      setTopTickers(data.top)
      setBottomTickers(data.bottom)
    } catch {
      // Silently handle - tickers will show empty state
    }
  }

  const handleBacktest = async (startDate: string, endDate: string) => {
    setIsLoading(true)
    setMessage('')
    try {
      const result = await runBacktest({ start_date: startDate, end_date: endDate })
      setMessage(result.message)
      await loadTickers()
    } catch (error) {
      setMessage('Backtest failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTickerClick = (ticker: string) => {
    // Support both old prop-based and new router-based navigation
    if (onNavigateToChart) {
      onNavigateToChart(ticker)
      return
    }
    navigate(`/chart/${ticker}`)
  }

  return (
    <div data-testid="home-page" className="mx-auto max-w-7xl px-4 pb-12 pt-8 md:px-6">
      <section className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-950 to-blue-950 p-8 shadow-glow md:p-12">
        <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl" />
        <div className="relative z-10 max-w-3xl">
          <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">
            Quant Backtesting Platform
          </p>
          <h1 className="text-3xl font-bold leading-tight text-white md:text-5xl">
            Invest Backtest Dashboard
          </h1>
          <p className="mt-4 text-base text-slate-300 md:text-lg">
            バックテスト結果、チャート検証、トレード分析を一つの画面で。画像チャートの拡大確認とダッシュボード運用をすぐ開始できます。
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="rounded-lg bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            >
              ダッシュボードを開く
            </button>
            <button
              onClick={() => window.scrollTo({ top: 680, behavior: 'smooth' })}
              className="rounded-lg border border-slate-700 bg-slate-900/70 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-500"
            >
              クイック実行へ
            </button>
          </div>
        </div>
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
          <p className="text-xs uppercase tracking-wide text-slate-400">Charts</p>
          <p className="mt-2 text-2xl font-bold text-white">Zoom Ready</p>
          <p className="mt-2 text-sm text-slate-400">拡大してエントリー/エグジット位置を詳細に確認</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
          <p className="text-xs uppercase tracking-wide text-slate-400">Backtests</p>
          <p className="mt-2 text-2xl font-bold text-white">Job Runner</p>
          <p className="mt-2 text-sm text-slate-400">実行ジョブの状態とログをリアルタイム表示</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
          <p className="text-xs uppercase tracking-wide text-slate-400">Analytics</p>
          <p className="mt-2 text-2xl font-bold text-white">Trade Insights</p>
          <p className="mt-2 text-sm text-slate-400">勝率・損益・トレード履歴を同時に分析</p>
        </div>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="mb-4 text-xl font-semibold text-white">Run Backtest</h2>
          <div className="rounded-lg bg-slate-950/70 p-4">
            <BacktestForm onSubmit={handleBacktest} isLoading={isLoading} />
          </div>
          {message && (
            <p data-testid="status-message" className="mt-3 rounded-md border border-sky-800 bg-sky-950/40 p-3 text-sm text-sky-200">
              {message}
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6">
          <h2 className="mb-4 text-xl font-semibold text-white">Top / Bottom Movers</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border border-emerald-900/50 bg-emerald-950/20 p-4">
              <TickerList
                title="Top 5 Winners"
                tickers={topTickers}
                onTickerClick={handleTickerClick}
                variant="winners"
              />
            </div>
            <div className="rounded-lg border border-rose-900/50 bg-rose-950/20 p-4">
              <TickerList
                title="Bottom 5 Losers"
                tickers={bottomTickers}
                onTickerClick={handleTickerClick}
                variant="losers"
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
