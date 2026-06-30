import { expect, test } from "vitest";
import { createTutorRefusalResponse, filterTutorInput, filterTutorOutput, sanitizeLearnerPrompt, validateTutorRequest } from "@/lib/tutor/safety";

test("validateTutorRequest rejects invalid payloads", () => {
  expect(validateTutorRequest(null).ok).toBe(false);
  expect(validateTutorRequest({ question: "hi" }).ok).toBe(false);
  expect(validateTutorRequest({ lesson_id: "lesson-1" }).ok).toBe(false);
});

test("sanitizeLearnerPrompt removes email and numeric identifiers", () => {
  const sanitized = sanitizeLearnerPrompt("Contact me at alice@example.com or 555-123-4567.");
  expect(sanitized).not.toContain("alice@example.com");
  expect(sanitized).not.toContain("555-123-4567");
  expect(sanitized).toContain("[REDACTED]");
});

test("filterTutorInput refuses broad free-chat prompts", () => {
  const result = filterTutorInput({ lesson_id: "lesson-1", question: "Tell me a story", subject_code: "ENG" });
  expect(result.refusalReason).toContain("lesson-focused questions");
});

test("filterTutorOutput converts empty responses into safe refusals", () => {
  const response = filterTutorOutput({ type: "answer", message: "" });
  expect(response.type).toBe("refusal");
  expect(response.safe).toBe(true);
});

test("createTutorRefusalResponse returns a safe refusal shape", () => {
  const response = createTutorRefusalResponse("No free chat allowed.");
  expect(response.type).toBe("refusal");
  expect(response.safe).toBe(true);
  expect(response.message).toContain("No free chat allowed.");
});
