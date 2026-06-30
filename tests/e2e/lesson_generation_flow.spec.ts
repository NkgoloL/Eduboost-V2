// tests/e2e/lesson_generation_flow.spec.ts
//
// L5-01 — EduBoost SA Phase 5
// Playwright E2E: complete diagnostic → lesson generator receives gap topic
// (caps_ref) + misconception_tags → lesson returned is fully validated.
//
// Covers DoD gates: #10, #12
//
// Prerequisites: full docker-compose stack running; guardian + learner
// accounts created by the global setup fixture.

import { test, expect, type APIRequestContext } from "@playwright/test";

const LAUNCH_CAPS_REFS = ["4.M.1.1", "4.M.1.2", "4.M.1.3"] as const;
const API_BASE = process.env.API_BASE_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function completeDiagnostic(
  request: APIRequestContext,
  token: string,
  capsRef: string,
): Promise<{ caps_ref: string; misconception_tags: string[] }> {
  // Simulate completing a diagnostic for the given caps_ref.
  // The diagnostic engine is already live; we POST a completed session.
  const res = await request.post(`${API_BASE}/api/v2/diagnostics/complete`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      caps_ref: capsRef,
      responses: [
        { question_id: "q1", answer: "B", time_spent_ms: 12000 },
        { question_id: "q2", answer: "A", time_spent_ms: 9500 },
        { question_id: "q3", answer: "C", time_spent_ms: 14000 },
      ],
    },
  });
  expect(res.ok(), `Diagnostic completion failed for ${capsRef}: ${res.status()}`).toBeTruthy();
  const body = await res.json();
  return {
    caps_ref: body.gap_topic ?? capsRef,
    misconception_tags: body.misconception_tags ?? [],
  };
}

async function generateLesson(
  request: APIRequestContext,
  token: string,
  capsRef: string,
  misconceptionTags: string[],
): Promise<Record<string, unknown>> {
  const res = await request.post(`${API_BASE}/api/v2/lessons/generate`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      caps_ref: capsRef,
      difficulty: "on_level",
      misconception_tags: misconceptionTags,
    },
    timeout: 30_000,
  });
  expect(
    res.ok(),
    `Lesson generation failed (${capsRef}): HTTP ${res.status()}`,
  ).toBeTruthy();
  return res.json();
}

// ---------------------------------------------------------------------------
// Auth fixture — reuses guardian auth state created by global setup
// ---------------------------------------------------------------------------

test.use({ storageState: "playwright/.auth/guardian.json" });

// ---------------------------------------------------------------------------
// L5-01: Full diagnostic → lesson generation → schema validation
// ---------------------------------------------------------------------------

for (const capsRef of LAUNCH_CAPS_REFS) {
  test(`L5-01 | diagnostic → lesson generation → validation | ${capsRef}`, async ({
    page,
    request,
  }) => {
    // 1. Sign in via UI to obtain a learner token
    await page.goto("/login");
    await page.getByLabel("Email").fill(process.env.LEARNER_EMAIL ?? "learner@test.eduboost.sa");
    await page.getByLabel("Password").fill(process.env.LEARNER_PASSWORD ?? "TestPass123!");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });

    // Extract the JWT from localStorage / cookie via the API
    const tokenResponse = await request.post(`${API_BASE}/api/v2/auth/token`, {
      data: {
        email: process.env.LEARNER_EMAIL ?? "learner@test.eduboost.sa",
        password: process.env.LEARNER_PASSWORD ?? "TestPass123!",
      },
    });
    expect(tokenResponse.ok()).toBeTruthy();
    const { access_token } = await tokenResponse.json();

    // 2. Complete a diagnostic and retrieve the gap topic + misconception tags
    const { caps_ref: gapCapsRef, misconception_tags } = await completeDiagnostic(
      request,
      access_token,
      capsRef,
    );

    expect(gapCapsRef).toBe(capsRef);

    // 3. Generate a lesson targeted at the gap topic
    const lesson = await generateLesson(request, access_token, gapCapsRef, misconception_tags);

    // 4. Schema assertions — all DoD gate #4 criteria
    expect(lesson.caps_ref, "caps_ref must match requested ref").toBe(capsRef);

    expect(
      typeof lesson.explanation === "string" && (lesson.explanation as string).length > 50,
      "explanation must be non-empty (>50 chars)",
    ).toBeTruthy();

    const workedExamples = lesson.worked_examples as unknown[];
    expect(
      Array.isArray(workedExamples) && workedExamples.length >= 2,
      "≥2 worked examples required",
    ).toBeTruthy();

    const practiceQuestions = lesson.practice_questions as unknown[];
    expect(
      Array.isArray(practiceQuestions) && practiceQuestions.length >= 3,
      "≥3 practice questions required",
    ).toBeTruthy();

    expect(lesson.answer_key_verified, "answer_key_verified must be true").toBe(true);

    expect(lesson.safety_classification, "safety_classification must be 'safe'").toBe("safe");

    expect(lesson.pii_check_passed, "pii_check_passed must be true").toBe(true);

    // 5. Quality score must be a float in [0, 1]
    const qs = lesson.quality_score as number | null;
    if (qs !== null) {
      expect(qs).toBeGreaterThanOrEqual(0.0);
      expect(qs).toBeLessThanOrEqual(1.0);
    }

    // 6. Verify lesson appears in the learner's study plan on the UI
    await page.goto(`/lessons/${lesson.lesson_id}`);
    await expect(page.getByTestId("lesson-caps-ref")).toHaveText(capsRef, { timeout: 10_000 });

    // 7. L5-11: AI transparency label must be visible (DoD gate #12)
    await expect(
      page.getByTestId("lesson-trust-label"),
      "AI trust label must be visible on lesson page",
    ).toBeVisible();

    // 8. L5-11: 'Report a content problem' button must be wired up
    await expect(
      page.getByTestId("lesson-report-btn"),
      "'Report a content problem' button must be present",
    ).toBeVisible();

    // Clicking the report button should open the report modal (not navigate away)
    await page.getByTestId("lesson-report-btn").click();
    await expect(page.getByTestId("report-modal")).toBeVisible({ timeout: 5_000 });
    // Close the modal cleanly
    await page.getByTestId("report-modal-close").click();
    await expect(page.getByTestId("report-modal")).not.toBeVisible();
  });
}

// ---------------------------------------------------------------------------
// Additional: confirm misconception_tags are used when provided
// ---------------------------------------------------------------------------

test("L5-01 | lesson uses misconception_tags from diagnostic", async ({ request }) => {
  const tokenResponse = await request.post(`${API_BASE}/api/v2/auth/token`, {
    data: {
      email: process.env.LEARNER_EMAIL ?? "learner@test.eduboost.sa",
      password: process.env.LEARNER_PASSWORD ?? "TestPass123!",
    },
  });
  expect(tokenResponse.ok()).toBeTruthy();
  const { access_token } = await tokenResponse.json();

  const lesson = await generateLesson(request, access_token, "4.M.1.1", [
    "place_value_confusion",
    "leading_zeros",
  ]);

  // Lesson must carry remediation hints tied to the supplied misconception tags
  const hints = lesson.remediation_hints as Array<{ misconception_tag: string }>;
  expect(Array.isArray(hints) && hints.length > 0, "remediation_hints required").toBeTruthy();

  const tags = hints.map((h) => h.misconception_tag);
  const hasAtLeastOne = tags.some((t) =>
    ["place_value_confusion", "leading_zeros"].includes(t),
  );
  expect(hasAtLeastOne, "At least one supplied misconception tag must appear in hints").toBeTruthy();
});
