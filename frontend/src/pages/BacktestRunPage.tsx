import React from 'react'
import { useTranslation } from 'react-i18next'
import { RunPanel } from '../components/RunPanel'
import { BacktestSummary } from '../components/BacktestSummary'
import { ConditionComparisonPanel } from '../components/ConditionComparisonPanel'
import { ExperimentListTable } from '../components/ExperimentListTable'
import { useBacktestDashboardContext } from './BacktestDashboard'
import '../styles/dashboard-cards.css'

export const BacktestRunPage: React.FC = () => {
  const { t } = useTranslation()
  const {
    backtests,
    results,
    loading,
    selectedTimestamp,
    setSelectedTimestamp,
    activeJob,
    jobLogs,
    runError,
    handleRunCommand,
    handleCancelCommand,
  } = useBacktestDashboardContext()

  return (
    <div className="dashboard-page-stack">
      <section className="dashboard-card dashboard-card--summary">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.overviewTitle')}</h2>
            <p>{t('dashboard.overviewHint')}</p>
          </div>
        </div>
        <BacktestSummary data={results?.summary ?? null} loading={loading} />
      </section>

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
              <h2>{t('dashboard.conditionComparison')}</h2>
              <p>{t('dashboard.conditionComparisonHint')}</p>
            </div>
          </div>
          <ConditionComparisonPanel
            backtests={backtests}
            selectedTimestamp={selectedTimestamp}
          />
        </section>
      </div>

      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.experimentList')}</h2>
            <p>{t('dashboard.pinnedHint')} {t('dashboard.experimentListHint')}</p>
          </div>
        </div>
        <ExperimentListTable
          backtests={backtests}
          selectedTimestamp={selectedTimestamp}
          onSelect={setSelectedTimestamp}
        />
      </section>
    </div>
  )
}
