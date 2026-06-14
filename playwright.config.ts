/**
 * playwright.config.ts — EduBoost SA V2
 *
 * Place at the project root:
 *   playwright.config.ts
 *
 * Install:
 *   npm install -D @playwright/test
 *   npx playwright install --with-deps chromium firefox
 *
 * Run all E2E tests:
 *   npx playwright test
 *
 * Run a specific suite:
 *   npx playwright test tests/e2e/auth.spec.ts
 *
 * Run with UI (interactive):
 *   npx playwright test --ui
 *
 * Generate report:
 *   npx playwright show-report
 */

import { defineConfig, devices } from "@playwright/test";

// Scaffold variables expected by checks
export const FRONTEND_BASE_URL =
  process.env.PLAYWRIGHT_BASE_URL ?? process.env.FRONTEND_BASE_URL ?? "http://localhost:3050";
export const PLAYWRIGHT_WEB_SERVER_COMMAND =
  process.env.PLAYWRIGHT_WEB_SERVER_COMMAND?.trim() || "pnpm --dir app/frontend exec next dev --webpack -p 3050";
const shouldStartWebServer = process.env.PLAYWRIGHT_SKIP_WEB_SERVER !== "1";

export default defineConfig({
  // ── Test discovery ──────────────────────────────────────────────────────────
  testDir: "./tests/e2e",
  testMatch: ["**/*.spec.ts"],

  // ── Global test timeout (ms) ───────────────────────────────────────────────
  timeout: 60_000,

  // ── Parallelism ─────────────────────────────────────────────────────────────
  fullyParallel: true,
  workers:       process.env.CI ? 2 : undefined,   // cap workers on CI

  // ── Retry logic ─────────────────────────────────────────────────────────────
  retries: process.env.CI ? 2 : 0,

  // ── Reporting ───────────────────────────────────────────────────────────────
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
    // Uncomment for CI JUnit output:
    // ["junit", { outputFile: "test-results/junit.xml" }],
  ],

  // ── Global test settings ────────────────────────────────────────────────────
  use: {
    baseURL:            FRONTEND_BASE_URL,

    // Navigation & network
    navigationTimeout: 15_000,
    actionTimeout: 8_000,

    // Capture artefacts on failure
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",

    // Extra HTTP headers (pass auth cookies / CSRF tokens if needed)
    // extraHTTPHeaders: { "x-test-mode": "1" },
  },

  // ── Browser projects ────────────────────────────────────────────────────────
  projects: [
    {
      name:  "chromium",
      use:   { ...devices["Desktop Chrome"] },
    },
    {
      name:  "firefox",
      use:   { ...devices["Desktop Firefox"] },
    },
    {
      name:  "webkit",
      use:   { ...devices["Desktop Safari"] },
    },
    // Mobile viewports
    {
      name:  "Mobile Chrome",
      use:   { ...devices["Pixel 5"] },
    },
    {
      name:  "Mobile Safari",
      use:   { ...devices["iPhone 13"] },
    },
  ],

  // ── Dev-server auto-start ────────────────────────────────────────────────────
  webServer: shouldStartWebServer
    ? {
        command:             PLAYWRIGHT_WEB_SERVER_COMMAND,
        url:                 FRONTEND_BASE_URL,
        reuseExistingServer: !process.env.CI,
        timeout:             120_000,
      }
    : undefined,

  // ── Output directories ───────────────────────────────────────────────────────
  outputDir: "test-results",
});
