import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.FRONTEND_BASE_URL || "http://127.0.0.1:3050";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure"
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],
  webServer: process.env.PLAYWRIGHT_WEB_SERVER_COMMAND
    ? {
        command: process.env.PLAYWRIGHT_WEB_SERVER_COMMAND,
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000
      }
    : undefined
});
