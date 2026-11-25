/// <reference types="vitest" />
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  DiagnosticResultsPage,
  ParentLearnerReportPage,
  SeededDiagnosticPage,
} from "@/components/e2e/SeededE2ERoutePages";

describe("learner features paused pending review", () => {
  it("does not render a seeded diagnostic or placement result", () => {
    const { rerender, container } = render(<SeededDiagnosticPage />);
    expect(screen.getByTestId("diagnostic-disabled")).toBeInTheDocument();
    expect(screen.getByText(/check-ins are temporarily unavailable/i)).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/θ|subject mastery|knowledge gaps/i);

    rerender(<DiagnosticResultsPage learnerId="synthetic-learner" />);
    expect(screen.getByText(/diagnostic results unavailable/i)).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/θ|subject mastery|knowledge gaps/i);
  });

  it("does not expose mastery values in the parent report", () => {
    const { container } = render(<ParentLearnerReportPage learnerId="synthetic-learner" />);
    expect(screen.getByTestId("learning-summary-disabled")).toBeInTheDocument();
    expect(screen.getByText(/temporarily unavailable/i)).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/θ\\s*[-+]?\\d|\\b\\d+%\\b|subject mastery|knowledge gaps/i);
  });
});

it("does not serialize a mastery fixture in the dashboard shell data", async () => {
  const { getLearnerDashboardShellData } = await import("@/lib/learner/server-loaders");
  const shell = await getLearnerDashboardShellData();
  expect(shell).not.toHaveProperty("initialMastery");
  expect(shell.initialLearner).not.toHaveProperty("archetype");
});
