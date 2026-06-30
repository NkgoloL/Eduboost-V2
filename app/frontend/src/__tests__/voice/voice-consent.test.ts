import { expect, test, beforeEach } from 'vitest'
import { getGuardianConsent, setGuardianConsent } from '@/lib/voice/consent'

beforeEach(() => {
  if (typeof window !== 'undefined') window.localStorage.clear()
})

test('consent set/get roundtrip', () => {
  const id = 'learnerX'
  expect(getGuardianConsent(id).consented).toBe(false)
  setGuardianConsent(id, true)
  expect(getGuardianConsent(id).consented).toBe(true)
})
