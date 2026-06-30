---
title: "ADR-002 — State Management (Zustand + TanStack Query)"
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
# ADR-002 — State Management (Zustand + TanStack Query)

```text
Status: Accepted
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC1
Blocks: FE-P2-013 · FE-P2-014 · FE-P2-015 · FE-P2-016 · FE-P2-017 · FE-P2-021
Reviewers: Frontend Lead, Product Engineering Manager
Evidence: TODO_V4.1 Phase 2 requirements, prior RC2 performance audits
```

## Context

The learner dashboard, consent flows, and guardian portal require shared state that spans server components, client islands, and offline storage. Previous prototypes mixed Redux Toolkit and React Context, causing bundle bloat and duplication. RC2 tasks depend on a consistent client-store layer and an explicit separation between server-state and UI hints.

## Decision

- **Server state:** Use TanStack Query for data fetched from FastAPI (diagnostic status, lessons, audit logs). Queries must be declared in server components and hydrated via `dehydrate` when necessary.
- **Client state:** Use Zustand stores for ephemeral UI state (modal visibility, touch targets, grade mode overrides) and for offline-friendly caches that never contain PII beyond what is already on screen.
- **No Redux / MobX / Recoil:** These libraries stay out of the bundle unless a future ADR explicitly revisits the choice.
- **Testing:** Provide mock providers for both libraries so Playwright and Vitest can simulate learner journeys deterministically.

## Consequences

### Positive

- Predictable data handling: server data uses TanStack Query cache invalidation, while UI-only state remains lightweight.
- Minimises bundle growth relative to Redux while retaining devtools for debugging (Query Devtools only in dev builds).

### Negative

- Requires discipline to avoid pushing long-lived server data into Zustand stores.
- Engineers must learn two libraries and follow hydration rules for server components.

## Implementation Notes

1. Create `src/lib/state/queryClient.ts` and `src/lib/state/learnerStore.ts` as canonical entry points.
2. Add lint rule (FE-PR-003 scope) preventing direct `fetch` calls in client components when a Query exists.
3. Document cache keys, stale times, and background refetch expectations in `docs/frontend/state_management_contract.md` (to be added alongside FE-P2 tasks).

## Compliance & Evidence

- RC2 evidence must show server-state hydration for learner dashboard plus Zustand snapshot tests for grade mode switches.
- Sign-off recorded in `docs/adr/frontend/sign-off.md`.
