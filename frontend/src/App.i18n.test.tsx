import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { setAppLanguage } from './i18n'

describe('App language toggle', () => {
  let consoleErrorSpy: {
    mock: { calls: unknown[][] }
    mockRestore: () => void
  }

  async function flushAsyncUpdates() {
    await Promise.resolve()
    await Promise.resolve()
  }

  async function clickAndFlush(user: ReturnType<typeof userEvent.setup>, target: Element) {
    await act(async () => {
      await user.click(target)
      await flushAsyncUpdates()
    })
  }

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    setAppLanguage('en')
    window.history.replaceState({}, '', '/home?lang=en')
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) =>
          typeof message === 'string'
          && (message.includes('not wrapped in act') || message.includes('React Router Future Flag Warning')),
      ),
    ).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('switches UI labels to Japanese when JA button is clicked', async () => {
    const user = userEvent.setup()
    render(<App />)

    await clickAndFlush(user, screen.getByRole('button', { name: 'JA' }))

    await waitFor(() => {
      expect(screen.getByRole('link', { name: 'ホーム' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'バックテストダッシュボード' })).toBeInTheDocument()
    })
  })

  it('switches the brand label to the dashboard title only on dashboard routes', async () => {
    const user = userEvent.setup()
    render(<App />)

    await clickAndFlush(user, screen.getByRole('button', { name: 'JA' }))
    expect(screen.getByRole('link', { name: '株式スクリーニング' })).toBeInTheDocument()

    await clickAndFlush(user, screen.getByRole('link', { name: 'バックテストダッシュボード' }))

    await waitFor(() => {
      expect(screen.queryByRole('link', { name: '株式スクリーニング' })).not.toBeInTheDocument()
      expect(screen.getAllByRole('link', { name: 'バックテストダッシュボード' }).length).toBeGreaterThan(1)
      expect(screen.getByRole('button', { name: '最新データを再読み込み' })).toBeInTheDocument()
    })
  })

  it('toggles mobile navigation menu state and closes after navigation click', async () => {
    const user = userEvent.setup()
    render(<App />)

    const menuButton = screen.getByRole('button', { name: 'Open navigation menu' })
    expect(menuButton).toHaveAttribute('aria-expanded', 'false')

    await clickAndFlush(user, menuButton)
    expect(menuButton).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByTestId('app-nav-links')).toHaveClass('mobile-open')

    await clickAndFlush(user, screen.getByRole('link', { name: 'Backtest Dashboard' }))
    await waitFor(() => {
      expect(menuButton).toHaveAttribute('aria-expanded', 'false')
      expect(screen.getByTestId('app-nav-links')).not.toHaveClass('mobile-open')
    })
  })
})
