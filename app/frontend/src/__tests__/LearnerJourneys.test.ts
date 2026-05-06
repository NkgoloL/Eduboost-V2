import { readFileSync } from "node:fs";
import { join } from "node:path";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LearnerService } from "../lib/api/services";

const sourcePath = (...parts: string[]) => join(process.cwd(), "src", ...parts);

describe("learner journey contracts", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    window.localStorage.setItem("guardian_token", "token-123");
  });

  it("loads dashboard data from mastery and gamification contracts", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ learner_id: "learner-1", mastery: [{ subject_code: "MATH", mastery_score: 0.72 }] }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ learner_id: "learner-1", total_xp: 35, level: 1, streak_days: 2, badges: [] }),
      } as Response);

    const mastery = await LearnerService.getMastery("learner-1");
    const profile = await LearnerService.getGamificationProfile("learner-1");

    expect(mastery.mastery[0]).toMatchObject({ subject_code: "MATH", mastery_score: 0.72 });
    expect(profile.earned_badges).toEqual([]);
    expect(fetchMock).toHaveBeenNthCalledWith(1, expect.stringContaining("/learners/learner-1/mastery"), expect.any(Object));
    expect(fetchMock).toHaveBeenNthCalledWith(2, expect.stringContaining("/gamification/profile/learner-1"), expect.any(Object));
  });

  it("normalizes study-plan jobs into both days and schedule shapes", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ job_id: "job-plan", operation: "study_plan_generation", status: "queued" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          job_id: "job-plan",
          operation: "study_plan_generation",
          status: "completed",
          payload: {},
          result: { plan_id: "plan-1", schedule: { Mon: [{ label: "Fractions", type: "gap-fill" }] } },
          error: null,
          created_at: "now",
          updated_at: "later",
        }),
      } as Response);

    const plan = await LearnerService.getStudyPlan("learner-1");

    expect(plan.days?.Mon[0].label).toBe("Fractions");
    expect(plan.schedule?.Mon[0].type).toBe("gap-fill");
    expect(plan.week_focus).toBe("Balanced revision and grade-level progress");
  });

  it("normalizes lesson generation and completion award responses", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ job_id: "job-lesson", operation: "lesson_generation", status: "queued" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          job_id: "job-lesson",
          operation: "lesson_generation",
          status: "completed",
          payload: {},
          result: { id: "lesson-1", title: "Fractions" },
          error: null,
          created_at: "now",
          updated_at: "later",
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          awarded: true,
          xp_amount: 35,
          lesson_completed: true,
          profile: { learner_id: "learner-1", total_xp: 35, level: 1, streak_days: 0, earned_badges: [] },
        }),
      } as Response);

    const lesson = await LearnerService.generateLesson({
      learner_id: "learner-1",
      subject: "MATH",
      topic: "Fractions",
      language: "en",
    });
    const award = await LearnerService.awardXP({
      learner_id: "learner-1",
      xp_amount: 35,
      event_type: "lesson_completed",
      lesson_id: "lesson-1",
    });

    expect(lesson.content).toBe("Your lesson is ready.");
    expect(award.profile?.total_xp).toBe(35);
  });

  it("keeps learner pages wired for failed and empty states", () => {
    const dashboard = readFileSync(sourcePath("app", "(learner)", "dashboard", "page.tsx"), "utf8");
    const plan = readFileSync(sourcePath("app", "(learner)", "plan", "page.tsx"), "utf8");
    const badges = readFileSync(sourcePath("app", "(learner)", "badges", "page.tsx"), "utf8");
    const lesson = readFileSync(sourcePath("app", "(learner)", "lesson", "page.tsx"), "utf8");

    expect(dashboard).toContain("error && !gamification");
    expect(plan).toContain("error && !plan");
    expect(plan).toContain("lessonHrefForPlanItem");
    expect(badges).toContain("error && !profile");
    expect(badges).toContain("No badges yet!");
    expect(lesson).toContain("completionError");
    expect(lesson).toContain("Reconnect to generate this lesson");
  });
});
