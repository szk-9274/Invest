/**
 * TimeRangeControl Component (Phase C)
 *
 * Provides time range switching for chart view:
 * - Full period view
 * - Auto-focus from first Entry to last Exit
 * - User-controlled time range
 */
import React from 'react'

export type TimeRangeMode = 'full' | 'auto-focus' | 'custom'

export interface TimeRange {
  start: string
  end: string
}

export interface TradeRange {
  firstEntry: string | null
  lastExit: string | null
}

interface TimeRangeControlProps {
  mode: TimeRangeMode
  onModeChange: (mode: TimeRangeMode) => void
  customRange?: TimeRange
  onCustomRangeChange?: (range: TimeRange) => void
  tradeRange?: TradeRange
  fullRange?: TimeRange
}

/**
 * Calculate the auto-focus range from trade data.
 * Adds padding of 20 trading days (~1 month) before first entry
 * and after last exit for context.
 */
export function calculateAutoFocusRange(
  tradeRange: TradeRange,
  fullRange: TimeRange,
): TimeRange {
  if (!tradeRange.firstEntry || !tradeRange.lastExit) {
    return fullRange
  }

  // Add 30-day padding before first entry
  const paddedStart = new Date(tradeRange.firstEntry)
  paddedStart.setDate(paddedStart.getDate() - 30)
  const startStr = paddedStart.toISOString().split('T')[0]

  // Add 30-day padding after last exit
  const paddedEnd = new Date(tradeRange.lastExit)
  paddedEnd.setDate(paddedEnd.getDate() + 30)
  const endStr = paddedEnd.toISOString().split('T')[0]

  return {
    start: startStr < fullRange.start ? fullRange.start : startStr,
    end: endStr > fullRange.end ? fullRange.end : endStr,
  }
}

export function TimeRangeControl({
  mode,
  onModeChange,
  customRange,
  onCustomRangeChange,
  tradeRange,
  fullRange,
}: TimeRangeControlProps) {
  return (
    <div data-testid="time-range-control">
      <div data-testid="mode-buttons">
        <button
          data-testid="mode-full"
          onClick={() => onModeChange('full')}
          aria-pressed={mode === 'full'}
          style={{ fontWeight: mode === 'full' ? 'bold' : 'normal' }}
        >
          Full Period
        </button>
        <button
          data-testid="mode-auto-focus"
          onClick={() => onModeChange('auto-focus')}
          aria-pressed={mode === 'auto-focus'}
          style={{ fontWeight: mode === 'auto-focus' ? 'bold' : 'normal' }}
          disabled={!tradeRange?.firstEntry}
        >
          Trade Focus
        </button>
        <button
          data-testid="mode-custom"
          onClick={() => onModeChange('custom')}
          aria-pressed={mode === 'custom'}
          style={{ fontWeight: mode === 'custom' ? 'bold' : 'normal' }}
        >
          Custom
        </button>
      </div>

      {mode === 'custom' && (
        <div data-testid="custom-range-inputs">
          <input
            data-testid="custom-start"
            type="date"
            value={customRange?.start || ''}
            onChange={(e) =>
              onCustomRangeChange?.({
                start: e.target.value,
                end: customRange?.end || '',
              })
            }
          />
          <input
            data-testid="custom-end"
            type="date"
            value={customRange?.end || ''}
            onChange={(e) =>
              onCustomRangeChange?.({
                start: customRange?.start || '',
                end: e.target.value,
              })
            }
          />
        </div>
      )}
    </div>
  )
}
