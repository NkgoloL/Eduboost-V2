import type { ConsentState } from './types'

const KEY_PREFIX = 'eduboost_voice_consent_'

export function getGuardianConsent(learnerId?: string): ConsentState {
  try {
    if (!learnerId) return { consented: false }
    const key = KEY_PREFIX + learnerId
    const raw = typeof window !== 'undefined' ? window.localStorage.getItem(key) : null
    return { learnerId, consented: raw === 'true' }
  } catch (_) {
    return { learnerId, consented: false }
  }
}

export function setGuardianConsent(learnerId: string, value: boolean) {
  try {
    const key = KEY_PREFIX + learnerId
    if (typeof window !== 'undefined') window.localStorage.setItem(key, value ? 'true' : 'false')
    return true
  } catch (_) {
    return false
  }
}
