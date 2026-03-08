import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    strictPort: true,
    allowedHosts: ['desktop-995hk1t.tailc6a96c.ts.net'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Split large TopBottomPurchaseCharts into its own chunk to reduce initial bundle size
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('TopBottomPurchaseCharts')) return 'top-bottom-chart';
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
  },
})
