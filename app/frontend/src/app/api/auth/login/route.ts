import { NextRequest, NextResponse } from "next/server";

import { backendFetch, forwardSetCookies } from "@/lib/api/server-client";
import { clearSessionCookie, setSessionCookie } from "@/lib/auth/cookies";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const backendResponse = await backendFetch("/auth/login", {
    method: "POST",
    body,
    headers: { "Content-Type": "application/json" },
    cookieHeader: request.headers.get("cookie") ?? undefined,
  });

  const payload = await backendResponse.json().catch(() => null);
  const response = NextResponse.json(payload, { status: backendResponse.status });
  forwardSetCookies(backendResponse, response);

  const accessToken =
    payload && typeof (payload as Record<string, unknown>).access_token === "string"
      ? (payload as Record<string, string>).access_token
      : null;

  if (backendResponse.ok && accessToken) {
    setSessionCookie(response, accessToken);
  } else if (!backendResponse.ok) {
    clearSessionCookie(response);
  }

  return response;
}
