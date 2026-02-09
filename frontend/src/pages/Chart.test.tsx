/**
 * Tests for Chart page
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
})
