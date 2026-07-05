---
title: RR-016 Operational Drills Policy
status: active
owner: operations
reviewers: [operations, reliability, security, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make rr016-operational-drills-check
code_anchors: [docs/operations/drills, scripts/roadmap_reconciliation]
---

# RR-016 Operational Drills Policy

Operational drills authority recorded: true
Backup drill required: true
Restore drill required: true
Rollback drill required: true
Monitoring dashboard verification required: true
Incident handoff verification required: true

## Evidence rule

RR-016 evidence must be captured from a clean tracked baseline after final drill reports are present. Template files are not evidence.

## Required drill reports

Each final report must include the required success marker and preserve the release boundary markers.

## Carried caveats

- RR-003 remains valid, but its fallback coverage baseline recorded 0.0 because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-017 release safety controls remain outstanding.
- RR-018 trustworthy beta product quality remains outstanding.

## Boundary

Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Public beta authorised: false
Public beta live traffic authorised: false
Runtime KG implementation claimed: false
