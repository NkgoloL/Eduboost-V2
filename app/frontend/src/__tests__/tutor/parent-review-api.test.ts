import { expect, test } from 'vitest'
import { POST, GET } from '@/app/api/tutor/review/route'

test('POST /api/tutor/review saves redacted review and returns DTO', async () => {
  const payload = { learnerId: 'p1', lessonId: 'l1', eventType: 'question', prompt: 'What is 2+2?', response: '4', summary: 'asked math', safetyOutcome: 'ok' }
  const req = new Request('http://localhost/api/tutor/review', { method: 'POST', body: JSON.stringify(payload) })
  const res = await POST(req as unknown as Request)
  const json = await res.json()
  expect(json.ok).toBe(true)
  expect(json.review).toBeDefined()
  expect(json.review.redactedSummary).toBeDefined()
  // should not include raw prompt/response
  expect(json.review.prompt).toBeUndefined()
  expect(json.review.response).toBeUndefined()
})

test('GET /api/tutor/review requires guardian auth and learnerId', async () => {
  const badReq = new Request('http://localhost/api/tutor/review')
  const badRes = await GET(badReq as unknown as Request)
  const badJson = await badRes.json()
  expect(badJson.error).toBeDefined()
})
