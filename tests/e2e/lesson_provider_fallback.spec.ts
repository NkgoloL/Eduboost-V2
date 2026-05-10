// tests/e2e/lesson_provider_fallback.spec.ts
//
// L5-02 — EduBoost SA Phase 5
// Playwright E2E: LLM provider unavailable → circuit breaker activates →
// learner sees an appropriate offline/fallback message (not an unhandled 500).
//
// Strategy: the test uses the admin chaos endpoint (only available in
// non-production environments) to force the primary provider into a
// simulated fault state, then verifies the UI surfaces the correct
// degraded-mode message and the circuit breaker telemetry increments.

import { test, expect, type APIRequestContext } from "@playwright/test";

const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";
const ADMIN_TOKEN = process.env.ADMIN_API_TOKEN ?? "dev-admin-token";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function forceProviderFault(
  request: APIRequestContext,
  provider: "groq" | "anthropic",
  fault: "timeout" | "error_500",
): Promise<void> {
  const res = await request.post(`${API_BASE}/api/v2/admin/chaos/llm-provider`, {
    headers: { Authorization: `Bearer ${ADMIN_TOKEN}` },
    data: { provider, fault_mode: fault, duration_seconds: 60 },
  });
  expect(res.ok(), `Could not inject fault into provider ${provider}`).toBeTruthy();
}

async function clearProviderFaults(request: APIRequestContext): Promise<void> {
  await request.delete(`${API_BASE}/api/v2/admin/chaos/llm-provider`, {
    headers: { Authorization: `Bearer ${ADMIN_TOKEN}` },
  });
}

async function getLearnerToken(request: APIRequestContext): Promise<string> {
  const res = await request.post(`${API_BASE}/api/v2/auth/token`, {
    data: {
      email: process.env.LEARNER_EMAIL ?? "learner@test.eduboost.sa",
      password: process.env.LEARNER_PASSWORD ?? "TestPass123!",
    },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.access_token as string;
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

test.use({ storageState: "playwright/.auth/guardian.json" });

test.afterEach(async ({ request }) => {
  // Always clear injected faults so subsequent tests are not affected.
  await clearProviderFaults(request);
});

// ---------------------------------------------------------------------------
// L5-02: Both providers unavailable → circuit breaker → graceful UI message
// ---------------------------------------------------------------------------

test(
  "L5-02 | primary + fallback provider unavailable → circuit breaker → learner sees fallback message",
  async ({ page, request }) => {
    // 1. Inject faults on both Groq (primary) and Anthropic (fallback)
    await forceProviderFault(request, "groq", "error_500");
    await forceProviderFault(request, "anthropic", "error_500");

    // 2. Navigate to a lesson generation trigger in the UI
    await page.goto("/dashboard");
    await expect(page.getByTestId("start-lesson-btn")).toBeVisible({ timeout: 10_000 });
    await page.getByTestId("start-lesson-btn").click();

    // 3. The UI should enter a loading state, then show a graceful degraded message
    // (not a raw error or empty screen)
    const fallbackBanner = page.getByTestId("lesson-unavailable-banner");
    await expect(fallbackBanner).toBeVisible({ timeout: 35_000 });

    // 4. The banner must contain an actionable message — never a raw stack trace
    const bannerText = await fallbackBanner.textContent();
    expect(bannerText).not.toContain("Traceback");
    expect(bannerText).not.toContain("500 Internal");
    expect(
      bannerText?.toLowerCase().includes("unavailable") ||
        bannerText?.toLowerCase().includes("try again") ||
        bannerText?.toLowerCase().includes("offline"),
      "Banner must contain a user-friendly offline/unavailable message",
    ).toBeTruthy();

    // 5. Verify via API that the circuit breaker state was recorded
    const token = await getLearnerToken(request);
    const healthRes = await request.get(`${API_BASE}/api/v2/health/llm-gateway`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(healthRes.ok()).toBeTruthy();
    const health = await healthRes.json();

    // Circuit breaker must report open state for the primary provider
    const groqState = health.providers?.groq?.circuit_breaker_state ?? health.circuit_breaker_state;
    expect(
      groqState === "open" || groqState === "half_open",
      `Circuit breaker must be open or half_open after consecutive failures — got: ${groqState}`,
    ).toBeTruthy();
  },
);

// ---------------------------------------------------------------------------
// L5-02b: Primary provider timeout → Anthropic fallback activates
// ---------------------------------------------------------------------------

test(
  "L5-02b | primary provider timeout → Anthropic fallback activates → lesson is returned",
  async ({ request }) => {
    // Only fault the primary (Groq) — fallback (Anthropic) stays healthy
    await forceProviderFault(request, "groq", "timeout");

    const token = await getLearnerToken(request);

    const res = await request.post(`${API_BASE}/api/v2/lessons/generate`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { caps_ref: "4.M.1.1", difficulty: "on_level" },
      timeout: 60_000, // Allow extra time for fallback path
    });

    // The fallback path must still return a valid lesson, not an error
    expect(res.ok(), `Fallback generation failed: HTTP ${res.status()}`).toBeTruthy();
    const lesson = await res.json();

    // Verify the lesson was served by the fallback provider
    expect(lesson.provider, "Lesson must be served by anthropic fallback").toBe("anthropic");

    // Core schema integrity must hold even on the fallback path
    expect(lesson.caps_ref).toBe("4.M.1.1");
    expect(lesson.answer_key_verified).toBe(true);
    expect(
      (lesson.worked_examples as unknown[]).length >= 2,
      "Fallback lesson must still have ≥2 worked examples",
    ).toBeTruthy();
  },
);

// ---------------------------------------------------------------------------
// L5-02c: Circuit breaker does not recover until fault is cleared
// ---------------------------------------------------------------------------

test(
  "L5-02c | circuit breaker stays open until fault is cleared",
  async ({ request }) => {
    // Inject 3 consecutive failures to trip the breaker
    await forceProviderFault(request, "groq", "error_500");

    const token = await getLearnerToken(request);

    // Trigger 3 generation attempts that will fail
    for (let i = 0; i < 3; i++) {
      await request.post(`${API_BASE}/api/v2/lessons/generate`, {
        headers: { Authorization: `Bearer ${token}` },
        data: { caps_ref: "4.M.1.1", difficulty: "on_level" },
        timeout: 15_000,
      });
    }

    // Breaker should now be open
    const beforeClear = await request.get(`${API_BASE}/api/v2/health/llm-gateway`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const beforeBody = await beforeClear.json();
    const stateBeforeClear =
      beforeBody.providers?.groq?.circuit_breaker_state ?? beforeBody.circuit_breaker_state;
    expect(["open", "half_open"]).toContain(stateBeforeClear);

    // Clear the fault
    await clearProviderFaults(request);

    // After a short cool-down the breaker should reset (half_open → closed)
    // The half-open probe happens on the next request
    await request.post(`${API_BASE}/api/v2/lessons/generate`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { caps_ref: "4.M.1.1", difficulty: "on_level" },
      timeout: 30_000,
    });

    const afterClear = await request.get(`${API_BASE}/api/v2/health/llm-gateway`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const afterBody = await afterClear.json();
    const stateAfterClear =
      afterBody.providers?.groq?.circuit_breaker_state ?? afterBody.circuit_breaker_state;
    expect(["closed", "half_open"]).toContain(stateAfterClear);
  },
);
