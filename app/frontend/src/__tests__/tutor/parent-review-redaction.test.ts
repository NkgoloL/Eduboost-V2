import { expect, test } from 'vitest'
import { redactString, redactObjectForStorage } from '@/lib/tutor/parent-review/redaction'

test('redaction removes email-like strings', () => {
  const input = 'Contact me at parent@example.com for follow up.'
  const out = redactString(input)
  expect(out).not.toContain('parent@example.com')
  expect(out).toContain('[REDACTED]')
})

test('redaction removes phone-like strings', () => {
  const input = 'Call +1 555-123-4567 after class.'
  const out = redactString(input)
  expect(out).not.toContain('+1 555-123-4567')
  expect(out).toContain('[REDACTED]')
})

test('redaction removes child-name-like labeled fields in object', () => {
  const obj = { learnerId: 'p1', lessonId: 'l1', eventType: 'question', summary: 'childName: Alice asked about fractions' }
  const rec = redactObjectForStorage(obj as Record<string, unknown>)
  expect(rec).not.toBeNull()
  expect(rec?.redactedSummary).not.toContain('Alice')
  expect(rec?.redactedSummary).toContain('[REDACTED]')
})
