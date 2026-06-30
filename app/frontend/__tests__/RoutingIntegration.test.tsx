import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach, afterAll } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LearnerProvider, useLearner } from "../src/context/LearnerContext";
import { DashboardClient } from "../src/components/learner/DashboardClient";
import { LessonEntryClient } from "../src/components/learner/LessonEntryClient";
import { DiagnosticEntryClient } from "../src/components/learner/DiagnosticEntryClient";
import { LearnerService } from "../src/lib/api/services";
import type { LessonCompletionResponse } from "../src/lib/learner/lesson-completion-boundary";
import type { SubjectCode } from "../src/lib/api/types";

interface DashboardPanelProps {
  onStartLesson?: () => void;
  onStartDiag?: () => void;
}

interface LessonPanelProps {
  onComplete?: () => void;
  onBack?: () => void;
  completionState?: { status?: string; message?: string };
  isCompleting?: boolean;
}

interface DiagnosticPanelProps {
  onComplete?: (subject: SubjectCode, mastery: number) => void;
  onBack?: () => void;
}

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  usePathname: () => "/dashboard",
  useSearchParams: () => new URLSearchParams("subject=MATH&topic=Fractions"),
}));

const serviceMocks = vi.hoisted(() => ({
  getMastery: vi.fn(),
  getGamificationProfile: vi.fn(),
  generateLesson: vi.fn(),
}));

const completionBoundaryMocks = vi.hoisted(() => ({
  completeLessonTransaction: vi.fn<[], Promise<LessonCompletionResponse>>(),
}));

const offlineSyncMocks = vi.hoisted(() => ({
  cacheLessonSnapshot: vi.fn(),
  getCachedLessonSnapshot: vi.fn().mockReturnValue(null),
  queueLessonSync: vi.fn(),
}));

vi.mock("../src/lib/api/services", () => ({
  LearnerService: {
    getMastery: serviceMocks.getMastery,
    getGamificationProfile: serviceMocks.getGamificationProfile,
    generateLesson: serviceMocks.generateLesson,
  },
}));

vi.mock("@/lib/learner/lesson-completion-boundary", () => ({
  completeLessonTransaction: completionBoundaryMocks.completeLessonTransaction,
}));

vi.mock("@/lib/api/offlineSync", () => offlineSyncMocks);

// Mock the components used in pages to avoid massive dependency chain
vi.mock("../src/components/eduboost/FeaturePanels", () => {
  const DashboardPanel = ({ onStartLesson, onStartDiag }: DashboardPanelProps) => (
    <div>
      <button onClick={onStartLesson}>Start lesson</button>
      <button onClick={onStartDiag}>Open diagnostic</button>
    </div>
  );
  const LessonPanel = ({ onComplete, onBack }: LessonPanelProps) => (
    <div>
      <button onClick={onComplete}>Complete Lesson</button>
      <button onClick={onBack}>Back</button>
    </div>
  );
  return { __esModule: true, DashboardPanel, LessonPanel, default: { DashboardPanel, LessonPanel } };
});

vi.mock("../src/components/eduboost/InteractiveDiagnostic", () => {
  const InteractiveDiagnostic = ({ onComplete, onBack }: DiagnosticPanelProps) => (
    <div>
      <button onClick={() => onComplete?.("MATH", 80)}>Complete Diagnostic</button>
      <button onClick={onBack}>Back</button>
    </div>
  );
  return { __esModule: true, InteractiveDiagnostic, default: { InteractiveDiagnostic } };
});

vi.mock("../src/components/eduboost/InteractiveLesson", () => {
  const InteractiveLesson = ({ onComplete, onBack, completionState, isCompleting }: LessonPanelProps) => (
    <div>
      {completionState?.message ? <p>{completionState.message}</p> : null}
      <button disabled={isCompleting} onClick={onComplete}>
        Complete Lesson
      </button>
      <button onClick={onBack}>Back</button>
    </div>
  );
  return { __esModule: true, default: InteractiveLesson };
});

const originalFetch = global.fetch;

const mockLearner = {
  learner_id: "learner-1",
  id: "learner-1",
  nickname: "Test Learner",
  display_name: "Test Learner",
  grade: 3,
  avatar: 0,
};

const dashboardShell = {
  initialLearner: mockLearner,
  initialMastery: { MATH: 70 },
  initialGamification: {
    learner_id: mockLearner.learner_id,
    total_xp: 120,
    level: 3,
    streak_days: 5,
    earned_badges: [],
  },
};

const lessonShell = {
  initialLearner: mockLearner,
  recommendedSubject: "MATH" as SubjectCode,
  recommendedTopic: "Fractions",
  initialLesson: null,
  completionContract: {
    xpAward: 35,
    auditActorId: "actor",
    auditStreamId: "stream",
    completionWindowMinutes: 10,
    offlineQueueEnabled: true,
    source: "fixture",
  },
};

const diagnosticShell = {
  initialLearner: mockLearner,
};

function LearnerInitializer({ children }: { children: React.ReactNode }) {
  const { setLearner } = useLearner();
  React.useEffect(() => {
    setLearner(mockLearner);
  }, [setLearner]);
  return <>{children}</>;
}

