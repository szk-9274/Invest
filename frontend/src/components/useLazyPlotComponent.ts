import React from 'react'

type PlotComponentType = React.ComponentType<Record<string, unknown>>
type PlotComponentFactory = (plotly: unknown) => PlotComponentType

function toErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message) {
    return error.message
  }
  return String(error)
}

export function useLazyPlotComponent(enabled = true) {
  const [PlotComponent, setPlotComponent] = React.useState<PlotComponentType | null>(null)
  const [plotError, setPlotError] = React.useState<string | null>(null)

  React.useEffect(() => {
    if (!enabled) {
      setPlotComponent(null)
      setPlotError(null)
      return
    }

    let mounted = true

    void Promise.all([
      import('react-plotly.js/factory'),
      import('plotly.js-dist-min'),
    ])
      .then(([factoryModule, plotlyModule]) => {
        if (!mounted) return
        const createPlotComponent = (factoryModule.default ?? factoryModule) as PlotComponentFactory
        const plotly = plotlyModule.default ?? plotlyModule
        setPlotComponent(() => createPlotComponent(plotly))
      })
      .catch((error: unknown) => {
        if (!mounted) return
        setPlotError(toErrorMessage(error))
      })

    return () => {
      mounted = false
    }
  }, [enabled])

  return { PlotComponent, plotError }
}
