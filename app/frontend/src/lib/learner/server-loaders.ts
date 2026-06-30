"use server";

import "server-only";

import type { ActiveLearner, GamificationProfile, LessonPayload, SubjectCode } from "@/lib/api/types";

export interface LessonCompletionContract {
  xpAward: number;
  auditActorId: string;
  auditStreamId: string;
  completionWindowMinutes: number;
  offlineQueueEnabled: boolean;
  source: ShellDataSource;
}

export type ShellDataSource = "api" | "fixture";

export interface DashboardShellData {
  initialLearner: ActiveLearner | null;
  initialMastery: Record<string, number>;
  initialGamification: GamificationProfile | null;
  fetchedAt: string;
  source: ShellDataSource;
}

export interface DiagnosticShellData {
  initialLearner: ActiveLearner | null;
  availableSubjects: SubjectCode[];
  fetchedAt: string;
  source: ShellDataSource;
}

export interface LessonShellData {
  initialLearner: ActiveLearner | null;
  recommendedSubject: SubjectCode;
  recommendedTopic: string;
  initialLesson: LessonPayload | null;
  completionContract: LessonCompletionContract;
  fetchedAt: string;
  source: ShellDataSource;
}

const LEARNER_FIXTURE: ActiveLearner = {
  learner_id: "fixture-learner-001",
  id: "fixture-learner-001",
  nickname: "Naledi",
  display_name: "Naledi M",
  grade: 5,
  language: "en",
  avatar: 2,
  streak_days: 4,
  archetype: "trailblazer",
};

const LESSON_COMPLETION_CONTRACT_FIXTURE: LessonCompletionContract = {
  xpAward: 35,
  auditActorId: "fixture-audit-actor",
  auditStreamId: "audit-fixture-stream",
  completionWindowMinutes: 10,
  offlineQueueEnabled: true,
  source: "fixture",
};

const GAMIFICATION_FIXTURE: GamificationProfile = {
  learner_id: LEARNER_FIXTURE.learner_id,
  level: 6,
  total_xp: 1420,
  streak_days: 7,
  badges: [
    { badge_key: "streak-3", name: "3 Day Streak", icon: "🔥", earned_at: "2026-05-20" },
    { badge_key: "lesson-pro", name: "Lesson Pro", icon: "⭐", earned_at: "2026-05-24" },
  ],
};

const MASTERY_FIXTURE: Record<string, number> = {
  MATH: 74,
  ENG: 63,
  LIFE: 58,
  NS: 69,
  SS: 61,
};

const LESSON_FIXTURE: LessonPayload = {
  id: "lesson-fixture-001",
  title: "Explore Fraction Stories at the Tuck Shop",
  summary: "Use everyday South African moments to understand fractions and sharing.",
  subject: "MATH",
  topic: "Fractions",
  content: [
    {
      heading: "Warm-up",
      body: "Remember a time you shared vetkoek with a friend. How many pieces did you make?",
    },
    {
      heading: "Try It Out",
      body: "Naledi and Thabo split 3 chocolate bars equally. Build your own drawing showing the pieces.",
    },
    "Use the bar model to show what fraction of the treats belongs to each person.",
  ],
};

const AVAILABLE_SUBJECTS_FIXTURE: SubjectCode[] = ["MATH", "ENG", "NS", "SS", "LIFE"];

export async function getLearnerDashboardShellData(): Promise<DashboardShellData> {
  return {
    initialLearner: LEARNER_FIXTURE,
    initialMastery: { ...MASTERY_FIXTURE },
    initialGamification: GAMIFICATION_FIXTURE,
    fetchedAt: new Date().toISOString(),
    source: "fixture",
  };
}

export async function getDiagnosticEntryShellData(): Promise<DiagnosticShellData> {
  return {
    initialLearner: LEARNER_FIXTURE,
    availableSubjects: [...AVAILABLE_SUBJECTS_FIXTURE],
    fetchedAt: new Date().toISOString(),
    source: "fixture",
  };
}

export async function getLessonShellData(): Promise<LessonShellData> {
  return {
    initialLearner: LEARNER_FIXTURE,
    recommendedSubject: "MATH",
    recommendedTopic: "Fractions",
    initialLesson: LESSON_FIXTURE,
    completionContract: LESSON_COMPLETION_CONTRACT_FIXTURE,
    fetchedAt: new Date().toISOString(),
    source: "fixture",
  };
}
