---
title: Phase 18 Controlled Beta Data Handling Register
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

# Phase 18 Controlled Beta Data Handling Register

This controlled beta data-handling register supports governance review and does not authorise production release, deployment, public beta, controlled beta launch activation, live learner traffic, learner data migration, or runtime KG implementation.

## Data Categories

- Guardian account/contact data
- Learner profile data
- Diagnostic responses and scores
- Study-plan progress
- Lesson completion records
- Consent records
- Data export and erasure request records

## Controls

- Collect only data required for the controlled beta objective.
- Keep support evidence free of unnecessary personal information.
- Preserve data-rights request evidence.
- Require explicit launch activation before any live learner cohort data is processed.
