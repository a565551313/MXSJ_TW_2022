/// <reference types="vitest/config" />
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * The dev server only ever proxies `/api/...` to the Python review API.
 * The browser never receives an absolute sandbox URL: every request the app
 * makes is a relative `/api/v1/review/...` path, and this proxy (server side,
 * inside the sandbox) forwards it to the Python backend.
 */
const DEFAULT_API_PROXY_TARGET = 'http://127.0.0.1:8000'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_PROXY_TARGET || DEFAULT_API_PROXY_TARGET
  const port = Number(env.PORT || 5173)
  const allowedHosts = true // Arena preview domains are proxied; allow them.

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port,
      strictPort: false,
      allowedHosts,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    preview: {
      host: '0.0.0.0',
      port: port + 1,
      strictPort: false,
      allowedHosts,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
    test: {
      environment: 'jsdom',
      globals: false,
      setupFiles: ['./src/test/setup.ts'],
      include: ['src/**/*.test.{ts,tsx}'],
      css: false,
      restoreMocks: true,
    },
  }
})
