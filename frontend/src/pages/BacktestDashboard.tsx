/**
 * Backtest Dashboard Page
 * Main page displaying backtest results with multiple views.
 * UI inspired by Metaplanet Analytics dashboard.
 */
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { BacktestSummary } from '../components/BacktestSummary';
import { TradeTable } from '../components/TradeTable';
import { RunPanel } from '../components/RunPanel';
import { Notification } from '../components/Notification';
import {
  fetchLatestBacktest,
  fetchBacktestResults,
  listAllBacktests,
  BacktestResults,
  BacktestMetadata,
} from '../api/backtest';
import {
  createJob,
  getJob,
  getJobLogs,
  cancelJob,
  JobCreateRequest,
  JobResponse,
} from '../api/jobs';

const TopBottomPurchaseCharts = React.lazy(() =>
  import('../components/TopBottomPurchaseCharts').then((module) => ({
    default: module.TopBottomPurchaseCharts,
  })),
);

export const BacktestDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [results, setResults] = useState<BacktestResults | null>(null);
  const [backtests, setBacktests] = useState<BacktestMetadata[]>([]);
  const [selectedTimestamp, setSelectedTimestamp] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'summary' | 'charts' | 'trades'>('summary');
  const [activeJob, setActiveJob] = useState<JobResponse | null>(null);
  const [jobLogs, setJobLogs] = useState<string[]>([]);
  const [runError, setRunError] = useState<string | null>(null);

  // Fetch list of available backtests
  useEffect(() => {
    const loadBacktests = async () => {
      try {
        const data = await listAllBacktests();
        setBacktests(data);
        if (data.length > 0) {
          setSelectedTimestamp(data[0].timestamp);
        }
      } catch (err) {
        setError(t('dashboard.loadBacktestListError', { error: String(err) }));
      }
    };

    loadBacktests();
  }, []);

  // Fetch results when timestamp is selected
  useEffect(() => {
    if (!selectedTimestamp) return;

    const loadResults = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchBacktestResults(selectedTimestamp);
        setResults(data);
      } catch (err) {
        setError(t('dashboard.loadBacktestResultsError', { error: String(err) }));
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [selectedTimestamp]);

  const handleLoadLatest = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLatestBacktest();
      setResults(data);
      setSelectedTimestamp(data.timestamp);
    } catch (err) {
      setError(t('dashboard.loadLatestError', { error: String(err) }));
    } finally {
      setLoading(false);
    }
  };

  const refreshJobLogs = async (jobId: string) => {
    const logs = await getJobLogs(jobId, 300);
    setJobLogs(logs.lines);
  };

  const handleRunCommand = async (request: JobCreateRequest) => {
    setRunError(null);
    try {
      const job = await createJob(request);
      setActiveJob(job);
      setJobLogs([]);
      await refreshJobLogs(job.job_id);
    } catch (err) {
      setRunError(t('dashboard.startCommandError', { error: String(err) }));
    }
  };

  const handleCancelCommand = async () => {
    if (!activeJob) return;
    try {
      const cancelled = await cancelJob(activeJob.job_id);
      setActiveJob(cancelled);
      await refreshJobLogs(cancelled.job_id);
    } catch (err) {
      setRunError(t('dashboard.cancelCommandError', { error: String(err) }));
    }
  };

  useEffect(() => {
    if (!activeJob) return;
    if (activeJob.status !== 'queued' && activeJob.status !== 'running') return;

    const timer = setInterval(async () => {
      try {
        const latest = await getJob(activeJob.job_id);
        setActiveJob(latest);
        await refreshJobLogs(latest.job_id);

        if (latest.status === 'succeeded') {
          await handleLoadLatest();
        }
      } catch (err) {
        setRunError(t('dashboard.pollJobStatusError', { error: String(err) }));
      }
    }, 2000);

    return () => clearInterval(timer);
  }, [activeJob?.job_id, activeJob?.status]);

  return (
    <div className="backtest-dashboard">
      <header className="dashboard-header">
        <h1>{t('dashboard.title')}</h1>
        <button onClick={handleLoadLatest} className="button-primary" disabled={loading}>
          {loading ? t('common.loading') : t('dashboard.loadLatest')}
        </button>
      </header>

      {error && (
        <div className="dashboard-notification">
          <Notification type="error" message={error} onDismiss={() => setError(null)} />
        </div>
      )}

      <div className="dashboard-layout">
        <aside className="sidebar">
          <RunPanel
            onRun={handleRunCommand}
            onCancel={handleCancelCommand}
            activeJob={activeJob}
            logs={jobLogs}
            runError={runError}
          />

          <h3>{t('dashboard.availableTests')}</h3>
          <div className="backtest-list">
            {backtests.length === 0 ? (
              <p className="empty-list">{t('dashboard.noBacktests')}</p>
            ) : (
              backtests.map((backtest) => (
                <div
                  key={backtest.timestamp}
                  className={`backtest-item ${selectedTimestamp === backtest.timestamp ? 'active' : ''}`}
                  onClick={() => setSelectedTimestamp(backtest.timestamp)}
                >
                  <div className="item-period">{backtest.period}</div>
                  <div className="item-details">
                    <span>{t('dashboard.tradesCount', { count: backtest.trade_count })}</span>
                  </div>
                  <div className="item-timestamp">{backtest.timestamp}</div>
                </div>
              ))
            )}
          </div>
        </aside>

        <main className="main-content">
          {results ? (
            <>
              <div className="results-header">
                <h2>
                  {results.timestamp.split('_').slice(0, -1).join('_')}
                </h2>
              </div>

              <div className="tabs">
                <button
                  className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
                  onClick={() => setActiveTab('summary')}
                >
                  {t('dashboard.summaryTab')}
                </button>
                <button
                  className={`tab-button ${activeTab === 'charts' ? 'active' : ''}`}
                  onClick={() => setActiveTab('charts')}
                >
                  {t('dashboard.chartsTab')}
                </button>
                <button
                  className={`tab-button ${activeTab === 'trades' ? 'active' : ''}`}
                  onClick={() => setActiveTab('trades')}
                >
                  {t('dashboard.tradesTab')}
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'summary' && (
                  <BacktestSummary data={results.summary} loading={loading} />
                )}
                {activeTab === 'charts' && (
                  <React.Suspense fallback={<div style={{ padding: 20 }}>Loading charts...</div>}>
                    <TopBottomPurchaseCharts
                      trades={results.trades}
                      tickerStats={results.ticker_stats}
                      loading={loading}
                    />
                  </React.Suspense>
                )}
                {activeTab === 'trades' && (
                  <TradeTable trades={results.trades} loading={loading} />
                )}
              </div>
            </>
          ) : (
            <div className="no-results">
              {loading ? t('common.loading') : t('dashboard.selectBacktest')}
            </div>
          )}
        </main>
      </div>

      <style>{`
        .backtest-dashboard {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          background: var(--bg-page, #f8fafc);
          font-family: var(--font-sans, 'Segoe UI', sans-serif);
        }

        /* ---- Dashboard Header ---- */
        .dashboard-header {
          background: var(--bg-nav, #0f172a);
          border-bottom: 1px solid rgba(255,255,255,0.08);
          padding: 16px 28px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 1px 8px rgba(0,0,0,0.3);
        }

        .dashboard-header h1 {
          margin: 0;
          font-size: 20px;
          font-weight: 700;
          color: #ffffff;
          letter-spacing: 0.2px;
        }

        .dashboard-notification {
          padding: 12px 20px 0;
        }

        /* ---- Buttons ---- */
        .button-primary {
          padding: 8px 18px;
          background: var(--primary, #3b82f6);
          color: white;
          border: none;
          border-radius: var(--radius-sm, 4px);
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          transition: background 0.15s, transform 0.1s;
        }

        .button-primary:hover:not(:disabled) {
          background: var(--primary-hover, #2563eb);
          transform: translateY(-1px);
        }

        .button-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .button-secondary {
          padding: 8px 16px;
          background: rgba(255,255,255,0.08);
          color: var(--text-on-dark, #f1f5f9);
          border: 1px solid rgba(255,255,255,0.15);
          border-radius: var(--radius-sm, 4px);
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          transition: background 0.15s;
        }

        .button-secondary:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .button-secondary:hover:not(:disabled) {
          background: rgba(255,255,255,0.14);
        }

        /* ---- Layout ---- */
        .dashboard-layout {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        /* ---- Sidebar ---- */
        .sidebar {
          width: var(--sidebar-width, 360px);
          background: var(--bg-sidebar, #ffffff);
          border-right: 1px solid var(--border, #e2e8f0);
          padding: 20px;
          overflow-y: auto;
          flex-shrink: 0;
        }

        .sidebar h3 {
          margin: 0 0 12px;
          font-size: 13px;
          font-weight: 700;
          color: var(--text-secondary, #475569);
          text-transform: uppercase;
          letter-spacing: 0.6px;
        }

        /* ---- Run Panel ---- */
        .run-panel {
          margin-bottom: 24px;
          padding: 16px;
          border: 1px solid var(--border, #e2e8f0);
          border-radius: var(--radius-md, 8px);
          background: #f8fbff;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .run-panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 8px;
        }

        .run-panel-header h3 {
          margin: 0;
          font-size: 13px;
          color: var(--bg-nav, #0f172a);
          text-transform: none;
          letter-spacing: 0;
        }

        .status-line {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: var(--text-secondary, #475569);
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
        }

        .run-grid {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .run-grid label {
          font-size: 12px;
          color: var(--text-secondary, #475569);
          font-weight: 500;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .run-grid input,
        .run-grid select {
          font-size: 13px;
          padding: 7px 10px;
          border: 1px solid var(--border, #e2e8f0);
          border-radius: var(--radius-sm, 4px);
          background: #fff;
          color: var(--text-primary, #0f172a);
          transition: border-color 0.15s;
        }

        .run-grid input:focus,
        .run-grid select:focus {
          outline: none;
          border-color: var(--primary, #3b82f6);
          box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
        }

        .checkbox-label {
          display: flex;
          flex-direction: row !important;
          align-items: center;
          gap: 8px;
        }

        .run-actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .job-meta {
          font-size: 11px;
          color: var(--text-secondary, #475569);
          display: flex;
          flex-direction: column;
          gap: 3px;
        }

        .run-error {
          font-size: 12px;
          color: #991b1b;
          background: var(--danger-bg, #fee2e2);
          border: 1px solid var(--danger-border, #fca5a5);
          border-radius: var(--radius-sm, 4px);
          padding: 8px 10px;
        }

        .log-panel h4 {
          margin: 0 0 8px;
          font-size: 12px;
          font-weight: 700;
          color: var(--text-secondary, #475569);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .log-panel pre {
          background: var(--bg-nav, #0f172a);
          color: #cbd5e1;
          border-radius: var(--radius-md, 8px);
          padding: 10px 12px;
          font-size: 11px;
          font-family: var(--font-mono, monospace);
          max-height: 220px;
          overflow: auto;
          margin: 0;
        }

        /* ---- Backtest List ---- */
        .backtest-list {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .backtest-item {
          padding: 12px;
          background: var(--bg-hover, #f1f5f9);
          border: 1px solid var(--border, #e2e8f0);
          border-radius: var(--radius-md, 8px);
          cursor: pointer;
          transition: all 0.15s;
        }

        .backtest-item:hover {
          background: #e8f0fe;
          border-color: #93c5fd;
        }

        .backtest-item.active {
          background: var(--info-bg, #dbeafe);
          border-color: var(--primary, #3b82f6);
          border-left-width: 3px;
        }

        .item-period {
          font-size: 12px;
          font-weight: 700;
          color: var(--text-primary, #0f172a);
        }

        .item-details {
          font-size: 11px;
          color: var(--text-muted, #94a3b8);
          margin-top: 4px;
        }

        .item-timestamp {
          font-size: 10px;
          color: var(--text-muted, #94a3b8);
          margin-top: 4px;
          font-family: var(--font-mono, monospace);
        }

        .empty-list {
          color: var(--text-muted, #94a3b8);
          font-size: 13px;
          text-align: center;
          padding: 24px 0;
        }

        /* ---- Main Content ---- */
        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          background: var(--bg-page, #f8fafc);
        }

        .results-header {
          background: var(--bg-card, #ffffff);
          border-bottom: 1px solid var(--border, #e2e8f0);
          padding: 14px 28px;
        }

        .results-header h2 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
          color: var(--text-secondary, #475569);
          font-family: var(--font-mono, monospace);
        }

        /* ---- Tabs ---- */
        .tabs {
          background: var(--bg-card, #ffffff);
          border-bottom: 1px solid var(--border, #e2e8f0);
          padding: 0 28px;
          display: flex;
          gap: 0;
        }

        .tab-button {
          padding: 14px 20px;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          color: var(--text-muted, #94a3b8);
          transition: color 0.15s, border-color 0.15s;
          letter-spacing: 0.2px;
        }

        .tab-button:hover {
          color: var(--text-primary, #0f172a);
        }

        .tab-button.active {
          color: var(--primary, #3b82f6);
          border-bottom-color: var(--primary, #3b82f6);
        }

        .tab-content {
          flex: 1;
          overflow-y: auto;
          background: var(--bg-page, #f8fafc);
        }

        .no-results {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--text-muted, #94a3b8);
          font-size: 15px;
          gap: 10px;
        }

        /* ---- Responsive ---- */
        @media (max-width: 768px) {
          .dashboard-layout {
            flex-direction: column;
          }

          .sidebar {
            width: 100%;
            border-right: none;
            border-bottom: 1px solid var(--border, #e2e8f0);
            max-height: 220px;
          }

          .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
            padding: 14px 16px;
          }

          .tabs {
            padding: 0 16px;
          }
        }
      `}</style>
    </div>
  );
};
