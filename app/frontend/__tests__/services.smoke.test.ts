import { AuthService, LearnerService, ConsentService, DataRightsService, DiagnosticService } from '../src/lib/api/services'
import { vi } from 'vitest'

const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
  vi.restoreAllMocks()
})

function setupLocalStorage(initial: Record<string, string> = {}) {
  const store = { ...initial }
  // @ts-ignore
  globalThis.localStorage = {
    getItem: (key: string) => (key in store ? store[key] : null),
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
  }
  return store
}

test('Auth registerGuardian stores token', async () => {
  setupLocalStorage()
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ access_token: 't' }), { status: 200 }))
  const res = await AuthService.registerGuardian({ email: 'a@b' } as any)
  expect(res.access_token).toBe('t')
  expect(globalThis.localStorage.getItem('guardian_token')).toBe('t')
})

test('Auth loginGuardian stores token', async () => {
  setupLocalStorage()
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ access_token: 'l' }), { status: 200 }))
  const res = await AuthService.loginGuardian({ email: 'a@b' } as any)
  expect(res.access_token).toBe('l')
  expect(globalThis.localStorage.getItem('guardian_token')).toBe('l')
})

test('Auth logout clears token even when fetch fails', async () => {
  const storage = setupLocalStorage({ guardian_token: 'existing' })
  globalThis.fetch = vi.fn(async () => { throw new Error('network') })
  await AuthService.logout()
  expect(storage.guardian_token).toBeUndefined()
})

test('Learner registerLearner normalizes learner fields', async () => {
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ id: 'L1', display_name: 'Kid' }), { status: 200 }))
  const learner = await LearnerService.registerLearner({ name: 'Kid' } as any)
  expect(learner.learner_id).toBe('L1')
  expect(learner.nickname).toBe('Kid')
})

test('Learner markLessonComplete and syncLessonResponses call fetch', async () => {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.endsWith('/complete')) {
      return new Response(JSON.stringify({ detail: 'ok' }), { status: 200 })
    }
    if (url.endsWith('/sync')) {
      return new Response(JSON.stringify({ processed: 1, queued: 0 }), { status: 200 })
    }
    return new Response(JSON.stringify({}), { status: 200 })
  })
  const complete = await LearnerService.markLessonComplete('lesson-1')
  expect(complete.detail).toBe('ok')
  const sync = await LearnerService.syncLessonResponses([{ learner_id: 'L1', answers: [] }] as any)
  expect((sync as any).processed).toBe(1)
})

test('Learner awardXP forwards request', async () => {
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ xp_awarded: 10 }), { status: 200 }))
  const result = await LearnerService.awardXP({ learner_id: 'L1', amount: 10 })
  expect((result as any).xp_awarded).toBe(10)
})

test('Consent revoke and DataRights cancelErasure/deletionStatus work', async () => {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
    if (url.includes('/consent/revoke')) {
      return new Response(JSON.stringify({ revoked: 1, message: 'ok' }), { status: 200 })
    }
    if (url.includes('/popia/deletion-cancel')) {
      return new Response(JSON.stringify({ status: 'ok' }), { status: 200 })
    }
    if (url.includes('/popia/deletion-status')) {
      return new Response(JSON.stringify({ status: 'pending' }), { status: 200 })
    }
    return new Response(JSON.stringify({}), { status: 200 })
  })
  const revokeResult = await ConsentService.revoke('L1')
  expect(revokeResult.revoked).toBe(1)

  const cancel = await DataRightsService.cancelErasure('L1')
  expect((cancel as any).status).toBe('ok')

  const deletionStatus = await DataRightsService.deletionStatus('L1')
  expect((deletionStatus as any).status).toBe('pending')
})

test('DiagnosticService runLegacy submits legacy diagnostic payload', async () => {
  globalThis.fetch = vi.fn(async () => new Response(JSON.stringify({ theta_after: 1, ranked_gaps: [] }), { status: 200 }))
  const result = await DiagnosticService.runLegacy({ learner_id: 'L1', answers: [] })
  expect((result as any).theta_after).toBe(1)
})
