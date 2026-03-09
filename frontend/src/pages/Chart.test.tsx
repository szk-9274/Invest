/**
 * Tests for Chart page
 */
import { describe, it, expect, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { Chart } from './Chart'

describe('Chart', () => {
  it('renders ticker name in title', () => {
    render(<Chart ticker="AAPL" />)
    expect(screen.getByTestId('chart-title')).toHaveTextContent('AAPL Chart')
  })

  it('renders chart container', () => {
    render(<Chart ticker="AAPL" />)
    expect(screen.getByTestId('chart-container')).toBeInTheDocument()
  })

  it('renders back button when onBack is provided', () => {
    render(<Chart ticker="AAPL" onBack={vi.fn()} />)
    expect(screen.getByTestId('back-button')).toBeInTheDocument()
  })

  it('does not render back button when onBack is not provided', () => {
    render(<Chart ticker="AAPL" />)
    expect(screen.queryByTestId('back-button')).not.toBeInTheDocument()
  })

  it('calls onBack when back button is clicked', async () => {
    const mockBack = vi.fn()
    const user = userEvent.setup()
    render(<Chart ticker="AAPL" onBack={mockBack} />)

    await user.click(screen.getByTestId('back-button'))
    expect(mockBack).toHaveBeenCalled()
  })

  it('renders chart-page data-testid', () => {
    render(<Chart ticker="MSFT" />)
    expect(screen.getByTestId('chart-page')).toBeInTheDocument()
  })

  it('uses the route ticker and shows a back button inside router context', () => {
    render(
      <MemoryRouter
        initialEntries={['/chart/TSLA']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/chart/:ticker" element={<Chart />} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByTestId('chart-title')).toHaveTextContent('TSLA Chart')
    expect(screen.getByTestId('back-button')).toBeInTheDocument()
  })

  it('navigates back to the home route when the router back button is clicked', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter
        initialEntries={['/chart/NVDA']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/" element={<div>Home route</div>} />
          <Route path="/chart/:ticker" element={<Chart />} />
        </Routes>
      </MemoryRouter>,
    )

    await act(async () => {
      await user.click(screen.getByTestId('back-button'))
    })

    expect(screen.getByText('Home route')).toBeInTheDocument()
  })
})
