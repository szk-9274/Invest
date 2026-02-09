/**
 * BacktestForm Component
 *
 * Provides input fields for start/end dates and a "Run Backtest" button.
 */
import React, { useState } from 'react'

interface BacktestFormProps {
  onSubmit: (startDate: string, endDate: string) => void
  isLoading?: boolean
}

export function BacktestForm({ onSubmit, isLoading = false }: BacktestFormProps) {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (startDate && endDate) {
      onSubmit(startDate, endDate)
    }
  }

  return (
    <form onSubmit={handleSubmit} data-testid="backtest-form">
      <div>
        <label htmlFor="start-date">Start Date</label>
        <input
          id="start-date"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="end-date">End Date</label>
        <input
          id="end-date"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          required
        />
      </div>
      <button type="submit" disabled={isLoading || !startDate || !endDate}>
        {isLoading ? 'Running...' : 'Run Backtest'}
      </button>
    </form>
  )
}
