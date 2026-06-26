---
title: "ADR-001 — Frontend Auth Model (FastAPI JWT + httpOnly cookie)"
status: active
owner: frontend
reviewers: [frontend, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-001 — Frontend Auth Model (FastAPI JWT + httpOnly cookie)

```text
Status: Accepted
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC1
Blocks: FE-P1-038 · FE-P1-039 · FE-P1-040 · FE-P1-041 · FE-P1-042 · FE-P1-043 · FE-P1-044
Reviewers: Backend Lead, POPIA Compliance Officer
Evidence: FE-SPIKE-001 (runtime viability), TODO_V4.1 Phase 1 auth tasks, ADR-001-rollback plan
```

## Context

Supabase Auth was previously embedded in the legacy frontend, creating divergent auth logic between the FastAPI backend and the Next.js client. RC1 requires a single source of truth for auth, audit relays, and consent gating. The backend already issues JWTs and httpOnly cookies, but the frontend still uses Supabase helpers and exposes tokens to the browser, which is incompatible with POPIA and the unified audit log.

## Decision

- Use FastAPI as the sole session authority. All login, logout, and refresh operations flow through `/api/v2/auth/*` endpoints.
- Store session state in httpOnly cookies issued by the backend proxy; never copy tokens into `localStorage` or expose them to client components.
- Provide server-only helpers under `src/lib/auth/session.server.ts` and `src/lib/auth/jwt.ts`. Importing them from client components is prohibited.
- Implement Next.js route handlers (`src/app/api/auth/login|logout|refresh/route.ts`) that proxy to FastAPI, enforce POPIA audit relays, and surface typed errors.
- Middleware enforces protected routes by validating JWT claims server-side before rendering learner or guardian surfaces.

## Consequences

### Positive

- Aligns frontend and backend auth semantics, enabling consistent audit/logging and easier incident response.
- Eliminates token exposure in browser storage, improving POPIA posture and reducing attack surface.
- Simplifies rollback because Supabase SDKs can be fully removed once the migration succeeds.

### Negative

- Requires migrating existing Supabase-powered components and tests.
- Depends on backend uptime; local development needs the FastAPI stack running for auth flows.

## Implementation Notes

1. Land ADR-001-rollback (Supabase fall-back) before removing Supabase dependencies.
2. Remove `@supabase/auth-helpers-nextjs` and related packages after FE-PR-001 merges and FE-PR-002 verifies pnpm discipline.
3. Introduce a shared `AuthContext` wrapper only for client-side display state; all security decisions live on the server.
4. Update Playwright fixtures to log in via the API proxy to avoid bypassing middleware.

## Compliance & Evidence

- POPIA Compliance Officer approval recorded in `docs/adr/frontend/sign-off.md`.
- Rollback protocol described in `docs/adr/frontend/ADR-001-rollback.md`.
- Evidence attachments: FE-SPIKE-001 runtime report, FE-PR-002 runtime hardening log, and future FE-PR-005 auth PR.
