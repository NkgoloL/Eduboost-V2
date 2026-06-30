import type { VoiceCapability } from './types'

export function detectVoiceSupport(): VoiceCapability {
  if (typeof window === 'undefined') return { supported: false, recognitionApi: null }
  const win = window as unknown as Record<string, unknown>
  if (typeof win['webkitSpeechRecognition'] !== 'undefined') return { supported: true, recognitionApi: 'webkit' }
  if (typeof win['SpeechRecognition'] !== 'undefined') return { supported: true, recognitionApi: 'standard' }
  return { supported: false, recognitionApi: null }
}
