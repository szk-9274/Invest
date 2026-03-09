import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from 'react'
import { useTranslation } from 'react-i18next'
import {
  fetchLatestBacktest,
  fetchBacktestResults,
  listAllBacktests,
  type BacktestMetadata,
  type BacktestResults,
} from '../api/backtest'
import { type JobCreateRequest, type JobResponse } from '../api/jobs'
import { useBacktestJobManagement } from './useBacktestJobManagement'

export interface UseBacktestDashboardStateResult {
  results: BacktestResults | null
  backtests: BacktestMetadata[]
  selectedTimestamp: string | null
  setSelectedTimestamp: Dispatch<SetStateAction<string | null>>
  loading: boolean
  error: string | null
  setError: Dispatch<SetStateAction<string | null>>
  activeJob: JobResponse | null
  jobLogs: string[]
  runError: string | null
  handleLoadLatest: () => Promise<void>
  handleRunCommand: (request: JobCreateRequest) => Promise<void>
  handleCancelCommand: () => Promise<void>
}

export function useBacktestDashboardState(): UseBacktestDashboardStateResult {
  const { t } = useTranslation()
  const [results, setResults] = useState<BacktestResults | null>(null)
  const [backtests, setBacktests] = useState<BacktestMetadata[]>([])
  const [selectedTimestamp, setSelectedTimestamp] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadBacktests = async () => {
      try {
        const data = await listAllBacktests()
        setBacktests(data)
        if (data.length > 0) {
          setSelectedTimestamp((current) => current ?? data[0].timestamp)
        }
      } catch (err) {
        setError(t('dashboard.loadBacktestListError', { error: String(err) }))
      }
    }

    void loadBacktests()
  }, [t])

  useEffect(() => {
    if (!selectedTimestamp) return

    const loadResults = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchBacktestResults(selectedTimestamp)
        setResults(data)
      } catch (err) {
        setError(t('dashboard.loadBacktestResultsError', { error: String(err) }))
      } finally {
        setLoading(false)
      }
    }

    void loadResults()
  }, [selectedTimestamp, t])

  const handleLoadLatest = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchLatestBacktest()
      setResults(data)
      setSelectedTimestamp(data.timestamp)
    } catch (err) {
      setError(t('dashboard.loadLatestError', { error: String(err) }))
    } finally {
      setLoading(false)
    }
  }, [t])

  const {
    activeJob,
    jobLogs,
    runError,
    handleRunCommand,
    handleCancelCommand,
  } = useBacktestJobManagement({
    onJobSucceeded: handleLoadLatest,
  })

  return {
    results,
    backtests,
    selectedTimestamp,
    setSelectedTimestamp,
    loading,
    error,
    setError,
    activeJob,
    jobLogs,
    runError,
    handleLoadLatest,
    handleRunCommand,
    handleCancelCommand,
  }
}
