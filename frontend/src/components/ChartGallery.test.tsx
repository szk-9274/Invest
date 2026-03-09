import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ChartGallery } from './ChartGallery'

describe('ChartGallery', () => {
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
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) => typeof message === 'string' && message.includes('not wrapped in act'),
      ),
    ).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('renders loading and empty states', () => {
    const { rerender } = render(<ChartGallery charts={{}} loading />)
    expect(screen.getByText('Loading charts...')).toBeInTheDocument()

    rerender(<ChartGallery charts={{}} />)
    expect(screen.getByText('No charts available')).toBeInTheDocument()
  })

  it('groups charts and opens a modal when clicked', async () => {
    const user = userEvent.setup()

    render(
      <ChartGallery
        charts={{
          top_AAA: 'data:image/png;base64,aaa',
          bottom_CCC: 'data:image/png;base64,ccc',
          equity_curve: 'data:image/png;base64,eq',
        }}
      />,
    )

    expect(screen.getByText('Top Winners')).toBeInTheDocument()
    expect(screen.getByText('Bottom Losers')).toBeInTheDocument()
    expect(screen.getByText('Other Charts')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByAltText('top_AAA'))
    expect(screen.getAllByText('top AAA')).toHaveLength(2)

    await clickAndFlush(user, screen.getByRole('button', { name: '×' }))
    expect(screen.getAllByText('top AAA')).toHaveLength(1)
  })
})
