import { NextResponse } from "next/server";

import { getSessionClaims, getSessionToken } from "@/lib/auth/session.server";

export async function GET() {
  const token = getSessionToken();
  const claims = getSessionClaims();
  return NextResponse.json({ authenticated: Boolean(token), claims });
}
