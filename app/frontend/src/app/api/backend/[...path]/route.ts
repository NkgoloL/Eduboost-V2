import { NextRequest, NextResponse } from "next/server";

import { backendFetch, forwardSetCookies } from "@/lib/api/server-client";
import { getSessionToken } from "@/lib/auth/session.server";

const ALLOWED_HEADERS = ["accept", "content-type", "x-request-id"];
const BODYLESS_METHODS = new Set(["GET", "HEAD"]);

function sanitizePath(pathSegments: string[] | undefined) {
  const segments = pathSegments ?? [];
  if (segments.length === 0) return "/";
  for (const segment of segments) {
    if (segment.includes("..")) {
      throw new Error("Invalid path segment");
    }
  }
  return `/${segments.map((segment) => encodeURIComponent(segment)).join("/")}`;
}

function pickForwardHeaders(request: NextRequest) {
  const headers = new Headers();
  for (const key of ALLOWED_HEADERS) {
    const value = request.headers.get(key);
    if (value) headers.set(key, value);
  }
  return headers;
}

type BackendRouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: BackendRouteContext) {
  const params = await context.params;
  let backendPath: string;
  try {
    backendPath = `${sanitizePath(params?.path)}${request.nextUrl.search}`;
  } catch {
    return NextResponse.json({ error: { message: "Invalid request path" } }, { status: 400 });
  }

  const headers = pickForwardHeaders(request);
  const hasBody = !BODYLESS_METHODS.has(request.method.toUpperCase());
  const body = hasBody ? await request.text() : undefined;

  const backendResponse = await backendFetch(backendPath, {
    method: request.method,
    headers,
    body,
    token: getSessionToken(),
    cookieHeader: request.headers.get("cookie") ?? undefined,
  });

  const responseHeaders = new Headers();
  const contentType = backendResponse.headers.get("content-type");
  if (contentType) {
    responseHeaders.set("Content-Type", contentType);
  }

  const textBody = BODYLESS_METHODS.has(request.method.toUpperCase()) ? null : await backendResponse.text();
  const response = new NextResponse(textBody, {
    status: backendResponse.status,
    headers: responseHeaders,
  });

  forwardSetCookies(backendResponse, response);
  return response;
}

export function GET(request: NextRequest, context: BackendRouteContext) {
  return proxy(request, context);
}

export function POST(request: NextRequest, context: BackendRouteContext) {
  return proxy(request, context);
}

export function PUT(request: NextRequest, context: BackendRouteContext) {
  return proxy(request, context);
}

export function PATCH(request: NextRequest, context: BackendRouteContext) {
  return proxy(request, context);
}

export function DELETE(request: NextRequest, context: BackendRouteContext) {
  return proxy(request, context);
}

export function OPTIONS(request: NextRequest, context: BackendRouteContext) {
  return proxy(request, context);
}
