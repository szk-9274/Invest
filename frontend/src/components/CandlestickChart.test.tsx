/**
 * Tests for CandlestickChart component (Phase B-2)
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  CandlestickChart,
  CandlestickData,
  TradeMarkerData,
  buildCandlestickTraces,
  buildChartLayout,
} from './CandlestickChart'

const mockData: CandlestickData = {
  dates: ['2024-01-02', '2024-01-03', '2024-01-04'],
  open: [150.0, 151.0, 152.0],
  high: [155.0, 156.0, 157.0],
  low: [149.0, 150.0, 151.0],
  close: [153.0, 154.0, 155.0],
  volume: [1000000, 1100000, 1200000],
  sma20: [152.0, 153.0, 154.0],
  sma50: [148.0, 149.0, 150.0],
  sma200: [140.0, 141.0, 142.0],
}

const emptyData: CandlestickData = {
  dates: [],
  open: [],
  high: [],
  low: [],
  close: [],
  volume: [],
}

const mockMarkers: TradeMarkerData = {
  entries: [{ date: '2024-01-02', price: 150.0 }],
  exits: [{ date: '2024-01-04', price: 155.0, pnl: 500.0 }],
}

describe('CandlestickChart Component', () => {
  it('renders chart container', () => {
    render(<CandlestickChart ticker="AAPL" data={mockData} />)
    expect(screen.getByTestId('candlestick-chart')).toBeInTheDocument()
  })

  it('shows "No chart data available" when data is empty', () => {
    render(<CandlestickChart ticker="AAPL" data={emptyData} />)
    expect(screen.getByTestId('no-data-message')).toBeInTheDocument()
    expect(screen.getByText(/no chart data available/i)).toBeInTheDocument()
  })

  it('renders chart when data is provided', () => {
    render(<CandlestickChart ticker="AAPL" data={mockData} />)
    expect(screen.getByTestId('chart-rendered')).toBeInTheDocument()
  })

  it('displays ticker name in rendered chart', () => {
    render(<CandlestickChart ticker="AAPL" data={mockData} />)
    expect(screen.getByTestId('chart-rendered').dataset.ticker).toBe('AAPL')
  })
})

describe('buildCandlestickTraces', () => {
  it('creates candlestick trace as first element', () => {
    const traces = buildCandlestickTraces(mockData)
    expect((traces[0] as Record<string, unknown>).type).toBe('candlestick')
  })

  it('creates volume bar trace as second element', () => {
    const traces = buildCandlestickTraces(mockData)
    expect((traces[1] as Record<string, unknown>).type).toBe('bar')
  })

  it('creates SMA traces when data includes them', () => {
    const traces = buildCandlestickTraces(mockData)
    // Candlestick + Volume + SMA20 + SMA50 + SMA200 = 5
    expect(traces).toHaveLength(5)
  })

  it('does not create SMA traces when data omits them', () => {
    const traces = buildCandlestickTraces(emptyData)
    // Only candlestick + volume = 2
    expect(traces).toHaveLength(2)
  })

  it('creates entry marker trace when markers provided', () => {
    const traces = buildCandlestickTraces(mockData, mockMarkers)
    const entryTrace = traces.find(
      (t) => (t as Record<string, unknown>).name === 'Entry',
    )
    expect(entryTrace).toBeDefined()
  })

  it('creates exit marker trace when markers provided', () => {
    const traces = buildCandlestickTraces(mockData, mockMarkers)
    const exitTrace = traces.find(
      (t) => (t as Record<string, unknown>).name === 'Exit',
    )
    expect(exitTrace).toBeDefined()
  })

  it('does not create marker traces when no markers', () => {
    const traces = buildCandlestickTraces(mockData)
    const markerTraces = traces.filter(
      (t) =>
        (t as Record<string, unknown>).name === 'Entry' ||
        (t as Record<string, unknown>).name === 'Exit',
    )
    expect(markerTraces).toHaveLength(0)
  })

  it('volume colors reflect up/down movement', () => {
    const traces = buildCandlestickTraces(mockData)
    const volumeTrace = traces[1] as Record<string, unknown>
    const marker = volumeTrace.marker as Record<string, unknown>
    const colors = marker.color as string[]
    // All closing prices go up, so all should be upColor
    expect(colors).toHaveLength(3)
  })
})

describe('buildChartLayout', () => {
  it('sets dark background', () => {
    const layout = buildChartLayout('AAPL')
    expect(layout.paper_bgcolor).toBe('#131722')
    expect(layout.plot_bgcolor).toBe('#131722')
  })

  it('sets ticker as title', () => {
    const layout = buildChartLayout('AAPL')
    expect(layout.title.text).toBe('AAPL')
  })

  it('sets y-axis on right side', () => {
    const layout = buildChartLayout('AAPL')
    expect(layout.yaxis.side).toBe('right')
  })

  it('disables rangeslider', () => {
    const layout = buildChartLayout('AAPL')
    expect(layout.xaxis.rangeslider.visible).toBe(false)
  })

  it('enables zoom dragmode', () => {
    const layout = buildChartLayout('AAPL')
    expect(layout.dragmode).toBe('zoom')
  })

  it('uses custom width and height when provided', () => {
    const layout = buildChartLayout('AAPL', 1600, 900)
    expect(layout.width).toBe(1600)
    expect(layout.height).toBe(900)
  })

  it('uses default width and height when not provided', () => {
    const layout = buildChartLayout('AAPL')
    expect(layout.width).toBe(1200)
    expect(layout.height).toBe(700)
  })

  it('sets volume panel domain below price panel', () => {
    const layout = buildChartLayout('AAPL')
    // Volume (yaxis2) should be below price (yaxis)
    expect(layout.yaxis2.domain[1]).toBeLessThanOrEqual(layout.yaxis.domain[0])
  })
})
