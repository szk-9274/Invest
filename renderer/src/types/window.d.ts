export {}
declare global {
  interface Window {
    win: {
      minimize: () => void
      close: () => void
    }
    gitlab: {
      openProjectWeb: () => Promise
    }
  }
}