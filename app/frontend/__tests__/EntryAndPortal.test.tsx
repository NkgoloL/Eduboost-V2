import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Landing, Onboarding, ParentGateway } from "../src/components/eduboost/EntryScreens";
import { ParentDashboard } from "../src/components/eduboost/ParentDashboard";
import InteractiveLesson from "../src/components/eduboost/InteractiveLesson";
import { BadgePopup, PlaceholderPanel, Sidebar } from "../src/components/eduboost/ShellComponents";
import * as context from "../src/context/LearnerContext";
import * as services from "../src/lib/api/services";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Bar: () => <div>bar</div>,
  XAxis: () => <div>x-axis</div>,
  YAxis: () => <div>y-axis</div>,
  Tooltip: () => <div>tooltip</div>,
}));

describe("Entry and portal components", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    vi.spyOn(context, "useLearner").mockReturnValue({
      learner: { learner_id: "learner-1", id: "learner-1", nickname: "Avi", grade: 4, avatar: 0 },
      setLearner: vi.fn(),
      masteryData: {},
      setMasteryData: vi.fn(),
      gamification: { total_xp: 140, level: 2, streak_days: 3, earned_badges: [] },
      setGamification: vi.fn(),
      refreshState: vi.fn(),
      badge: null,
      setBadge: vi.fn(),
      loading: false,
    });
  });

  it("renders landing and onboarding flows", async () => {
    const onStart = vi.fn();
    render(<Landing onStart={onStart} onParent={vi.fn()} />);
    fireEvent.click(screen.getByText(/Start Learning!/i));
    expect(onStart).toHaveBeenCalled();

    const onComplete = vi.fn();
    render(<Onboarding onComplete={onComplete} />);
    fireEvent.click(screen.getByText("Grade 1"));
    fireEvent.click(screen.getByText(/Next/i));
    fireEvent.click(screen.getAllByRole("button").find((button) => button.textContent === "🦁")!);
    fireEvent.click(screen.getByText(/Next/i));
    fireEvent.change(screen.getByPlaceholderText(/StarLearner/i), { target: { value: "Avi" } });
    fireEvent.click(screen.getByText(/Next/i));
    fireEvent.click(screen.getByText(/Let's Go!/i));
    await waitFor(() => expect(onComplete).toHaveBeenCalled());
  });

  it("renders parent dashboard, lesson, and sidebar widgets", async () => {
    window.localStorage.setItem("guardian_id", "guardian-1");
    vi.spyOn(services.ParentService, "getTrustDashboard").mockResolvedValue({
      guardian_id: "guardian-1",
      subscription_tier: "premium",
      generated_at: "now",
      learners: [
        {
          learner_id: "learner-1",
          display_name: "Avi",
          grade_level: 4,
          irt_theta: 0.4,
          top_knowledge_gaps: ["Fractions"],
          ai_progress_summary: "Great momentum this week.",
          lesson_completion_rate_7d: 80,
          streak_days: 3,
          export_url: "/api/v2/popia/data-export/learner-1",
        },
      ],
    });
    vi.spyOn(services.ParentService, "getExportBundle").mockResolvedValue({
      guardian_id: "guardian-1",
      subscription_tier: "premium",
      exports: [{ learner_id: "learner-1", display_name: "Avi", export_url: "/api/v2/popia/data-export/learner-1" }],
    });

    render(<ParentDashboard onBack={vi.fn()} />);
    await waitFor(() => screen.getByText(/Parent Trust Dashboard/i));
    await waitFor(() => screen.getByText("Great momentum this week."));

    render(
      <InteractiveLesson
        lesson={{ id: "lesson-1", title: "Fractions", content: "Half a pizza is 1/2." }}
        subject="MATH"
        topic="Fractions"
        onBack={vi.fn()}
        onComplete={vi.fn()}
        loading={false}
      />
    );
    expect(screen.getAllByText("Fractions").length).toBeGreaterThan(0);

    render(
      <>
        <Sidebar learner={{ learner_id: "learner-1", id: "learner-1", nickname: "Avi", grade: 4, avatar: 0 }} activeTab="dashboard" onTab={vi.fn()} onLogout={vi.fn()} />
        <BadgePopup badge="You did it!" onDismiss={vi.fn()} />
        <PlaceholderPanel title="Placeholder" description="Testing area">Hello</PlaceholderPanel>
        <ParentGateway onBack={vi.fn()} />
      </>
    );

    expect(screen.getByText("EduBoost SA")).toBeInTheDocument();
    expect(screen.getByText("You did it!")).toBeInTheDocument();
    expect(screen.getByText("Placeholder")).toBeInTheDocument();
  });

  it("renders empty and error parent dashboard states", async () => {
    window.localStorage.setItem("guardian_id", "guardian-1");
    vi.spyOn(services.ParentService, "getTrustDashboard").mockRejectedValueOnce(new Error("boom"));
    vi.spyOn(services.ParentService, "getExportBundle").mockResolvedValue({
      guardian_id: "guardian-1",
      subscription_tier: "free",
      exports: [],
    });

    render(<ParentDashboard onBack={vi.fn()} />);
    await waitFor(() => screen.getByText(/Failed to load the parent dashboard./i));
  });
});
