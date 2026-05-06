import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { InteractiveDiagnostic } from "../src/components/eduboost/InteractiveDiagnostic";
import * as services from "../src/lib/api/services";

describe("InteractiveDiagnostic", () => {
  const learner = {
    learner_id: "learner-1",
    id: "learner-1",
    nickname: "Avi",
    grade: 4,
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("runs a one-item diagnostic flow to completion", async () => {
    vi.spyOn(services.DiagnosticService, "getItems").mockResolvedValue([
      { item_id: "item-1", question_text: "2 + 2 = ?", options: ["4"], subject: "MATH", topic: "Addition" },
    ]);
    vi.spyOn(services.DiagnosticService, "submit").mockResolvedValue({
      theta_after: 0.4,
      ranked_gaps: [{ subject: "MATH", topic: "Fractions" }],
    });

    const onComplete = vi.fn();
    render(<InteractiveDiagnostic learner={learner} onComplete={onComplete} onBack={vi.fn()} />);

    fireEvent.click(screen.getByText("Mathematics"));
    await waitFor(() => screen.getByText("2 + 2 = ?"));
    fireEvent.click(screen.getByText("4"));
    await waitFor(() => screen.getByText(/Assessment Complete!/i));
    fireEvent.click(screen.getByText(/Update My Study Plan/i));

    expect(onComplete).toHaveBeenCalled();
  });

  it("surfaces empty-subject and mastered-all states", async () => {
    vi.spyOn(services.DiagnosticService, "getItems")
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([
        { item_id: "item-2", question_text: "Water freezes at?", options: ["0°C"], subject: "NS", topic: "Matter" },
      ]);
    vi.spyOn(services.DiagnosticService, "submit").mockResolvedValue({
      theta_after: undefined,
      ranked_gaps: [],
    });

    render(<InteractiveDiagnostic learner={learner} onComplete={vi.fn()} onBack={vi.fn()} />);

    fireEvent.click(screen.getByText("English"));
    await waitFor(() => screen.getByText(/No diagnostic items are available/i));

    fireEvent.click(screen.getByText("Natural Science"));
    await waitFor(() => screen.getByText("Water freezes at?"));
    fireEvent.click(screen.getByText("0°C"));
    await waitFor(() => screen.getByText(/You have mastered all current concepts!/i));
    expect(screen.getByText("70%")).toBeInTheDocument();
  });
});
