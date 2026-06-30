import { expect, test, beforeEach } from 'vitest'
import { requireGuardianAuth } from '@/lib/tutor/parent-review/access'

beforeEach(() => {
  process.env.GUARDIAN_API_KEY = 'test-key'
})

test('requireGuardianAuth fails without proper Authorization header', () => {
  const req = new Request('http://localhost')
  const out = requireGuardianAuth(req as unknown as Request)
  expect(out.ok).toBe(false)
})

test('requireGuardianAuth succeeds with correct bearer token', () => {
  const req = new Request('http://localhost', { headers: { authorization: 'Bearer test-key' } })
  const out = requireGuardianAuth(req as unknown as Request)
  expect(out.ok).toBe(true)
})
