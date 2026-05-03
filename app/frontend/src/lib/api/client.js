const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v2";

/**
 * Enhanced fetch wrapper that handles authorization headers
 * and standardizes error responses.
 */
export async function fetchApi(endpoint, options = {}) {
  // Try to get tokens from localStorage
  let token = null;
  if (typeof window !== "undefined") {
    // Guardian auth is the V2 token source for parent and learner-scoped calls.
    if (endpoint.includes("/auth") || endpoint.includes("/consent") || endpoint.includes("/parent")) {
      token = localStorage.getItem("guardian_token");
    } else {
      token = localStorage.getItem("guardian_token") || localStorage.getItem("learner_token");
    }
  }

  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const url = endpoint.startsWith("http") ? endpoint : `${BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, { ...options, headers });
    
    // For 204 No Content, return null
    if (response.status === 204) return null;

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(data?.detail || data?.message || response.statusText || "API request failed");
    }

    return data;
  } catch (error) {
    console.error(`[API Error] ${options.method || "GET"} ${url}:`, error.message);
    throw error;
  }
}
