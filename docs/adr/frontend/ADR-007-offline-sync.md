---
title: "ADR-007 — Offline Sync & Conflict Resolution"
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
# ADR-007 — Offline Sync & Conflict Resolution

```text
Status: Draft (RC4 gate)
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC4
Blocks: FE-P4-NEW-001 · FE-PR-010 · FE-PR-011
Reviewers: POPIA Compliance Officer, Information Officer, Offline Working Group
Evidence: FE-SPIKE-006 (pending), backend sync contract, Dexie prototype notes
```

## Context

Offline resilience (RC4) requires lesson downloads, progress queues, and compliance-safe audit replay. The decision framework must clarify caching strategy, IndexedDB schema, and how conflicts are resolved once the device reconnects. Until FE-SPIKE-006 finishes, the ADR remains Draft but records the intended approach.

## Decision

- Use Dexie.js for IndexedDB interactions, storing only lesson manifests, queued progress events, and metadata—never raw learner PII beyond required IDs.
- Progress queue uses server-authoritative merge: the backend is source-of-truth; client queues only append events until server ack.
- Audit replay remains disabled until POPIA approval; offline audit events stay in a separate queue flagged for compliance review.
- Service worker will be built with the library chosen in FE-SPIKE-006 (next-pwa vs Workbox) and must respect cache versioning per RC4 maturity ladder.

## Consequences

### Positive

- Aligns with backend expectations, preventing divergent progress states.
- Keeps offline data minimal, reducing POPIA exposure if a device is compromised.

### Negative

- Requires careful cache invalidation and migration scripts when Dexie schemas change.
- Audit replay delay may frustrate product expectations; explicit toggles are necessary.

## Implementation Notes

1. FE-SPIKE-006 must prove the service worker tooling before this ADR can move to Accepted.
2. Document Dexie schema under `docs/frontend/offline_sync_schema.md` (future file) and version migrations through tests.
3. Add synthetic offline test journeys (Playwright) to prove queue resilience before RC4 sign-off.

## Compliance & Evidence

- POPIA Compliance Officer + Information Officer approvals required to promote status.
- Offline evidence stored under `docs/frontend/evidence/offline/` once implementation begins.
