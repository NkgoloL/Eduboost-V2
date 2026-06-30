import { NextRequest, NextResponse } from "next/server";

import { backendFetch, forwardSetCookies } from "@/lib/api/server-client";
import { clearSessionCookie } from "@/lib/auth/cookies";
import { getSessionToken } from "@/lib/auth/session.server";

export async function POST(request: NextRequest) {
  const token = getSessionToken();
  const backendResponse = await backendFetch("/auth/logout", {
    method: "POST",
    token,
    headers: { "Content-Type": "application/json" },
    cookieHeader: request.headers.get("cookie") ?? undefined,
  });

  const payload = await backendResponse.json().catch(() => null);
  const response = NextResponse.json(payload, { status: backendResponse.status });
  forwardSetCookies(backendResponse, response);
  clearSessionCookie(response);
  return response;
}
