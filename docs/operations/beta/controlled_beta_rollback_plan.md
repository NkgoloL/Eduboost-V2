---
title: Phase 18 Controlled Beta Rollback Plan
status: active-control
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 18 Controlled Beta Rollback Plan

This controlled beta rollback plan documents governance readiness and does not authorise production release, deployment, controlled beta launch activation, live learner traffic, learner data migration, or runtime KG implementation.

## Rollback Triggers

- Consent enforcement failure
- Authentication/session failure
- Diagnostic journey data corruption
- Parent portal privacy failure
- Sustained runtime outage

## Rollback Actions

1. Stop new beta access.
2. Preserve evidence and logs without exposing personal data.
3. Notify beta owner and support owner.
4. Revert the application or configuration to the last known-good protected baseline.
5. Re-run readiness verification before any reactivation.
