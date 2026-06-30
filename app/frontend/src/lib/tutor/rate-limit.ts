export const RATE_LIMIT_MESSAGE = "Let's keep tutor questions focused and lesson-specific. Please wait a moment before asking again."

// In-memory counters keyed by identity (IP or userId). This is intentionally
// simple and used only for tests and the initial safety shell.
const counters: Record<string, number> = {}
const LIMIT = 6

export function checkRateLimit(identity?: string): { ok: boolean; message?: string } {
  const id = (identity || 'anon') as string
  counters[id] = (counters[id] || 0) + 1
  if ((counters[id] || 0) > LIMIT) return { ok: false, message: RATE_LIMIT_MESSAGE }
  return { ok: true }
}

export function clearRateLimitStore() {
  for (const k of Object.keys(counters)) delete counters[k]
}
