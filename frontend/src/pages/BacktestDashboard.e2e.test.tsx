import path from 'node:path'
import fs from 'node:fs'
import net from 'node:net'
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { beforeAll, afterAll, describe, expect, it, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

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
  const port = await findFreePort()
  apiBaseUrl = `http://127.0.0.1:${port}`

  backendProcess = spawn(
    resolvePythonBinary(),
    ['-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', String(port)],
    {
      cwd: rootDir,
      env: {
        ...process.env,
        INVEST_OUTPUT_DIR: fixtureOutputDir,
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
      const { BacktestDashboard } = await import('./BacktestDashboard')
      const user = userEvent.setup()

      render(<BacktestDashboard />)

      expect(await screen.findByRole('heading', { name: 'Backtest Dashboard' })).toBeInTheDocument()
      expect(await screen.findByText('2026-01-01 to 2026-01-31')).toBeInTheDocument()
      expect(await screen.findByText('backtest_2026-01-01_to_2026-01-31')).toBeInTheDocument()

      await act(async () => {
        await user.click(screen.getByRole('button', { name: 'Trades' }))
        await flushAsyncUpdates()
      })

      expect(await screen.findByText('AAA')).toBeInTheDocument()
      expect(await screen.findByText('CCC')).toBeInTheDocument()
    },
    60000,
  )
})
