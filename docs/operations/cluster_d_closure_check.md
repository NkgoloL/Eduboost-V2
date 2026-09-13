---
title: "Operations — Cluster D Closure Check"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Cluster D Closure Check

## Purpose

`make cluster-d-closure-check` is the aggregate command for CI, deployment, and
environment-gate evidence.

## Included Checks

- environment security contract
- production placeholder-secret guard
- production Key Vault behavior tests
- dev-only endpoint exposure guard
- deployment readiness documentation
- Cluster D CI evidence

## Command

```bash
make cluster-d-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_cluster_d_closure_check.py -q --no-cov
```
