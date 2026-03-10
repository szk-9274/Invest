import React from 'react'
import { useTranslation } from 'react-i18next'
import type { BacktestMetadata } from '../api/backtest'

interface ExperimentListTableProps {
  backtests: BacktestMetadata[]
  selectedTimestamp: string | null
  onSelect: (timestamp: string) => void
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined) return '-'
  return `${(value * 100).toFixed(2)}%`
}

function formatNumber(value?: number | null) {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

export const ExperimentListTable: React.FC<ExperimentListTableProps> = ({
  backtests,
  selectedTimestamp,
  onSelect,
}) => {
  const { t } = useTranslation()

  if (backtests.length === 0) {
    return <p className="empty-list">{t('dashboard.noBacktests')}</p>
  }

  return (
    <div className="experiment-table-wrapper">
      <table className="experiment-table" aria-label={t('dashboard.experimentList')}>
        <thead>
          <tr>
            <th>{t('dashboard.periodColumn')}</th>
            <th>{t('dashboard.experimentColumn')}</th>
            <th>{t('dashboard.strategyColumn')}</th>
            <th>{t('dashboard.conditionColumn')}</th>
            <th>{t('dashboard.tradesColumn')}</th>
            <th>{t('summary.annualReturn')}</th>
            <th>{t('summary.informationRatio')}</th>
            <th>{t('summary.maxDrawdown')}</th>
          </tr>
        </thead>
        <tbody>
          {backtests.map((backtest) => {
            const isActive = backtest.timestamp === selectedTimestamp
            const headlineMetrics = backtest.headline_metrics
            const availableRunCount = backtest.available_runs ?? 1
            return (
              <tr key={backtest.timestamp} className={isActive ? 'selected' : ''}>
                <td>
                  <div className="experiment-period-cell">
                    <button
                      type="button"
                      className="experiment-select-button"
                      onClick={() => onSelect(backtest.timestamp)}
                    >
                      <span>{backtest.period}</span>
                      {backtest.is_pinned ? <span className="backtest-badge">{t('dashboard.pinnedLabel')}</span> : null}
                    </button>
                    {availableRunCount > 1 ? (
                      <span className="experiment-period-note">{t('dashboard.availableRuns', { count: availableRunCount })}</span>
                    ) : null}
                  </div>
                </td>
                <td>
                  <div className="experiment-primary-cell">
                    <strong>{backtest.run_label ?? backtest.experiment_name ?? backtest.timestamp}</strong>
                    {backtest.experiment_name && backtest.experiment_name !== backtest.run_label ? (
                      <span>{backtest.experiment_name}</span>
                    ) : null}
                  </div>
                </td>
                <td>{backtest.strategy_name ?? '-'}</td>
                <td>
                  <div className="experiment-condition">
                    {backtest.rule_profile ? <span>{backtest.rule_profile}</span> : null}
                    {backtest.benchmark_enabled === false ? (
                      <span>{t('dashboard.benchmarkDisabledShort')}</span>
                    ) : null}
                  </div>
                </td>
                <td>{backtest.trade_count}</td>
                <td>{formatPercent(headlineMetrics?.annual_return_pct)}</td>
                <td>{formatNumber(headlineMetrics?.information_ratio)}</td>
                <td>{formatPercent(headlineMetrics?.max_drawdown_pct)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <style>{`
        .experiment-table-wrapper {
          overflow-x: auto;
        }

        .experiment-table {
          width: 100%;
          border-collapse: collapse;
          min-width: 860px;
        }

        .experiment-table th,
        .experiment-table td {
          padding: 12px 10px;
          border-bottom: 1px solid #e2e8f0;
          text-align: left;
          vertical-align: top;
          font-size: 13px;
        }

        .experiment-table th {
          color: #475569;
          font-weight: 700;
          background: #f8fafc;
        }

        .experiment-table tr.selected {
          background: #eff6ff;
        }

        .experiment-select-button {
          border: none;
          background: transparent;
          padding: 0;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: #0f172a;
          font-weight: 600;
          cursor: pointer;
          text-align: left;
        }

        .experiment-period-cell {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .experiment-period-note {
          color: #64748b;
          font-size: 12px;
        }

        .experiment-condition {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .experiment-primary-cell {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .experiment-primary-cell strong {
          color: #0f172a;
        }

        .experiment-primary-cell span {
          color: #64748b;
          font-size: 12px;
        }

        .experiment-condition span {
          display: inline-flex;
          align-items: center;
          padding: 2px 8px;
          border-radius: 999px;
          background: #e2e8f0;
          color: #334155;
          font-size: 12px;
        }
      `}</style>
    </div>
  )
}
