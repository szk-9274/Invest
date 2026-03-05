/**
 * Home Page
 *
 * Main page with backtest form and top/bottom ticker lists.
 */
import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { BacktestForm } from '../components/BacktestForm'
import { TickerList, TickerItem } from '../components/TickerList'
import { runBacktest, getTopBottomTickers } from '../api/client'

interface HomeProps {
  onNavigateToChart?: (ticker: string) => void
}

export function Home({ onNavigateToChart }: HomeProps) {
  const { t } = useTranslation()
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
      setMessage(t('home.backtestFailed'))
    } finally {
      setIsLoading(false)
    }
  }

  const handleTickerClick = (ticker: string) => {
    // Support both old prop-based and new router-based navigation
    if (onNavigateToChart) {
      onNavigateToChart(ticker)
    }
  }

  return (
    <div data-testid="home-page">
      <h1>{t('home.title')}</h1>

      <section>
        <h2>{t('home.runBacktest')}</h2>
        <BacktestForm onSubmit={handleBacktest} isLoading={isLoading} />
        {message && <p data-testid="status-message">{message}</p>}
      </section>

      <section>
        <TickerList
          title={t('home.topWinners')}
          tickers={topTickers}
          onTickerClick={onNavigateToChart}
          variant="winners"
        />
        <TickerList
          title={t('home.bottomLosers')}
          tickers={bottomTickers}
          onTickerClick={onNavigateToChart}
          variant="losers"
        />
      </section>
    </div>
  )
}
