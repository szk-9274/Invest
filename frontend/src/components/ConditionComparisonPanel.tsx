import React from 'react'
import { useTranslation } from 'react-i18next'
import type { BacktestMetadata } from '../api/backtest'

interface ConditionComparisonPanelProps {
  backtests: BacktestMetadata[]
  selectedTimestamp: string | null
}

function normalizeWidth(value: number, maxValue: number) {
  if (!maxValue) return 0
  return Math.max(10, Math.round((Math.abs(value) / maxValue) * 100))
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined) return '-'
  return `${(value * 100).toFixed(2)}%`
}

function formatNumber(value?: number | null) {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

export const ConditionComparisonPanel: React.FC<ConditionComparisonPanelProps> = ({
  backtests,
  selectedTimestamp,
}) => {
  const { t } = useTranslation()
  const rows = backtests
    .map((backtest) => ({
      timestamp: backtest.timestamp,
      label: backtest.run_label ?? backtest.experiment_name ?? backtest.period,
      annualReturn: backtest.headline_metrics?.annual_return_pct ?? 0,
      informationRatio: backtest.headline_metrics?.information_ratio ?? 0,
      maxDrawdown: Math.abs(backtest.headline_metrics?.max_drawdown_pct ?? 0),
      selected: backtest.timestamp === selectedTimestamp,
    }))
    .slice(0, 6)

  const maxAnnualReturn = Math.max(...rows.map((row) => Math.abs(row.annualReturn)), 0)
  const maxInformationRatio = Math.max(...rows.map((row) => Math.abs(row.informationRatio)), 0)
  const maxDrawdown = Math.max(...rows.map((row) => Math.abs(row.maxDrawdown)), 0)

  if (rows.length === 0) {
    return <p className="empty-list">{t('dashboard.noBacktests')}</p>
  }

  const metrics = [
    { key: 'annual', label: t('summary.annualReturn'), maxValue: maxAnnualReturn, getValue: (row: typeof rows[number]) => row.annualReturn, format: formatPercent, tone: 'positive' },
    { key: 'ratio', label: t('summary.informationRatio'), maxValue: maxInformationRatio, getValue: (row: typeof rows[number]) => row.informationRatio, format: formatNumber, tone: 'info' },
    { key: 'drawdown', label: t('summary.maxDrawdown'), maxValue: maxDrawdown, getValue: (row: typeof rows[number]) => row.maxDrawdown, format: formatPercent, tone: 'danger' },
  ] as const

  return (
    <div className="comparison-metric-grid">
      {metrics.map((metric) => (
        <section key={metric.key} className="comparison-metric-card">
          <h3>{metric.label}</h3>
          <div className="comparison-rows">
            {rows.map((row) => {
              const value = metric.getValue(row)
              return (
                <div key={`${metric.key}-${row.timestamp}`} className={`comparison-row ${row.selected ? 'selected' : ''}`}>
                  <div className="comparison-row-copy">
                    <span>{row.label}</span>
                    <strong>{metric.format(value)}</strong>
                  </div>
                  <div className="comparison-bar-track" aria-hidden="true">
                    <div
                      className={`comparison-bar comparison-bar--${metric.tone}`}
                      style={{ width: `${normalizeWidth(value, metric.maxValue)}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      ))}

      <style>{`
        .comparison-metric-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 14px;
        }

        .comparison-metric-card {
          border: 1px solid #e2e8f0;
          border-radius: 14px;
          padding: 16px;
          background: #f8fafc;
        }

        .comparison-metric-card h3 {
          margin: 0 0 14px;
          font-size: 15px;
          color: #0f172a;
        }

        .comparison-rows {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .comparison-row {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .comparison-row.selected strong {
          color: #2563eb;
        }

        .comparison-row-copy {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          font-size: 12px;
          color: #475569;
        }

        .comparison-row-copy strong {
          color: #0f172a;
          font-size: 13px;
        }

        .comparison-bar-track {
          width: 100%;
          height: 8px;
          border-radius: 999px;
          background: #e2e8f0;
          overflow: hidden;
        }

        .comparison-bar {
          height: 100%;
          border-radius: 999px;
        }

        .comparison-bar--positive {
          background: linear-gradient(90deg, #22c55e, #16a34a);
        }

        .comparison-bar--info {
          background: linear-gradient(90deg, #60a5fa, #2563eb);
        }

        .comparison-bar--danger {
          background: linear-gradient(90deg, #fda4af, #ef4444);
        }
      `}</style>
    </div>
  )
}
