// Tutor route integration tests (full suite below)
import { beforeEach, describe, expect, test, vi } from "vitest";
import type { NextRequest } from "next/server";
import { POST as tutorRoute } from "@/app/api/tutor/route";
import { clearRateLimitStore } from "@/lib/tutor/rate-limit";
import { clearTutorAuditEvents } from "@/lib/tutor/audit";

const createRequest = (body: unknown, headers: Record<string, string> = {}) => {
  const jsonBody = JSON.stringify(body);
  const request = {
    headers: new Headers({ "content-type": "application/json", ...headers }),
    method: "POST",
    json: async () => JSON.parse(jsonBody),
  } as unknown as NextRequest;
  return request;
};

beforeEach(() => {
  clearRateLimitStore();
  clearTutorAuditEvents();
  vi.restoreAllMocks();
});

describe("Tutor API route", () => {
  test("rejects a request missing lesson_id", async () => {
    const response = await tutorRoute(createRequest({ question: "What is 2+2?" }));
    expect(response.status).toBe(400);
    const payload = await response.json();
    expect(payload.error.message).toBe("Lesson identifier is required.");
  });

  test("returns a safe refusal for broad free-chat prompts before provider call", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ message: "Should never reach provider" }), { status: 200, headers: { "Content-Type": "application/json" } })
    );

    const response = await tutorRoute(createRequest({ lesson_id: "lesson-1", question: "Tell me a story about unicorns." }));
    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.type).toBe("refusal");
    expect(payload.message).toContain("lesson-focused questions");
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  test("rate-limits repeated requests from the same identity", async () => {
    const identity = "203.0.113.1";
    const request = createRequest({ lesson_id: "lesson-1", question: "What is the lesson about?" }, { "x-forwarded-for": identity });

    for (let i = 0; i < 6; i += 1) {
      const response = await tutorRoute(request);
      expect(response.status).toBe(200);
    }

    const response = await tutorRoute(request);
    expect(response.status).toBe(429);
    const payload = await response.json();
    expect(payload.message).toContain("Please wait a moment");
  });

  test("forwards a lesson-bounded tutor request to the provider and returns filtered output", async () => {
    process.env.TUTOR_PROVIDER_API_URL = "https://provider.example.com/tutor";
    process.env.TUTOR_PROVIDER_API_KEY = "secret-key";

    const providerResponse = new Response(JSON.stringify({ message: "The lesson answer is 42." }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(providerResponse);
    const response = await tutorRoute(createRequest({ lesson_id: "lesson-1", question: "What is 2+2?", subject_code: "MATH" }));

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const [url, options] = fetchSpy.mock.calls[0]!;
    expect(url).toBe("https://provider.example.com/tutor");
    expect((options as RequestInit).headers).toBeInstanceOf(Headers);
    const headers = (options as RequestInit).headers as Headers | undefined;
    expect(headers?.get("authorization")).toBe("Bearer secret-key");

    expect(response.status).toBe(200);
    const payload = await response.json();
    expect(payload.type).toBe("answer");
    expect(payload.message).toBe("The lesson answer is 42.");
  });
});
