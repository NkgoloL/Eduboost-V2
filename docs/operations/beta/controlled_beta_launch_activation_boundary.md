---
title: "Controlled Beta Launch Activation Boundary (Controlled Beta Launch Activation Boundary)"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: make docs-housekeeping-check
code_anchors: "[]"
---
# Controlled Beta Launch Activation Boundary

This document defines what Phase 19 does **not** authorise.
This document does not authorise controlled beta launch.

- Controlled beta launch authorised: false
- Live learner traffic authorised: false

## Phase 19 Allows

- Review of activation preflight materials.
- Evidence capture that readiness and governance records exist.
- Preparation for a later go/no-go decision.

## Phase 19 Does Not Allow

- production release;
- deployment;
- release tagging;
- public beta;
- controlled beta launch activation;
- learner data migration;
- live learner traffic;
- runtime KG implementation; or
- expansion beyond the approved Grade 4 Mathematics controlled-beta scope.

## Required Later Gate

A later launch activation gate must explicitly state the cohort, owner,
activation time, rollback owner, live traffic boundary, and learner-data handling
approval before any real learner access is enabled.
