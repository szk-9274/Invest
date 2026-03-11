import React, { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { JobResponse } from '../api/jobs'
import { formatElapsedDuration, getBacktestStatusDotColor, getBacktestStatusTranslationKey } from '../utils/backtestStatus'

type Props = {
  activeJob: JobResponse | null
  logs?: string[]
  latestLines?: number
}

export const BacktestStatus: React.FC<Props> = ({ activeJob, logs = [], latestLines = 8 }) => {
  const { t, i18n } = useTranslation()
  const latest = logs.slice(-latestLines)
  const status = activeJob?.status ?? 'idle'
  const statusLabel = t(getBacktestStatusTranslationKey(activeJob?.status, latest.length > 0))

  const elapsed = useMemo(() => {
    if (!activeJob) return null
    const startedAt = activeJob.started_at || activeJob.created_at
    if (!startedAt) return null
    const start = new Date(startedAt)
    if (Number.isNaN(start.getTime())) return null
    return formatElapsedDuration(Date.now() - start.getTime(), i18n.resolvedLanguage ?? 'en')
  }, [activeJob, i18n.resolvedLanguage])

  const dotColor = getBacktestStatusDotColor(status)

  return (
    <div className="backtest-status" style={{display: 'flex', alignItems: 'center', gap: 12}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
        <span className="status-dot" style={{background: dotColor}} aria-hidden />
        <div style={{display:'flex', flexDirection:'column'}}>
          <small style={{fontSize:12, color:'#cbd5e1'}}>{t('dashboard.chromeStatus', { status: statusLabel })}</small>
          {elapsed && <small style={{fontSize:12, color:'#e6eef8'}}>{elapsed}</small>}
        </div>
      </div>
      <div className="status-logs" style={{maxWidth:420}}>
        {latest.length > 0 ? (
          <pre style={{margin:0, padding:'6px 8px', background:'#0f172a', color:'#cbd5e1', borderRadius:6, fontSize:11, maxHeight:80, overflow:'auto'}}>{latest.join('\n')}</pre>
        ) : (
          <small style={{fontSize:12, color:'#94a3b8'}}>{t('dashboard.statusNoLogs')}</small>
        )}
      </div>
    </div>
  )
}
