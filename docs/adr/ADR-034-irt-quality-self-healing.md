---
title: "ADR-034 — IRT Quality and Self-Healing Controls"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-034 — IRT Quality and Self-Healing Controls

**Status:** Proposed for Phase 4 approval  
**Date:** 2026-06-15

## Context

EduBoost requires evidence-based monitoring of diagnostic-item quality without allowing an automated process to silently rewrite or republish learner-facing assessment content. Existing item exposures contain correctness and session identifiers but do not yet contain an independently estimated learner ability at response time.

## Decision

1. Use a conservative, versioned two-parameter logistic fit based on a session-rest-score ability proxy (`2pl-session-proxy-v1`).
2. Require minimum response, unique-learner, session, and answered-ratio gates before any intervention.
3. Separate calibration state from educator review status.
4. Use deterministic states: healthy, monitor, review required, quarantine, and retire/rewrite review.
5. Never shuffle answer options or mutate item wording automatically.
6. Exclude review-required, quarantined, retired, and rewrite-review items from learner selection.
7. Create rewrites only as Phase 3 `pending_review` artifacts with publication eligibility false.
8. Keep calibration events append-only and runs idempotent.
9. Permit attributable, reasoned manual overrides; automation is suppressed while an override is active.
10. Treat thresholds as provisional until a qualified statistical or assessment reviewer approves them.

## Consequences

- The workflow is fail-closed and auditable.
- Calibration is useful for quality triage but must not be described as nationally normed IRT.
- Richer ability snapshots and population calibration can replace the proxy in a future ADR without losing event history.
- Low-quality items leave the learner-serving pool immediately; rewrites cannot bypass Phase 3 governance.
