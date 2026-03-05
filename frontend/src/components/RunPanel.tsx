import React, { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { JobCreateRequest, JobResponse } from '../api/jobs';

type RunPanelProps = {
  onRun: (request: JobCreateRequest) => Promise<void>;
  onCancel: () => Promise<void>;
  activeJob: JobResponse | null;
  logs: string[];
  runError: string | null;
};

const COMMAND_OPTIONS = [
  { value: 'backtest', labelKey: 'runPanel.options.backtest' },
  { value: 'stage2', labelKey: 'runPanel.options.stage2' },
  { value: 'full', labelKey: 'runPanel.options.full' },
  { value: 'chart', labelKey: 'runPanel.options.chart' },
  { value: 'update_tickers', labelKey: 'runPanel.options.updateTickers' },
] as const;

export const RunPanel: React.FC<RunPanelProps> = ({
  onRun,
  onCancel,
  activeJob,
  logs,
  runError,
}) => {
  const { t } = useTranslation();
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
        <h3>{t('runPanel.title')}</h3>
        <div className="status-line">
          <span className="status-dot" style={{ background: statusColor }} />
          <span>
            {activeJob
              ? `${t('runPanel.status')}: ${activeJob.status}`
              : `${t('runPanel.status')}: ${t('runPanel.idle')}`}
          </span>
        </div>
      </div>

      <div className="run-grid">
        <label>
          {t('runPanel.command')}
          <select
            value={command}
            onChange={(e) => setCommand(e.target.value as JobCreateRequest['command'])}
            disabled={isRunning || submitting}
          >
            {COMMAND_OPTIONS.map((item) => (
              <option key={item.value} value={item.value}>
                {t(item.labelKey)}
              </option>
            ))}
          </select>
        </label>

        {(command === 'backtest' || command === 'chart') && (
          <>
            <label>
              {t('runPanel.startDate')}
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
            <label>
              {t('runPanel.endDate')}
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
              {t('runPanel.tickersOptional')}
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
              {t('runPanel.skipCharts')}
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
            {t('runPanel.includeFundamentals')}
          </label>
        )}

        {command === 'chart' && (
          <label>
            {t('runPanel.ticker')}
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
              {t('runPanel.minMarketCap')}
              <input
                type="number"
                value={minMarketCap}
                onChange={(e) => setMinMarketCap(e.target.value)}
                disabled={isRunning || submitting}
              />
            </label>
            <label>
              {t('runPanel.maxTickersOptional')}
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
          {t('runPanel.timeoutSeconds')}
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
          {submitting ? t('runPanel.starting') : t('runPanel.runCommand')}
        </button>
        <button className="button-secondary" onClick={onCancel} disabled={!isRunning || submitting}>
          {t('runPanel.cancelRunningJob')}
        </button>
      </div>

      {activeJob && (
        <div className="job-meta">
          <div><strong>{t('runPanel.jobId')}:</strong> {activeJob.job_id}</div>
          <div><strong>{t('runPanel.commandLine')}:</strong> {activeJob.command_line}</div>
          {activeJob.error && <div className="run-error"><strong>{t('runPanel.error')}:</strong> {activeJob.error}</div>}
        </div>
      )}

      {runError && <div className="run-error"><strong>{t('runPanel.runError')}:</strong> {runError}</div>}

      <div className="log-panel">
        <h4>{t('runPanel.liveLogs')}</h4>
        <pre>{logs.length ? logs.join('\n') : t('runPanel.noLogsYet')}</pre>
      </div>
    </section>
  );
};
