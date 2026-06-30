import { NextResponse } from 'next/server'

export function requireGuardianAuth(req: Request) {
  const auth = req.headers.get('authorization') || ''
  const expected = process.env.GUARDIAN_API_KEY || ''
  if (!expected) return { ok: false, reason: 'server_not_configured' }
  if (auth !== `Bearer ${expected}`) return { ok: false, reason: 'unauthorized' }
  return { ok: true }
}

export function guardResponse(reason = 'unauthorized') {
  return NextResponse.json({ error: { message: reason } }, { status: 401 })
}
