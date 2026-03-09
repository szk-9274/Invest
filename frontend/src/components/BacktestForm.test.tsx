/**
 * Tests for BacktestForm component
 */
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BacktestForm } from './BacktestForm'

describe('BacktestForm', () => {
  let consoleErrorSpy: {
    mock: { calls: unknown[][] }
    mockRestore: () => void
  }

  async function flushAsyncUpdates() {
    await Promise.resolve()
    await Promise.resolve()
  }

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) => typeof message === 'string' && message.includes('not wrapped in act'),
      ),
    ).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('renders start date and end date inputs', () => {
    render(<BacktestForm onSubmit={vi.fn()} />)
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument()
  })

  it('renders Run Backtest button', () => {
    render(<BacktestForm onSubmit={vi.fn()} />)
    expect(screen.getByRole('button', { name: /run backtest/i })).toBeInTheDocument()
  })

  it('button is disabled when dates are empty', () => {
    render(<BacktestForm onSubmit={vi.fn()} />)
    const button = screen.getByRole('button', { name: /run backtest/i })
    expect(button).toBeDisabled()
  })

  it('button is disabled when isLoading is true', () => {
    render(<BacktestForm onSubmit={vi.fn()} isLoading={true} />)
    expect(screen.getByRole('button', { name: /running/i })).toBeDisabled()
  })

  it('calls onSubmit with dates when form is submitted', async () => {
    const mockSubmit = vi.fn()
    const user = userEvent.setup()
    render(<BacktestForm onSubmit={mockSubmit} />)

    const startInput = screen.getByLabelText(/start date/i)
    const endInput = screen.getByLabelText(/end date/i)

    await act(async () => {
      await user.type(startInput, '2024-01-01')
      await user.type(endInput, '2024-12-31')
      await flushAsyncUpdates()
    })

    const button = screen.getByRole('button', { name: /run backtest/i })
    await act(async () => {
      await user.click(button)
      await flushAsyncUpdates()
    })

    expect(mockSubmit).toHaveBeenCalledWith('2024-01-01', '2024-12-31')
  })

  it('shows "Running..." text when loading', () => {
    render(<BacktestForm onSubmit={vi.fn()} isLoading={true} />)
    expect(screen.getByText(/running/i)).toBeInTheDocument()
  })
})
