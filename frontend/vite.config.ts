import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      host: true,
      port: 3000,
      strictPort: true,
      allowedHosts: ['desktop-995hk1t.tailc6a96c.ts.net'],
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      // Split large TopBottomPurchaseCharts into its own chunk to reduce initial bundle size
      chunkSizeWarningLimit: 2500,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('lightweight-charts')) return 'lightweight-chart-core'
            if (id.includes('TopBottomPurchaseCharts')) return 'top-bottom-chart'
          },
        },
      },
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test-setup.ts',
      coverage: {
        provider: 'v8',
        reporter: ['text', 'lcov'],
        exclude: ['scripts/**', 'src/api/generated/**', 'src/test-setup.ts'],
        thresholds: {
          statements: 80,
          branches: 80,
          functions: 80,
          lines: 80,
        },
      },
    },
  }
})
