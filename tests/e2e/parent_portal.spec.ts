import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const FIXTURE_FILE = path.join(__dirname, "../../playwright/.auth/fixtures.json");
const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v2";

test.describe("Parent Portal — Progress Reports", () => {
  let learnerId: string;
  test.beforeAll(() => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); learnerId = fx.learnerId; });
  test("parent portal dashboard loads and shows learner card", async ({ page }) => { await page.goto("/parent"); await expect(page.getByRole("heading", { name: /parent portal/i })).toBeVisible({ timeout: 10000 }); await expect(page.getByText("E2E Test Learner")).toBeVisible({ timeout: 10000 }); });
  test("learner progress report shows grade, subject, and activity", async ({ page }) => { await page.goto(`/parent/learners/${learnerId}/report`); await expect(page.getByTestId("learner-grade")).toBeVisible({ timeout: 10000 }); await expect(page.getByTestId("subject-progress")).toBeVisible(); await expect(page.getByTestId("recent-activity")).toBeVisible(); });
  test("consent status badge shows active/granted consent", async ({ page }) => { await page.goto(`/parent/learners/${learnerId}/consent`); await expect(page.getByTestId("consent-status-badge")).toContainText(/active|granted/i); await expect(page.getByText(/expires/i)).toBeVisible(); });
  test("consent expiry date is approximately 1 year from now", async ({ request }) => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); const res = await request.get(`${API_BASE_URL}/consent/status/${learnerId}`, { headers: { Authorization: `Bearer ${fx.accessToken}` } }); expect(res.status()).toBe(200); const payload = await res.json(); const data = payload?.data ?? payload; const expiresAt = new Date(data.expires_at ?? data.expiresAt).getTime(); const oneYear = 365 * 24 * 60 * 60 * 1000; expect(expiresAt - Date.now()).toBeGreaterThan(oneYear - 2 * 86400 * 1000); expect(expiresAt - Date.now()).toBeLessThan(oneYear + 2 * 86400 * 1000); });
});

test.describe("Parent Portal — Consent Management", () => {
  test("guardian can view and download data export", async ({ page }) => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); await page.goto(`/parent/learners/${fx.learnerId}/data`); await expect(page.getByRole("button", { name: /export data|download/i })).toBeVisible({ timeout: 10000 }); });
  test("right-to-erasure flow shows confirmation dialog", async ({ page }) => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); await page.goto(`/parent/learners/${fx.learnerId}/consent`); const eraseBtn = page.getByRole("button", { name: /delete|erase|remove data/i }); await expect(eraseBtn).toBeVisible({ timeout: 10000 }); await eraseBtn.click(); await expect(page.getByRole("dialog", { name: /confirm/i })).toBeVisible({ timeout: 5000 }); await page.getByRole("button", { name: /cancel/i }).click(); await expect(page.getByRole("dialog")).not.toBeVisible(); });
});

test.describe("Parent Portal — API Consent Enforcement", () => {
  test("out-of-scope learner data access is blocked", async ({ request }) => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); const res = await request.post(`${API_BASE_URL}/study-plans/generate/00000000-0000-0000-0000-000000000000`, { headers: { Authorization: `Bearer ${fx.accessToken}` }, data: { subject: "mathematics", gap_ratio: 0.4 } }); expect([403, 404, 422]).toContain(res.status()); });
});
