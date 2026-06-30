export type PseudonymousLearnerId = string

export type ParentReviewRecord = {
  id?: string
  learnerId: PseudonymousLearnerId
  lessonId: string
  eventType: string
  timestamp: string
  safetyOutcome: string
  refusalCategory?: string
  rateLimitOutcome?: string
  // short redacted summary suitable for guardian view
  redactedSummary: string
}

export type ParentReviewDTO = {
  learnerId: PseudonymousLearnerId
  lessonId: string
  eventType: string
  timestamp: string
  safetyOutcome: string
  refusalCategory?: string
  rateLimitOutcome?: string
  redactedSummary: string
}

export type RetentionPolicy = {
  retentionDays: number
}
