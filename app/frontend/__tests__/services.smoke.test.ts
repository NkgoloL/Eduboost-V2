import { AuthService, LearnerService } from '../src/lib/api/services'
import { vi } from 'vitest'

// Basic smoke tests that call a couple of service wrappers with mocked fetch

test('Auth registerGuardian stores token', async () => {
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ access_token: 't' }), { status: 200 }))
  const res = await AuthService.registerGuardian({ email: 'a@b' } as any)
  expect(res.access_token).toBe('t')
})

test('Learner getProfile handles fetch', async () => {
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ id: 'L1', learner_id: 'L1' }), { status: 200 }))
  const profile = await LearnerService.getProfile('L1')
  expect(profile.id).toBe('L1')
})
