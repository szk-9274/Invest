import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from 'react'
import { useTranslation } from 'react-i18next'
import {
  fetchLatestBacktest,
  fetchBacktestResults,
  listAllBacktests,
  listStrategyProfiles,
  type BacktestMetadata,
  type BacktestResults,
  type StrategyProfile,
} from '../api/backtest'
import { type JobCreateRequest, type JobResponse } from '../api/jobs'
import { useBacktestJobManagement } from './useBacktestJobManagement'
import { localizeStrategyProfile } from '../utils/strategyProfileLocalization'

export interface UseBacktestDashboardStateResult {
  results: BacktestResults | null
  backtests: BacktestMetadata[]
  strategyProfiles: StrategyProfile[]
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
  const [strategyProfiles, setStrategyProfiles] = useState<StrategyProfile[]>([])
  const [selectedTimestamp, setSelectedTimestamp] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadBacktests = useCallback(async () => {
    const data = await listAllBacktests()
    setBacktests(data)
    if (data.length > 0) {
      setSelectedTimestamp((current) => current ?? data[0].timestamp)
    }
  }, [])

  const loadStrategyMetadata = useCallback(async () => {
    const data = await listStrategyProfiles()
    const localizedProfiles = data.map(localizeStrategyProfile)
    setStrategyProfiles(localizedProfiles)
  }, [])

  useEffect(() => {
    const loadInitialState = async () => {
      try {
        await Promise.all([loadBacktests(), loadStrategyMetadata()])
      } catch (err) {
        setError(t('dashboard.loadBacktestListError', { error: String(err) }))
      }
    }

    void loadInitialState()
  }, [loadBacktests, loadStrategyMetadata, t])

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
      await loadBacktests()
    } catch (err) {
      setError(t('dashboard.loadLatestError', { error: String(err) }))
    } finally {
      setLoading(false)
    }
  }, [loadBacktests, t])

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
    strategyProfiles,
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
