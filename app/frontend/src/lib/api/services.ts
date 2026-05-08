import { fetchApi, storeAccessToken } from "./client";
import type {
  ActiveLearner,
  AuthSessionsResponse,
  AuthTokenResponse,
  AwardXPResponse,
  ConsentGrantResponse,
  ConsentStatusResponse,
  DataExportBundle,
  DataRightsStatus,
  DevSessionResponse,
  DiagnosticAnswerInput,
  DiagnosticItem,
  DiagnosticResult,
  GamificationProfile,
  JobAcceptedResponse,
  LearnerCreateInput,
  LessonJobResult,
  LessonPayload,
  OfflineLessonSyncEvent,
  MasteryResponse,
  ParentExportBundle,
  ParentTrustDashboardResponse,
  StudyPlanResponse,
} from "./types";
import { waitForJobResult } from "./client";

const normalizeLearner = (learner: ActiveLearner): ActiveLearner => ({
  ...learner,
  learner_id: learner.learner_id || learner.id || "",
  id: learner.id || learner.learner_id,
  nickname: learner.nickname || learner.display_name,
});

const normalizeGamification = (profile: GamificationProfile): GamificationProfile => ({
  ...profile,
  total_xp: profile.total_xp ?? 0,
  level: profile.level ?? 1,
  streak_days: profile.streak_days ?? 0,
  earned_badges: profile.earned_badges ?? profile.badges ?? [],
});

const normalizeStudyPlan = (plan: StudyPlanResponse): StudyPlanResponse => {
  const schedule = plan.days ?? plan.schedule ?? {};
  return {
    ...plan,
    schedule,
    days: schedule,
    week_focus: plan.week_focus ?? "Balanced revision and grade-level progress",
  };
};

const normalizeLesson = (lesson: LessonJobResult): LessonJobResult => ({
  ...lesson,
  title: lesson.title || "Generated Lesson",
  content: lesson.content || lesson.summary || "Your lesson is ready.",
});

export const AuthService = {
  registerLearner: (data: LearnerCreateInput) => LearnerService.registerLearner(data),

  registerGuardian: async (data: Record<string, unknown>) => {
    const response = await fetchApi<AuthTokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    storeAccessToken(response.access_token);
    return response;
  },

  loginGuardian: async (data: Record<string, unknown>) => {
    const response = await fetchApi<AuthTokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    storeAccessToken(response.access_token);
    return response;
  },

  logout: async () => {
    await fetchApi<null>("/auth/logout", { method: "POST" }).catch(() => null);
    storeAccessToken(null);
  },

  revokeAll: async () => fetchApi<null>("/auth/revoke-all", { method: "POST" }),

  sessions: () => fetchApi<AuthSessionsResponse>("/auth/sessions"),

  createDevSession: async () => {
    const response = await fetchApi<DevSessionResponse>("/auth/dev-session", { method: "POST" });
    storeAccessToken(response.access_token);
    return { ...response, learner: normalizeLearner(response.learner) };
  },
};

export const LearnerService = {
  registerLearner: async (data: LearnerCreateInput) =>
    normalizeLearner(
      await fetchApi<ActiveLearner>("/learners/", {
        method: "POST",
        body: JSON.stringify(data),
      })
    ),

  getProfile: async (learnerId: string) => normalizeLearner(await fetchApi<ActiveLearner>(`/learners/${learnerId}`)),

  getGamificationProfile: async (learnerId: string) =>
    normalizeGamification(await fetchApi<GamificationProfile>(`/gamification/profile/${learnerId}`)),

  getStudyPlan: async (learnerId: string) => {
    const accepted = await fetchApi<JobAcceptedResponse>(`/study-plans/generate/${learnerId}`, {
      method: "POST",
      body: JSON.stringify({ gap_ratio: 0.4 }),
    });
    return normalizeStudyPlan(await waitForJobResult<StudyPlanResponse>(accepted));
  },

  getMastery: (learnerId: string) => fetchApi<MasteryResponse>(`/learners/${learnerId}/mastery`),

  generateLesson: async (data: Record<string, unknown>) => {
    const accepted = await fetchApi<JobAcceptedResponse>("/lessons/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
    return normalizeLesson(await waitForJobResult<LessonJobResult>(accepted));
  },

  markLessonComplete: (lessonId: string) =>
    fetchApi<{ detail: string }>(`/lessons/${lessonId}/complete`, {
      method: "POST",
    }),

  syncLessonResponses: (responses: OfflineLessonSyncEvent[]) =>
    fetchApi<{ processed: number; queued: number }>("/lessons/sync", {
      method: "POST",
      body: JSON.stringify({ responses }),
    }),

  awardXP: (data: Record<string, unknown>) =>
    fetchApi<AwardXPResponse>("/gamification/award-xp", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export const ConsentService = {
  grant: (learnerId: string, consentVersion = "1.0") =>
    fetchApi<ConsentGrantResponse>("/consent/grant", {
      method: "POST",
      body: JSON.stringify({ learner_id: learnerId, consent_version: consentVersion }),
    }),

  revoke: (learnerId: string, reason = "guardian_request") =>
    fetchApi<{ revoked: number; message: string }>("/consent/revoke", {
      method: "POST",
      body: JSON.stringify({ learner_id: learnerId, reason }),
    }),

  status: (learnerId: string) => fetchApi<ConsentStatusResponse>(`/consent/status/${learnerId}`),
};

export const DataRightsService = {
  exportLearner: (learnerId: string, format: "json" | "csv" = "json") =>
    fetchApi<DataExportBundle>(`/popia/data-export/${learnerId}?export_format=${format}`),
  requestErasure: (learnerId: string, reason = "guardian_request") =>
    fetchApi<DataRightsStatus>(`/popia/deletion-request/${learnerId}`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  cancelErasure: (learnerId: string) => fetchApi<DataRightsStatus>(`/popia/deletion-cancel/${learnerId}`, { method: "POST" }),
  restrictProcessing: (learnerId: string, reason = "guardian_request") =>
    fetchApi<DataRightsStatus>(`/popia/restriction-request/${learnerId}`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  deletionStatus: (learnerId: string) => fetchApi<DataRightsStatus>(`/popia/deletion-status/${learnerId}`),
};

export const ParentService = {
  getTrustDashboard: (guardianId: string) => fetchApi<ParentTrustDashboardResponse>(`/parents/${guardianId}/dashboard`),

  getExportBundle: (guardianId: string) => fetchApi<ParentExportBundle>(`/parents/${guardianId}/export`),
};

export const DiagnosticService = {
  getItems: async (learnerId: string): Promise<DiagnosticItem[]> => {
    const items = await fetchApi<
      Array<{ id?: string; item_id?: string; question?: string; question_text?: string; options: string[]; subject?: string; topic?: string; skill?: string; caps_reference?: string }>
    >(`/diagnostics/items/${learnerId}`);
    return items.map((item) => ({
      item_id: item.item_id || item.id,
      id: item.id || item.item_id,
      question_text: item.question_text || item.question,
      question: item.question || item.question_text,
      options: item.options,
      subject: item.subject,
      topic: item.topic,
      skill: item.skill,
      caps_reference: item.caps_reference,
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
