---
name: electron-patterns
description: Electron development patterns for main process, renderer, IPC, and security best practices.
---

# Electron Development Patterns

## Architecture Overview

```
Main Process (Node.js)     Renderer Process (Chromium)
    |                              |
    |  <-- IPC (contextBridge) --> |
    |                              |
  main.ts                    React App
  preload.ts                 components/
```

## IPC Communication Patterns

### Safe IPC with contextBridge

```typescript
// preload.ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  // Invoke (request-response)
  getData: (id: string) => ipcRenderer.invoke('get-data', id),

  // Send (fire-and-forget)
  logEvent: (event: string) => ipcRenderer.send('log-event', event),

  // Subscribe (main -> renderer)
  onUpdate: (callback: (data: any) => void) => {
    const subscription = (_event: any, data: any) => callback(data)
    ipcRenderer.on('data-updated', subscription)
    return () => ipcRenderer.removeListener('data-updated', subscription)
  }
})
```

### Main Process Handlers

```typescript
// main.ts
import { ipcMain } from 'electron'

// Handle invoke (returns promise)
ipcMain.handle('get-data', async (event, id: string) => {
  // Validate input
  if (typeof id !== 'string') {
    throw new Error('Invalid ID')
  }
  return await fetchData(id)
})

// Handle send (no return)
ipcMain.on('log-event', (event, eventName: string) => {
  console.log('Event:', eventName)
})

// Send to renderer
function notifyRenderer(win: BrowserWindow, data: any) {
  win.webContents.send('data-updated', data)
}
```

## Window Management

### Create Secure Window

```typescript
function createWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true
    }
  })

  // Load content
  if (process.env.USE_DEV_SERVER === 'true') {
    win.loadURL('http://127.0.0.1:5173')
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(__dirname, '../renderer-dist/index.html'))
  }

  return win
}
```

## React Integration

### Type-Safe API Access

```typescript
// renderer/src/types/api.d.ts
interface ElectronAPI {
  getData: (id: string) => Promise<Data>
  logEvent: (event: string) => void
  onUpdate: (callback: (data: Data) => void) => () => void
}

declare global {
  interface Window {
    api: ElectronAPI
  }
}
```

### Custom Hook for IPC

```typescript
// renderer/src/hooks/useElectronData.ts
export function useElectronData(id: string) {
  const [data, setData] = useState<Data | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    setLoading(true)
    window.api.getData(id)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [id])

  // Subscribe to updates
  useEffect(() => {
    const unsubscribe = window.api.onUpdate(setData)
    return unsubscribe
  }, [])

  return { data, loading, error }
}
```

## Error Handling

### Main Process

```typescript
ipcMain.handle('risky-operation', async (event, data) => {
  try {
    return await performOperation(data)
  } catch (error) {
    // Log for debugging
    console.error('Operation failed:', error)
    // Return safe error message
    throw new Error('Operation failed. Please try again.')
  }
})
```

### Renderer Process

```typescript
async function handleClick() {
  try {
    const result = await window.api.riskyOperation(data)
    setResult(result)
  } catch (error) {
    setError(error.message)
    // Show user-friendly error
  }
}
```

## Performance Tips

1. **Heavy operations in main process** - Keep renderer responsive
2. **Batch IPC calls** - Reduce overhead
3. **Use invoke for request-response** - Better than send+reply
4. **Lazy load modules** - Faster startup
5. **Minimize window redraws** - Use will-change CSS sparingly
