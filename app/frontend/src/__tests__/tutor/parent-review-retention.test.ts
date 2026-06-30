import { expect, test } from 'vitest'
import { ParentReviewRetentionPolicy, isExpired, DEFAULT_RETENTION_DAYS } from '@/lib/tutor/parent-review/retention'

test('retention window is explicit and bounded', () => {
  expect(ParentReviewRetentionPolicy.retentionDays).toBe(DEFAULT_RETENTION_DAYS)
  expect(typeof ParentReviewRetentionPolicy.retentionDays).toBe('number')
  expect(ParentReviewRetentionPolicy.retentionDays).toBeGreaterThan(0)
})

test('isExpired returns true for old timestamps and false for recent ones', () => {
  const now = Date.now()
  const old = new Date(now - (DEFAULT_RETENTION_DAYS + 1) * 24 * 60 * 60 * 1000).toISOString()
  const recent = new Date(now - (DEFAULT_RETENTION_DAYS - 1) * 24 * 60 * 60 * 1000).toISOString()
  expect(isExpired(old, ParentReviewRetentionPolicy, now)).toBe(true)
  expect(isExpired(recent, ParentReviewRetentionPolicy, now)).toBe(false)
})
