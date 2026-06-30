import type { ApiEnvelope, NormalizedApiError } from "./types";

const BROWSER_GLOBAL = typeof window !== "undefined" ? window : undefined;

export function normalizeApiBaseUrl(value: string) {
  const trimmed = value.trim().replace(/\/+$/, "");
  if (trimmed.endsWith("/api/v2")) return trimmed;
  return `${trimmed}/api/v2`;
}

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

export function extractErrorMessage(error: unknown, fallback = "API request failed") {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return fallback;
}

export function generateRequestId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object");
}

export function isEnvelope<T>(payload: unknown): payload is ApiEnvelope<T> {
  return Boolean(payload && typeof payload === "object" && ("data" in payload || "error" in payload || "request_id" in payload));
}

export function isNormalizedApiError(value: unknown): value is NormalizedApiError {
  return isRecord(value) && typeof value.message === "string";
}

export function normalizeApiError(payload: unknown, response: Response): NormalizedApiError {
  if (isRecord(payload)) {
    const envelopeError = isNormalizedApiError(payload.error) ? payload.error : undefined;
    const requestId = (typeof payload.request_id === "string" ? payload.request_id : undefined) || envelopeError?.request_id;
    const detail = payload.detail;
    if (envelopeError?.message) {
      return { ...envelopeError, request_id: requestId, status: response.status };
    }
    if (typeof detail === "string") {
      return {
        message: detail,
        code: typeof payload.error_code === "string" ? payload.error_code : undefined,
        details: isRecord(payload.details) ? payload.details : undefined,
        request_id: requestId,
        status: response.status,
      };
    }
    if (Array.isArray(detail)) {
      return {
        message: "Request validation failed",
        code: "validation_error",
        field_errors: detail.map((item) => {
          if (!isRecord(item)) return { field: undefined, message: "Invalid value" };
          const location = Array.isArray(item.loc) ? item.loc.join(".") : undefined;
          const message = typeof item.msg === "string" ? item.msg : "Invalid value";
          return { field: location, message };
        }),
        request_id: requestId,
        status: response.status,
      };
    }
    if (typeof payload.message === "string") {
      return {
        message: payload.message,
        code: typeof payload.error_code === "string" ? payload.error_code : undefined,
        details: isRecord(payload.details) ? payload.details : undefined,
        request_id: requestId,
        status: response.status,
      };
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

export async function parseJson(response: Response): Promise<unknown> {
  if (response.status === 204) return null;
  return response.json().catch(() => null);
}

export function decodeJwtPayload<T extends Record<string, unknown> = Record<string, unknown>>(token: string): T | null {
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      decodeBase64(base64)
        .split("")
        .map((char) => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join("")
    );
    return JSON.parse(json) as T;
  } catch {
    return null;
  }
}

function decodeBase64(value: string) {
  if (typeof atob === "function") {
    return atob(value);
  }
  if (BROWSER_GLOBAL && typeof BROWSER_GLOBAL.atob === "function") {
    return BROWSER_GLOBAL.atob(value);
  }
  return Buffer.from(value, "base64").toString("binary");
}
