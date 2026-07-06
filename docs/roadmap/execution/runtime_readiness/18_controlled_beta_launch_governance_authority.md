---
title: Phase 18 — Controlled Beta Launch Governance Authority
status: active-policy
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 18 — Controlled Beta Launch Governance Authority

**Status:** Harness pending  
**Scope:** Controlled beta launch governance only  

Phase 18 verifies that EduBoost has the operational governance pack needed for a later controlled beta launch decision. It does not authorise production release, deployment, release tagging, public beta, controlled beta launch activation, learner data migration, live learner traffic, or runtime KG implementation.

## Preconditions

Phase 18 requires Phase 17 controlled beta readiness evidence to verify as valid.

## Required Operations Pack

The launch-governance gate requires these documents:

- Controlled beta launch governance plan
- Candidate cohort manifest template
- Consent pack checklist
- Support runbook
- Incident response runbook
- Rollback plan
- Observability plan
- Data-handling register

## Exit Criteria

The gate may be recorded only when:

1. `verify_controlled_beta_readiness.py --json` is valid.
2. All Phase 18 launch operation documents exist and pass marker checks.
3. The tracked worktree is clean before capture.
4. The evidence index and SHA256 manifest are written.
5. All release, deployment, launch activation, live traffic, data migration, and runtime KG boundaries remain false.
