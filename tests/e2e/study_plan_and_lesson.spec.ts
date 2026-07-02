import { test, expect, APIResponse } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const FIXTURE_FILE = path.join(__dirname, "../../playwright/.auth/fixtures.json");
const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v2";

async function expectAcceptedJob(response: APIResponse, operation: RegExp) {
  expect([200, 201, 202]).toContain(response.status());
  const payload = await response.json();
  const data = payload?.data ?? payload;
  expect(data).toHaveProperty("job_id");
  expect(String(data.operation)).toMatch(operation);
  return data;
}

test.describe("Study Plan Generation", () => {
  let learnerId: string; let accessToken: string;
  test.beforeAll(() => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); learnerId = fx.learnerId; accessToken = fx.accessToken; });
  test("study plan page renders for the learner", async ({ page }) => { await page.goto(`/learners/${learnerId}/plan`); await expect(page.getByRole("heading", { name: /study plan/i })).toBeVisible({ timeout: 15000 }); });
  test("can request study plan generation via V2 async job contract", async ({ request }) => { const res = await request.post(`${API_BASE_URL}/study-plans/generate/${learnerId}`, { headers: { Authorization: `Bearer ${accessToken}` }, data: { subject: "mathematics", gap_ratio: 0.4 } }); await expectAcceptedJob(res, /study_plan/i); });
  test("study plan page displays weekly topic breakdown", async ({ page }) => { await page.goto(`/learners/${learnerId}/plan`); await expect(page.getByTestId("plan-week-card").first()).toBeVisible({ timeout: 15000 }); expect(await page.getByTestId("plan-week-card").count()).toBeGreaterThanOrEqual(1); });
  test("study plan mutation blocks out-of-scope learner", async ({ request }) => { const res = await request.post(`${API_BASE_URL}/study-plans/generate/00000000-0000-0000-0000-000000000000`, { headers: { Authorization: `Bearer ${accessToken}` }, data: { subject: "mathematics", gap_ratio: 0.4 } }); expect([403, 404, 422]).toContain(res.status()); });
});

test.describe("Lesson Delivery", () => {
  let learnerId: string; let accessToken: string;
  test.beforeAll(() => { const fx = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8")); learnerId = fx.learnerId; accessToken = fx.accessToken; });
  test("lesson page loads for a learner with active plan", async ({ page }) => { await page.goto(`/learners/${learnerId}/lesson`); const hasLesson = await page.getByTestId("lesson-content").isVisible({ timeout: 15000 }).catch(() => false); const hasCTA = await page.getByRole("button", { name: /start adventure|start lesson/i }).isVisible().catch(() => false); expect(hasLesson || hasCTA).toBe(true); });
  test("can request a new lesson via V2 async job contract", async ({ request }) => { const res = await request.post(`${API_BASE_URL}/lessons/generate`, { headers: { Authorization: `Bearer ${accessToken}` }, data: { learner_id: learnerId, subject: "MATH", topic: "Fractions", grade: "4", language: "en" } }); await expectAcceptedJob(res, /lesson/i); });
  test("lesson content renders with explanation and examples", async ({ page }) => { await page.goto(`/learners/${learnerId}/lesson`); await page.getByRole("button", { name: /start adventure|start lesson/i }).click().catch(() => undefined); await expect(page.getByTestId("lesson-content")).toBeVisible({ timeout: 30000 }); expect((await page.getByTestId("lesson-content").textContent())?.length).toBeGreaterThan(100); });
  test("learner can see completion control", async ({ page }) => { await page.goto(`/learners/${learnerId}/lesson`); await expect(page.getByRole("button", { name: /complete|done|finished|claim my stars/i })).toBeVisible({ timeout: 10000 }); });
});
