export function getBacktestStatusDotColor(status?: string | null) {
  if (status === 'running') return '#10b981'
  if (status === 'queued') return '#f59e0b'
  if (status === 'succeeded') return '#3b82f6'
  if (status === 'failed') return '#ef4444'
  if (status === 'cancelled') return '#64748b'
  return '#6b7280'
}

export function getBacktestStatusTranslationKey(status?: string | null, hasLogs = false) {
  if (!status || status === 'idle') {
    return hasLogs ? 'dashboard.statusLogsAvailable' : 'dashboard.statusNoLogs'
  }
  if (status === 'queued') return 'dashboard.statusQueued'
  if (status === 'running') return 'dashboard.statusRunning'
  if (status === 'succeeded') return 'dashboard.statusSucceeded'
  if (status === 'failed') return 'dashboard.statusFailed'
  if (status === 'cancelled') return 'dashboard.statusCancelled'
  return 'dashboard.statusIdle'
}

export function formatElapsedDuration(diffMs: number, language: string) {
  const totalSeconds = Math.max(0, Math.floor(diffMs / 1000))
  const seconds = totalSeconds % 60
  const minutes = Math.floor(totalSeconds / 60) % 60
  const hours = Math.floor(totalSeconds / 3600)

  if (language === 'ja') {
    if (hours > 0) return `${hours}時間 ${minutes}分 ${seconds}秒`
    if (minutes > 0) return `${minutes}分 ${seconds}秒`
    return `${seconds}秒`
  }

  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}
