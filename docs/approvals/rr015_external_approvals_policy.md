---
title: "RR-015 External Approvals Policy"
status: active
owner: governance
reviewers: [security, privacy, legal, curriculum, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-04
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr015_external_approvals.py --json"
code_anchors: [docs/approvals]
---

# RR-015 External Approvals Policy

External approvals authority recorded: true
Security review required: true
POPIA/privacy review required: true
Legal review required: true
CAPS/content review required: true
Release-owner go/no-go required: true
Repository-only approval substitution allowed: false

RR-015 reconciles approval evidence. It does not replace the later release-safety, operational-drill, or trustworthy-beta-quality work.

## Required approvals

- Security review must be approved by a named reviewer with an evidence URL or evidence pointer.
- POPIA/privacy review must be approved by a named reviewer with an evidence URL or evidence pointer.
- Legal review must be approved by a named reviewer with an evidence URL or evidence pointer.
- CAPS/content review must be approved by a named reviewer with an evidence URL or evidence pointer.
- Release-owner go/no-go signoff must be recorded, but it may only proceed to the next governance gate.

## Carried caveats

- RR-003 remains valid, but its fallback coverage baseline recorded 0.0 because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-016 operational drills remain outstanding.
- RR-017 release safety controls remain outstanding.
- RR-018 trustworthy beta product quality remains outstanding.

## Boundary

Public beta expansion authorised: false
Public beta live traffic authorised: false
Expanded learner data migration authorised: false
Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Runtime KG implementation claimed: false
