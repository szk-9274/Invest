/**
 * Tests for Home page
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Home } from './Home'
import { getTopBottomTickers } from '../api/client'

// Mock the API client
vi.mock('../api/client', () => ({
  runBacktest: vi.fn().mockResolvedValue({ status: 'started', message: 'Backtest started' }),
  getTopBottomTickers: vi.fn().mockResolvedValue({ top: [], bottom: [] }),
}))

const mockGetTopBottomTickers = vi.mocked(getTopBottomTickers)

async function renderHome() {
  render(
    <MemoryRouter>
      <Home />
    </MemoryRouter>,
  )
  await waitFor(() => expect(mockGetTopBottomTickers).toHaveBeenCalled())
}

describe('Home', () => {
  beforeEach(() => {
    mockGetTopBottomTickers.mockClear()
  })

  it('renders the page title', async () => {
    await renderHome()
    expect(screen.getByText('Invest Backtest Dashboard')).toBeInTheDocument()
  })

  it('renders the backtest form', async () => {
    await renderHome()
    expect(screen.getByTestId('backtest-form')).toBeInTheDocument()
  })

  it('renders ticker lists', async () => {
    await renderHome()
    expect(screen.getByText('Top 5 Winners')).toBeInTheDocument()
    expect(screen.getByText('Bottom 5 Losers')).toBeInTheDocument()
  })

  it('renders home page data-testid', async () => {
    await renderHome()
    expect(screen.getByTestId('home-page')).toBeInTheDocument()
  })
})
