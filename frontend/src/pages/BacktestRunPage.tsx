import React from 'react'
import { useTranslation } from 'react-i18next'
import { RunPanel } from '../components/RunPanel'
import { useBacktestDashboardContext } from './BacktestDashboard'
import '../styles/dashboard-cards.css'

export const BacktestRunPage: React.FC = () => {
  const { t } = useTranslation()
  const {
    backtests,
    selectedTimestamp,
    setSelectedTimestamp,
    activeJob,
    jobLogs,
    runError,
    handleRunCommand,
    handleCancelCommand,
  } = useBacktestDashboardContext()

  return (
    <div className="dashboard-page-grid dashboard-page-grid--run">
      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.runRoute', 'Run & Manage')}</h2>
            <p>{t('dashboard.runRouteHint', 'Manage command execution, pinned annual results, and live logs from one screen.')}</p>
          </div>
        </div>
        <RunPanel
          onRun={handleRunCommand}
          onCancel={handleCancelCommand}
          activeJob={activeJob}
          logs={jobLogs}
          runError={runError}
        />
      </section>

      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.availableTests')}</h2>
            <p>{t('dashboard.pinnedHint')}</p>
          </div>
        </div>

        <div className="backtest-list">
          {backtests.length === 0 ? (
            <p className="empty-list">{t('dashboard.noBacktests')}</p>
          ) : (
            backtests.map((backtest) => {
              const availableRunCount = backtest.available_runs ?? 1

              return (
                <button
                  type="button"
                  key={backtest.timestamp}
                  className={`backtest-item ${selectedTimestamp === backtest.timestamp ? 'active' : ''}`}
                  onClick={() => setSelectedTimestamp(backtest.timestamp)}
                >
                  <div className="item-period">
                    <span>{backtest.period}</span>
                    {backtest.is_pinned && <span className="backtest-badge">{t('dashboard.pinnedLabel')}</span>}
                  </div>
                  {(backtest.run_label || backtest.experiment_name || backtest.strategy_name || backtest.rule_profile) && (
                    <div className="item-metadata">
                      {backtest.run_label ? <span>{backtest.run_label}</span> : null}
                      {backtest.experiment_name ? <span>{backtest.experiment_name}</span> : null}
                      {backtest.strategy_name ? <span>{backtest.strategy_name}</span> : null}
                      {backtest.rule_profile ? <span>{backtest.rule_profile}</span> : null}
                      {backtest.benchmark_enabled === false ? (
                        <span>{t('dashboard.benchmarkDisabledShort', 'No benchmark')}</span>
                      ) : null}
                    </div>
                  )}
                  <div className="item-details">
                    <span>{t('dashboard.tradesCount', { count: backtest.trade_count })}</span>
                    {availableRunCount > 1 && (
                      <span title={t('dashboard.availableRunsHint')}>
                        {t('dashboard.availableRuns', { count: availableRunCount })}
                      </span>
                    )}
                  </div>
                  <div className="item-timestamp">{backtest.timestamp}</div>
                </button>
              )
            })
          )}
        </div>
      </section>
    </div>
  )
}
