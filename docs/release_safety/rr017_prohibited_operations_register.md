---
title: "RR-017 Prohibited Operations Register"
status: active
owner: release-engineering
reviewers: [release, operations, security, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr017_release_safety_controls.py --json"
code_anchors: [docs/release_safety]
---

# RR-017 Prohibited Operations Register

Prohibited operations register recorded: true
Destructive audit consent DB changes blocked: true
Alembic stamp head repair blocked: true
Production DB mutation requires migration window: true
Mutating health probes blocked: true
Break-glass exception process recorded: true

## Control Result

This register records prohibited release operations so they remain visible as blocked work unless a later approved governance gate explicitly authorises an exception.

## Boundary

Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Public beta authorised: false
Public beta live traffic authorised: false
Runtime KG implementation claimed: false
