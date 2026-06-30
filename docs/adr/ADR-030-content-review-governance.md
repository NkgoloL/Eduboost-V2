---
title: "ADR-030 — Educator Consensus and Content Governance"
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
# ADR-030 — Educator Consensus and Content Governance

**Status:** Proposed for Phase 3 integration  
**Date:** 2026-06-14  
**Owner:** Curriculum Lead and Engineering Lead

## Context

EduBoost generates learner-facing educational content. A single mutable approval action is insufficient for educational quality, safeguarding, accountability, and reproducible publication decisions. The existing lifecycle allowed direct approval and bulk approval without an attributable multi-reviewer quorum.

## Decision

EduBoost will use a version-scoped, fail-closed content review workflow:

- three distinct qualified reviewers by default;
- creator approval does not count;
- every approval includes a completed versioned rubric;
- decisions and state transitions are append-only;
- material edits create a new artifact version and reset quorum;
- approval and publication are separate transitions;
- emergency quarantine is immediate and independently auditable;
- rejected, quarantined, superseded, and unpublished generated artifacts are excluded from learner delivery, semantic retrieval, and training export;
- stale review automation may remind and escalate but may never approve content.

The authoritative configuration defaults are:

```text
CONTENT_CONSENSUS_THRESHOLD=3
CONTENT_CONSENSUS_TIMEOUT_HOURS=72
CONTENT_REVIEW_POLICY_VERSION=phase3-v1
CONTENT_REVIEW_RUBRIC_VERSION=1.0
CONTENT_CREATOR_APPROVAL_COUNTS=false
CONTENT_DIRECT_PUBLISH_ALLOWED=false
```

## Consequences

### Positive

- Review decisions are attributable and independently auditable.
- Concurrent final approvals cannot over-count quorum.
- Content changes cannot inherit stale approval.
- Publication fails closed.
- Phase 2 retrieval shares an explicit generated-artifact eligibility contract.

### Negative

- Review throughput depends on educator capacity.
- New migrations, APIs, operational metrics, and reviewer procedures are required.
- Existing direct and bulk approval clients must migrate.

## Validation

This ADR is accepted only after the Phase 3 PostgreSQL concurrency suite, authorization suite, retrieval-exclusion suite, and independent audit pass on the canonical merged commit.
