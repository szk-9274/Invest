import React from 'react'
import Plot from 'react-plotly.js'
import { CandlestickChart } from './CandlestickChart'
import { TradeRecord, TickerStats } from '../api/backtest'

interface PurchasePoint {
  timestamp: string
  price: number
  amount: number
}

export interface PurchaseChartItem {
  ticker: string
  totalPnl: number
  group: 'top' | 'bottom'
  purchases: PurchasePoint[]
}

interface TopBottomPurchaseChartsProps {
  trades: TradeRecord[]
  tickerStats: TickerStats[]
  loading?: boolean
  limit?: number
}

const MIN_MARKER_SIZE = 6
const MAX_MARKER_SIZE = 28

function toFiniteNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function toPurchasePoint(rawTrade: TradeRecord): PurchasePoint | null {
  const trade = rawTrade as TradeRecord & Record<string, unknown>
  const timestamp =
    typeof trade.entry_date === 'string'
      ? trade.entry_date
      : typeof trade.date === 'string'
        ? trade.date
        : null
  const price = toFiniteNumber(trade.entry_price ?? trade.price)
  const shares = toFiniteNumber(trade.shares) ?? 1

  if (!timestamp || price === null || shares <= 0) return null
  return {
    timestamp,
    price,
    amount: price * shares,
  }
}

export function calculateMarkerSize(amount: number, scale = 1): number {
  if (!Number.isFinite(amount) || amount <= 0) return MIN_MARKER_SIZE
  const raw = Math.sqrt(amount) * scale
  return Math.max(MIN_MARKER_SIZE, Math.min(MAX_MARKER_SIZE, Number(raw.toFixed(2))))
}

// Backwards-compatible export: some tests and older code expect calculateSymbolSize
export const calculateSymbolSize = calculateMarkerSize

export function buildTopBottomPurchaseCharts(
  trades: TradeRecord[],
  tickerStats: TickerStats[],
  limit = 5,
): PurchaseChartItem[] {
  if (!tickerStats || tickerStats.length === 0) return []

  const sorted = [...tickerStats].sort((a, b) => b.total_pnl - a.total_pnl)
  const top = sorted.slice(0, limit)
  const bottom = sorted.slice(Math.max(sorted.length - limit, 0)).sort((a, b) => a.total_pnl - b.total_pnl)

  const selected: { stat: TickerStats; group: 'top' | 'bottom' }[] = []
  const seen = new Set<string>()
  for (const stat of top) {
    if (seen.has(stat.ticker)) continue
    seen.add(stat.ticker)
    selected.push({ stat, group: 'top' })
  }
  for (const stat of bottom) {
    if (seen.has(stat.ticker)) continue
    seen.add(stat.ticker)
    selected.push({ stat, group: 'bottom' })
  }

  return selected.map(({ stat, group }) => {
    const purchases = trades
      .filter((trade) => trade.ticker === stat.ticker)
      .map(toPurchasePoint)
      .filter((point): point is PurchasePoint => point !== null)
      .sort((a, b) => a.timestamp.localeCompare(b.timestamp))

    return {
      ticker: stat.ticker,
      totalPnl: stat.total_pnl,
      group,
      purchases,
    }
  })
}

export const TopBottomPurchaseCharts: React.FC<TopBottomPurchaseChartsProps> = ({
  trades,
  tickerStats,
  loading = false,
  limit = 5,
}) => {
  if (loading) {
    return <div className="purchase-charts loading">Loading charts...</div>
  }

  const items = React.useMemo(
    () => buildTopBottomPurchaseCharts(trades, tickerStats, limit),
    [trades, tickerStats, limit],
  )
  const visibleItems = items.filter((item) => item.purchases.length > 0)
  if (visibleItems.length === 0) {
    return <div className="purchase-charts empty">No purchase data available</div>
  }

  return (
    <div className="purchase-charts" data-testid="purchase-charts">
      <div className="purchase-grid">
        {visibleItems.map((item) => (
          <div className="purchase-card" key={`${item.group}-${item.ticker}`} data-testid="purchase-chart-card">
            <div className="purchase-card-title">
              <span>{item.ticker}</span>
              <span className={`badge ${item.group}`}>{item.group === 'top' ? 'TOP' : 'BOTTOM'}</span>
            </div>
            <div style={{ width: '100%' }}>
              <CandlestickChart
                ticker={item.ticker}
                data={{ dates: [], open: [], high: [], low: [], close: [], volume: [] }}
                markers={{ entries: item.purchases.map(p => ({ date: p.timestamp, price: p.price })), exits: [] }}
                width={420}
                height={240}
              />
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .purchase-charts {
          padding: 20px;
        }
        .purchase-charts.loading,
        .purchase-charts.empty {
          min-height: 260px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #64748b;
        }
        .purchase-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 14px;
        }
        .purchase-card {
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          background: #fff;
          overflow: hidden;
        }
        .purchase-card-title {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 10px;
          border-bottom: 1px solid #e2e8f0;
          font-size: 12px;
          font-weight: 600;
          color: #0f172a;
        }
        .badge {
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
          letter-spacing: 0.4px;
        }
        .badge.top {
          background: #dcfce7;
          color: #166534;
        }
        .badge.bottom {
          background: #fee2e2;
          color: #991b1b;
        }
      `}</style>
    </div>
  )
}

export default TopBottomPurchaseCharts
