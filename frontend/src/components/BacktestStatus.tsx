import React, { useMemo } from 'react';
import { JobResponse } from '../api/jobs';

type Props = {
  activeJob: JobResponse | null;
  logs?: string[];
  latestLines?: number;
};

export const BacktestStatus: React.FC<Props> = ({ activeJob, logs = [], latestLines = 8 }) => {
  const status = activeJob?.status ?? 'idle';

  const elapsed = useMemo(() => {
    if (!activeJob) return null;
    const start = (activeJob.started_at || activeJob.created_at) ? new Date(activeJob.started_at || activeJob.created_at) : null;
    if (!start) return null;
    const diff = Math.max(0, Date.now() - start.getTime());
    const s = Math.floor(diff / 1000) % 60;
    const m = Math.floor(diff / 1000 / 60) % 60;
    const h = Math.floor(diff / 1000 / 3600);
    return h > 0 ? `${h}h ${m}m ${s}s` : m > 0 ? `${m}m ${s}s` : `${s}s`;
  }, [activeJob]);

  const dotColor = status === 'running' ? '#10b981' : status === 'queued' ? '#f59e0b' : status === 'succeeded' ? '#3b82f6' : status === 'failed' ? '#ef4444' : '#6b7280';

  const latest = logs.slice(-latestLines);

  return (
    <div className="backtest-status" style={{display: 'flex', alignItems: 'center', gap: 12}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
        <span className="status-dot" style={{background: dotColor}} aria-hidden />
        <div style={{display:'flex', flexDirection:'column'}}>
          <small style={{fontSize:12, color:'#cbd5e1'}}>{status.toUpperCase()}</small>
          {elapsed && <small style={{fontSize:12, color:'#e6eef8'}}>{elapsed}</small>}
        </div>
      </div>
      <div className="status-logs" style={{maxWidth:420}}>
        {latest.length > 0 ? (
          <pre style={{margin:0, padding:'6px 8px', background:'#0f172a', color:'#cbd5e1', borderRadius:6, fontSize:11, maxHeight:80, overflow:'auto'}}>{latest.join('\n')}</pre>
        ) : (
          <small style={{fontSize:12, color:'#94a3b8'}}>No recent logs</small>
        )}
      </div>
    </div>
  );
};
