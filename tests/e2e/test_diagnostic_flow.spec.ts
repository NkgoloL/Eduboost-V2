/**
 * Phase 5 — P5-01 & P5-02
 * Playwright E2E Tests: Full Diagnostic + Post-Diagnostic Lesson Generation
 *
 * P5-01: guardian login → consent → diagnostic (Grade 4 Maths)
 *        → verify 8–12 items served → ability estimate returned → study plan updated
 * P5-02: post-diagnostic → lesson generation receives gap topic
 *        → lesson returned has correct caps_ref → lesson contains explanation + practice questions
 */

import { test, expect, type Page, type APIRequestContext } from "@playwright/test";

// ─── helpers ────────────────────────────────────────────────────────────────

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3050";
const API_URL = process.env.API_URL ?? "http://localhost:8000";

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

interface DiagnosticSession {
  session_id: string;
  caps_ref: string;
  grade: number;
  subject: string;
}

interface DiagnosticItem {
  item_id: string;
  stem: string;
  options: { label: string; text: string }[];
  caps_ref: string;
}

interface DiagnosticResult {
  session_id: string;
  ability_estimate: number;
  standard_error: number;
  gap_topics: { caps_ref: string; misconception_tags: string[] }[];
  items_served: number;
  completed_at: string;
}

interface StudyPlan {
  plan_id: string;
  learner_id: string;
  topics: { caps_ref: string; priority: number; mastery_score: number }[];
  updated_at: string;
}

interface Lesson {
  lesson_id: string;
  caps_ref: string;
  title: string;
  explanation: string;
  practice_questions: { stem: string; answer_key: string }[];
  misconceptions_addressed: string[];
}

async function guardianLogin(
  request: APIRequestContext,
  email: string,
  password: string
): Promise<AuthTokens> {
  const resp = await request.post(`${API_URL}/api/v2/auth/login`, {
    data: { email, password },
  });
  expect(resp.status()).toBe(200);
  return resp.json();
}

async function createLearnerConsent(
  request: APIRequestContext,
  token: string,
  learnerId: string
): Promise<void> {
  const resp = await request.post(`${API_URL}/api/v2/consent`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      learner_id: learnerId,
      consent_version: "1.0",
      data_processing: true,
      ai_personalisation: true,
      guardian_signature: "E2E Test Guardian",
    },
  });
  expect(resp.status()).toBe(201);
}

async function startDiagnosticSession(
  request: APIRequestContext,
  token: string,
  learnerId: string
): Promise<DiagnosticSession> {
  const resp = await request.post(`${API_URL}/api/v2/diagnostics/sessions`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      learner_id: learnerId,
      grade: 4,
      subject: "Mathematics",
      caps_refs: ["4.M.1.1", "4.M.1.2", "4.M.1.3"],
    },
  });
  expect(resp.status()).toBe(201);
  return resp.json();
}

