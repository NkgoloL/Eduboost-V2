import { expect, test } from 'vitest'
import { saveSanitizedReview, listReviewsForLearner } from '@/lib/tutor/parent-review/service'

test('service saves and lists redacted reviews without raw transcript', async () => {
  const payload = { learnerId: 'p42', lessonId: 'lX', eventType: 'question', prompt: 'Tell me about Alice', response: 'Alice likes math', summary: 'asked about Alice', safetyOutcome: 'ok' }
  const dto = await saveSanitizedReview(payload as Record<string, unknown>)
  expect(dto).toBeDefined()
  expect(dto.redactedSummary).not.toContain('Alice')
  const list = await listReviewsForLearner('p42')
  expect(Array.isArray(list)).toBe(true)
  expect(list.length).toBeGreaterThan(0)
  expect(list[0]!.redactedSummary).toBe(dto.redactedSummary)
})
