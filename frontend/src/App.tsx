/**
 * Main App Component
 *
 * Simple routing between Home and Chart pages.
 */
import React, { useState } from 'react'
import { Home } from './pages/Home'
import { Chart } from './pages/Chart'

function App() {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)

  if (selectedTicker) {
    return (
      <Chart
        ticker={selectedTicker}
        onBack={() => setSelectedTicker(null)}
      />
    )
  }

  return <Home onNavigateToChart={setSelectedTicker} />
}

export default App
