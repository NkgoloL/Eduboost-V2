---
title: "Operations — Cluster E Closure Check"
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
# Cluster E Closure Check

## Purpose

`make cluster-e-closure-check` is the aggregate command for data-resilience
backup/restore evidence.

## Included Checks

- database backup contract
- database restore drill documentation
- backup dry-run command scaffold
- restore dry-run command scaffold
- backup manifest generation
- restore evidence generation
- backup integrity verification
- restore integrity verification
- Cluster E evidence aggregation

## Command

```bash
make cluster-e-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_cluster_e_closure_check.py -q --no-cov
```
