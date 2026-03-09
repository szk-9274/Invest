declare module 'react-plotly.js' {
  import { ComponentType } from 'react'

  const Plot: ComponentType<any>
  export default Plot
}

declare module 'react-plotly.js/factory' {
  import { ComponentType } from 'react'

  const createPlotlyComponent: (plotly: unknown) => ComponentType<any>
  export default createPlotlyComponent
}
