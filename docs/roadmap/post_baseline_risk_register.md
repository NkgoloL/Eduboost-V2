---
title: "Roadmap — Post-Baseline Risk Register"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'product']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Post-Baseline Risk Register

## Required Risk Fields

- risk ID
- title
- category
- impact
- likelihood
- owner
- mitigation
- evidence path
- blocks GA flag

## Required Rules

- risk ID must follow RISK-### format
- risk owner is required
- risk mitigation is required
- critical post-baseline risk must block GA
- risk evidence path must live under docs/roadmap/

## Boundary

This register records post-baseline risks. It does not close risks.
