---
title: "ADR-006 — RSC Boundaries & Route Component Map"
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
# ADR-006 — RSC Boundaries & Route Component Map

```text
Status: Accepted
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC1
Blocks: FE-P2-064..068 · FE-PR-006 · FE-PR-007
Reviewers: Frontend Architecture Review Board
Evidence: Next.js App Router guidance, FE-SPIKE-003 (PPR defer), TODO_V4.1 Phase 2 tasks
```

## Context

The frontend relies on Next.js App Router with React Server Components (RSC). Without explicit boundaries, previous prototypes mixed server/client concerns, causing hydration bugs and bundle bloat. RC2 requires a canonical map so engineers know which parts of each route run on the server, which run on the client, and where streaming or Suspense are allowed.

## Decision

- **Server Components by default:** Route segments (`/dashboard`, `/diagnostic`, `/lesson`, `/parent`, `/settings`) render as RSC. Client components are imported only for interactive widgets.
- **Client islands:** Forms, tactile feedback, and offline toggles live in `src/components/client/*`. Each island is dynamically imported with `ssr: false` when necessary.
- **Data fetching:** All backend calls happen in server components or route handlers. Client islands receive data via props or context only.
- **Streaming vs. Suspense:** Use Suspense boundaries for learner dashboard tiles; streaming is allowed but PPR remains disabled until FE-SPIKE-003 revisit.
- **Instrumentation:** `src/instrumentation.ts` runs once per deployment; route-level instrumentation uses server actions.

## Consequences

### Positive

- Keeps sensitive data out of the client bundles and simplifies POPIA compliance.
- Enables targeted bundle splits and easier reasoning about client interactivity.

### Negative

- Requires more boilerplate when adding new interactive widgets; engineers must intentionally create client components.
- Some third-party libraries might be incompatible with RSC and need wrappers or alternatives.

## Implementation Notes

1. Maintain a living component map in `docs/frontend/frontend_route_inventory.md` (already exists) and annotate server/client classification.
2. Add ESLint rule (FE-PR-003) forbidding `use client` in files located under `src/app/(learner)` unless explicitly necessary.
3. Document streaming toggles in each PR to avoid accidental PPR enablement.

## Compliance & Evidence

- FE-SPIKE-003 outcome ensures PPR stays disabled; references included.
- Server-only data handling supports POPIA guardrails documented in ADR-003.
