---
title: "RR-014 Public Beta Expansion Policy"
status: active
owner: product
reviewers: [product, privacy, operations, support]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-03
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr014_public_beta_expansion.py --json"
code_anchors: [docs/public_beta, scripts/public_beta]
---

# RR-014 Public Beta Expansion Policy

Public beta expansion authority recorded: true
Public beta expansion planning boundary recorded: true
Controlled beta outcome reviewed before public beta: true
Public beta expansion authorised: false
Public beta live traffic authorised: false
Expanded learner data migration authorised: false
Production release authorised: false
Runtime KG implementation claimed: false

## Boundary and caveats carried forward

- RR-003 remains valid, but its fallback coverage baseline recorded 0.0 because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-015 external approvals remain outstanding and are required before public beta activation.
- RR-016 operational drills remain outstanding and are required before public beta activation.
- RR-017 release safety controls remain outstanding and are required before public beta activation.
- RR-018 trustworthy beta product quality remains outstanding and is required before public beta activation.

## Scope

RR-014 may record a public-beta expansion readiness plan, a bounded cohort plan, privacy/consent attestation, support/incident readiness, and launch boundaries. It may not authorise public beta traffic, broader learner migration, production release, deployment, billing launch, live payment processing, or runtime KG implementation.
