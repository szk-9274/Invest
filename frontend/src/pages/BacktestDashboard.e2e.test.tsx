import path from 'node:path'
import fs from 'node:fs'
import net from 'node:net'
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { beforeAll, afterAll, describe, expect, it, vi } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Navigate, Route, Routes } from 'react-router-dom'

const rootDir = path.resolve(__dirname, '../../..')
const fixtureOutputDir = path.join(rootDir, 'tests', 'fixtures', 'backtest_sample')

let apiBaseUrl = ''
let backendProcess: ChildProcessWithoutNullStreams | null = null

vi.mock('../api/base', () => ({
  buildApiUrl: (requestPath: string) => `${apiBaseUrl}/api${requestPath.startsWith('/') ? requestPath : `/${requestPath}`}`,
}))

function resolvePythonBinary(): string {
  const venvPython = path.join(rootDir, 'python', '.venv', 'bin', 'python')
  return fs.existsSync(venvPython) ? venvPython : 'python3'
}

async function findFreePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer()
    server.on('error', reject)
    server.listen(0, '127.0.0.1', () => {
      const address = server.address()
      if (!address || typeof address === 'string') {
        reject(new Error('Failed to resolve a free port'))
        return
      }
      server.close((error) => {
        if (error) {
          reject(error)
          return
        }
        resolve(address.port)
      })
    })
  })
}

async function waitForBackend(url: string, timeoutMs = 60000): Promise<void> {
  const startedAt = Date.now()
  while (Date.now() - startedAt < timeoutMs) {
    try {
      const response = await fetch(url)
      if (response.ok) {
        return
      }
    } catch {
      // Keep polling until the backend is ready.
    }
    await new Promise((resolve) => setTimeout(resolve, 500))
  }

  throw new Error(`Backend did not become ready: ${url}`)
}

beforeAll(async () => {
  class AlwaysVisibleObserver {
    constructor(private callback: IntersectionObserverCallback) {}
    observe(target: Element) {
      this.callback([{ isIntersecting: true, target } as IntersectionObserverEntry], this as unknown as IntersectionObserver)
    }
    disconnect() {}
    unobserve() {}
    takeRecords() { return [] }
    root = null
    rootMargin = '0px'
    thresholds = []
  }

  vi.stubGlobal('IntersectionObserver', AlwaysVisibleObserver)

  const port = await findFreePort()
  apiBaseUrl = `http://127.0.0.1:${port}`

  backendProcess = spawn(
    resolvePythonBinary(),
    ['-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', String(port)],
    {
      cwd: rootDir,
      env: {
        ...process.env,
        MINERVILISM_OUTPUT_DIR: fixtureOutputDir,
      },
      stdio: 'pipe',
    },
  )

  await waitForBackend(`${apiBaseUrl}/health`)
}, 60000)

afterAll(async () => {
  if (!backendProcess || backendProcess.killed) {
    return
  }

  backendProcess.kill('SIGTERM')
  await new Promise<void>((resolve) => {
    backendProcess?.once('exit', () => resolve())
    setTimeout(() => resolve(), 5000)
  })

  vi.unstubAllGlobals()
})

describe('BacktestDashboard E2E', () => {
  async function flushAsyncUpdates() {
    await Promise.resolve()
    await Promise.resolve()
  }

  it(
    'renders fixture-backed results from the real backend',
    async () => {
      vi.resetModules()
      await import('../i18n')
      const { AppChromeProvider } = await import('../contexts/AppChromeContext')
      const { BacktestDashboard } = await import('./BacktestDashboard')
      const { BacktestRunPage } = await import('./BacktestRunPage')
      const { BacktestAnalysisPage } = await import('./BacktestAnalysisPage')
      const { TraderStrategiesPage } = await import('./TraderStrategiesPage')

      render(
        <AppChromeProvider>
          <MemoryRouter initialEntries={['/dashboard/analysis']}>
            <Routes>
              <Route path="/dashboard" element={<BacktestDashboard />}>
                <Route index element={<Navigate to="run" replace />} />
                <Route path="run" element={<BacktestRunPage />} />
                <Route path="analysis" element={<BacktestAnalysisPage />} />
                <Route path="strategies" element={<TraderStrategiesPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AppChromeProvider>,
      )

      expect(await screen.findByText('Summary')).toBeInTheDocument()
      expect(await screen.findByText('backtest_2026-01-01_to_2026-01-31')).toBeInTheDocument()

      await act(async () => {
        await flushAsyncUpdates()
      })

      expect((await screen.findAllByText('AAA')).length).toBeGreaterThan(0)
      expect((await screen.findAllByText('CCC')).length).toBeGreaterThan(0)
      expect(await screen.findByRole('button', { name: /expand chart for aaa/i }, { timeout: 10000 })).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getByText(/^Top1$/)).toBeInTheDocument()
      }, { timeout: 10000 })
    },
    60000,
  )

  it(
    'shows the Minervini baseline on the trader strategies route',
    async () => {
      const user = userEvent.setup()
      vi.resetModules()
      await import('../i18n')
      const { AppChromeProvider } = await import('../contexts/AppChromeContext')
      const { BacktestDashboard } = await import('./BacktestDashboard')
      const { BacktestRunPage } = await import('./BacktestRunPage')
      const { BacktestAnalysisPage } = await import('./BacktestAnalysisPage')
      const { TraderStrategiesPage } = await import('./TraderStrategiesPage')

      render(
        <AppChromeProvider>
          <MemoryRouter initialEntries={['/dashboard/run']}>
            <Routes>
              <Route path="/dashboard" element={<BacktestDashboard />}>
                <Route index element={<Navigate to="run" replace />} />
                <Route path="run" element={<BacktestRunPage />} />
                <Route path="analysis" element={<BacktestAnalysisPage />} />
                <Route path="strategies" element={<TraderStrategiesPage />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AppChromeProvider>,
      )

      await user.click(await screen.findByRole('link', { name: 'Trader Strategies' }))

      expect(await screen.findByRole('button', { name: /マーク・ミネルヴィニ/i })).toBeInTheDocument()
      expect(screen.getByRole('img', { name: /マーク・ミネルヴィニ portrait/i })).toBeInTheDocument()
      expect(await screen.findByText('トレンドテンプレート主導')).toBeInTheDocument()
      expect(await screen.findByText('Current baseline')).toBeInTheDocument()
    },
    60000,
  )
})
