import { beforeEach, describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import { setAppLanguage } from './i18n'

describe('App language toggle', () => {
  beforeEach(() => {
    setAppLanguage('en')
    window.history.replaceState({}, '', '/home?lang=en')
  })

  it('switches UI labels to Japanese when JA button is clicked', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole('button', { name: 'JA' }))

    expect(screen.getByRole('link', { name: 'ホーム' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'バックテストダッシュボード' })).toBeInTheDocument()
  })

  it('toggles mobile navigation menu state and closes after navigation click', async () => {
    const user = userEvent.setup()
    render(<App />)

    const menuButton = screen.getByRole('button', { name: 'Open navigation menu' })
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')

    await user.click(menuButton)
    expect(menuButton).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByTestId('app-nav-links')).toHaveClass('mobile-open')

    await user.click(screen.getByRole('link', { name: 'Backtest Dashboard' }))
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')
    expect(screen.getByTestId('app-nav-links')).not.toHaveClass('mobile-open')
  })
})
