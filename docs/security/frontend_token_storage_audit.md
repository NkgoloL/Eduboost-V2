---
title: "Frontend Token Storage Audit"
status: current-evidence
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# Frontend Token Storage Audit

**Status:** ✅ No violations found  
**Date:** 2026-06-12  
**Phase:** 8 (A.5)  
**Auditor:** Phase 8 implementation (automated + manual review)

---

## Scope

Audit of `app/frontend/src/` for insecure access-token storage patterns:
- `localStorage.setItem` with token values
- `sessionStorage.setItem` with token values  
- Cookies set without `HttpOnly` (JS-readable)
- Access tokens embedded in non-memory state (Redux, Zustand, context) that persists to storage

---

## Findings

### Access Token Handling

**File:** `app/frontend/src/lib/auth/cookies.ts`

```typescript
export const sessionCookieOptions = {
  httpOnly: true,        // ✅ HttpOnly — not JS-readable
  sameSite: "strict",    // ✅ CSRF-safe
  secure: isProduction,  // ✅ Secure in production
  path: "/",
  maxAge: 60 * 60 * 12,  // 12 hours
};
```

The session cookie is set **server-side** via `NextResponse.cookies.set()` (in Next.js API routes/middleware), which means the `httpOnly: true` flag is respected by the browser. The JavaScript layer never touches the raw token.

**File:** `app/frontend/src/lib/auth/session.server.ts`

This file is marked `"use server-only"` — it imports from `next/headers` which is only available in Server Components and Route Handlers. The access token is never passed to client-side JavaScript.

```typescript
import "server-only";  // ✅ Enforces server-only import boundary
export function getSessionToken(): string | null { ... }  // server-only
```

### localStorage / sessionStorage

No `localStorage.setItem` or `sessionStorage.setItem` calls involving token values were found in any of the following:
- `app/frontend/src/lib/auth/`
- `app/frontend/src/lib/api/`
- `app/frontend/src/hooks/`
- `app/frontend/src/context/`

### Cookie Flags Summary

| Attribute | Value | Compliant |
|---|---|---|
| `HttpOnly` | `true` | ✅ |
| `Secure` | `true` (production) / `false` (dev) | ✅ |
| `SameSite` | `strict` | ✅ |
| `Path` | `/` | ⚠️ (see note below) |
| `MaxAge` | 12 hours | ✅ |

> **Note on Path:** The session cookie uses `path: "/"` which broadcasts to all routes. This is acceptable for a Next.js session cookie because the cookie is HttpOnly and the server validates it on every request. The backend refresh token cookie (managed separately in `app/core/cookies.py`) uses the more restrictive `path: "/api/auth"`. These serve different purposes and both are acceptable.

---

## One Minor Note (Non-blocking)

The frontend session cookie `maxAge` is 12 hours, but the backend JWT access token TTL is 15 minutes. These are aligned by design: the frontend cookie is a Next.js session token used for SSR, while the short-lived access JWT is refreshed independently. Both are not JS-readable.

---

## Verdict

**No violations.** Access tokens are stored in `HttpOnly` cookies via server-side Next.js code. No `localStorage`, `sessionStorage`, or JS-readable cookie storage was found.

---

## References

- `app/frontend/src/lib/auth/cookies.ts` — cookie options
- `app/frontend/src/lib/auth/session.server.ts` — server-only session helpers
- `app/core/cookies.py` — backend refresh cookie policy (Python)
- Phase 8 execution plan §A.5
