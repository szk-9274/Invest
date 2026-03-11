import React from 'react'

type PlotComponentType = React.ComponentType<Record<string, unknown>>
type PlotComponentFactory = (plotly: unknown) => PlotComponentType

type PlotlyCore = {
  register?: (modules: unknown[]) => void
}

let plotComponentPromise: Promise<PlotComponentType> | null = null

function toErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message) {
    return error.message
  }
  return String(error)
}

function loadPlotComponent(): Promise<PlotComponentType> {
  if (!plotComponentPromise) {
    plotComponentPromise = Promise.all([
      import('react-plotly.js/factory.js'),
      import('plotly.js-dist-min'),
    ])
      .then(([factoryModule, plotlyModule]) => {
      const createPlotComponent = (factoryModule.default ?? factoryModule) as PlotComponentFactory
      const plotly = (plotlyModule.default ?? plotlyModule) as PlotlyCore
      return createPlotComponent(plotly)
    })
      .catch((error: unknown) => {
        plotComponentPromise = null
        throw error
      })
  }

  return plotComponentPromise
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

    void loadPlotComponent()
      .then((component) => {
        if (!mounted) return
        setPlotComponent(() => component)
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
