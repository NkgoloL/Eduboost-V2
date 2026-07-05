---
title: RR-017 Release Safety Control Attestation Template
status: active
owner: release-engineering
reviewers: [release, operations, security, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make rr017-release-safety-controls-check
code_anchors: [docs/release_safety, scripts/roadmap_reconciliation]
---

# RR-017 Release Safety Control Attestation Template

Release safety controls attested: true
Destructive audit consent DB changes blocked: true
Alembic stamp head repair blocked: true
Production DB mutation requires migration window: true
Mutating health probes blocked: true
Break-glass exception process recorded: true

## Boundary

Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Public beta authorised: false
Public beta live traffic authorised: false
Runtime KG implementation claimed: false
