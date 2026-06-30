export type SubjectCode = "MATH" | "ENG" | "LIFE" | "NS" | "SS" | string;

export type ApiEnvelope<T> = {
  data?: T | null;
  error?: NormalizedApiError | null;
  meta?: Record<string, unknown>;
  request_id?: string;
};

export interface FieldError {
  field?: string;
  message: string;
  code?: string;
}

export interface NormalizedApiError {
  code?: string;
  message: string;
  field_errors?: FieldError[];
  remediation?: string;
  details?: Record<string, unknown>;
  request_id?: string;
  status?: number;
}

export interface ActiveLearner {
  learner_id: string;
  id?: string;
  pseudonym_id?: string;
  nickname?: string;
  display_name?: string;
  grade: number;
  language?: string;
  avatar?: number;
  archetype?: string | null;
  streak_days?: number;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type?: string;
  expires_in?: number;
}

export interface DevSessionResponse extends AuthTokenResponse {
  guardian_id: string;
  learner: ActiveLearner;
}

export interface AuthSessionMetadata {
  jti?: string;
  family?: string;
  user_id?: string;
  created_at?: string;
  expires_at?: string;
  last_seen_at?: string;
}

export interface AuthSessionsResponse {
  sessions: AuthSessionMetadata[];
}

export interface ApiErrorShape {
  detail?: string;
  message?: string;
  error?: NormalizedApiError;
  request_id?: string;
}

export interface LearnerCreateInput {
  display_name: string;
  grade: number;
  language?: string;
}

export interface ConsentGrantResponse {
  id: string;
  learner_id: string;
  granted_at: string;
  expires_at: string;
  message: string;
}

export interface ConsentStatusResponse {
  active: boolean;
  learner_id: string;
  granted_at?: string;
  expires_at?: string;
  days_remaining?: number;
}

export interface DataRightsStatus {
  request_type: string;
  status: string;
  learner_id: string;
  requested_at?: string;
  due_at?: string;
  audit_event?: string;
}

export interface DataExportBundle {
  filename: string;
  content_type: string;
  payload?: Record<string, unknown>;
  csv?: string;
  status: DataRightsStatus;
}

export interface GamificationBadge {
  badge_key?: string;
  name: string;
  icon?: string;
  date_earned?: string;
  earned_at?: string;
}

export interface GamificationProfile {
  learner_id?: string;
  level: number;
  total_xp: number;
  streak_days: number;
  badges?: GamificationBadge[];
  earned_badges?: GamificationBadge[];
  [key: string]: unknown;
}

export interface MasteryEntry {
  subject_code: string;
  mastery_score: number;
}

export interface MasteryResponse {
  learner_id?: string;
  mastery: MasteryEntry[];
}

export interface LessonSection {
  heading?: string;
  body?: string;
}

export interface OfflineLessonSyncEvent {
  lesson_id: string;
  event_type: "complete" | "feedback";
  completed_at?: string;
  score?: number;
}

export interface LessonPayload {
  id?: string;
  title: string;
  summary?: string;
  content?: string | Array<LessonSection | string>;
  subject?: SubjectCode;
  topic?: string;
  caps_reference?: string;
  alignment_confidence?: number;
  quality_score?: number | Record<string, unknown>;
  trust_label?: string | Record<string, unknown>;
  cache_hit?: boolean;
  caps_aligned?: boolean;
  served_from_cache?: boolean;
}

export interface LessonJobResult extends LessonPayload {
  created_at?: string;
  language?: string;
  archetype?: string | null;
}

export interface StudyPlanItem {
  code?: string;
  label: string;
  emoji?: string;
  type?: string;
}

export interface StudyPlanResponse {
  plan_id?: string;
  learner_id?: string;
  week_focus?: string;
  schedule?: Record<string, StudyPlanItem[]>;
  days?: Record<string, StudyPlanItem[]>;
  gap_ratio?: number;
}

export interface AwardXPResponse {
  awarded: boolean;
  xp_amount: number;
  lesson_completed?: boolean;
  profile?: GamificationProfile;
}

export interface DiagnosticItem {
  id?: string;
  item_id?: string;
  question?: string;
  question_text?: string;
  options: string[];
  subject?: string;
  topic?: string;
  skill?: string;
  caps_reference?: string;
  difficulty_label?: string;
}

export interface DiagnosticAnswerInput {
  item_id: string;
  selected_option: string;
}

export interface RankedGap {
  grade?: number;
  gap_grade?: number;
  subject: string;
  topic: string;
  severity?: number;
}

export interface DiagnosticResult {
  session_id?: string;
  theta_before?: number;
  theta_after?: number;
  gaps_identified?: string[];
  standard_error?: number | null;
  grade_equivalent?: number | null;
  ranked_gaps?: RankedGap[];
}

export interface ParentTrustDashboardLearner {
  learner_id: string;
  display_name: string;
  grade_level: number;
  archetype?: string | null;
  irt_theta: number;
  top_knowledge_gaps: string[];
  ai_progress_summary: string;
  lesson_completion_rate_7d: number;
  streak_days: number;
  export_url: string;
}

export interface ParentTrustDashboardResponse {
  guardian_id: string;
  subscription_tier: string;
  generated_at: string;
  learners: ParentTrustDashboardLearner[];
}

export interface ParentDashboardLearner {
  learner_id: string;
  display_name: string;
  grade_level: string;
  archetype?: string | null;
  irt_theta?: number;
  lessons_this_week?: number;
  active_knowledge_gaps?: number;
  last_lesson_at?: string | null;
}

export interface ParentDashboardResponse {
  guardian_id: string;
  subscription_tier: string;
  total_lessons_generated: number;
  learners: ParentDashboardLearner[];
}

export interface ParentExportEntry {
  learner_id: string;
  display_name: string;
  export_url: string;
}

export interface ParentExportBundle {
  guardian_id: string;
  subscription_tier: string;
  exports: ParentExportEntry[];
}

export interface JobAcceptedResponse {
  job_id: string;
  operation: string;
  status: string;
}

export interface JobStatusResponse<T = unknown> extends JobAcceptedResponse {
  payload: Record<string, unknown>;
  result: T | null;
  error: { type?: string; message?: string } | null;
  created_at: string;
  updated_at: string;
}
