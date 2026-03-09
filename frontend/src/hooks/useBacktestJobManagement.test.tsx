import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../api/jobs', () => ({
  createJob: vi.fn(),
  getJob: vi.fn(),
  getJobLogs: vi.fn(),
  cancelJob: vi.fn(),
}))

import { cancelJob, createJob, getJob, getJobLogs } from '../api/jobs'
import { useBacktestJobManagement } from './useBacktestJobManagement'

describe('useBacktestJobManagement', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts a job, refreshes logs, and reloads latest results when it succeeds', async () => {
    const onJobSucceeded = vi.fn().mockResolvedValue(undefined)

    vi.mocked(createJob).mockResolvedValue({
      job_id: 'job-1',
      command: 'backtest',
      command_line: 'python run.py',
      status: 'running',
      created_at: '2026-01-01T00:00:00Z',
      timeout_seconds: 600,
    })
    vi.mocked(getJobLogs).mockResolvedValue({ job_id: 'job-1', status: 'running', lines: ['line-a'] })
    vi.mocked(getJob).mockResolvedValue({
      job_id: 'job-1',
      command: 'backtest',
      command_line: 'python run.py',
      status: 'succeeded',
      created_at: '2026-01-01T00:00:00Z',
      timeout_seconds: 600,
    })

    const { result } = renderHook(() => useBacktestJobManagement({ onJobSucceeded, pollInterval: 1000 }))

    await act(async () => {
      await result.current.handleRunCommand({ command: 'backtest', start_date: '2024-01-01', end_date: '2024-01-31' })
    })

    expect(result.current.activeJob?.job_id).toBe('job-1')
    expect(result.current.jobLogs).toEqual(['line-a'])

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000)
    })

    expect(onJobSucceeded).toHaveBeenCalledTimes(1)
    expect(result.current.activeJob?.status).toBe('succeeded')
  })

  it('cancels the active job and keeps updated logs', async () => {
    vi.mocked(createJob).mockResolvedValue({
      job_id: 'job-2',
      command: 'backtest',
      command_line: 'python run.py',
      status: 'running',
      created_at: '2026-01-01T00:00:00Z',
      timeout_seconds: 600,
    })
    vi.mocked(getJobLogs)
      .mockResolvedValueOnce({ job_id: 'job-2', status: 'running', lines: ['queued'] })
      .mockResolvedValueOnce({ job_id: 'job-2', status: 'cancelled', lines: ['cancelled'] })
    vi.mocked(cancelJob).mockResolvedValue({
      job_id: 'job-2',
      command: 'backtest',
      command_line: 'python run.py',
      status: 'cancelled',
      created_at: '2026-01-01T00:00:00Z',
      timeout_seconds: 600,
    })

    const { result } = renderHook(() => useBacktestJobManagement({ onJobSucceeded: vi.fn() }))

    await act(async () => {
      await result.current.handleRunCommand({ command: 'backtest', start_date: '2024-01-01', end_date: '2024-01-31' })
    })

    await act(async () => {
      await result.current.handleCancelCommand()
    })

    expect(result.current.activeJob?.status).toBe('cancelled')
    expect(result.current.jobLogs).toEqual(['cancelled'])
  })
})
