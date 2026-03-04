import React, { useMemo, useState } from 'react';
import { JobCreateRequest, JobResponse } from '../api/jobs';

type RunPanelProps = {
  onRun: (request: JobCreateRequest) => Promise<void>;
  onCancel: () => Promise<void>;
  activeJob: JobResponse | null;
  logs: string[];
  runError: string | null;
};

const COMMAND_OPTIONS = [
  { value: 'backtest', label: 'Backtest' },
  { value: 'stage2', label: 'Stage2 Screening' },
  { value: 'full', label: 'Full Screening + VCP' },
  { value: 'chart', label: 'Chart Generation' },
  { value: 'update_tickers', label: 'Ticker List Update' },
] as const;

export const RunPanel: React.FC<RunPanelProps> = ({
  onRun,
  onCancel,
  activeJob,
  logs,
  runError,
}) => {
  const [command, setCommand] = useState<JobCreateRequest['command']>('backtest');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [tickers, setTickers] = useState('');
  const [singleTicker, setSingleTicker] = useState('AAPL');
  const [noCharts, setNoCharts] = useState(false);
  const [withFundamentals, setWithFundamentals] = useState(false);
  const [minMarketCap, setMinMarketCap] = useState('5000000000');
  const [maxTickers, setMaxTickers] = useState('');
  const [timeoutSeconds, setTimeoutSeconds] = useState('7200');
  const [submitting, setSubmitting] = useState(false);

  const isRunning = activeJob?.status === 'queued' || activeJob?.status === 'running';

  const statusColor = useMemo(() => {
    switch (activeJob?.status) {
      case 'queued':
        return '#7c3aed';
      case 'running':
        return '#2563eb';
      case 'succeeded':
        return '#15803d';
      case 'failed':
      case 'timeout':
        return '#b91c1c';
      case 'cancelled':
        return '#b45309';
      default:
        return '#4b5563';
    }
  }, [activeJob?.status]);

  const buildRequest = (): JobCreateRequest => {
    const req: JobCreateRequest = {
      command,
      timeout_seconds: Number(timeoutSeconds) || 7200,
    };

    if (command === 'backtest') {
      req.start_date = startDate;
      req.end_date = endDate;
      if (tickers.trim()) {
        req.tickers = tickers.trim();
      }
      req.no_charts = noCharts;
    }

    if (command === 'stage2') {
      req.with_fundamentals = withFundamentals;
    }

    if (command === 'chart') {
      req.ticker = singleTicker.trim().toUpperCase();
      req.start_date = startDate;
      req.end_date = endDate;
    }

    if (command === 'update_tickers') {
      const minValue = Number(minMarketCap);
      if (!Number.isNaN(minValue) && minValue > 0) {
        req.min_market_cap = minValue;
      }
      const maxValue = Number(maxTickers);
      if (!Number.isNaN(maxValue) && maxValue > 0) {
        req.max_tickers = maxValue;
      }
    }

    return req;
  };

  const handleRun = async () => {
    setSubmitting(true);
    try {
      await onRun(buildRequest());
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="run-panel">
      <div className="run-panel-header">
        <h3>Python Command Runner</h3>
        <div className="status-line">
          <span className="status-dot" style={{ background: statusColor }} />
          <span>
            {activeJob ? `Status: ${activeJob.status}` : 'Status: idle'}
          </span>
        </div>
      </div>

      <div className="run-grid">
        <label>
          Command
          <select
            value={command}
            onChange={(e) => setCommand(e.target.value as JobCreateRequest['command'])}
            disabled={isRunning || submitting}
          >
            {COMMAND_OPTIONS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        {(command === 'backtest' || command === 'chart') && (
          <>
            <label>
              Start Date
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
            <label>
              End Date
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
          </>
        )}

        {command === 'backtest' && (
          <>
            <label>
              Tickers (comma-separated, optional)
              <input
                type="text"
                value={tickers}
                placeholder="AAPL,MSFT,NVDA"
                onChange={(e) => setTickers(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={noCharts}
                onChange={(e) => setNoCharts(e.target.checked)}
                disabled={isRunning || submitting}
              />
              Skip chart generation (--no-charts)
            </label>
          </>
        )}

        {command === 'stage2' && (
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={withFundamentals}
              onChange={(e) => setWithFundamentals(e.target.checked)}
              disabled={isRunning || submitting}
            />
            Include fundamentals (--with-fundamentals)
          </label>
        )}

        {command === 'chart' && (
          <label>
            Ticker
            <input
              type="text"
              value={singleTicker}
              placeholder="AAPL"
              onChange={(e) => setSingleTicker(e.target.value.toUpperCase())}
              disabled={isRunning || submitting}
            />
          </label>
        )}

        {command === 'update_tickers' && (
          <>
            <label>
              Min Market Cap
              <input
                type="number"
                value={minMarketCap}
                onChange={(e) => setMinMarketCap(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
            <label>
              Max Tickers (optional)
              <input
                type="number"
                value={maxTickers}
                onChange={(e) => setMaxTickers(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
          </>
        )}

        <label>
          Timeout (seconds)
          <input
            type="number"
            min={30}
            max={86400}
            value={timeoutSeconds}
            onChange={(e) => setTimeoutSeconds(e.target.value)}
            disabled={isRunning || submitting}
          />
        </label>
      </div>

      <div className="run-actions">
        <button className="button-primary" onClick={handleRun} disabled={isRunning || submitting}>
          {submitting ? 'Starting...' : 'Run Command'}
        </button>
        <button className="button-secondary" onClick={onCancel} disabled={!isRunning || submitting}>
          Cancel Running Job
        </button>
      </div>

      {activeJob && (
        <div className="job-meta">
          <div><strong>Job ID:</strong> {activeJob.job_id}</div>
          <div><strong>Command:</strong> {activeJob.command_line}</div>
          {activeJob.error && <div className="run-error"><strong>Error:</strong> {activeJob.error}</div>}
        </div>
      )}

      {runError && <div className="run-error"><strong>Run Error:</strong> {runError}</div>}

      <div className="log-panel">
        <h4>Live Logs</h4>
        <pre>{logs.length ? logs.join('\n') : 'No logs yet.'}</pre>
      </div>
    </section>
  );
};
