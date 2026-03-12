import React from 'react'
import { useTranslation } from 'react-i18next'
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

function ExpandIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">
      <path
        d="M4 8V4h4M12 4h4v4M16 12v4h-4M8 16H4v-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 4 4 8M12 4l4 4M4 12l4 4M16 12l-4 4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

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
  const { t } = useTranslation()
  const [expandedTicker, setExpandedTicker] = React.useState<PurchaseChartItem | null>(null)

  React.useEffect(() => {
    if (!expandedTicker) return undefined

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setExpandedTicker(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [expandedTicker])

  if (loading) {
    return <div className="purchase-charts loading">{t('chartGallery.loadingCharts')}</div>
  }

  const items = React.useMemo(
    () => buildTopBottomPurchaseCharts(trades, tickerStats, limit),
    [trades, tickerStats, limit],
  )
  const visibleItems = items.filter((item) => item.purchases.length > 0)
  const rankByItemKey = React.useMemo(() => {
    const ranks = new Map<string, number>()
    let topRank = 0
    let bottomRank = 0
    for (const item of visibleItems) {
      if (item.group === 'top') {
        topRank += 1
        ranks.set(`${item.group}-${item.ticker}`, topRank)
      } else {
        bottomRank += 1
        ranks.set(`${item.group}-${item.ticker}`, bottomRank)
      }
    }
    return ranks
  }, [visibleItems])
  if (visibleItems.length === 0) {
    return <div className="purchase-charts empty">{t('chartGallery.noPurchaseData')}</div>
  }

  return (
    <div className="purchase-charts" data-testid="purchase-charts">
      <div className="purchase-grid">
        {visibleItems.map((item) => (
          <div className="purchase-card" key={`${item.group}-${item.ticker}`} data-testid="purchase-chart-card">
            <div className="purchase-card-title">
              <span>{item.ticker}</span>
              <div className="purchase-card-actions">
                <span className={`badge ${item.group}`}>{item.group === 'top' ? t('chartGallery.topShort') : t('chartGallery.bottomShort')}</span>
                <span className={`rank-badge ${item.group}`}>
                  {item.group === 'top'
                    ? t('chartGallery.topRankBadge', { rank: rankByItemKey.get(`${item.group}-${item.ticker}`) ?? 1 })
                    : t('chartGallery.bottomRankBadge', { rank: rankByItemKey.get(`${item.group}-${item.ticker}`) ?? 1 })}
                </span>
                <button
                  type="button"
                  className="purchase-expand-button"
                  aria-label={t('chartGallery.expandChartFor', { ticker: item.ticker })}
                  title={t('chartGallery.expandChart')}
                  onClick={() => setExpandedTicker(item)}
                >
                  <ExpandIcon />
                </button>
              </div>
            </div>
            <button
              type="button"
              className="purchase-chart-button"
              aria-label={t('chartGallery.expandChart')}
              onClick={() => setExpandedTicker(item)}
            >
              <CandlestickChart
                ticker={item.ticker}
                data={{ dates: [], open: [], high: [], low: [], close: [], volume: [] }}
                markers={{ entries: item.purchases.map(p => ({ date: p.timestamp, price: p.price })), exits: [] }}
                width={420}
                height={240}
              />
            </button>
          </div>
        ))}
      </div>

      {expandedTicker ? (
        <div
          className="purchase-lightbox"
          role="dialog"
          aria-modal="true"
          aria-label={t('chartGallery.expandChart')}
          onClick={() => setExpandedTicker(null)}
        >
          <div className="purchase-lightbox-content" onClick={(event) => event.stopPropagation()}>
            <div className="purchase-lightbox-header">
              <div>
                <strong>{expandedTicker.ticker}</strong>
                <p>{expandedTicker.group === 'top' ? t('chartGallery.topPerformerDetail') : t('chartGallery.bottomPerformerDetail')}</p>
              </div>
              <button type="button" className="purchase-expand-button" onClick={() => setExpandedTicker(null)}>
                {t('nav.close')}
              </button>
            </div>
            <CandlestickChart
              ticker={expandedTicker.ticker}
              data={{ dates: [], open: [], high: [], low: [], close: [], volume: [] }}
              markers={{ entries: expandedTicker.purchases.map((p) => ({ date: p.timestamp, price: p.price })), exits: [] }}
              width={960}
              height={560}
            />
          </div>
        </div>
      ) : null}

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
        .purchase-card-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .purchase-chart-button {
          width: 100%;
          padding: 0;
          border: none;
          background: transparent;
          cursor: zoom-in;
        }
        .purchase-expand-button {
          width: 34px;
          height: 34px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: 1px solid #cbd5e1;
          border-radius: 999px;
          background: #f8fafc;
          color: #0f172a;
          cursor: pointer;
          box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
        }
        .purchase-expand-button svg {
          width: 18px;
          height: 18px;
        }
        .purchase-expand-button:hover {
          background: #e2e8f0;
        }
        .badge {
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 10px;
          letter-spacing: 0.4px;
        }
        .rank-badge {
          min-width: 48px;
          padding: 4px 8px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 700;
          text-align: center;
          line-height: 1;
        }
        .badge.top {
          background: #dcfce7;
          color: #166534;
        }
        .rank-badge.top {
          background: #dbeafe;
          color: #1d4ed8;
        }
        .badge.bottom {
          background: #fee2e2;
          color: #991b1b;
        }
        .rank-badge.bottom {
          background: #fee2e2;
          color: #b91c1c;
        }
        .purchase-lightbox {
          position: fixed;
          inset: 0;
          background: rgba(15, 23, 42, 0.88);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
        }
        .purchase-lightbox-content {
          width: min(100%, 1040px);
          max-height: 100%;
          overflow: auto;
          background: #0f172a;
          border-radius: 18px;
          padding: 16px;
        }
        .purchase-lightbox-header {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: center;
          color: #e2e8f0;
          margin-bottom: 12px;
        }
        .purchase-lightbox-header p {
          margin: 4px 0 0;
          color: #94a3b8;
          font-size: 13px;
        }
        @media (max-width: 768px) {
          .purchase-grid {
            grid-template-columns: 1fr;
          }
          .purchase-charts {
            padding: 8px 0;
          }
        }
      `}</style>
    </div>
  )
}

export default TopBottomPurchaseCharts
