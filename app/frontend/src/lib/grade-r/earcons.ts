import { EarconName } from './types'

// A minimal earcon engine payload map. We rely on WebAudio where available and
// otherwise degrade to no-op; we do NOT request microphone permission.

export const EARCON_NAMES: EarconName[] = ['success', 'retry', 'start', 'complete', 'attention']

export function playEarcon(name: EarconName) {
  try {
    const w = window as unknown as { AudioContext?: typeof AudioContext; webkitAudioContext?: typeof AudioContext }
    const AudioCtxCtor = w.AudioContext ?? w.webkitAudioContext
    if (!AudioCtxCtor) return
    const ctx = new AudioCtxCtor()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.type = 'sine'
    // simple mapping for short tones
    const freqMap: Record<EarconName, number> = {
      success: 880,
      retry: 440,
      start: 660,
      complete: 990,
      attention: 220,
    }
    osc.frequency.value = freqMap[name]
    gain.gain.value = 0.001
    osc.connect(gain)
    gain.connect(ctx.destination)
    const now = ctx.currentTime
    gain.gain.setValueAtTime(0.001, now)
    gain.gain.exponentialRampToValueAtTime(0.1, now + 0.01)
    osc.start(now)
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12)
    osc.stop(now + 0.13)
    // close context after a short delay
    setTimeout(() => {
      try { ctx.close() } catch (e) { /* ignore */ }
    }, 200)
  } catch (e) {
    // degrade silently
  }
}
