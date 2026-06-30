import { expect, test } from 'vitest'
import { detectVoiceSupport } from '@/lib/voice/capability'

test('detectVoiceSupport returns capability shape', () => {
  const cap = detectVoiceSupport()
  expect(typeof cap.supported).toBe('boolean')
  expect(cap.recognitionApi === null || cap.recognitionApi === 'webkit' || cap.recognitionApi === 'standard').toBe(true)
})
