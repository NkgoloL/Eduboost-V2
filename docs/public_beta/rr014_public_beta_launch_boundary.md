---
title: "RR-014 Public Beta Launch Boundary"
status: active
owner: product
reviewers: [product, operations, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-03
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr014_public_beta_expansion.py --json"
code_anchors: [docs/public_beta]
---

# RR-014 Public Beta Launch Boundary

Public beta launch boundary recorded: true
Public beta expansion authorised: false
Public beta live traffic authorised: false
Expanded learner data migration authorised: false
Production release authorised: false
Runtime KG implementation claimed: false

## Notes

This boundary keeps public beta expansion distinct from launch execution.
It preserves the prohibition on live traffic, expanded learner migration,
production release, and runtime KG claims.
