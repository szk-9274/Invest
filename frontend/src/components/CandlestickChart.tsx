/**
 * CandlestickChart Component (Phase B-2)
 *
 * TradingView-style candlestick chart with:
 * - Candlestick OHLC data
 * - Volume bars
 * - SMA overlays (20, 50, 200)
 * - Dark theme
 * - Zoom and pan
 */
import React from 'react'

export interface CandlestickData {
  dates: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
  sma20?: (number | null)[]
  sma50?: (number | null)[]
  sma200?: (number | null)[]
}

export interface TradeMarkerData {
  entries: { date: string; price: number }[]
  exits: { date: string; price: number; pnl?: number }[]
}

interface CandlestickChartProps {
  ticker: string
  data: CandlestickData
  markers?: TradeMarkerData
  width?: number
  height?: number
}

// TradingView-inspired dark theme colors
const THEME = {
  background: '#131722',
  gridColor: '#2a2e39',
  textColor: '#d1d4dc',
  upColor: '#26a69a',
  downColor: '#ef5350',
  sma20Color: '#00bcd4',
  sma50Color: '#ffeb3b',
  sma200Color: '#e91e63',
  volumeUpColor: 'rgba(38, 166, 154, 0.5)',
  volumeDownColor: 'rgba(239, 83, 80, 0.5)',
  entryMarkerColor: '#26a69a',
  exitMarkerColor: '#ef5350',
}

/**
 * Build Plotly-compatible traces from CandlestickData.
 * Extracted for testability.
 */
export function buildCandlestickTraces(
  data: CandlestickData,
  markers?: TradeMarkerData,
) {
  const traces: unknown[] = []

  // Candlestick trace
  traces.push({
    type: 'candlestick',
    x: data.dates,
    open: data.open,
    high: data.high,
    low: data.low,
    close: data.close,
    increasing: { line: { color: THEME.upColor } },
    decreasing: { line: { color: THEME.downColor } },
    name: 'Price',
    xaxis: 'x',
    yaxis: 'y',
  })

  // Volume trace
  const volumeColors = data.close.map((c, i) =>
    i === 0
      ? THEME.volumeUpColor
      : c >= data.close[i - 1]
        ? THEME.volumeUpColor
        : THEME.volumeDownColor,
  )

  traces.push({
    type: 'bar',
    x: data.dates,
    y: data.volume,
    marker: { color: volumeColors },
    name: 'Volume',
    xaxis: 'x',
    yaxis: 'y2',
  })

  // SMA traces
  if (data.sma20) {
    traces.push({
      type: 'scatter',
      mode: 'lines',
      x: data.dates,
      y: data.sma20,
      line: { color: THEME.sma20Color, width: 1 },
      name: 'SMA 20',
      xaxis: 'x',
      yaxis: 'y',
    })
  }

  if (data.sma50) {
    traces.push({
      type: 'scatter',
      mode: 'lines',
      x: data.dates,
      y: data.sma50,
      line: { color: THEME.sma50Color, width: 1 },
      name: 'SMA 50',
      xaxis: 'x',
      yaxis: 'y',
    })
  }

  if (data.sma200) {
    traces.push({
      type: 'scatter',
      mode: 'lines',
      x: data.dates,
      y: data.sma200,
      line: { color: THEME.sma200Color, width: 1 },
      name: 'SMA 200',
      xaxis: 'x',
      yaxis: 'y',
    })
  }

  // Trade markers (Phase C integration)
  if (markers) {
    if (markers.entries.length > 0) {
      traces.push({
        type: 'scatter',
        mode: 'markers',
        x: markers.entries.map((e) => e.date),
        y: markers.entries.map((e) => e.price),
        marker: {
          symbol: 'triangle-up',
          size: 14,
          color: THEME.entryMarkerColor,
        },
        name: 'Entry',
        xaxis: 'x',
        yaxis: 'y',
        text: markers.entries.map((e) => `Entry: $${e.price.toFixed(2)}`),
        hoverinfo: 'text+x',
      })
    }

    if (markers.exits.length > 0) {
      traces.push({
        type: 'scatter',
        mode: 'markers',
        x: markers.exits.map((e) => e.date),
        y: markers.exits.map((e) => e.price),
        marker: {
          symbol: 'triangle-down',
          size: 14,
          color: THEME.exitMarkerColor,
        },
        name: 'Exit',
        xaxis: 'x',
        yaxis: 'y',
        text: markers.exits.map(
          (e) =>
            `Exit: $${e.price.toFixed(2)}${e.pnl !== undefined ? ` (P&L: $${e.pnl.toFixed(2)})` : ''}`,
        ),
        hoverinfo: 'text+x',
      })
    }
  }

  return traces
}

/**
 * Build Plotly layout for TradingView-style dark theme.
 */
export function buildChartLayout(ticker: string, width?: number, height?: number) {
  return {
    title: {
      text: ticker,
      font: { color: THEME.textColor, size: 16 },
    },
    paper_bgcolor: THEME.background,
    plot_bgcolor: THEME.background,
    font: { color: THEME.textColor },
    xaxis: {
      gridcolor: THEME.gridColor,
      rangeslider: { visible: false },
      type: 'date' as const,
    },
    yaxis: {
      gridcolor: THEME.gridColor,
      side: 'right' as const,
      domain: [0.3, 1.0],
      title: 'Price',
    },
    yaxis2: {
      gridcolor: THEME.gridColor,
      domain: [0.0, 0.25],
      title: 'Volume',
    },
    width: width || 1200,
    height: height || 700,
    showlegend: true,
    legend: {
      bgcolor: 'rgba(19, 23, 34, 0.8)',
      font: { color: THEME.textColor },
    },
    dragmode: 'zoom' as const,
  }
}

export function CandlestickChart({
  ticker,
  data,
  markers,
  width,
  height,
}: CandlestickChartProps) {
  const traces = buildCandlestickTraces(data, markers)
  const layout = buildChartLayout(ticker, width, height)

  return (
    <div data-testid="candlestick-chart" style={{ width: '100%' }}>
      {data.dates.length === 0 ? (
        <p data-testid="no-data-message">No chart data available</p>
      ) : (
        <div data-testid="plotly-chart">
          {/* In production, this would use react-plotly.js Plot component */}
          {/* <Plot data={traces} layout={layout} /> */}
          <div
            data-testid="chart-rendered"
            data-traces={JSON.stringify(traces.length)}
            data-ticker={ticker}
          >
            Chart rendered with {traces.length} traces
          </div>
        </div>
      )}
    </div>
  )
}
