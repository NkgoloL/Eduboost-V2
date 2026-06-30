import type { TutorRequest, TutorResponse } from './types'

const FREE_CHAT_PATTERNS = [
  /\btell me a story\b/i,
  /\bwhat is your opinion\b/i,
  /\bfree chat\b/i,
  /\bjust chat\b/i,
  /\banything\b/i,
  /\btell me about yourself\b/i,
  /\bhow are you\b/i,
  /\bmake up a story\b/i,
  /\bwrite a poem\b/i,
  /\bjoke\b/i,
  /\bsing\b/i,
  /\bchat with you\b/i,
]

const EMAIL_PATTERN = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi
const PHONE_PATTERN = /\+?\d[\d\s-]{6,}\d/g
const ID_PATTERN = /\b\d{6,}\b/g

export function validateTutorRequest(body: unknown): { ok: boolean; reason?: string } {
  if (!body || typeof body !== 'object') return { ok: false, reason: 'empty_body' }
  const b = body as Record<string, unknown>
  const lessonId = (b.lessonId ?? b.lesson_id) as string | undefined
  const prompt = (b.prompt ?? b.question) as string | undefined
  if (!lessonId || typeof lessonId !== 'string') return { ok: false, reason: 'missing_lesson_id' }
  if (!prompt || typeof prompt !== 'string') return { ok: false, reason: 'missing_prompt' }
  return { ok: true }
}

export function filterTutorInput(request: unknown): { request: TutorRequest; refusalReason?: string } {
  // Accept legacy shapes (snake_case) as unknown and normalize.
  const r = request as Record<string, unknown>
  const promptVal = (r['prompt'] ?? r['question'] ?? r['question_text'] ?? r['question']) as unknown
  const prompt = typeof promptVal === 'string' ? promptVal : ''
  const sanitized = sanitizeLearnerPrompt(prompt)
  const lessonId = typeof r['lessonId'] === 'string' ? r['lessonId'] : typeof r['lesson_id'] === 'string' ? r['lesson_id'] as string : ''
  const lessonContext = typeof r['lessonContext'] === 'string' ? r['lessonContext'] : typeof r['lesson_context'] === 'string' ? r['lesson_context'] as string : undefined
  const subjectCode = typeof r['subjectCode'] === 'string' ? r['subjectCode'] : typeof r['subject_code'] === 'string' ? r['subject_code'] as string : undefined
  const userId = typeof r['userId'] === 'string' ? r['userId'] : typeof r['user_id'] === 'string' ? r['user_id'] as string : undefined

  const normalized: TutorRequest = { lessonId: lessonId || '', prompt: sanitized, lessonContext, subjectCode, userId }
  if (isBroadFreeChat(sanitized)) {
    return { request: normalized, refusalReason: 'This tutor only answers lesson-focused questions. Please ask about the current lesson or exercise.' }
  }
  return { request: normalized }
}

export function createTutorRefusalResponse(reason: string): TutorResponse {
  return { type: 'refusal', message: reason, safe: true }
}

export function filterTutorOutput(response: unknown): TutorResponse {
  const r = response as Record<string, unknown>
  const messageVal = r['message']
  if (!messageVal || typeof messageVal !== 'string' || !messageVal.trim()) {
    return createTutorRefusalResponse('The tutor is temporarily unavailable. Please try again later.')
  }
  const typeVal = typeof r['type'] === 'string' ? (r['type'] as string) : 'answer'
  if (typeVal !== 'answer') return createTutorRefusalResponse(String(messageVal))
  const safeFlag = typeof r['safe'] === 'boolean' ? r['safe'] : true
  return { type: typeVal as import('./types').TutorResponseType, message: messageVal.trim(), safe: safeFlag }
}

export function sanitizeLearnerPrompt(prompt: string): string {
  return prompt.replace(EMAIL_PATTERN, '[REDACTED]').replace(PHONE_PATTERN, '[REDACTED]').replace(ID_PATTERN, '[REDACTED]').trim()
}

function isBroadFreeChat(text: string) {
  return FREE_CHAT_PATTERNS.some((p) => p.test(text))
}

