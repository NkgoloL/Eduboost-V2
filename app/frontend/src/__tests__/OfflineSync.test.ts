import { beforeEach, describe, expect, it, vi } from "vitest";
import { cacheLessonSnapshot, flushOfflineLessonSync, getCachedLessonSnapshot, queueLessonSync } from "../lib/api/offlineSync";
import { LearnerService } from "../lib/api/services";

describe("offline sync helpers", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  it("queues and flushes lesson sync events", async () => {
    vi.spyOn(window.navigator, "onLine", "get").mockReturnValue(true);
    vi.spyOn(LearnerService, "syncLessonResponses").mockResolvedValue({ processed: 1, queued: 0 });

    queueLessonSync({
      lesson_id: "lesson-1",
      event_type: "complete",
      completed_at: "2026-05-04T00:00:00Z",
    });

    await flushOfflineLessonSync();
    expect(window.localStorage.getItem("eb_offline_lesson_sync_queue")).toBe("[]");
  });

  it("leaves the queue untouched while offline", async () => {
    vi.spyOn(window.navigator, "onLine", "get").mockReturnValue(false);
    const syncSpy = vi.spyOn(LearnerService, "syncLessonResponses");
    queueLessonSync({
      lesson_id: "lesson-2",
      event_type: "complete",
      completed_at: "2026-05-04T00:00:00Z",
    });

    await flushOfflineLessonSync();
    expect(syncSpy).not.toHaveBeenCalled();
  });

  it("caches lesson snapshots for offline reuse", () => {
    cacheLessonSnapshot("learner-1", "MATH", "Fractions", {
      id: "lesson-1",
      title: "Fractions",
      content: "Half a pizza is 1/2.",
    });

    expect(getCachedLessonSnapshot("learner-1", "MATH", "Fractions")?.title).toBe("Fractions");
  });
});
