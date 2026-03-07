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

  const [showModal, setShowModal] = React.useState(false)
  const [PlotComponent, setPlotComponent] = React.useState<any>(null)
  const [plotError, setPlotError] = React.useState<string | null>(null)

  // Background chart image (base64 data URI) fetched from backend latest results
  const [bgImage, setBgImage] = React.useState<string | null>(null)

  // Fetch latest backtest charts and pick the one corresponding to this ticker
  React.useEffect(() => {
    let mounted = true
    async function fetchChartImage() {
      try {
        const res = await fetch('/api/backtest/latest')
        if (!res.ok) return
        const data = await res.json()
        const charts = (data && (data as any).charts) || {}
        const keys = Object.keys(charts || {})
        // Prefer explicit '{ticker}_price_chart', then exact ticker, then any key containing ticker
        let key = keys.find((k) => k === `${ticker}_price_chart`) || keys.find((k) => k === ticker) || keys.find((k) => k.includes(ticker)) || keys.find((k) => k.includes('_price_chart'))
        // Fallback: if no per-ticker chart, use the first available chart (e.g., equity_curve)
        if (!key && keys.length > 0) key = keys[0]
        if (key && charts[key]) {
          if (!mounted) return
          setBgImage(charts[key])
        }
      } catch (e) {
        // Non-fatal - background image is optional
        // eslint-disable-next-line no-console
        console.warn('Failed to fetch chart image for background', e)
      }
    }

    fetchChartImage()
    return () => {
      mounted = false
    }
  }, [ticker])

  React.useEffect(() => {
    let mounted = true
    if (!showModal) return
    // Dynamic import react-plotly.js only when modal is opened
    ;(async () => {
      try {
        const mod = await import('react-plotly.js')
        if (!mounted) return
        setPlotComponent(() => (mod && (mod.default || mod)))
      } catch (err: any) {
        // Import failed (likely package not installed in environment)
        if (!mounted) return
        setPlotError(String(err))
      }
    })()
    return () => {
      mounted = false
    }
  }, [showModal])

  // If a background image is available, add it to the Plotly layout so it scales with the plot
  const layoutWithImage = React.useMemo(() => {
    if (!bgImage) return layout
    const img = {
      source: bgImage,
      xref: 'paper',
      yref: 'paper',
      x: 0,
      y: 1,
      sizex: 1,
      sizey: 1,
      sizing: 'stretch',
      layer: 'below',
      opacity: 0.95,
    }
    return { ...layout, images: [img], autosize: true }
  }, [bgImage, layout])

  return (
    <div data-testid="candlestick-chart" style={{ width: '100%' }}>
      {data.dates.length === 0 ? (
        <p data-testid="no-data-message">No chart data available</p>
      ) : (
        <div data-testid="plotly-chart">
          {/* In production, this would use react-plotly.js Plot component */}
          {/* Static placeholder for testability; clicking opens interactive modal */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => setShowModal(true)}
            onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && setShowModal(true)}
            data-testid="chart-rendered"
            data-traces={JSON.stringify(traces.length)}
            data-ticker={ticker}
            style={{
              outline: 'none',
              cursor: 'zoom-in',
              minHeight: 200,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundImage: bgImage ? `url(${bgImage})` : undefined,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
            }}
          >
            {/* Keep marker count for tests and accessibility */}
            <div style={{background: 'rgba(0,0,0,0.45)', padding: 8, borderRadius: 6}}>
              Chart rendered with {traces.length} traces
            </div>
          </div>
        </div>
      )}

      {/* Full-screen interactive modal */}
      {showModal && (
        <div className="candlestick-modal" role="dialog" aria-modal="true">
          <div className="candlestick-modal-content">
            <button className="modal-close" onClick={() => setShowModal(false)} aria-label="Close">×</button>
            {plotError ? (
              <div style={{padding:20}}>
                <p>Interactive chart unavailable: {plotError}</p>
                <p>Please ensure react-plotly.js is installed in the environment.</p>
              </div>
            ) : PlotComponent ? (
              // Render Plotly interactive chart with background image if available
              <div style={{width: '100%', height: '100%'}}>
                <PlotComponent
                  data={traces as any}
                  layout={layoutWithImage as any}
                  config={{responsive: true, scrollZoom: true}}
                  useResizeHandler
                  style={{width: '100%', height: '100%'}}
                />
              </div>
            ) : (
              <div style={{padding:20}}>Loading interactive chart...</div>
            )}
          </div>
          <style>{`
            .candlestick-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display:flex; align-items:center; justify-content:center; z-index:2000; }
            .candlestick-modal-content { position: relative; width: 90vw; height: 85vh; background: ${THEME.background}; border-radius:8px; overflow:hidden; }
            .modal-close { position:absolute; top:10px; right:10px; z-index:2010; background:rgba(255,255,255,0.08); color:${THEME.textColor}; border:none; width:40px; height:40px; border-radius:6px; font-size:22px; cursor:pointer; }
          `}</style>
        </div>
      )}
    </div>
  )
}
