/**
 * Tests for Home page
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Home } from './Home'

// Mock the API client
vi.mock('../api/client', () => ({
  runBacktest: vi.fn().mockResolvedValue({ status: 'started', message: 'Backtest started' }),
  getTopBottomTickers: vi.fn().mockResolvedValue({ top: [], bottom: [] }),
}))

describe('Home', () => {
  it('renders the page title', () => {
    render(<Home />)
    expect(screen.getByText('Invest Backtest')).toBeInTheDocument()
  })

  it('renders the backtest form', () => {
    render(<Home />)
    expect(screen.getByTestId('backtest-form')).toBeInTheDocument()
  })

  it('renders ticker lists', () => {
    render(<Home />)
    expect(screen.getByText('Top 5 Winners')).toBeInTheDocument()
    expect(screen.getByText('Bottom 5 Losers')).toBeInTheDocument()
  })

  it('renders home page data-testid', () => {
    render(<Home />)
    expect(screen.getByTestId('home-page')).toBeInTheDocument()
  })
})
