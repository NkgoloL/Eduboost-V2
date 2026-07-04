---
title: "RR-017 Release Safety Controls Policy"
status: active
owner: release-engineering
reviewers: [release, operations, security, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-04
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr017_release_safety_controls.py --json"
code_anchors: [docs/release_safety]
---


# RR-017 Release Safety Controls Policy

Release safety controls authority recorded: true
Destructive audit consent DB changes blocked: true
Alembic stamp head repair blocked: true
Production DB mutation outside migration window blocked: true
Mutating health probes blocked: true
Break-glass exception process required: true
Release change-control boundary required: true

## Evidence rule

RR-017 evidence must be captured from a clean tracked baseline after final release-safety files are present. Template files are not evidence.

## Prohibited operations until explicit later authority

- Destructive audit or consent database changes must remain blocked.
- `alembic stamp head` repair against production databases must remain blocked.
- Production database mutation outside an approved migration window must remain blocked.
- Health probes must remain read-only and non-mutating.

## Carried caveats

- RR-003 remains valid, but its fallback coverage baseline recorded 0.0 because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-016 operational drills are required before this evidence capture.
- RR-016 clean_git_state_at_capture was false in the uploaded snapshot because docs/reports/ appeared as untracked local residue; this remains a transparency caveat, not new scope.
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
