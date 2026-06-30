import { NextResponse } from 'next/server'
import { validateTutorRequest, filterTutorInput, filterTutorOutput, createTutorRefusalResponse } from '../../../lib/tutor/safety'
import { callProvider } from '../../../lib/tutor/client'
import { auditEventStub } from '../../../lib/tutor/audit'
import { checkRateLimit, RATE_LIMIT_MESSAGE } from '../../../lib/tutor/rate-limit'

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}))
  // Normalize identity from headers or body (tests supply x-forwarded-for)
  const headers = (req as Request).headers as Headers | undefined
  const forwarded = headers?.get('x-forwarded-for') || headers?.get('x-real-ip')
  const identity = forwarded ?? (body && (body.userId ?? body.user_id))

  // Rate limit check
  const rl = checkRateLimit(typeof identity === 'string' ? identity : undefined)
  if (!rl.ok) {
    await auditEventStub({ event: 'tutor.rate_limited', reason: rl.message ?? 'rate_limited' })
    return NextResponse.json({ message: rl.message ?? RATE_LIMIT_MESSAGE }, { status: 429 })
  }

  // Basic contract validation
  const validation = validateTutorRequest(body)
  if (!validation.ok) {
    await auditEventStub({ event: 'tutor.request.rejected', reason: validation.reason })
    const human = validation.reason === 'missing_lesson_id' ? 'Lesson identifier is required.' : validation.reason === 'missing_prompt' ? 'A lesson question is required.' : validation.reason === 'empty_body' ? 'Tutor request must be a JSON object.' : 'Invalid request.'
    return NextResponse.json({ error: { message: human } }, { status: 400 })
  }

  // Audit: request received (stub) — normalize lesson id for legacy shapes
  const lessonIdNorm = body.lessonId ?? body.lesson_id
  await auditEventStub({ event: 'tutor.request.received', lessonId: lessonIdNorm })

  // Input filtering
  const filtered = filterTutorInput(body)
  if (filtered.refusalReason) {
    await auditEventStub({ event: 'tutor.request.refused', lessonId: lessonIdNorm, reason: filtered.refusalReason })
    return NextResponse.json(createTutorRefusalResponse(filtered.refusalReason), { status: 200 })
  }

  // Call provider via server-only client
  try {
    const resp = await callProvider(filtered.request)
    const safe = filterTutorOutput(resp)
    await auditEventStub({ event: 'tutor.request.accepted', lessonId: lessonIdNorm })
    return NextResponse.json(safe)
  } catch (err) {
    await auditEventStub({ event: 'tutor.request.error', error: String(err) })
    return NextResponse.json({ error: { message: 'Provider error' } }, { status: 502 })
  }
}
