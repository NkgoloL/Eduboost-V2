import type { ParentReviewRecord, ParentReviewDTO } from './types'

export function toGuardianDTO(record: ParentReviewRecord): ParentReviewDTO {
  return {
    learnerId: record.learnerId,
    lessonId: record.lessonId,
    eventType: record.eventType,
    timestamp: record.timestamp,
    safetyOutcome: record.safetyOutcome,
    refusalCategory: record.refusalCategory,
    rateLimitOutcome: record.rateLimitOutcome,
    redactedSummary: record.redactedSummary,
  }
}
