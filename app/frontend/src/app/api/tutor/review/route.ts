import { NextResponse } from 'next/server'
import { requireGuardianAuth, guardResponse } from '../../../../lib/tutor/parent-review/access'
import { parentReviewService } from '../../../../lib/tutor/parent-review/service'

export async function POST(req: Request) {
  // accept server-side tutor events or internal services; require no guardian auth for writes
  const body = await req.json().catch(() => ({}))
  try {
    const dto = await parentReviewService.saveSanitizedReview(body)
    return NextResponse.json({ ok: true, review: dto })
  } catch (err) {
    return NextResponse.json({ error: { message: String(err) } }, { status: 400 })
  }
}

export async function GET(req: Request) {
  // guardian list endpoint — require guardian auth
  const auth = requireGuardianAuth(req)
  if (!auth.ok) return guardResponse(auth.reason)

  const url = new URL(req.url)
  const learnerId = url.searchParams.get('learnerId')
  if (!learnerId) return NextResponse.json({ error: { message: 'missing learnerId' } }, { status: 400 })

  try {
    const list = await parentReviewService.listReviewsForLearner(learnerId)
    return NextResponse.json({ ok: true, reviews: list })
  } catch (err) {
    return NextResponse.json({ error: { message: String(err) } }, { status: 500 })
  }
}
