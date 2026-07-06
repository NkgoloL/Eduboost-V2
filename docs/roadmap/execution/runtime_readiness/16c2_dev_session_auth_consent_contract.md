---
title: Phase 16C-2 — Dev-Session Auth and Consent Contract Repair
status: active-control
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

# Phase 16C-2 — Dev-Session Auth and Consent Contract Repair

**Status:** repair harness installed; evidence unclaimed.

## Purpose

Align local non-production `/auth/dev-session` with the same runtime
authorization and consent gates used by real learner-scoped endpoints.

## Repairs

- Normalise enum roles such as `UserRole.PARENT` to the stable JWT/API value
  `parent`.
- Ensure dev-session consent uses the canonical runtime policy version
  `1.0.0`.
- Normalise stale active dev-session consent rows in place to avoid partial
  unique-index collisions.

## Boundary

This slice is dev-session contract repair only. It does not claim Phase 16
seeded E2E evidence or any production release/deployment authority.
