import type { VoiceCapability } from './types'

export function canUseVoice(cap: VoiceCapability, consented: boolean, online = true) {
  const reasons: string[] = []
  if (!cap.supported) reasons.push('unsupported_browser')
  if (!online) reasons.push('offline')
  if (!consented) reasons.push('guardian_consent_required')
  return { allowed: cap.supported && consented && online, reasons }
}
