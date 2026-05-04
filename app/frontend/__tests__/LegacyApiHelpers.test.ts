import { beforeEach, describe, expect, it, vi } from "vitest";
import { awardXPAPI, getLearnerMasteryAPI, getLearnerProfileAPI, runDiagnosticAPI } from "../src/components/eduboost/api";

describe("legacy helper wrappers", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("delegates helper requests to fetch", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: true }),
    } as Response);

    await getLearnerMasteryAPI("learner-1");
    await runDiagnosticAPI("learner-1", { answers: [] });
    await awardXPAPI("learner-1", 35);
    await getLearnerProfileAPI("learner-1");

    expect(fetchMock).toHaveBeenCalledTimes(4);
  });
});
