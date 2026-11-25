import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import FeaturePanels, { DashboardPanel, DiagnosticPanel, LessonPanel } from "../src/components/eduboost/FeaturePanels";
import { LearnerProvider } from "../src/context/LearnerContext";

// Mock the API calls so we don't try to fetch during tests
vi.mock("../src/components/eduboost/api", () => ({
  getLearnerMasteryAPI: vi.fn().mockResolvedValue({ mastery: [] }),
  runDiagnosticAPI: vi.fn().mockResolvedValue({ gap_report: { mastery_score: 0.85 } }),
  awardXPAPI: vi.fn().mockResolvedValue({ success: true }),
  getLearnerProfileAPI: vi.fn().mockResolvedValue({ level: 2, total_xp: 150 }),
}));

describe("DashboardPanel", () => {
  it("renders the welcome message without learner mastery estimates", () => {
    const mockLearner = { nickname: "TestUser", grade: 4 };
    const mockMastery = { MATH: 50, ENG: 70 };

    render(
      <LearnerProvider>
        <DashboardPanel
          learner={mockLearner}
          masteryData={mockMastery}
          onStartLesson={vi.fn()}
          onStartDiag={vi.fn()}
        />
      </LearnerProvider>
    );

    expect(screen.getByText(/Welcome, TestUser!/i)).toBeInTheDocument();
    expect(screen.getByText(/Mastery estimates and adaptive check-ins are temporarily unavailable/i)).toBeInTheDocument();
    expect(screen.queryByText("60%")).not.toBeInTheDocument();
  });
});

describe("DiagnosticPanel", () => {
  it("shows a disabled message instead of an assessment flow", async () => {
    const mockLearner = { nickname: "TestUser", grade: 4 };
    const mockOnComplete = vi.fn();

    render(
      <LearnerProvider>
        <DiagnosticPanel
          learner={mockLearner}
          onComplete={mockOnComplete}
          onBack={vi.fn()}
        />
      </LearnerProvider>
    );

    expect(screen.getByText(/Check-in unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/question bank is being rebuilt/i)).toBeInTheDocument();
    expect(mockOnComplete).not.toHaveBeenCalled();
    expect(screen.queryByText("Mathematics")).not.toBeInTheDocument();
  });
});

describe("LessonPanel and default export", () => {
  it("renders the lesson panel and wrapper export", () => {
    render(
      <LearnerProvider>
        <LessonPanel onComplete={vi.fn()} onBack={vi.fn()} />
        <FeaturePanels />
      </LearnerProvider>
    );

    expect(screen.getByText("Lesson")).toBeInTheDocument();
    expect(screen.getByText("Check-in unavailable")).toBeInTheDocument();
  });
});
