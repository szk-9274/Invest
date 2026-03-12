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

const LOCALHOST_HOSTS = new Set(['localhost', '127.0.0.1'])
const NETWORK_UNAVAILABLE_TOKENS = [
  'failed to fetch',
  'econnrefused',
  'networkerror',
  'load failed',
]
const PROXY_UNAVAILABLE_TOKENS = [
  'internal server error',
  'bad gateway',
  'gateway timeout',
]
type DashboardRequestPhase = 'initial' | 'latest' | 'results'

function getErrorMessage(error: unknown): string {
  return error instanceof Error && error.message ? error.message : String(error)
}

function isLocalhostRuntime(): boolean {
  if (typeof window === 'undefined') {
    return true
  }

  return window.location.protocol === 'file:' || LOCALHOST_HOSTS.has(window.location.hostname)
}

function resolveBackendUnavailableDetail(error: unknown, phase: DashboardRequestPhase): string | null {
  if (!isLocalhostRuntime()) {
    return null
  }

  const message = getErrorMessage(error)
  const normalized = message.toLowerCase()
  if (NETWORK_UNAVAILABLE_TOKENS.some((token) => normalized.includes(token))) {
    return message
  }
  if (phase !== 'results' && PROXY_UNAVAILABLE_TOKENS.some((token) => normalized.includes(token))) {
    return message
  }
  return null
}

export interface UseBacktestDashboardStateResult {
  results: BacktestResults | null
  backtests: BacktestMetadata[]
  strategyProfiles: StrategyProfile[]
  selectedTimestamp: string | null
  setSelectedTimestamp: Dispatch<SetStateAction<string | null>>
  loading: boolean
  error: string | null
  backendUnavailableDetail: string | null
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
  const [backendUnavailableDetail, setBackendUnavailableDetail] = useState<string | null>(null)

  const setDashboardError = useCallback((err: unknown, translationKey: string, phase: DashboardRequestPhase) => {
    const unavailableDetail = resolveBackendUnavailableDetail(err, phase)
    if (unavailableDetail) {
      setBackendUnavailableDetail(unavailableDetail)
      setError(null)
      return
    }

    setBackendUnavailableDetail(null)
    setError(t(translationKey, { error: getErrorMessage(err) }))
  }, [t])

  const loadBacktests = useCallback(async () => {
    const data = await listAllBacktests()
    setBackendUnavailableDetail(null)
    setBacktests(data)
    if (data.length > 0) {
      setSelectedTimestamp((current) => current ?? data[0].timestamp)
    }
  }, [])

  const loadStrategyMetadata = useCallback(async () => {
    const data = await listStrategyProfiles()
    setBackendUnavailableDetail(null)
    const localizedProfiles = data.map(localizeStrategyProfile)
    setStrategyProfiles(localizedProfiles)
  }, [])

  useEffect(() => {
    const loadInitialState = async () => {
      try {
        setError(null)
        setBackendUnavailableDetail(null)
        await Promise.all([loadBacktests(), loadStrategyMetadata()])
      } catch (err) {
        setDashboardError(err, 'dashboard.loadBacktestListError', 'initial')
      }
    }

    void loadInitialState()
  }, [loadBacktests, loadStrategyMetadata, setDashboardError])

  useEffect(() => {
    if (!selectedTimestamp) return

    const loadResults = async () => {
      setLoading(true)
      setError(null)
      setBackendUnavailableDetail(null)
      try {
        const data = await fetchBacktestResults(selectedTimestamp)
        setBackendUnavailableDetail(null)
        setResults(data)
      } catch (err) {
        setDashboardError(err, 'dashboard.loadBacktestResultsError', 'results')
      } finally {
        setLoading(false)
      }
    }

    void loadResults()
  }, [selectedTimestamp, t])

  const handleLoadLatest = useCallback(async () => {
    setLoading(true)
    setError(null)
    setBackendUnavailableDetail(null)
    try {
      const data = await fetchLatestBacktest()
      setBackendUnavailableDetail(null)
      setResults(data)
      setSelectedTimestamp(data.timestamp)
      await loadBacktests()
    } catch (err) {
      setDashboardError(err, 'dashboard.loadLatestError', 'latest')
    } finally {
      setLoading(false)
    }
  }, [loadBacktests, setDashboardError])

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
    backendUnavailableDetail,
    setError,
    activeJob,
    jobLogs,
    runError,
    handleLoadLatest,
    handleRunCommand,
    handleCancelCommand,
  }
}
