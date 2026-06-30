import { NextRequest, NextResponse } from "next/server";

import { backendFetch, forwardSetCookies } from "@/lib/api/server-client";
import { clearSessionCookie, setSessionCookie } from "@/lib/auth/cookies";
import { getSessionToken } from "@/lib/auth/session.server";

export async function POST(request: NextRequest) {
  const token = getSessionToken();
  const backendResponse = await backendFetch("/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    token,
    cookieHeader: request.headers.get("cookie") ?? undefined,
  });

  const payload = await backendResponse.json().catch(() => null);
  const response = NextResponse.json(payload, { status: backendResponse.status });
  forwardSetCookies(backendResponse, response);

  const nextToken = payload && typeof (payload as Record<string, unknown>).access_token === "string"
    ? (payload as Record<string, string>).access_token
    : null;

  if (backendResponse.ok && nextToken) {
    setSessionCookie(response, nextToken);
  } else if (!backendResponse.ok) {
    clearSessionCookie(response);
  }

  return response;
}
