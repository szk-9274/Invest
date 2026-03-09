import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

const PlotMock = () => null

async function loadHook(options?: {
  factoryModule?: unknown
  plotlyModule?: unknown
}) {
  vi.resetModules()
  vi.doMock('react-plotly.js/factory', () => options?.factoryModule ?? { default: vi.fn(() => PlotMock) })
  vi.doMock('plotly.js-dist-min', () => options?.plotlyModule ?? { default: { version: 'mock-plotly' } })
  return import('./useLazyPlotComponent')
}

describe('useLazyPlotComponent', () => {
  afterEach(() => {
    vi.resetModules()
    vi.doUnmock('react-plotly.js/factory')
    vi.doUnmock('plotly.js-dist-min')
  })

  it('does not load Plotly until enabled', async () => {
    const plotFactoryMock = vi.fn(() => PlotMock)
    const { useLazyPlotComponent } = await loadHook({
      factoryModule: { default: plotFactoryMock },
    })

    const { result, rerender } = renderHook(
      ({ enabled }) => useLazyPlotComponent(enabled),
      { initialProps: { enabled: false } },
    )

    await act(async () => {
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(result.current.PlotComponent).toBeNull()
    expect(plotFactoryMock).not.toHaveBeenCalled()

    rerender({ enabled: true })

    await waitFor(() => {
      expect(plotFactoryMock).toHaveBeenCalledTimes(1)
      expect(result.current.PlotComponent).not.toBeNull()
    })
  })

  it('clears the loaded Plot component when disabled again', async () => {
    const plotFactoryMock = vi.fn(() => PlotMock)
    const { useLazyPlotComponent } = await loadHook({
      factoryModule: { default: plotFactoryMock },
    })

    const { result, rerender } = renderHook(
      ({ enabled }) => useLazyPlotComponent(enabled),
      { initialProps: { enabled: true } },
    )

    await waitFor(() => {
      expect(plotFactoryMock).toHaveBeenCalledTimes(1)
      expect(result.current.PlotComponent).toBe(PlotMock)
    })

    rerender({ enabled: false })

    await waitFor(() => {
      expect(result.current.PlotComponent).toBeNull()
      expect(result.current.plotError).toBeNull()
    })
  })

  it('stores a readable error when Plotly loading fails', async () => {
    const { useLazyPlotComponent } = await loadHook({
      factoryModule: {
        get default() {
          throw new Error('factory load failed')
        },
      },
    })

    const { result } = renderHook(() => useLazyPlotComponent(true))

    await waitFor(() => {
      expect(result.current.PlotComponent).toBeNull()
      expect(result.current.plotError).toBe('factory load failed')
    })
  })
})
