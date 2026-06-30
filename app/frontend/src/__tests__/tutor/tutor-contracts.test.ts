import { expect, test, vi } from "vitest";
import { askTutor } from "@/lib/tutor/client";
import type { TutorRequest } from "@/lib/tutor/types";

test("askTutor posts a lesson-bounded tutor request to the API route", async () => {
  const request: TutorRequest = {
    lesson_id: "lesson-1",
    question: "How do I solve this exercise?",
    subject_code: "MATH",
  };

  const responsePayload = { type: "answer", message: "Use the formula from the lesson.", safe: true };
  const fetchSpy = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(responsePayload), { status: 200, headers: { "Content-Type": "application/json" } })
  );
  vi.stubGlobal("fetch", fetchSpy);

  const result = await askTutor(request);
  expect(result).toEqual(responsePayload);
  expect(fetchSpy).toHaveBeenCalledWith("/api/tutor", expect.objectContaining({ method: "POST", body: JSON.stringify(request) }));
});
