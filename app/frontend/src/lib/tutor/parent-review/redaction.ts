import type { ParentReviewRecord } from './types'

const EMAIL_REGEX = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi
const PHONE_REGEX = /\+?\d[\d\s-]{6,}\d/g
// Conservative single-token capitalized name matcher (may over-redact common
// capitalized words; acceptable within this safety-first boundary)
const NAME_REGEX = /\b[A-Z][a-z]{1,20}\b/g

export function redactString(input: string): string {
  return input
    .replace(EMAIL_REGEX, '[REDACTED]')
    .replace(PHONE_REGEX, '[REDACTED]')
    .replace(NAME_REGEX, '[REDACTED]')
}

export function redactObjectForStorage(obj: Record<string, unknown>): ParentReviewRecord | null {
  // Expect certain fields to be present; return null if minimal fields missing
  const learnerId = typeof obj['learnerId'] === 'string' ? obj['learnerId'] : typeof obj['pseudonymousLearnerId'] === 'string' ? obj['pseudonymousLearnerId'] as string : undefined
  const lessonId = typeof obj['lessonId'] === 'string' ? obj['lessonId'] : typeof obj['lesson_id'] === 'string' ? obj['lesson_id'] as string : undefined
  const eventType = typeof obj['eventType'] === 'string' ? obj['eventType'] : undefined
  const timestamp = typeof obj['timestamp'] === 'string' ? obj['timestamp'] : new Date().toISOString()
  const safetyOutcome = typeof obj['safetyOutcome'] === 'string' ? obj['safetyOutcome'] : 'unknown'
  const refusalCategory = typeof obj['refusalCategory'] === 'string' ? obj['refusalCategory'] : undefined
  const rateLimitOutcome = typeof obj['rateLimitOutcome'] === 'string' ? obj['rateLimitOutcome'] : undefined

  if (!learnerId || !lessonId || !eventType) return null

  // Build a short redacted summary from any provided summary or prompt/response snippets
  const rawSummary = typeof obj['summary'] === 'string' ? obj['summary'] : typeof obj['prompt'] === 'string' ? obj['prompt'] : ''
  const rawResponse = typeof obj['response'] === 'string' ? obj['response'] : ''
  const joined = `${rawSummary} ${rawResponse}`.trim()
  const redacted = redactString(joined).replace(/\b(childName|child_name|name)\b[:=]?\s*\w+/gi, '[REDACTED]')
  const short = redacted.length > 200 ? redacted.slice(0, 197) + '...' : redacted

  const record: ParentReviewRecord = {
    learnerId,
    lessonId,
    eventType,
    timestamp,
    safetyOutcome,
    refusalCategory,
    rateLimitOutcome,
    redactedSummary: short || '[REDACTED]'
  }

  return record
}
