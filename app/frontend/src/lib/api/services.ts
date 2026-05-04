import { fetchApi, waitForJobResult } from "./client";
import type {
  ActiveLearner,
  AuthTokenResponse,
  DiagnosticAnswerInput,
  DiagnosticItem,
  DiagnosticResult,
  GamificationProfile,
  JobAcceptedResponse,
  LessonJobResult,
  LessonPayload,
  MasteryResponse,
  ParentExportBundle,
  ParentTrustDashboardResponse,
  StudyPlanResponse,
} from "./types";

const normalizeGamification = (profile: GamificationProfile): GamificationProfile => ({
  ...profile,
  total_xp: profile.total_xp ?? 0,
  level: profile.level ?? 1,
  streak_days: profile.streak_days ?? 0,
  earned_badges: profile.earned_badges ?? profile.badges ?? [],
});

export const AuthService = {
  registerLearner: (data: Record<string, unknown>) =>
    fetchApi<ActiveLearner>("/learners/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  registerGuardian: (data: Record<string, unknown>) =>
    fetchApi<AuthTokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  loginGuardian: (data: Record<string, unknown>) =>
    fetchApi<AuthTokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export const LearnerService = {
  registerLearner: (data: Record<string, unknown>) =>
    fetchApi<ActiveLearner>("/learners/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getProfile: (learnerId: string) => fetchApi<ActiveLearner>(`/learners/${learnerId}`),

  getGamificationProfile: async (learnerId: string) =>
    normalizeGamification(await fetchApi<GamificationProfile>(`/gamification/profile/${learnerId}`)),

  getStudyPlan: async (learnerId: string) => {
    const accepted = await fetchApi<JobAcceptedResponse>(`/study-plans/generate/${learnerId}`, {
      method: "POST",
      body: JSON.stringify({ gap_ratio: 0.4 }),
    });
    return waitForJobResult<StudyPlanResponse>(accepted);
  },

  getMastery: (learnerId: string) => fetchApi<MasteryResponse>(`/learners/${learnerId}/mastery`),

  generateLesson: async (data: Record<string, unknown>) => {
    const accepted = await fetchApi<JobAcceptedResponse>("/lessons/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
    return waitForJobResult<LessonJobResult>(accepted);
  },

  markLessonComplete: (lessonId: string) =>
    fetchApi<{ detail: string }>(`/lessons/${lessonId}/complete`, {
      method: "POST",
    }),

  syncLessonResponses: (responses: Array<Record<string, unknown>>) =>
    fetchApi<{ processed: number; queued: number }>("/lessons/sync", {
      method: "POST",
      body: JSON.stringify({ responses }),
    }),

  awardXP: (data: Record<string, unknown>) =>
    fetchApi<{ awarded: boolean; xp_amount: number }>("/gamification/award-xp", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export const ParentService = {
  getTrustDashboard: (guardianId: string) =>
    fetchApi<ParentTrustDashboardResponse>(`/parents/${guardianId}/dashboard`),

  getExportBundle: (guardianId: string) =>
    fetchApi<ParentExportBundle>(`/parents/${guardianId}/export`),
};

export const DiagnosticService = {
  getItems: async (learnerId: string): Promise<DiagnosticItem[]> => {
    const items = await fetchApi<
      Array<{ id: string; question: string; options: string[]; subject: string; topic: string }>
    >(`/diagnostics/items/${learnerId}`);
    return items.map((item) => ({
      item_id: item.id,
      question_text: item.question,
      options: item.options,
      subject: item.subject,
      topic: item.topic,
      difficulty_label: "Adaptive",
    }));
  },

  submit: (learnerId: string, answers: DiagnosticAnswerInput[]) =>
    fetchApi<DiagnosticResult>("/diagnostics/submit", {
      method: "POST",
      body: JSON.stringify({ learner_id: learnerId, answers }),
    }),

  runLegacy: async (data: { learner_id: string; answers: DiagnosticAnswerInput[] }) =>
    fetchApi<DiagnosticResult>("/diagnostics/submit", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export type { LessonPayload };
