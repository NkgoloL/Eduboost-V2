/// <reference types="vitest" />
import path from 'node:path'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Note: The "CJS build of Vite's Node API is deprecated" warning is a known
// issue in vitest that doesn't affect functionality. Tests pass normally.
// This warning comes from transitive dependencies and can be safely ignored.
// See: https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'server-only': path.resolve(__dirname, '__tests__/mocks/server-only.ts'),
    },
  },
  test: {
    environment: 'jsdom',
    environmentOptions: {
      jsdom: {
        url: 'https://eduboost.local',
      },
    },
    globals: true,
    setupFiles: ['./__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/components/eduboost/**/*.{ts,tsx}', 'src/lib/api/**/*.{ts,tsx}'],
      exclude: ['src/components/eduboost/styles.ts'],
      reporter: ['text', 'html', 'json-summary'],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
})
