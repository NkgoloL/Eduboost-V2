export type TutorRequest = {
  // Accept both camelCase and snake_case to support legacy tests and clients.
  lessonId?: string;
  lesson_id?: string;
  prompt?: string;
  question?: string;
  lessonContext?: string;
  lesson_context?: string;
  subjectCode?: string;
  subject_code?: string;
  userId?: string;
  user_id?: string;
};

export type TutorResponseType = 'answer' | 'refusal';

export type TutorResponse = {
  type: TutorResponseType;
  message: string;
  safe: boolean;
};

export interface TutorAuditEvent {
  lessonId: string;
  eventType: string;
  timestamp: string;
  safe: boolean;
  metadata?: Record<string, string>;
}
