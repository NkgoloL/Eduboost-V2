---
title: "Beta Launch — Beta Cohort Rollout Contract"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Beta Cohort Rollout Contract

## Required Cohort Fields

- cohort ID
- beta stage
- max learners
- max guardians
- allowed grades
- allowed subjects
- consent required
- support channel ready
- rollback supported

## Required Rules

- max learners must be positive
- max guardians must be positive
- allowed grades must be South African school grades 1-12
- allowed subjects are required
- beta cohort requires consent
- beta cohort requires support channel readiness
- beta cohort requires rollback support

## Boundary

This contract records controlled cohort readiness. It does not invite, enroll, or activate beta participants.
