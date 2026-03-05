/**
 * BacktestForm Component
 *
 * Provides input fields for start/end dates and a "Run Backtest" button.
 */
import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'

interface BacktestFormProps {
  onSubmit: (startDate: string, endDate: string) => void
  isLoading?: boolean
}

export function BacktestForm({ onSubmit, isLoading = false }: BacktestFormProps) {
  const { t } = useTranslation()
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
        <label htmlFor="start-date">{t('backtestForm.startDate')}</label>
        <input
          id="start-date"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="end-date">{t('backtestForm.endDate')}</label>
        <input
          id="end-date"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          required
        />
      </div>
      <button type="submit" disabled={isLoading || !startDate || !endDate}>
        {isLoading ? t('backtestForm.running') : t('backtestForm.runBacktest')}
      </button>
    </form>
  )
}
