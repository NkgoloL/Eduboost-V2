import type { ApiEnvelope, NormalizedApiError, JobAcceptedResponse, JobStatusResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v2";
const ACCESS_TOKEN_KEY = "guardian_token";
const LEARNER_TOKEN_KEY = "learner_token";

export class ApiError extends Error implements NormalizedApiError {
  code?: string;
  field_errors?: NormalizedApiError["field_errors"];
  remediation?: string;
  details?: Record<string, unknown>;
  request_id?: string;
  status?: number;

  constructor(error: NormalizedApiError) {
    super(error.message);
    this.name = "ApiError";
    this.code = error.code;
    this.field_errors = error.field_errors;
    this.remediation = error.remediation;
    this.details = error.details;
    this.request_id = error.request_id;
    this.status = error.status;
  }
}

export function getApiBaseUrl() {
  return BASE_URL;
}

export function getStoredAccessToken(endpoint = "") {
  if (typeof window === "undefined") return null;
  if (endpoint.includes("/auth") || endpoint.includes("/consent") || endpoint.includes("/parent") || endpoint.includes("/popia")) {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
  }
  return window.localStorage.getItem(ACCESS_TOKEN_KEY) || window.localStorage.getItem(LEARNER_TOKEN_KEY);
}

export function storeAccessToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  } else {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(LEARNER_TOKEN_KEY);
  }
}

export function extractErrorMessage(error: unknown, fallback = "API request failed") {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return fallback;
}

export function decodeJwtPayload<T extends Record<string, unknown> = Record<string, unknown>>(token: string): T | null {
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((char) => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join("")
    );
    return JSON.parse(json) as T;
  } catch {
    return null;
  }
}

function generateRequestId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function isEnvelope<T>(payload: unknown): payload is ApiEnvelope<T> {
  return Boolean(payload && typeof payload === "object" && ("data" in payload || "error" in payload || "request_id" in payload));
}

function normalizeApiError(payload: unknown, response: Response): NormalizedApiError {
  if (payload && typeof payload === "object") {
    const candidate = payload as Record<string, any>;
    const envelopeError = candidate.error as NormalizedApiError | undefined;
    const requestId = candidate.request_id || envelopeError?.request_id;
    if (envelopeError?.message) {
      return { ...envelopeError, request_id: requestId, status: response.status };
    }
    if (typeof candidate.detail === "string") {
      return { message: candidate.detail, code: candidate.error_code, details: candidate.details, request_id: requestId, status: response.status };
    }
    if (Array.isArray(candidate.detail)) {
      return {
        message: "Request validation failed",
        code: "validation_error",
        field_errors: candidate.detail.map((item: any) => ({ field: Array.isArray(item.loc) ? item.loc.join(".") : undefined, message: item.msg || "Invalid value" })),
        request_id: requestId,
        status: response.status,
      };
    }
    if (typeof candidate.message === "string") {
      return { message: candidate.message, code: candidate.error_code, details: candidate.details, request_id: requestId, status: response.status };
    }
  }

  const statusMessages: Record<number, string> = {
    401: "Your session has expired. Please log in again.",
    403: "You do not have permission to perform this action.",
    429: "Too many requests. Please wait a moment and try again.",
    503: "The server is currently busy. Please try again in a few seconds.",
    504: "The server timed out. Please retry shortly.",
  };
  return { message: statusMessages[response.status] || response.statusText || "API request failed", status: response.status };
}

async function parseJson(response: Response): Promise<unknown> {
  if (response.status === 204) return null;
  return response.json().catch(() => null);
}

async function refreshAccessToken(): Promise<string | null> {
  const response = await fetch(`${BASE_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-Request-ID": generateRequestId() },
  });
  const payload = await parseJson(response);
  if (!response.ok) {
    storeAccessToken(null);
    return null;
  }
  const token = (isEnvelope<{ access_token: string }>(payload) ? payload.data?.access_token : (payload as any)?.access_token) as string | undefined;
  if (token) storeAccessToken(token);
  return token || null;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}, retryOnUnauthorized = true): Promise<T> {
  const requestId = generateRequestId();
  const token = getStoredAccessToken(endpoint);
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    "X-Request-ID": requestId,
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };
  const url = endpoint.startsWith("http") ? endpoint : `${BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, { ...options, headers, credentials: options.credentials || "include" });
    const payload = await parseJson(response);

    if (response.status === 401 && retryOnUnauthorized && !endpoint.includes("/auth/refresh")) {
      const newToken = await refreshAccessToken();
      if (newToken) return fetchApi<T>(endpoint, options, false);
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

const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

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
