import React from 'react'
import Plot from 'react-plotly.js'

export default function TopBottomPurchaseChart({
  title,
  data = [],
  width = 360,
  height = 220,
}: {
  title?: string
  data?: Array<{ timestamp: string; price: number; amount: number }>
  width?: number
  height?: number
}) {
  const x = data.map((d) => d.timestamp)
  const y = data.map((d) => d.price)
  const sizes = data.map((d) => (d.amount ? Math.max(6, Math.min(28, Math.sqrt(d.amount))) : 8))

  return (
    <div className="purchase-card" style={{ width }}>
      <div className="purchase-card-title">
        <span>{title}</span>
      </div>
      <Plot
        data={[
          {
            type: data.length > 200 ? 'scattergl' : 'scatter',
            mode: 'markers',
            x,
            y,
            marker: { size: sizes, color: '#2563eb', opacity: 0.8 },
            hovertemplate: 'Date: %{x}<br>Price: $%{y:,.2f}<br>Amount: $%{marker.size}<extra></extra>',
          },
        ]}
        layout={{ margin: { t: 6, r: 8, l: 30, b: 24 }, height, showlegend: false }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%' }}
      />
    </div>
  )
}
