import { ApiError, decodeJwtPayload, extractErrorMessage, generateRequestId, isEnvelope, normalizeApiBaseUrl, normalizeApiError, parseJson } from "./http";
import type { JobAcceptedResponse, JobStatusResponse } from "./types";

const ABSOLUTE_API_BASE = normalizeApiBaseUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v2");
const PROXY_BASE_PATH = "/api/backend";

export { ApiError, decodeJwtPayload, extractErrorMessage } from "./http";

export function getApiBaseUrl() {
  return ABSOLUTE_API_BASE;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}, retryOnUnauthorized = true): Promise<T> {
  const requestId = generateRequestId();
  const headers = buildHeaders(options.headers, options.body);
  headers.set("X-Request-ID", requestId);

  const url = resolveRequestUrl(endpoint);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: options.credentials || "include",
    });
    const payload = await parseJson(response);

    if (response.status === 401 && retryOnUnauthorized && !endpoint.startsWith("/api/auth/refresh")) {
      const refreshed = await refreshSession();
      if (refreshed) {
        return fetchApi<T>(endpoint, options, false);
      }
    }

    if (!response.ok) {
      throw new ApiError(normalizeApiError(payload, response));
    }

    if (isEnvelope<T>(payload) && "data" in payload) {
      return payload.data as T;
    }
    return payload as T;
  } catch (error: unknown) {
    const message = extractErrorMessage(error, "Unknown API error");
    console.error(`[API Error] ${options.method || "GET"} ${url}:`, message);
    throw error;
  }
}

const sleep = (ms: number) => new Promise((resolve) => {
  if (typeof window !== "undefined" && window?.setTimeout) {
    window.setTimeout(resolve, ms);
  } else {
    setTimeout(resolve, ms);
  }
});

export async function waitForJobResult<T>(
  accepted: JobAcceptedResponse,
  pollIntervalMs = 500,
  maxAttempts = 60
): Promise<T> {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const status = await fetchApi<JobStatusResponse<T>>(`/jobs/${accepted.job_id}`);
    if (status.status === "completed") {
      return status.result as T;
    }
    if (status.status === "failed") {
      throw new Error(status.error?.message || `Job ${accepted.operation} failed`);
    }
    await sleep(pollIntervalMs);
  }
  throw new Error(`Timed out waiting for ${accepted.operation}`);
}

function resolveRequestUrl(endpoint: string) {
  if (endpoint.startsWith("http")) return endpoint;
  if (endpoint.startsWith("/api/")) return endpoint;
  const normalized = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${PROXY_BASE_PATH}${normalized}`;
}

function buildHeaders(inputHeaders: HeadersInit | undefined, body: RequestInit["body"]) {
  const headers = new Headers(inputHeaders);
  const hasContentType = Array.from(headers.keys()).some((key) => key.toLowerCase() === "content-type");
  const shouldSetJson = body !== undefined && !(body instanceof FormData) && !(body instanceof Blob) && typeof body !== "string";

  if (!hasContentType && body !== undefined && !(body instanceof FormData) && !(body instanceof Blob)) {
    headers.set("Content-Type", typeof body === "string" ? "application/json" : "application/json");
  } else if (!hasContentType && shouldSetJson) {
    headers.set("Content-Type", "application/json");
  }

  return headers;
}

async function refreshSession() {
  try {
    const response = await fetch("/api/auth/refresh", { method: "POST" });
    return response.ok;
  } catch (error) {
    return false;
  }
}