function LearnerWrapper({ children }: { children: React.ReactNode }) {
  return (
    <LearnerProvider>
      <LearnerInitializer>{children}</LearnerInitializer>
    </LearnerProvider>
  );
}

describe("Routing Integration", () => {
  const originalNavigatorOnLine = Object.getOwnPropertyDescriptor(window.navigator, "onLine");

  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(window.navigator, "onLine", { value: true, configurable: true });
    global.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
      if (url.includes("/api/auth/session")) {
        return new Response(JSON.stringify({ authenticated: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response(JSON.stringify({}), { status: 200, headers: { "Content-Type": "application/json" } });
    }) as typeof global.fetch;
    serviceMocks.getMastery.mockResolvedValue({
      learner_id: "learner-1",
      mastery: [{ subject_code: "MATH", mastery_score: 0.75 }],
    });
    serviceMocks.getGamificationProfile.mockResolvedValue({
      learner_id: "learner-1",
      total_xp: 80,
      level: 2,
      streak_days: 4,
      earned_badges: [],
    });
    serviceMocks.generateLesson.mockResolvedValue({
      id: "lesson-1",
      title: "Fractions",
      content: "A quick fractions lesson.",
      summary: "Fractions made friendly.",
    });
    completionBoundaryMocks.completeLessonTransaction.mockResolvedValue({
      lessonId: "lesson-1",
      learnerId: "learner-1",
      xpAward: 35,
      auditEventId: "audit-123",
      completedAt: new Date().toISOString(),
      completionStatus: "completed",
      xpStatus: "awarded",
      source: "fixture",
    });
    offlineSyncMocks.queueLessonSync.mockReset();
  });

  it("Dashboard routes to /lesson and /diagnostic (NOT /learner/*)", async () => {
    render(
      <LearnerWrapper>
        <DashboardClient {...dashboardShell} />
      </LearnerWrapper>
    );

    fireEvent.click(await screen.findByText("Start New Lesson"));
    expect(mockPush).toHaveBeenCalledWith("/lesson");

    fireEvent.click(screen.getByText("Take Assessment"));
    expect(mockPush).toHaveBeenCalledWith("/diagnostic");
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("Lesson page completion routes back to /dashboard", async () => {
    render(
      <LearnerWrapper>
        <LessonEntryClient {...lessonShell} />
      </LearnerWrapper>
    );

    fireEvent.click(await screen.findByText("Mathematics"));
    fireEvent.click(await screen.findByText("Fractions"));
    fireEvent.click(screen.getByText("Start Adventure"));

    fireEvent.click(await screen.findByText(/Complete Lesson/i));
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith("/dashboard"));
    expect(completionBoundaryMocks.completeLessonTransaction).toHaveBeenCalledWith(
      expect.objectContaining({ lessonId: "lesson-1", learnerId: "learner-1", xpAward: 35 })
    );
    expect(mockPush).toHaveBeenCalledWith("/dashboard");
  });

  it("surfaces completion error states when the boundary fails", async () => {
    completionBoundaryMocks.completeLessonTransaction.mockRejectedValueOnce(new Error("boom"));

    render(
      <LearnerWrapper>
        <LessonEntryClient {...lessonShell} />
      </LearnerWrapper>
    );

    fireEvent.click(await screen.findByText("Mathematics"));
    fireEvent.click(await screen.findByText("Fractions"));
    fireEvent.click(screen.getByText("Start Adventure"));

    fireEvent.click(await screen.findByText(/Complete Lesson/i));
    await waitFor(() => expect(screen.getByText(/could not sync your XP yet/i)).toBeInTheDocument());
  });

  it("queues lesson completion offline when navigator is offline", async () => {
    Object.defineProperty(window.navigator, "onLine", { value: false, configurable: true });
    render(
      <LearnerWrapper>
        <LessonEntryClient {...lessonShell} />
      </LearnerWrapper>
    );

    fireEvent.click(await screen.findByText("Mathematics"));
    fireEvent.click(await screen.findByText("Fractions"));
    fireEvent.click(screen.getByText("Start Adventure"));

    fireEvent.click(await screen.findByText(/Complete Lesson/i));

    await waitFor(() => expect(offlineSyncMocks.queueLessonSync).toHaveBeenCalled());
    expect(mockPush).toHaveBeenCalledWith("/dashboard");
  });

  it("Diagnostic page routes to /plan and /dashboard", () => {
    render(
      <LearnerWrapper>
        <DiagnosticEntryClient {...diagnosticShell} />
      </LearnerWrapper>
    );

    fireEvent.click(screen.getByText("Back"));
    expect(mockPush).toHaveBeenCalledWith("/dashboard");

    fireEvent.click(screen.getByText("Complete Diagnostic"));
    expect(mockPush).toHaveBeenCalledWith("/plan");
  });

  afterAll(() => {
    if (originalNavigatorOnLine) {
      Object.defineProperty(window.navigator, "onLine", originalNavigatorOnLine);
    }
  });
});
