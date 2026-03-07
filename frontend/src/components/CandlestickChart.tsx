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

  // Load Plotly component lazily on mount so preview can render markers over image
  React.useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const mod = await import('react-plotly.js')
        if (!mounted) return
        setPlotComponent(() => (mod && (mod.default || mod)))
      } catch (err: any) {
        // Non-fatal: interactive charts will be unavailable in some environments
        if (!mounted) return
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  // Modal view mode: initially show enlarged image, user can switch to interactive plot
  const [modalMode, setModalMode] = React.useState<'image' | 'plot'>('image')
  const [zoomScale, setZoomScale] = React.useState<number>(1)
  const zoomStep = 0.25
  const [imgOffset, setImgOffset] = React.useState<{x:number,y:number}>({x:0,y:0})
  const [isDragging, setIsDragging] = React.useState(false)
  const [lastMousePos, setLastMousePos] = React.useState<{x:number,y:number}|null>(null)
  const [lastTouchDistance, setLastTouchDistance] = React.useState<number|null>(null)
  const [lastTouchCenter, setLastTouchCenter] = React.useState<{x:number,y:number}|null>(null)

  const onWheelZoom = (e: React.WheelEvent) => {
    if (!e.ctrlKey && !e.metaKey) return
    e.preventDefault()
    setZoomScale((s) => Math.max(0.2, Math.min(8, Number((s + (e.deltaY > 0 ? -zoomStep : zoomStep)).toFixed(2)))))
  }

  const resetZoom = () => setZoomScale(1)

  let layoutWithImage: any = layout as any

  // If no per-ticker background image is available, generate a static PNG from Plotly traces/layout
  React.useEffect(() => {
    let cancelled = false
    async function generateImageFromPlot() {
      try {
        if (bgImage) return
        if (!showModal || modalMode !== 'image') return
        if (typeof document === 'undefined') return

        // If traces include a candlestick trace, use Plotly to render a faithful image
        const hasCandlestick = (traces || []).some((t: any) => t && t.type === 'candlestick')
        if (hasCandlestick && PlotComponent) {
          try {
            const Plotly = await import('plotly.js-dist-min')
            // Create offscreen div
            const div = document.createElement('div')
            div.style.position = 'fixed'
            div.style.left = '-9999px'
            div.style.top = '-9999px'
            document.body.appendChild(div)

            // Use layoutWithImage but hide images to avoid recursive background
            const layoutForImage = { ...layoutWithImage }
            if (layoutForImage.images) layoutForImage.images = []
            const width = (layoutForImage && layoutForImage.width) || 1200
            const height = (layoutForImage && layoutForImage.height) || 700

            // Render and export
            // @ts-ignore
            await Plotly.newPlot(div, traces as any, layoutForImage as any)
            // @ts-ignore
            const imgData = await Plotly.toImage(div, { format: 'png', width, height, scale: 1 })
            // Cleanup
            // @ts-ignore
            Plotly.purge(div)
            document.body.removeChild(div)

            if (!cancelled && imgData) {
              setBgImage(imgData)
              return
            }
          } catch (err) {
            // fall through to canvas fallback
            // eslint-disable-next-line no-console
            console.warn('Plotly image generation failed, falling back to canvas', err)
          }
        }

        // Canvas fallback: synthesize a TradingView-like background and plot markers on it.
        // This helps when no OHLC data exists but markers are present.
        const canvas = document.createElement('canvas')
        const width = 1200
        const height = 700
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        // Draw background
        ctx.fillStyle = THEME.background
        ctx.fillRect(0, 0, width, height)

        // Draw grid
        ctx.strokeStyle = THEME.gridColor
        ctx.lineWidth = 1
        const cols = 6
        const rows = 6
        for (let i = 1; i < cols; i++) {
          const x = Math.round((width * i) / cols)
          ctx.beginPath()
          ctx.moveTo(x, 0)
          ctx.lineTo(x, height)
          ctx.stroke()
        }
        for (let j = 1; j < rows; j++) {
          const y = Math.round((height * j) / rows)
          ctx.beginPath()
          ctx.moveTo(0, y)
          ctx.lineTo(width, y)
          ctx.stroke()
        }

        // Draw optional title
        ctx.fillStyle = THEME.textColor
        ctx.font = '16px sans-serif'
        ctx.fillText(ticker, 12, 24)

        // Determine marker positions from traces (entries/exits). If no markers, show placeholder
        const markerTrace: any = (traces || []).find((t: any) => t && (t.name === 'Entry' || t.name === 'Exit'))
        let entries: any[] = []
        let exits: any[] = []
        if (markerTrace) {
          // try to extract x (dates) and y (prices)
          const xs = markerTrace.x || []
          const ys = markerTrace.y || []
          for (let i = 0; i < xs.length; i++) {
            if ((markerTrace.marker && markerTrace.marker.symbol === 'triangle-up') || markerTrace.name === 'Entry') {
              entries.push({ x: xs[i], y: ys[i] })
            } else {
              exits.push({ x: xs[i], y: ys[i] })
            }
          }
        }

        // If traces include markers in separate traces (entries/exits), handle both
        const entryTrace: any = (traces || []).find((t: any) => t && t.name === 'Entry')
        const exitTrace: any = (traces || []).find((t: any) => t && t.name === 'Exit')
        if (entryTrace) {
          const xs = entryTrace.x || []
          const ys = entryTrace.y || []
          entries = xs.map((x: any, idx: number) => ({ x, y: ys[idx] }))
        }
        if (exitTrace) {
          const xs = exitTrace.x || []
          const ys = exitTrace.y || []
          exits = xs.map((x: any, idx: number) => ({ x, y: ys[idx] }))
        }

        // Prefer to derive date and price ranges from the candlestick trace (if available)
        const candleTrace: any = (traces || []).find((t: any) => t && t.type === 'candlestick')
        let minDate: any = null
        let maxDate: any = null
        if (candleTrace && candleTrace.x && candleTrace.x.length > 0) {
          const parsed = candleTrace.x.map((d: any) => new Date(d))
          minDate = Math.min(...parsed.map((d: Date) => d.getTime()))
          maxDate = Math.max(...parsed.map((d: Date) => d.getTime()))
        } else {
          // Fallback to marker-based range or a default 30-day window
          const allDates = [...(entries || []).map((e) => e.x), ...(exits || []).map((e) => e.x)].filter(Boolean)
          if (allDates.length > 0) {
            const parsed = allDates.map((d: any) => new Date(d))
            minDate = Math.min(...parsed.map((d) => d.getTime()))
            maxDate = Math.max(...parsed.map((d) => d.getTime()))
          } else {
            minDate = Date.now() - 1000 * 60 * 60 * 24 * 30
            maxDate = Date.now()
          }
        }

        // Price range: prefer candlestick highs/lows
        let minPrice: number
        let maxPrice: number
        if (candleTrace && candleTrace.low && candleTrace.high && candleTrace.low.length > 0 && candleTrace.high.length > 0) {
          const lows = candleTrace.low.map((v: any) => Number(v)).filter((n: number) => Number.isFinite(n))
          const highs = candleTrace.high.map((v: any) => Number(v)).filter((n: number) => Number.isFinite(n))
          const candPrices = [...lows, ...highs]
          minPrice = Math.min(...(candPrices.length ? candPrices : [0]))
          maxPrice = Math.max(...(candPrices.length ? candPrices : [1]))
        } else {
          const allPrices = [...(entries || []).map((e) => e.y), ...(exits || []).map((e) => e.y)].filter((p) => Number.isFinite(p))
          minPrice = Math.min(...(allPrices.length ? allPrices : [0]))
          maxPrice = Math.max(...(allPrices.length ? allPrices : [1]))
        }

        if (minPrice === maxPrice) {
          minPrice = minPrice - 1
          maxPrice = maxPrice + 1
        }

        const dateToX = (d: any) => {
          const t = new Date(d).getTime()
          return 60 + ((width - 120) * (t - minDate)) / (maxDate - minDate)
        }
        const priceToY = (p: number) => {
          return 40 + ((height - 80) * (maxPrice - p)) / (maxPrice - minPrice)
        }

        // Draw markers
        for (const e of entries) {
          const x = dateToX(e.x)
          const y = priceToY(e.y)
          ctx.fillStyle = THEME.entryMarkerColor
          ctx.beginPath()
          ctx.moveTo(x, y - 8)
          ctx.lineTo(x - 6, y + 6)
          ctx.lineTo(x + 6, y + 6)
          ctx.closePath()
          ctx.fill()
        }
        for (const ex of exits) {
          const x = dateToX(ex.x)
          const y = priceToY(ex.y)
          ctx.fillStyle = THEME.exitMarkerColor
          ctx.beginPath()
          ctx.moveTo(x, y + 8)
          ctx.lineTo(x - 6, y - 6)
          ctx.lineTo(x + 6, y - 6)
          ctx.closePath()
          ctx.fill()
        }

        const dataUrl = canvas.toDataURL('image/png')
        if (!cancelled) setBgImage(dataUrl)
      } catch (err) {
        // Non-fatal; keep bgImage null
        // eslint-disable-next-line no-console
        console.warn('Failed to generate static image from Plotly or canvas', err)
      }
    }

    generateImageFromPlot()
    return () => {
      cancelled = true
    }
  }, [showModal, modalMode, PlotComponent, bgImage, traces, layoutWithImage, ticker])

  // Prevent background scrolling when modal is open and restore on close
  React.useEffect(() => {
    if (typeof document === 'undefined') return
    const prev = document.body.style.overflow
    if (showModal) {
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.body.style.overflow = prev
    }
  }, [showModal])

  // If a background image is available, add it to the Plotly layout so it scales with the plot
  const computedLayoutWithImage = React.useMemo(() => {
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

  layoutWithImage = computedLayoutWithImage

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
            onClick={() => { setModalMode('image'); setShowModal(true) }}
            onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && (setModalMode('image'), setShowModal(true))}
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
              position: 'relative',
              backgroundColor: '#0f172a',
            }}
          >
            {/* If Plotly is available, render a small interactive preview (markers over background image)
                Otherwise fall back to a CSS background preview */}
            {PlotComponent ? (
              <div style={{ width: '100%', height: 260 }}>
                <PlotComponent
                  data={traces as any}
                  layout={{ ...layoutWithImage as any, autosize: true, margin: { t: 8, b: 30, l: 40, r: 8 }, height: 260 }}
                  config={{ responsive: true, displayModeBar: false }}
                  useResizeHandler
                  style={{ width: '100%', height: '100%' }}
                />
                <div style={{ position: 'absolute', left: 8, top: 8, background: 'rgba(0,0,0,0.45)', padding: 6, borderRadius: 6, color: '#fff' }}>
                  {ticker}
                </div>
              </div>
            ) : (
              <div
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
                  width: '100%',
                  height: 260,
                }}
              >
                <div style={{background: 'rgba(0,0,0,0.45)', padding: 8, borderRadius: 6, color: '#fff'}}>
                  Chart rendered with {traces.length} traces
                </div>
              </div>
            )}
          </div>

        </div>
      )}

      {/* Full-screen interactive modal */}
      {showModal && (
        <div className="candlestick-modal" role="dialog" aria-modal="true" onWheel={onWheelZoom}>
          <div className="candlestick-modal-content">
            <button className="modal-close" onClick={() => { setShowModal(false); resetZoom(); setModalMode('image') }} aria-label="Close">×</button>

            {/* Image-first modal: allow zoom/pan on the image, then user can switch to interactive plot */}
            {modalMode === 'image' ? (
              <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: 8, display: 'flex', gap: 8, alignItems: 'center' }}>
                  <div style={{ color: THEME.textColor }}>{ticker} — 拡大画像</div>
                  <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
                    <button onClick={() => setZoomScale((s) => Math.max(0.2, Number((s - zoomStep).toFixed(2))))} aria-label="Zoom out">−</button>
                    <button onClick={() => setZoomScale((s) => Math.min(8, Number((s + zoomStep).toFixed(2))))} aria-label="Zoom in">＋</button>
                    <button onClick={resetZoom} aria-label="Reset zoom">Reset</button>
                    <button onClick={() => setModalMode('plot')} aria-label="Open interactive chart">詳細を開く</button>
                  </div>
                </div>

                <div style={{ flex: 1, overflow: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000' }}>
                  {bgImage ? (
                    <img
                      data-testid="chart-modal-image"
                      src={bgImage}
                      alt={`${ticker} chart`}
                      style={{ transform: `translate(${imgOffset.x}px, ${imgOffset.y}px) scale(${zoomScale})`, transformOrigin: 'center', maxWidth: '100%', maxHeight: '100%', display: 'block', touchAction: 'none', cursor: isDragging ? 'grabbing' : 'grab' }}
                      draggable={false}
                      onMouseDown={(e) => { setIsDragging(true); setLastMousePos({x: e.clientX, y: e.clientY}) }}
                      onMouseMove={(e) => { if (!isDragging || !lastMousePos) return; const dx = e.clientX - lastMousePos.x; const dy = e.clientY - lastMousePos.y; setImgOffset((p) => ({x: p.x + dx, y: p.y + dy})); setLastMousePos({x: e.clientX, y: e.clientY}) }}
                      onMouseUp={() => { setIsDragging(false); setLastMousePos(null) }}
                      onMouseLeave={() => { setIsDragging(false); setLastMousePos(null) }}
                      onTouchStart={(e) => {
                        if (e.touches.length === 2) {
                          const dx = e.touches[0].clientX - e.touches[1].clientX
                          const dy = e.touches[0].clientY - e.touches[1].clientY
                          setLastTouchDistance(Math.hypot(dx, dy))
                          const cx = (e.touches[0].clientX + e.touches[1].clientX) / 2
                          const cy = (e.touches[0].clientY + e.touches[1].clientY) / 2
                          setLastTouchCenter({x: cx, y: cy})
                        } else if (e.touches.length === 1) {
                          setLastMousePos({x: e.touches[0].clientX, y: e.touches[0].clientY})
                          setIsDragging(true)
                        }
                      }}
                      onTouchMove={(e) => {
                        if (e.touches.length === 2 && lastTouchDistance) {
                          const dx = e.touches[0].clientX - e.touches[1].clientX
                          const dy = e.touches[0].clientY - e.touches[1].clientY
                          const dist = Math.hypot(dx, dy)
                          const factor = dist / lastTouchDistance
                          setZoomScale((s) => Math.max(0.2, Math.min(8, Number((s * factor).toFixed(2)))))
                          setLastTouchDistance(dist)
                        } else if (e.touches.length === 1 && isDragging && lastMousePos) {
                          const nx = e.touches[0].clientX
                          const ny = e.touches[0].clientY
                          const dx = nx - lastMousePos.x
                          const dy = ny - lastMousePos.y
                          setImgOffset((p) => ({x: p.x + dx, y: p.y + dy}))
                          setLastMousePos({x: nx, y: ny})
                        }
                      }}
                      onTouchEnd={(e) => { if (e.touches.length < 2) setLastTouchDistance(null); if (e.touches.length === 0) { setIsDragging(false); setLastMousePos(null); } }}
                    />
                  ) : (
                    <div style={{ color: THEME.textColor }}>No background image available</div>
                  )}
                </div>
              </div>
            ) : (
              plotError ? (
                <div style={{padding:20}}>
                  <p style={{color: THEME.textColor}}>Interactive chart unavailable: {plotError}</p>
                </div>
              ) : PlotComponent ? (
                <div style={{ width: '100%', height: '100%' }}>
                  <div style={{ padding: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ color: THEME.textColor }}>{ticker} — インタラクティブ表示</div>
                    <div style={{ marginLeft: 'auto' }}>
                      <button onClick={() => setModalMode('image')}>画像表示に戻る</button>
                    </div>
                  </div>
                  <div style={{ width: '100%', height: 'calc(100% - 48px)' }}>
                    <PlotComponent
                      data={traces as any}
                      layout={layoutWithImage as any}
                      config={{responsive: true, scrollZoom: true}}
                      useResizeHandler
                      style={{width: '100%', height: '100%'}}
                    />
                  </div>
                </div>
              ) : (
                <div style={{padding:20}}>Loading interactive chart...</div>
              )
            )}

          </div>
          <style>{`
            .candlestick-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display:flex; align-items:center; justify-content:center; z-index:2000; }
            .candlestick-modal-content { position: relative; width: 90vw; height: 85vh; background: ${THEME.background}; border-radius:8px; overflow:hidden; }
            .modal-close { position:absolute; top:10px; right:10px; z-index:2010; background:rgba(255,255,255,0.08); color:${THEME.textColor}; border:none; width:40px; height:40px; border-radius:6px; font-size:22px; cursor:pointer; }
            .candlestick-modal-content button { background: rgba(255,255,255,0.06); color: ${THEME.textColor}; border: none; padding: 6px 10px; border-radius:6px; cursor:pointer }
          `}</style>
        </div>
      )}
    </div>
  )
}
