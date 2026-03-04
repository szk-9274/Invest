/**
 * Backtest Dashboard Page
 * Main page displaying backtest results with multiple views
 */
import React, { useEffect, useState } from 'react';
import { BacktestSummary } from '../components/BacktestSummary';
import { ChartGallery } from '../components/ChartGallery';
import { TradeTable } from '../components/TradeTable';
import { RunPanel } from '../components/RunPanel';
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

export const BacktestDashboard: React.FC = () => {
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
        setError(`Failed to load backtest list: ${err}`);
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
        setError(`Failed to load backtest results: ${err}`);
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
      setError(`Failed to load latest backtest: ${err}`);
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
      setRunError(`Failed to start command: ${err}`);
    }
  };

  const handleCancelCommand = async () => {
    if (!activeJob) return;
    try {
      const cancelled = await cancelJob(activeJob.job_id);
      setActiveJob(cancelled);
      await refreshJobLogs(cancelled.job_id);
    } catch (err) {
      setRunError(`Failed to cancel command: ${err}`);
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
        setRunError(`Failed to poll job status: ${err}`);
      }
    }, 2000);

    return () => clearInterval(timer);
  }, [activeJob?.job_id, activeJob?.status]);

  return (
    <div className="backtest-dashboard">
      <header className="dashboard-header">
        <h1>Backtest Dashboard</h1>
        <button onClick={handleLoadLatest} className="button-primary" disabled={loading}>
          {loading ? 'Loading...' : 'Load Latest'}
        </button>
      </header>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
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

          <h3>Available Tests</h3>
          <div className="backtest-list">
            {backtests.length === 0 ? (
              <p className="empty-list">No backtests found</p>
            ) : (
              backtests.map((backtest) => (
                <div
                  key={backtest.timestamp}
                  className={`backtest-item ${selectedTimestamp === backtest.timestamp ? 'active' : ''}`}
                  onClick={() => setSelectedTimestamp(backtest.timestamp)}
                >
                  <div className="item-period">{backtest.period}</div>
                  <div className="item-details">
                    <span>{backtest.trade_count} trades</span>
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
                  Summary
                </button>
                <button
                  className={`tab-button ${activeTab === 'charts' ? 'active' : ''}`}
                  onClick={() => setActiveTab('charts')}
                >
                  Charts
                </button>
                <button
                  className={`tab-button ${activeTab === 'trades' ? 'active' : ''}`}
                  onClick={() => setActiveTab('trades')}
                >
                  Trades
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'summary' && (
                  <BacktestSummary data={results.summary} loading={loading} />
                )}
                {activeTab === 'charts' && (
                  <ChartGallery charts={results.charts} loading={loading} />
                )}
                {activeTab === 'trades' && (
                  <TradeTable trades={results.trades} loading={loading} />
                )}
              </div>
            </>
          ) : (
            <div className="no-results">
              {loading ? 'Loading...' : 'Select a backtest to view results'}
            </div>
          )}
        </main>
      </div>

      <style>{`
        .backtest-dashboard {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          background: #fafafa;
        }

        .dashboard-header {
          background: white;
          border-bottom: 1px solid #ddd;
          padding: 20px 30px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .dashboard-header h1 {
          margin: 0;
          font-size: 24px;
          color: #333;
        }

        .button-primary {
          padding: 8px 16px;
          background: #0066cc;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          transition: background 0.2s;
        }

        .button-primary:hover:not(:disabled) {
          background: #0052a3;
        }

        .button-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .error-message {
          background: #fee;
          border: 1px solid #fcc;
          border-radius: 4px;
          padding: 12px;
          margin: 15px;
          color: #c33;
          font-size: 13px;
        }

        .dashboard-layout {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        .sidebar {
          width: 360px;
          background: white;
          border-right: 1px solid #ddd;
          padding: 20px;
          overflow-y: auto;
        }

        .run-panel {
          margin-bottom: 20px;
          padding: 14px;
          border: 1px solid #dbe3f0;
          border-radius: 10px;
          background: #f8fbff;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .run-panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 8px;
        }

        .run-panel-header h3 {
          margin: 0;
          font-size: 14px;
          color: #1e3a5f;
        }

        .status-line {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #334155;
        }

        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 999px;
          display: inline-block;
        }

        .run-grid {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .run-grid label {
          font-size: 12px;
          color: #334155;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .run-grid input,
        .run-grid select {
          font-size: 12px;
          padding: 6px 8px;
          border: 1px solid #cbd5e1;
          border-radius: 6px;
          background: #fff;
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

        .button-secondary {
          padding: 8px 16px;
          background: #f5f5f5;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
        }

        .button-secondary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .job-meta {
          font-size: 11px;
          color: #334155;
          display: flex;
          flex-direction: column;
          gap: 3px;
        }

        .run-error {
          font-size: 12px;
          color: #b91c1c;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 6px;
          padding: 6px 8px;
        }

        .log-panel h4 {
          margin: 0 0 6px;
          font-size: 12px;
          color: #1e3a5f;
        }

        .log-panel pre {
          background: #0f172a;
          color: #cbd5e1;
          border-radius: 8px;
          padding: 8px;
          font-size: 11px;
          max-height: 220px;
          overflow: auto;
          margin: 0;
        }

        .sidebar h3 {
          margin: 0 0 15px 0;
          font-size: 14px;
          color: #333;
        }

        .backtest-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .backtest-item {
          padding: 10px;
          background: #f5f5f5;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .backtest-item:hover {
          background: #efefef;
          border-color: #999;
        }

        .backtest-item.active {
          background: #e3f2fd;
          border-color: #0066cc;
        }

        .item-period {
          font-size: 12px;
          font-weight: 600;
          color: #333;
        }

        .item-details {
          font-size: 11px;
          color: #666;
          margin-top: 4px;
        }

        .item-timestamp {
          font-size: 10px;
          color: #999;
          margin-top: 4px;
          font-family: 'Monaco', monospace;
        }

        .empty-list {
          color: #999;
          font-size: 12px;
          text-align: center;
          padding: 20px 0;
        }

        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .results-header {
          background: white;
          border-bottom: 1px solid #ddd;
          padding: 15px 30px;
        }

        .results-header h2 {
          margin: 0;
          font-size: 16px;
          color: #666;
        }

        .tabs {
          background: white;
          border-bottom: 1px solid #ddd;
          padding: 0 30px;
          display: flex;
          gap: 0;
        }

        .tab-button {
          padding: 12px 20px;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          font-size: 13px;
          color: #666;
          transition: all 0.2s;
        }

        .tab-button:hover {
          color: #333;
        }

        .tab-button.active {
          color: #0066cc;
          border-bottom-color: #0066cc;
        }

        .tab-content {
          flex: 1;
          overflow-y: auto;
          background: white;
        }

        .no-results {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #999;
          font-size: 14px;
        }

        @media (max-width: 768px) {
          .dashboard-layout {
            flex-direction: column;
          }

          .sidebar {
            width: 100%;
            border-right: none;
            border-bottom: 1px solid #ddd;
            max-height: 200px;
          }

          .dashboard-header {
            flex-direction: column;
            gap: 10px;
          }
        }
      `}</style>
    </div>
  );
};
