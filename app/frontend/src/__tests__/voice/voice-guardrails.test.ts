import { expect, test } from 'vitest'
import { canUseVoice } from '@/lib/voice/guardrails'

test('guard disallows when unsupported', () => {
  const out = canUseVoice({ supported: false, recognitionApi: null }, true, true)
  expect(out.allowed).toBe(false)
  expect(out.reasons).toContain('unsupported_browser')
})

test('guard disallows when consent missing', () => {
  const out = canUseVoice({ supported: true, recognitionApi: 'standard' }, false, true)
  expect(out.allowed).toBe(false)
  expect(out.reasons).toContain('guardian_consent_required')
})
