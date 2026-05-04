import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./__tests__/setup.ts'],
    coverage: {
      provider: "v8",
      all: true,
      include: ["src/components/eduboost/**/*.{ts,tsx}", "src/lib/api/**/*.{ts,tsx}"],
      exclude: ["src/components/eduboost/styles.ts"],
      reporter: ["text", "html", "json-summary"],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
})
