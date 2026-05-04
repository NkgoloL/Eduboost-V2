import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchApi, waitForJobResult } from "../lib/api/client";
import { AuthService, DiagnosticService, LearnerService, ParentService } from "../lib/api/services";

describe("API layer", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    window.localStorage.setItem("guardian_token", "token-123");
  });

  it("adds auth headers for API calls", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: true }),
    } as Response);

    await fetchApi("/parents/demo/export");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/parents/demo/export"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer token-123",
          "Content-Type": "application/json",
        }),
      })
    );
  });

  it("handles 204 responses cleanly", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => null,
    } as Response);

    await expect(fetchApi("/lessons/demo/complete", { method: "POST" })).resolves.toBeNull();
  });

  it("surfaces API detail messages on failure", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 403,
      statusText: "Forbidden",
      json: async () => ({ detail: "No access" }),
    } as Response);

    await expect(fetchApi("/parents/demo/export")).rejects.toThrow("No access");
  });

  it("waits for background jobs to complete", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          job_id: "job-1",
          operation: "lesson_generation",
          status: "running",
          payload: {},
          result: null,
          error: null,
          created_at: "now",
          updated_at: "now",
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          job_id: "job-1",
          operation: "lesson_generation",
          status: "completed",
          payload: {},
          result: { title: "Fractions" },
          error: null,
          created_at: "now",
          updated_at: "later",
        }),
      } as Response);

    const result = await waitForJobResult<{ title: string }>({
      job_id: "job-1",
      operation: "lesson_generation",
      status: "queued",
    });
    expect(result.title).toBe("Fractions");
  });

  it("hydrates lesson generation jobs through the service layer", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ job_id: "job-2", operation: "lesson_generation", status: "queued" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          job_id: "job-2",
          operation: "lesson_generation",
          status: "completed",
          payload: {},
          result: { id: "lesson-1", title: "Energy" },
          error: null,
          created_at: "now",
          updated_at: "later",
        }),
      } as Response);

    const result = await LearnerService.generateLesson({
      learner_id: "learner-1",
      subject: "NS",
      topic: "Energy",
      language: "en",
    });

    expect(result.id).toBe("lesson-1");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("supports the rest of the service layer endpoints", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ access_token: "a" }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ access_token: "b" }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ learner_id: "learner-1", grade: 4 }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ learner_id: "learner-1", grade: 4 }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ total_xp: 55, level: 1, streak_days: 2, badges: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ job_id: "job-3", operation: "study_plan_generation", status: "queued" }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ job_id: "job-3", operation: "study_plan_generation", status: "completed", payload: {}, result: { week_focus: "Math" }, error: null, created_at: "now", updated_at: "later" }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ mastery: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ detail: "done" }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ processed: 1, queued: 0 }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ awarded: true, xp_amount: 35 }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ guardian_id: "guardian-1", subscription_tier: "premium", exports: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ theta_after: 0.2 }) } as Response);

    await AuthService.registerGuardian({ display_name: "Sam", email: "sam@example.com", password: "password123" });
    await AuthService.loginGuardian({ email: "sam@example.com", password: "password123" });
    await LearnerService.registerLearner({ display_name: "Avi", grade: 4, language: "en" });
    await LearnerService.getProfile("learner-1");
    await LearnerService.getGamificationProfile("learner-1");
    await LearnerService.getStudyPlan("learner-1");
    await LearnerService.getMastery("learner-1");
    await LearnerService.markLessonComplete("lesson-1");
    await LearnerService.syncLessonResponses([{ lesson_id: "lesson-1", event_type: "complete" }]);
    await LearnerService.awardXP({ learner_id: "learner-1", xp_amount: 35 });
    await ParentService.getExportBundle("guardian-1");
    await DiagnosticService.runLegacy({ learner_id: "learner-1", answers: [] });

    expect(fetchMock).toHaveBeenCalled();
  });

  it("maps diagnostic item payloads into the UI shape", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [
        { id: "item-1", question: "Question?", options: ["A", "B"], subject: "MATH", topic: "Fractions" },
      ],
    } as Response);

    const items = await DiagnosticService.getItems("learner-1");
    expect(items[0].item_id).toBe("item-1");
    expect(items[0].question_text).toBe("Question?");
  });

  it("retrieves the parent dashboard bundle", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        guardian_id: "guardian-1",
        subscription_tier: "premium",
        generated_at: "now",
        learners: [],
      }),
    } as Response);

    const result = await ParentService.getTrustDashboard("guardian-1");
    expect(result.guardian_id).toBe("guardian-1");
  });
});
