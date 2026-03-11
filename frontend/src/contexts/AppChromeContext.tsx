import React from 'react'

export type AppChromeConfig = {
  brandLabel: string | null
  brandLink: string
  statusLabel: string | null
  reloadLabel: string | null
  onReload: (() => void | Promise<void>) | null
  reloadDisabled: boolean
}

const defaultAppChrome: AppChromeConfig = {
  brandLabel: null,
  brandLink: '/',
  statusLabel: null,
  reloadLabel: null,
  onReload: null,
  reloadDisabled: false,
}

const AppChromeContext = React.createContext<{
  chrome: AppChromeConfig
  setChrome: React.Dispatch<React.SetStateAction<AppChromeConfig>>
} | null>(null)

export function createDefaultAppChrome(): AppChromeConfig {
  return { ...defaultAppChrome }
}

export const AppChromeProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [chrome, setChrome] = React.useState<AppChromeConfig>(() => createDefaultAppChrome())

  return (
    <AppChromeContext.Provider value={{ chrome, setChrome }}>
      {children}
    </AppChromeContext.Provider>
  )
}

export function useAppChrome() {
  const context = React.useContext(AppChromeContext)
  if (!context) {
    throw new Error('useAppChrome must be used within AppChromeProvider')
  }
  return context
}
