import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const FIXTURE_FILE = path.join(__dirname, "../../playwright/.auth/fixtures.json");
const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v2";

async function pollJob(request: any, token: string, jobId: string) {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    const response = await request.get(`${API_BASE_URL}/jobs/${jobId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(response.ok()).toBeTruthy();
    const payload = await response.json();
    if (payload.status === "completed" || payload.status === "failed") {
      return payload;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Job ${jobId} did not finish`);
}

test.describe("Critical learner smoke", () => {
  let learnerId: string;
  let accessToken: string;

  test.beforeAll(() => {
    const fixtures = JSON.parse(fs.readFileSync(FIXTURE_FILE, "utf-8"));
    learnerId = fixtures.learnerId;
    accessToken = fixtures.accessToken;
  });

  test("dashboard, plan, lesson completion, and badges work through V2", async ({ page, request }) => {
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: /dashboard|welcome/i })).toBeVisible();
    await expect(page.getByText(/failed to load/i)).toHaveCount(0);

    const planResponse = await request.post(`${API_BASE_URL}/study-plans/generate/${learnerId}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { gap_ratio: 0.4 },
    });
    expect(planResponse.status()).toBe(202);
    const planJob = await pollJob(request, accessToken, (await planResponse.json()).job_id);
    expect(planJob.status).toBe("completed");
    expect(planJob.result.days.Mon.length).toBeGreaterThanOrEqual(1);

    const lessonResponse = await request.post(`${API_BASE_URL}/lessons/generate`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: {
        learner_id: learnerId,
        subject: "MATH",
        topic: "Fractions",
        language: "en",
      },
    });
    expect(lessonResponse.status()).toBe(202);
    const lessonJob = await pollJob(request, accessToken, (await lessonResponse.json()).job_id);
    expect(lessonJob.status).toBe("completed");
    expect(lessonJob.result.content.length).toBeGreaterThan(100);

    const lessonId = lessonJob.result.id;
    const completeResponse = await request.post(`${API_BASE_URL}/lessons/${lessonId}/complete`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(completeResponse.ok()).toBeTruthy();

    const awardResponse = await request.post(`${API_BASE_URL}/gamification/award-xp`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: {
        learner_id: learnerId,
        xp_amount: 35,
        event_type: "lesson_completed",
        lesson_id: lessonId,
      },
    });
    expect(awardResponse.ok()).toBeTruthy();
    expect((await awardResponse.json()).profile.total_xp).toBeGreaterThanOrEqual(35);

    await page.goto("/plan");
    await expect(page.getByRole("heading", { name: /study plan/i })).toBeVisible();
    await page.goto("/badges");
    await expect(page.getByRole("heading", { name: /achievements/i })).toBeVisible();
  });
});
