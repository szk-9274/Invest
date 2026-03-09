import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  cancelJob,
  createJob,
  getJob,
  getJobLogs,
  type JobCreateRequest,
  type JobResponse,
} from '../api/jobs'

interface UseBacktestJobManagementOptions {
  onJobSucceeded?: () => Promise<void> | void
  pollInterval?: number
  logTail?: number
}

export interface UseBacktestJobManagementResult {
  activeJob: JobResponse | null
  jobLogs: string[]
  runError: string | null
  handleRunCommand: (request: JobCreateRequest) => Promise<void>
  handleCancelCommand: () => Promise<void>
}

export function useBacktestJobManagement({
  onJobSucceeded,
  pollInterval = 2000,
  logTail = 300,
}: UseBacktestJobManagementOptions = {}): UseBacktestJobManagementResult {
  const { t } = useTranslation()
  const [activeJob, setActiveJob] = useState<JobResponse | null>(null)
  const [jobLogs, setJobLogs] = useState<string[]>([])
  const [runError, setRunError] = useState<string | null>(null)

  const refreshJobLogs = useCallback(async (jobId: string) => {
    const logs = await getJobLogs(jobId, logTail)
    setJobLogs(logs.lines)
  }, [logTail])

  const handleRunCommand = useCallback(async (request: JobCreateRequest) => {
    setRunError(null)
    try {
      const job = await createJob(request)
      setActiveJob(job)
      setJobLogs([])
      await refreshJobLogs(job.job_id)
    } catch (error) {
      setRunError(t('dashboard.startCommandError', { error: String(error) }))
    }
  }, [refreshJobLogs, t])

  const handleCancelCommand = useCallback(async () => {
    if (!activeJob) return

    setRunError(null)
    try {
      const cancelled = await cancelJob(activeJob.job_id)
      setActiveJob(cancelled)
      await refreshJobLogs(cancelled.job_id)
    } catch (error) {
      setRunError(t('dashboard.cancelCommandError', { error: String(error) }))
    }
  }, [activeJob, refreshJobLogs, t])

  useEffect(() => {
    if (!activeJob) return
    if (activeJob.status !== 'queued' && activeJob.status !== 'running') return

    const timer = window.setInterval(async () => {
      try {
        const latest = await getJob(activeJob.job_id)
        setActiveJob(latest)
        await refreshJobLogs(latest.job_id)

        if (latest.status === 'succeeded') {
          await onJobSucceeded?.()
        }
      } catch (error) {
        setRunError(t('dashboard.pollJobStatusError', { error: String(error) }))
      }
    }, pollInterval)

    return () => window.clearInterval(timer)
  }, [activeJob?.job_id, activeJob?.status, onJobSucceeded, pollInterval, refreshJobLogs, t])

  return {
    activeJob,
    jobLogs,
    runError,
    handleRunCommand,
    handleCancelCommand,
  }
}
