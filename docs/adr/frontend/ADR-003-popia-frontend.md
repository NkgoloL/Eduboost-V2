---
title: "ADR-003 — POPIA Frontend Audit Relay"
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
# ADR-003 — POPIA Frontend Audit Relay

```text
Status: Accepted
Date: 2026-05-28
Owner: Frontend Tech Lead + POPIA Compliance Officer
RC Gate: RC1
Blocks: FE-P2-021 · FE-P2-052 · FE-P3-001..009 · FE-P5-041..047
Reviewers: POPIA Compliance Officer, Information Officer
Evidence: POPIA roadmap, audit relay backend contracts, FE-SPIKE-001 runtime validation
```

## Context

Frontend surfaces (learner actions, guardian consent updates, offline progress replay) must emit auditable records to comply with POPIA §17 and §24. Previous implementations emitted partial client-side logs that never reached the backend. RC2 and RC3 tasks require a formal contract for when and how the frontend fires audit relays.

## Decision

- All POPIA-relevant user actions trigger `POST /api/v2/audit/events` via server components or route handlers; no client-only logging is allowed.
- Client components call typed helper hooks (`useAuditEvent`, `useConsent`) which marshal minimal, synthetic identifiers only; the server handler enriches with tenant metadata and actor IDs.
- Audit payload schemas live alongside backend contracts (`@/types/audit`), keeping frontend + backend typed in sync.
- Evidence must be captured per PR showing redacted payloads and Information Officer approval for any new event.

## Consequences

### Positive

- Creates a single source of truth for audit events, making RC3 guardian requests traceable.
- Simplifies POPIA reporting because every event flows through the same route.

### Negative

- Requires server components even for seemingly client-only UI actions, increasing implementation complexity.
- Developers must coordinate closely with POPIA Compliance Officer for every new event type.

## Implementation Notes

1. Scaffold `useAuditEvent` and `useConsent` hooks in RC2 with server actions to ensure audit events run server-side.
2. Add Playwright fixtures that assert audit route hits in learner and guardian journeys.
3. Store audit evidence artifacts (redacted JSON, screenshots) under `docs/frontend/evidence/audit/` for RC3 sign-off.

## Compliance & Evidence

- POPIA Compliance Officer’s approval recorded in `docs/adr/frontend/sign-off.md`.
- FE-PR-002 monitoring scaffolding plus future FE-PR-008/009 guardian PRs will attach audit evidence.
