import { beforeEach, describe, expect, it, vi } from "vitest";
import { DiagnosticService } from "../lib/api/services";

describe("Diagnostic API Contract", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("maps fetched diagnostic items into the frontend contract shape", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [
        {
          id: "item-1",
          question: "How many halves make a whole?",
          options: ["1", "2", "3", "4"],
          subject: "MATH",
          topic: "Fractions",
        },
      ],
    } as Response);

    const items = await DiagnosticService.getItems("learner-1");
    expect(items[0]).toMatchObject({
      item_id: "item-1",
      question_text: "How many halves make a whole?",
      subject: "MATH",
      topic: "Fractions",
    });
    expect(Array.isArray(items[0].options)).toBe(true);
  });

  it("submits the expected learner answer payload", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        session_id: "session-1",
        theta_after: 0.42,
        ranked_gaps: [],
      }),
    } as Response);

    const result = await DiagnosticService.submit("learner-1", [
      { item_id: "item-1", selected_option: "2" },
    ]);

    expect(result.theta_after).toBe(0.42);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/diagnostics/submit"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          learner_id: "learner-1",
          answers: [{ item_id: "item-1", selected_option: "2" }],
        }),
      })
    );
  });
});
