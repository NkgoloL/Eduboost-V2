---
title: Phase 18 Controlled Beta Incident Response Runbook
status: active
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

# Phase 18 Controlled Beta Incident Response Runbook

This incident response runbook supports controlled beta governance. It does not authorise production release, deployment, public beta, controlled beta launch activation, live learner traffic, or runtime KG implementation.

## Incident Classes

- P0: data exposure, consent bypass, authentication breakage
- P1: learner-blocking journey failure
- P2: parent portal/reporting defect
- P3: cosmetic or non-blocking issue

## Response

P0 and P1 incidents require immediate beta owner notification, engineering triage, evidence preservation, and rollback consideration. Learner data must not be copied into logs or chat systems.
