import React from 'react'
import { NavLink, Outlet, useOutletContext } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Notification } from '../components/Notification'
import {
  useBacktestDashboardState,
  type UseBacktestDashboardStateResult,
} from '../hooks/useBacktestDashboardState'
import { createDefaultAppChrome, useAppChrome } from '../contexts/AppChromeContext'
import { getBacktestStatusTranslationKey } from '../utils/backtestStatus'
import { resolveRuleProfileDisplayName, resolveStrategyDisplayName } from '../utils/strategyProfileLocalization'

export type BacktestDashboardContextValue = UseBacktestDashboardStateResult

export function useBacktestDashboardContext() {
  return useOutletContext<BacktestDashboardContextValue>()
}

function formatRunPeriodFromTimestamp(timestamp?: string | null) {
  if (!timestamp) return null
  const normalized = timestamp.replace('backtest_', '')
  const [startDate, remainder] = normalized.split('_to_')
  if (!startDate || !remainder) return null
  const [endDate] = remainder.split('_')
  if (!endDate) return null
  return `${startDate} to ${endDate}`
}

export const BacktestDashboard: React.FC = () => {
  const { t } = useTranslation()
  const dashboard = useBacktestDashboardState()
  const { setChrome } = useAppChrome()
  const selectedBacktest = dashboard.backtests.find((backtest) => backtest.timestamp === dashboard.selectedTimestamp)
  const activeRunLabel =
    selectedBacktest?.run_label
    ?? selectedBacktest?.experiment_name
    ?? dashboard.results?.run_metadata?.run_label
    ?? dashboard.results?.timestamp
    ?? null
  const activePeriod = selectedBacktest?.period ?? formatRunPeriodFromTimestamp(dashboard.results?.timestamp) ?? null
  const activeStrategy =
    selectedBacktest?.strategy_name
    ?? dashboard.results?.run_metadata?.strategy_name
    ?? null
  const activeRuleProfile =
    selectedBacktest?.rule_profile
    ?? dashboard.results?.run_metadata?.rule_profile
    ?? null
  const activeStrategyLabel = resolveStrategyDisplayName(activeStrategy, dashboard.strategyProfiles)
  const activeRuleProfileLabel = resolveRuleProfileDisplayName(activeRuleProfile, dashboard.strategyProfiles)
  const statusKey = dashboard.loading
    ? 'dashboard.statusLoading'
    : getBacktestStatusTranslationKey(dashboard.activeJob?.status, dashboard.jobLogs.length > 0)
  const chromeStatus = t('dashboard.chromeStatus', { status: t(statusKey) })

  React.useEffect(() => {
    setChrome({
      brandLabel: t('nav.dashboard'),
      brandLink: '/dashboard/run',
      statusLabel: chromeStatus,
      reloadLabel: t('dashboard.reloadLatestAria'),
      onReload: dashboard.handleLoadLatest,
      reloadDisabled: dashboard.loading,
    })

    return () => {
      setChrome(createDefaultAppChrome())
    }
  }, [chromeStatus, dashboard.handleLoadLatest, dashboard.loading, setChrome, t])

  return (
    <div className="backtest-dashboard">
      <nav className="dashboard-route-nav" aria-label={t('dashboard.routeNavigation', 'Backtest sections')}>
        <NavLink to="/dashboard/run" className={({ isActive }) => `route-tab ${isActive ? 'active' : ''}`}>
          {t('dashboard.runRoute', 'Run & Manage')}
        </NavLink>
        <NavLink to="/dashboard/analysis" className={({ isActive }) => `route-tab ${isActive ? 'active' : ''}`}>
          {t('dashboard.analysisRoute', 'Analysis & Results')}
        </NavLink>
        <NavLink to="/dashboard/strategies" className={({ isActive }) => `route-tab ${isActive ? 'active' : ''}`}>
          {t('dashboard.traderStrategiesRoute', 'Trader Strategies')}
        </NavLink>
      </nav>

      {activeRunLabel || activePeriod || activeStrategy ? (
        <section className="dashboard-active-run" aria-label={t('dashboard.selectedRunTitle', 'Selected run summary')}>
          <div className="dashboard-active-run__item">
            <span>{t('dashboard.selectedRunTitle', 'Selected run')}</span>
            <strong>{activeRunLabel ?? t('dashboard.selectBacktest')}</strong>
          </div>
          <div className="dashboard-active-run__item">
            <span>{t('dashboard.selectedPeriodLabel', 'Period')}</span>
            <strong>{activePeriod ?? '-'}</strong>
          </div>
          <div className="dashboard-active-run__item">
            <span>{t('dashboard.selectedStrategyLabel', 'Strategy')}</span>
            <strong>{activeStrategyLabel ?? '-'}</strong>
          </div>
          <div className="dashboard-active-run__item">
            <span>{t('dashboard.selectedProfileLabel', 'Profile')}</span>
            <strong>{activeRuleProfileLabel ?? '-'}</strong>
          </div>
        </section>
      ) : null}

      {dashboard.error && (
        <div className="dashboard-notification">
          <Notification type="error" message={dashboard.error} onDismiss={() => dashboard.setError(null)} />
        </div>
      )}

      <main className="dashboard-shell">
        <Outlet context={dashboard} />
      </main>

      <style>{`
        .backtest-dashboard {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          background: var(--bg-page, #f8fafc);
          font-family: var(--font-sans, 'Segoe UI', sans-serif);
        }

        .dashboard-route-nav {
          display: flex;
          gap: 12px;
          padding: 12px 28px 0;
          background: var(--bg-page, #f8fafc);
        }

        .route-tab {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 10px 16px;
          border-radius: 999px;
          text-decoration: none;
          color: #334155;
          background: #e2e8f0;
          font-weight: 600;
        }

        .route-tab.active {
          background: #3b82f6;
          color: #ffffff;
        }

        .dashboard-notification {
          padding: 12px 20px 0;
        }

        .dashboard-active-run {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
          padding: 12px 20px 0;
        }

        .dashboard-active-run__item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding: 12px 14px;
          border-radius: 14px;
          border: 1px solid #dbe4f0;
          background: #ffffff;
          box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        .dashboard-active-run__item span {
          color: #64748b;
          font-size: 12px;
          font-weight: 600;
        }

        .dashboard-active-run__item strong {
          color: #0f172a;
          font-size: 14px;
          word-break: break-word;
        }

        .dashboard-shell {
          flex: 1;
          padding: 16px 20px 24px;
        }

        @media (max-width: 768px) {
          .dashboard-route-nav {
            padding: 12px 20px 0;
            flex-direction: column;
          }

          .dashboard-active-run {
            grid-template-columns: 1fr;
            padding: 12px 12px 0;
          }

          .route-tab {
            width: 100%;
          }

          .dashboard-shell {
            padding: 16px 12px 24px;
          }
        }
      `}</style>
    </div>
  )
}
