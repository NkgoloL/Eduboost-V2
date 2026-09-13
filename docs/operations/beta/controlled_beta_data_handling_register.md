---
title: "Phase 18 Controlled Beta Data Handling Register (Controlled Beta Data Handling Register)"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
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
