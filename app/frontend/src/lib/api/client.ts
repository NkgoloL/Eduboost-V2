import type { ApiErrorShape, JobAcceptedResponse, JobStatusResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v2";

/**
 * Enhanced fetch wrapper that handles authorization headers
 * and standardizes error responses.
 */
export function getApiBaseUrl() {
  return BASE_URL;
}

export function extractErrorMessage(error: unknown, fallback = "API request failed") {
  if (error instanceof Error) return error.message;
  // If it's already a string, use it (handy for simple throws)
  if (typeof error === "string") return error;
  return fallback;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // Try to get tokens from localStorage
  let token: string | null = null;
  if (typeof window !== "undefined") {
    // Guardian auth is the V2 token source for parent and learner-scoped calls.
    if (endpoint.includes("/auth") || endpoint.includes("/consent") || endpoint.includes("/parent")) {
      token = localStorage.getItem("guardian_token");
    } else {
      token = localStorage.getItem("guardian_token") || localStorage.getItem("learner_token");
    }
  }

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const url = endpoint.startsWith("http") ? endpoint : `${BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, { ...options, headers });
    
    // For 204 No Content, return null
    if (response.status === 204) return null as T;

    const data = (await response.json().catch(() => null)) as ApiErrorShape | T | null;

    if (!response.ok) {
      let errorMessage = "API request failed";
      
      if (data && typeof data === "object") {
        errorMessage = (data as any).detail || (data as any).message || errorMessage;
      }

      if (response.status === 401) {
        errorMessage = "Your session has expired. Please log in again.";
      } else if (response.status === 403) {
        errorMessage = (data as any)?.detail || (data as any)?.message || "You don't have permission to perform this action.";
      } else if (response.status === 429) {
        errorMessage = "Too many requests. Please wait a moment or upgrade to Premium.";
      } else if (response.status === 503 || response.status === 504) {
        errorMessage = "The server is currently busy. Please try again in a few seconds.";
      } else {
        errorMessage = (data as any)?.detail || (data as any)?.message || response.statusText || errorMessage;
      }

      throw new Error(errorMessage);
    }

    return data as T;
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
