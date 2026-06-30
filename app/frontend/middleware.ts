import { NextRequest, NextResponse } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/auth/cookies";

const LOGIN_PATH = "/login";

const PROTECTED_MATCHERS = [
  "/dashboard",
  "/dashboard/:path*",
  "/parent-dashboard",
  "/parent-dashboard/:path*",
  "/teacher",
  "/teacher/:path*",
  "/admin",
  "/admin/:path*",
  "/settings",
  "/settings/:path*",
  "/onboarding",
  "/onboarding/:path*",
];

function buildRedirectUrl(request: NextRequest) {
  const redirect = `${request.nextUrl.pathname}${request.nextUrl.search}`;
  const loginUrl = new URL(LOGIN_PATH, request.nextUrl.origin);
  loginUrl.searchParams.set("redirect", redirect);
  return loginUrl;
}

export function middleware(request: NextRequest) {
  const hasSession = Boolean(request.cookies.get(SESSION_COOKIE_NAME)?.value);
  if (hasSession) {
    return NextResponse.next();
  }
  const loginUrl = buildRedirectUrl(request);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: [
    "/dashboard",
    "/dashboard/:path*",
    "/parent-dashboard",
    "/parent-dashboard/:path*",
    "/teacher",
    "/teacher/:path*",
    "/admin",
    "/admin/:path*",
    "/settings",
    "/settings/:path*",
    "/onboarding",
    "/onboarding/:path*",
  ],
};

