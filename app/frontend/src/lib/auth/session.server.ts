import "server-only";

import { cookies } from "next/headers";
import type { ReadonlyRequestCookies } from "next/dist/server/web/spec-extension/adapters/request-cookies";
import { decodeJwtPayload } from "@/lib/api/http";
import { SESSION_COOKIE_NAME } from "./cookies";

export type SessionClaims = {
  sub?: string;
  role?: string;
  exp?: number;
  [key: string]: unknown;
};

function getCookieStore(): ReadonlyRequestCookies {
  return cookies() as unknown as ReadonlyRequestCookies;
}

export function getSessionToken(): string | null {
  const store = getCookieStore();
  return store.get(SESSION_COOKIE_NAME)?.value ?? null;
}

export function clearSessionToken() {
  const store = getCookieStore();
  store.delete(SESSION_COOKIE_NAME);
}

export function getSessionClaims<T extends SessionClaims = SessionClaims>() {
  const token = getSessionToken();
  if (!token) return null;
  return decodeJwtPayload<T>(token);
}

export function requireSessionToken() {
  const token = getSessionToken();
  if (!token) {
    throw new Error("Session token is required");
  }
  return token;
}
