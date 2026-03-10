import React from 'react'
import { useTranslation } from 'react-i18next'
import { BacktestSummary } from '../components/BacktestSummary'
import { TradeTable } from '../components/TradeTable'
import { useDeferredVisibility } from '../hooks/useDeferredVisibility'
import { useBacktestDashboardContext } from './BacktestDashboard'
import '../styles/dashboard-cards.css'

const TopBottomPurchaseCharts = React.lazy(() =>
  import('../components/TopBottomPurchaseCharts').then((module) => ({
    default: module.TopBottomPurchaseCharts,
  })),
)

function formatTimestampLabel(timestamp: string) {
  return timestamp.split('_').slice(0, -1).join('_')
}

export const BacktestAnalysisPage: React.FC = () => {
  const { t } = useTranslation()
  const { results, loading } = useBacktestDashboardContext()
  const { isVisible: isChartsVisible, targetRef: chartsAnchorRef } = useDeferredVisibility<HTMLDivElement>()
  const runMetadata = results?.run_metadata
  const metadataLabel = [runMetadata?.experiment_name, runMetadata?.strategy_name, runMetadata?.rule_profile]
    .filter(Boolean)
    .join(' / ')

  if (!results) {
    return <div className="dashboard-empty-panel">{loading ? t('common.loading') : t('dashboard.selectBacktest')}</div>
  }

  return (
    <div className="dashboard-page-stack">
      <section className="dashboard-card dashboard-card--summary">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.analysisRoute', 'Analysis & Results')}</h2>
            <p>{runMetadata?.run_label ?? formatTimestampLabel(results.timestamp)}</p>
            {metadataLabel ? <p>{metadataLabel}</p> : null}
            {runMetadata?.benchmark_enabled === false ? (
              <p>{t('dashboard.benchmarkDisabledLabel', 'Benchmark disabled')}</p>
            ) : null}
          </div>
        </div>
        <BacktestSummary data={results.summary} loading={loading} />
      </section>

      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.chartsTab')}</h2>
            <p>{t('dashboard.chartsRouteHint', 'Review the standard-size chart gallery for top and bottom performers.')}</p>
          </div>
        </div>
        <div ref={chartsAnchorRef} data-testid="analysis-charts-anchor">
          {isChartsVisible ? (
            <React.Suspense
              fallback={(
                <div className="dashboard-deferred-placeholder" data-testid="analysis-charts-placeholder">
                  {t('common.loading')}
                </div>
              )}
            >
              <TopBottomPurchaseCharts
                trades={results.trades}
                tickerStats={results.ticker_stats}
                loading={loading}
              />
            </React.Suspense>
          ) : (
            <div className="dashboard-deferred-placeholder" data-testid="analysis-charts-placeholder">
              {t('dashboard.chartsDeferredHint', 'Scroll to load the chart gallery.')}
            </div>
          )}
        </div>
      </section>

      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.tradesTab')}</h2>
            <p>{t('dashboard.tradesRouteHint', 'Review trade outcomes with compact mobile cards and translated exit reasons.')}</p>
          </div>
        </div>
        <TradeTable trades={results.trades} loading={loading} />
      </section>
    </div>
  )
}
