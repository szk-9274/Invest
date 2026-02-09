/**
 * Tests for TimeRangeControl component (Phase C)
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  TimeRangeControl,
  TimeRangeMode,
  calculateAutoFocusRange,
} from './TimeRangeControl'

describe('TimeRangeControl Component', () => {
  it('renders all mode buttons', () => {
    render(
      <TimeRangeControl mode="full" onModeChange={vi.fn()} />,
    )
    expect(screen.getByTestId('mode-full')).toBeInTheDocument()
    expect(screen.getByTestId('mode-auto-focus')).toBeInTheDocument()
    expect(screen.getByTestId('mode-custom')).toBeInTheDocument()
  })

  it('highlights active mode button', () => {
    render(
      <TimeRangeControl mode="full" onModeChange={vi.fn()} />,
    )
    expect(screen.getByTestId('mode-full')).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByTestId('mode-custom')).toHaveAttribute('aria-pressed', 'false')
  })

  it('calls onModeChange when button clicked', async () => {
    const mockChange = vi.fn()
    const user = userEvent.setup()
    render(
      <TimeRangeControl mode="full" onModeChange={mockChange} />,
    )

    await user.click(screen.getByTestId('mode-custom'))
    expect(mockChange).toHaveBeenCalledWith('custom')
  })

  it('shows custom date inputs when mode is custom', () => {
    render(
      <TimeRangeControl
        mode="custom"
        onModeChange={vi.fn()}
        customRange={{ start: '2024-01-01', end: '2024-12-31' }}
        onCustomRangeChange={vi.fn()}
      />,
    )
    expect(screen.getByTestId('custom-range-inputs')).toBeInTheDocument()
    expect(screen.getByTestId('custom-start')).toBeInTheDocument()
    expect(screen.getByTestId('custom-end')).toBeInTheDocument()
  })

  it('hides custom date inputs when mode is not custom', () => {
    render(
      <TimeRangeControl mode="full" onModeChange={vi.fn()} />,
    )
    expect(screen.queryByTestId('custom-range-inputs')).not.toBeInTheDocument()
  })

  it('disables auto-focus when no trade range', () => {
    render(
      <TimeRangeControl mode="full" onModeChange={vi.fn()} />,
    )
    expect(screen.getByTestId('mode-auto-focus')).toBeDisabled()
  })

  it('enables auto-focus when trade range is present', () => {
    render(
      <TimeRangeControl
        mode="full"
        onModeChange={vi.fn()}
        tradeRange={{ firstEntry: '2024-03-15', lastExit: '2024-09-30' }}
      />,
    )
    expect(screen.getByTestId('mode-auto-focus')).not.toBeDisabled()
  })
})

describe('calculateAutoFocusRange', () => {
  const fullRange = { start: '2024-01-01', end: '2024-12-31' }

  it('returns full range when no trade data', () => {
    const result = calculateAutoFocusRange(
      { firstEntry: null, lastExit: null },
      fullRange,
    )
    expect(result).toEqual(fullRange)
  })

  it('adds padding before first entry', () => {
    const result = calculateAutoFocusRange(
      { firstEntry: '2024-03-15', lastExit: '2024-09-30' },
      fullRange,
    )
    // 30 days before 2024-03-15 = 2024-02-14
    expect(new Date(result.start).getTime()).toBeLessThan(new Date('2024-03-15').getTime())
  })

  it('adds padding after last exit', () => {
    const result = calculateAutoFocusRange(
      { firstEntry: '2024-03-15', lastExit: '2024-09-30' },
      fullRange,
    )
    // 30 days after 2024-09-30 = 2024-10-30
    expect(new Date(result.end).getTime()).toBeGreaterThan(new Date('2024-09-30').getTime())
  })

  it('does not exceed full range boundaries', () => {
    const result = calculateAutoFocusRange(
      { firstEntry: '2024-01-05', lastExit: '2024-12-25' },
      fullRange,
    )
    expect(new Date(result.start).getTime()).toBeGreaterThanOrEqual(new Date(fullRange.start).getTime())
    expect(new Date(result.end).getTime()).toBeLessThanOrEqual(new Date(fullRange.end).getTime())
  })

  it('clamps start to full range start when padding exceeds it', () => {
    const result = calculateAutoFocusRange(
      { firstEntry: '2024-01-10', lastExit: '2024-06-15' },
      fullRange,
    )
    // 30 days before 2024-01-10 = 2023-12-11, which is before full range start
    expect(result.start).toBe(fullRange.start)
  })
})
