---
title: Legacy Quarantine Boundary
status: active
owner: architecture
reviewers: [engineering, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-03
review_interval_days: 60
evidence_command: make docs-housekeeping-check
code_anchors: [docs/architecture/legacy_quarantine_boundary.md]
---

# Legacy Quarantine Boundary (TSR-6.12)

## Quarantine Directive
`app/legacy` contains legacy V1 endpoints and compatibility implementations. To protect architectural integrity in EduBoost V2, strict physical boundaries are enforced.

## Enforcement Mechanism
1. **Import Linter Contract:**
   - Contract `[importlinter:contract:legacy-quarantine]` in `.importlinter` forbids `app.core` and `app.domain` from importing `app.legacy`.
   - Verified via `lint-imports`.
2. **Deprecation Strategy:**
   - All active V2 features must interact exclusively through V2 services (`app.services.*`) and repositories (`app.repositories.*`).
   - Legacy routes are scheduled for decommission following public beta release gate closure.
