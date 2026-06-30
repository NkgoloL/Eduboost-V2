import { expect, test } from 'vitest'
import { redactObjectForStorage } from '@/lib/tutor/parent-review/redaction'
import { InMemoryParentReviewRepository } from '@/lib/tutor/parent-review/repository'
import type { ParentReviewRecord } from '@/lib/tutor/parent-review/types'

test('repository abstraction does not expose raw prompt or raw response', async () => {
  const repo = new InMemoryParentReviewRepository()
  const payload = { learnerId: 'p1', lessonId: 'l1', eventType: 'question', prompt: 'what is 2+2?', response: '4', summary: 'asked math', safetyOutcome: 'ok' }
  const rec = redactObjectForStorage(payload as Record<string, unknown>)
  expect(rec).not.toBeNull()
  const saved = await repo.save(rec as unknown as ParentReviewRecord)
  // saved record should not contain raw prompt/response properties
  expect((saved as unknown as Record<string, unknown>)['prompt']).toBeUndefined()
  expect((saved as unknown as Record<string, unknown>)['response']).toBeUndefined()
})
