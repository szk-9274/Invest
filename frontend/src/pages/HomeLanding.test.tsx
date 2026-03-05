import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { HomeLanding } from './HomeLanding'

describe('HomeLanding', () => {
  it('renders hero heading and CTA buttons', () => {
    render(
      <MemoryRouter>
        <HomeLanding />
      </MemoryRouter>,
    )

    expect(screen.getByText(/Bitcoin-first analytics home/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Subscribe Updates' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Open Dashboard' })).toBeInTheDocument()
  })

  it('renders feature cards and logo section', () => {
    render(
      <MemoryRouter>
        <HomeLanding />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText('Feature cards')).toBeInTheDocument()
    expect(screen.getByText('Bitcoin Treasury Insights')).toBeInTheDocument()
    expect(screen.getByLabelText('Partner logos')).toBeInTheDocument()
    expect(screen.getByText('METAPLANET')).toBeInTheDocument()
  })
})
