import type { TutorRequest, TutorResponse } from './types'

export async function callProvider(req: TutorRequest): Promise<TutorResponse> {
  // Read env vars at call time so tests can set process.env before invocation.
  const PROVIDER_URL = process.env.TUTOR_PROVIDER_API_URL || process.env.TUTOR_PROVIDER_URL || 'https://provider.example.local/v1/chat'
  const key = process.env.TUTOR_PROVIDER_API_KEY || process.env.TUTOR_PROVIDER_KEY

  if (!key) {
    // Provider not configured in this environment — return a benign placeholder
    return { type: 'answer', message: 'provider_unavailable', safe: true }
  }

  const headers = new Headers({ 'content-type': 'application/json', authorization: `Bearer ${key}` })
  const resp = await fetch(PROVIDER_URL, {
    method: 'POST',
    headers,
    body: JSON.stringify({ lessonId: req.lessonId ?? req.lesson_id, prompt: req.prompt ?? req.question, lessonContext: req.lessonContext ?? req.lesson_context, subjectCode: req.subjectCode ?? req.subject_code }),
  })

  if (!resp.ok) throw new Error('provider_error')
  const data = await resp.json().catch(() => ({})) as Record<string, unknown>
  const retType = typeof data.type === 'string' ? data.type : 'answer'
  const msg = typeof data.message === 'string' ? data.message : typeof data.text === 'string' ? data.text as string : ''
  const safeFlag = typeof data.safe === 'boolean' ? data.safe : true
  return { type: retType as import('./types').TutorResponseType, message: msg, safe: safeFlag }
}

// Client-side thin wrapper to call our server API from browser code.
export async function askTutorClient(request: TutorRequest): Promise<TutorResponse> {
  const r = await fetch('/api/tutor', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(request) })
  return await r.json()
}

// Backwards-compatible alias used by older tests/code
export const askTutor = askTutorClient
