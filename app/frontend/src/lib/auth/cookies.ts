import type { NextRequest, NextResponse } from "next/server";

const isProduction = process.env.NODE_ENV === "production";

export const SESSION_COOKIE_NAME = "eduboost_session";

export const sessionCookieOptions = {
  httpOnly: true,
  sameSite: "strict" as const,
  secure: isProduction,
  path: "/",
  maxAge: 60 * 60 * 12, // 12 hours
};

export function setSessionCookie(response: NextResponse, token: string) {
  response.cookies.set(SESSION_COOKIE_NAME, token, sessionCookieOptions);
}

export function clearSessionCookie(response: NextResponse) {
  response.cookies.set(SESSION_COOKIE_NAME, "", { ...sessionCookieOptions, maxAge: 0 });
}

export function readSessionCookie(request: NextRequest) {
  return request.cookies.get(SESSION_COOKIE_NAME)?.value ?? null;
}
