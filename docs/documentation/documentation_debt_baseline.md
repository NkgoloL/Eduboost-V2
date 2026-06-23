---
title: Documentation Debt Baseline
status: active
owner: documentation-governance
reviewers: [release-management, engineering]
audience: engineering
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: make docs-housekeeping-check
code_anchors: [docs/documentation/housekeeping_ratchet_baseline.json, docs/generated/documentation_inventory.json]
---

# Documentation Debt Baseline

EduBoost Stage 2 does not claim the documentation corpus is clean. It records the known debt and prevents regression.

The active ratchet files are:

- `docs/documentation/housekeeping_ratchet_baseline.json`
- `docs/documentation/adr_number_baseline.json`
- `docs/documentation/stale_term_baseline.json`

The generated evidence files are:

- `docs/generated/documentation_inventory.json`
- `docs/generated/documentation_inventory.csv`
- `docs/generated/documentation_findings.csv`

## Rules

1. The baseline may only move in the direction of less debt unless an explicit migration note explains the exception.
2. New duplicate ADR numbers are blocked.
3. New stale off-project terms are blocked.
4. The deterministic inventory must be reproducible without absolute paths or timestamps.
5. Strict checks are used for cleanup planning, not as a false release-readiness claim.
