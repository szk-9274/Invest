/**
 * Home Page
 *
 * Main page with backtest form and top/bottom ticker lists.
 */
import React, { useEffect, useState } from 'react'
import { BacktestForm } from '../components/BacktestForm'
import { TickerList, TickerItem } from '../components/TickerList'
import { runBacktest, getTopBottomTickers } from '../api/client'

interface HomeProps {
  onNavigateToChart?: (ticker: string) => void
}

export function Home({ onNavigateToChart }: HomeProps) {
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

  return (
    <div data-testid="home-page">
      <h1>Invest Backtest</h1>

      <section>
        <h2>Run Backtest</h2>
        <BacktestForm onSubmit={handleBacktest} isLoading={isLoading} />
        {message && <p data-testid="status-message">{message}</p>}
      </section>

      <section>
        <TickerList
          title="Top 5 Winners"
          tickers={topTickers}
          onTickerClick={onNavigateToChart}
          variant="winners"
        />
        <TickerList
          title="Bottom 5 Losers"
          tickers={bottomTickers}
          onTickerClick={onNavigateToChart}
          variant="losers"
        />
      </section>
    </div>
  )
}
