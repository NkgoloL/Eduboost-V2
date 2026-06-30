import "server-only";
import type { NextResponse } from "next/server";
import type { RequestInit } from "next/dist/server/web/spec-extension/request";
import { ApiError, generateRequestId, isEnvelope, normalizeApiBaseUrl, normalizeApiError, parseJson } from "./http";

const BASE_URL = normalizeApiBaseUrl(process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v2");

export interface BackendRequestOptions extends RequestInit {
  token?: string | null;
  cookieHeader?: string | null | undefined;
  rawResponse?: boolean;
}

export async function backendFetch(endpoint: string, options: BackendRequestOptions = {}) {
  const url = endpoint.startsWith("http") ? endpoint : `${BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const headers = new Headers(options.headers);

  if (options.cookieHeader) {
    headers.set("Cookie", options.cookieHeader);
  }

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData) && !(options.body instanceof Blob)) {
    headers.set("Content-Type", "application/json");
  }

  headers.set("X-Request-ID", headers.get("X-Request-ID") || generateRequestId());

  return fetch(url, {
    cache: "no-store",
    ...options,
    headers,
  });
}

export async function backendJson<T>(endpoint: string, options: BackendRequestOptions = {}): Promise<T> {
  const response = await backendFetch(endpoint, options);
  const payload = await parseJson(response);

  if (!response.ok) {
    throw new ApiError(normalizeApiError(payload, response));
  }

  if (isEnvelope<T>(payload) && "data" in payload) {
    return payload.data as T;
  }

  return payload as T;
}

export function forwardSetCookies(source: Response, target: NextResponse) {
  const headersAny = source.headers as unknown as {
    getSetCookie?: () => string[];
    raw?: () => Record<string, string[]>;
  };
  const raw = headersAny.raw?.();
  const values = headersAny.getSetCookie?.() || raw?.["set-cookie"] || [];
  if (!values.length) {
    const single = source.headers.get("set-cookie");
    if (single) {
      target.headers.append("Set-Cookie", single);
    }
    return;
  }
  values.forEach((cookie) => {
    if (cookie) {
      target.headers.append("Set-Cookie", cookie);
    }
  });
}