async function fetchNextItem(
  request: APIRequestContext,
  token: string,
  sessionId: string
): Promise<DiagnosticItem | null> {
  const resp = await request.get(
    `${API_URL}/api/v2/diagnostics/sessions/${sessionId}/next-item`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  if (resp.status() === 204) return null; // session complete
  expect(resp.status()).toBe(200);
  return resp.json();
}

async function submitAnswer(
  request: APIRequestContext,
  token: string,
  sessionId: string,
  itemId: string,
  answer: string,
  responseTimeMs: number
): Promise<void> {
  const resp = await request.post(
    `${API_URL}/api/v2/diagnostics/sessions/${sessionId}/responses`,
    {
      headers: { Authorization: `Bearer ${token}` },
      data: { item_id: itemId, answer, response_time_ms: responseTimeMs },
    }
  );
  expect(resp.status()).toBe(200);
}

async function completeDiagnosticSession(
  request: APIRequestContext,
  token: string,
  sessionId: string
): Promise<DiagnosticResult> {
  const resp = await request.post(
    `${API_URL}/api/v2/diagnostics/sessions/${sessionId}/complete`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  expect(resp.status()).toBe(200);
  return resp.json();
}

async function getStudyPlan(
  request: APIRequestContext,
  token: string,
  learnerId: string
): Promise<StudyPlan> {
  const resp = await request.get(
    `${API_URL}/api/v2/study-plans/${learnerId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  expect(resp.status()).toBe(200);
  return resp.json();
}

async function generateLesson(
  request: APIRequestContext,
  token: string,
  learnerId: string,
  capsRef: string,
  misconceptionTags: string[]
): Promise<Lesson> {
  const resp = await request.post(`${API_URL}/api/v2/lessons/generate`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      learner_id: learnerId,
      caps_ref: capsRef,
      misconception_tags: misconceptionTags,
      language: "en",
    },
  });
  expect(resp.status()).toBe(200);
  return resp.json();
}

// ─── test data ───────────────────────────────────────────────────────────────

const GUARDIAN_EMAIL = process.env.E2E_GUARDIAN_EMAIL ?? "e2e_guardian@test.eduboost.co.za";
const GUARDIAN_PASSWORD = process.env.E2E_GUARDIAN_PASSWORD ?? "E2eGuardian#2026!";
const LEARNER_ID = process.env.E2E_LEARNER_ID ?? "e2e-learner-grade4-maths";

const VALID_CAPS_REFS = new Set(["4.M.1.1", "4.M.1.2", "4.M.1.3"]);

// ─── P5-01 ───────────────────────────────────────────────────────────────────

test.describe("P5-01: Full Diagnostic Flow — Grade 4 Mathematics", () => {
  let tokens: AuthTokens;
  let sessionId: string;
  let diagnosticResult: DiagnosticResult;
  let itemsServed: DiagnosticItem[];
  let seenItemIds: Set<string>;

  test.beforeAll(async ({ request }) => {
    tokens = await guardianLogin(request, GUARDIAN_EMAIL, GUARDIAN_PASSWORD);
    await createLearnerConsent(request, tokens.access_token, LEARNER_ID);
  });

  test("1. Guardian can log in and receive JWT tokens", async ({ request }) => {
    const resp = await request.post(`${API_URL}/api/v2/auth/login`, {
      data: { email: GUARDIAN_EMAIL, password: GUARDIAN_PASSWORD },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("access_token");
    expect(body).toHaveProperty("refresh_token");
    expect(typeof body.access_token).toBe("string");
  });

  test("2. Consent record is accepted for the learner", async ({ request }) => {
    const resp = await request.get(
      `${API_URL}/api/v2/consent/${LEARNER_ID}`,
      { headers: { Authorization: `Bearer ${tokens.access_token}` } }
    );
    expect(resp.status()).toBe(200);
    const consent = await resp.json();
    expect(consent.data_processing).toBe(true);
    expect(consent.ai_personalisation).toBe(true);
  });

  test("3. Diagnostic session starts with valid Grade 4 Maths caps_refs", async ({
    request,
  }) => {
    const session = await startDiagnosticSession(
      request,
      tokens.access_token,
      LEARNER_ID
    );
    sessionId = session.session_id;
    expect(session.grade).toBe(4);
    expect(session.subject).toBe("Mathematics");
    expect(typeof sessionId).toBe("string");
    expect(sessionId.length).toBeGreaterThan(0);
  });

  test("4. 8–12 items served with no repeats; each item has required fields", async ({
    request,
  }) => {
    itemsServed = [];
    seenItemIds = new Set();
    let safetyBreak = 0;

    while (safetyBreak < 20) {
      const item = await fetchNextItem(request, tokens.access_token, sessionId);
      if (!item) break; // 204 — session complete

      // No item repeated within one session
      expect(seenItemIds.has(item.item_id)).toBe(false);
      seenItemIds.add(item.item_id);

      // Required fields present
      expect(typeof item.stem).toBe("string");
      expect(item.stem.length).toBeGreaterThan(0);
      expect(Array.isArray(item.options)).toBe(true);
      expect(item.options.length).toBeGreaterThanOrEqual(4);
      expect(VALID_CAPS_REFS.has(item.caps_ref)).toBe(true);

      itemsServed.push(item);

      // Answer with option A (deterministic for E2E)
      await submitAnswer(
        request,
        tokens.access_token,
        sessionId,
        item.item_id,
        "A",
        1500
      );
      safetyBreak++;
    }

    expect(itemsServed.length).toBeGreaterThanOrEqual(8);
    expect(itemsServed.length).toBeLessThanOrEqual(12);
  });

  test("5. Completing session returns ability estimate and gap topics", async ({
    request,
  }) => {
    diagnosticResult = await completeDiagnosticSession(
      request,
      tokens.access_token,
      sessionId
    );

    expect(diagnosticResult.session_id).toBe(sessionId);
    expect(typeof diagnosticResult.ability_estimate).toBe("number");
    expect(diagnosticResult.ability_estimate).toBeGreaterThanOrEqual(-4);
    expect(diagnosticResult.ability_estimate).toBeLessThanOrEqual(4);
    expect(typeof diagnosticResult.standard_error).toBe("number");
    expect(diagnosticResult.standard_error).toBeGreaterThan(0);
    expect(diagnosticResult.standard_error).toBeLessThan(2);
    expect(Array.isArray(diagnosticResult.gap_topics)).toBe(true);
    expect(diagnosticResult.items_served).toBe(itemsServed.length);
  });

  test("6. Gap topics reference valid CAPS refs with misconception tags", async () => {
    for (const gap of diagnosticResult.gap_topics) {
      expect(VALID_CAPS_REFS.has(gap.caps_ref)).toBe(true);
      expect(Array.isArray(gap.misconception_tags)).toBe(true);
      expect(gap.misconception_tags.length).toBeGreaterThan(0);
    }
  });

  test("7. Study plan updated after diagnostic — weakest topic has highest priority", async ({
    request,
  }) => {
    const studyPlan = await getStudyPlan(
      request,
      tokens.access_token,
      LEARNER_ID
    );

    expect(studyPlan.learner_id).toBe(LEARNER_ID);
    expect(Array.isArray(studyPlan.topics)).toBe(true);
    expect(studyPlan.topics.length).toBeGreaterThan(0);

    // updated_at should be recent (within last 60 seconds)
    const updatedAt = new Date(studyPlan.updated_at).getTime();
    const now = Date.now();
    expect(now - updatedAt).toBeLessThan(60_000);

    // Topics from launch scope should appear
    const planCapsRefs = studyPlan.topics.map((t) => t.caps_ref);
    const launchRefsInPlan = planCapsRefs.filter((r) => VALID_CAPS_REFS.has(r));
    expect(launchRefsInPlan.length).toBeGreaterThan(0);

    // Priority is ordered: higher priority number = weaker topic
    const sorted = [...studyPlan.topics].sort((a, b) => b.priority - a.priority);
    expect(studyPlan.topics[0].caps_ref).toBe(sorted[0].caps_ref);
  });
});

// ─── P5-02 ───────────────────────────────────────────────────────────────────

test.describe("P5-02: Post-Diagnostic Lesson Generation", () => {
  let tokens: AuthTokens;
  let gapCapsRef: string;
  let misconceptionTags: string[];
  let lesson: Lesson;

  test.beforeAll(async ({ request }) => {
    tokens = await guardianLogin(request, GUARDIAN_EMAIL, GUARDIAN_PASSWORD);

    // Run a short diagnostic to get real gap data
    const session = await startDiagnosticSession(
      request,
      tokens.access_token,
      LEARNER_ID
    );

    let itemCount = 0;
    while (itemCount < 8) {
      const item = await fetchNextItem(
        request,
        tokens.access_token,
        session.session_id
      );
      if (!item) break;
      await submitAnswer(
        request,
        tokens.access_token,
        session.session_id,
        item.item_id,
        "A",
        1200
      );
      itemCount++;
    }

    const result = await completeDiagnosticSession(
      request,
      tokens.access_token,
      session.session_id
    );

    // Use weakest gap topic (first in list) for lesson generation
    const topGap = result.gap_topics[0] ?? {
      caps_ref: "4.M.1.1",
      misconception_tags: ["place_value_confusion"],
    };
    gapCapsRef = topGap.caps_ref;
    misconceptionTags = topGap.misconception_tags;
  });

  test("1. Lesson generation accepts gap topic and misconception tags", async ({
    request,
  }) => {
    lesson = await generateLesson(
      request,
      tokens.access_token,
      LEARNER_ID,
      gapCapsRef,
      misconceptionTags
    );
    expect(lesson).toBeTruthy();
  });

  test("2. Returned lesson has the correct caps_ref matching the diagnostic gap", async () => {
    expect(lesson.caps_ref).toBe(gapCapsRef);
  });

  test("3. Lesson contains a non-empty explanation written for Grade 4 level", async () => {
    expect(typeof lesson.explanation).toBe("string");
    expect(lesson.explanation.length).toBeGreaterThan(50);
    // explanation must not be a raw JSON blob
    expect(lesson.explanation).not.toMatch(/^\{/);
  });

  test("4. Lesson contains at least 2 practice questions with answer keys", async () => {
    expect(Array.isArray(lesson.practice_questions)).toBe(true);
    expect(lesson.practice_questions.length).toBeGreaterThanOrEqual(2);

    for (const q of lesson.practice_questions) {
      expect(typeof q.stem).toBe("string");
      expect(q.stem.length).toBeGreaterThan(0);
      expect(typeof q.answer_key).toBe("string");
      expect(q.answer_key.length).toBeGreaterThan(0);
    }
  });

  test("5. Lesson addresses at least one misconception from the diagnostic", async () => {
    expect(Array.isArray(lesson.misconceptions_addressed)).toBe(true);
    expect(lesson.misconceptions_addressed.length).toBeGreaterThan(0);

    const addressed = new Set(lesson.misconceptions_addressed);
    const overlap = misconceptionTags.filter((t) => addressed.has(t));
    expect(overlap.length).toBeGreaterThan(0);
  });

  test("6. Lesson round-trip via UI — frontend renders lesson correctly", async ({
    page,
  }: {
    page: Page;
  }) => {
    // Navigate to the lesson page using the lesson_id
    await page.goto(`${BASE_URL}/lesson/${lesson.lesson_id}`);
    await page.waitForLoadState("networkidle");

    // Title rendered
    await expect(page.locator("[data-testid='lesson-title']")).toBeVisible();

    // Explanation text visible
    const explanationEl = page.locator("[data-testid='lesson-explanation']");
    await expect(explanationEl).toBeVisible();
    const explanationText = await explanationEl.textContent();
    expect(explanationText?.length ?? 0).toBeGreaterThan(10);

    // Practice questions rendered
    const questions = page.locator("[data-testid='practice-question']");
    await expect(questions).toHaveCount(
      lesson.practice_questions.length,
      { timeout: 5000 }
    );
  });
});

// ─── P5-05: Exposure enforcement across 3 sessions ───────────────────────────

test.describe("P5-05: Item Exposure Enforcement — No Repeats Across 3 Sessions", () => {
  let tokens: AuthTokens;
  const allSeenItemIds: Set<string> = new Set();

  test.beforeAll(async ({ request }) => {
    tokens = await guardianLogin(request, GUARDIAN_EMAIL, GUARDIAN_PASSWORD);
  });

  for (let sessionIndex = 1; sessionIndex <= 3; sessionIndex++) {
    test(`Session ${sessionIndex}: items served are all unseen`, async ({
      request,
    }) => {
      const session = await startDiagnosticSession(
        request,
        tokens.access_token,
        LEARNER_ID
      );

      const sessionItemIds: Set<string> = new Set();
      let safetyBreak = 0;

      while (safetyBreak < 15) {
        const item = await fetchNextItem(
          request,
          tokens.access_token,
          session.session_id
        );
        if (!item) break;

        // Must not repeat within this session
        expect(sessionItemIds.has(item.item_id)).toBe(false);
        sessionItemIds.add(item.item_id);

        // Must not repeat from any previous session
        expect(allSeenItemIds.has(item.item_id)).toBe(false);

        await submitAnswer(
          request,
          tokens.access_token,
          session.session_id,
          item.item_id,
          "B",
          1000
        );
        safetyBreak++;
      }

      await completeDiagnosticSession(
        request,
        tokens.access_token,
        session.session_id
      );

      // Add this session's items to global seen set
      sessionItemIds.forEach((id) => allSeenItemIds.add(id));
    });
  }
});
