---
title: "Operations — Release Evidence Artifacts Check"
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
# Release Evidence Artifacts Check

## Purpose

This check prevents release-evidence drift by validating that required closure
artifacts remain present and referenced.

## Command

```bash
make release-evidence-artifacts-check
```

## Required Evidence Areas

- runtime/API contract
- Phase 2 authorization closure
- Cluster C POPIA consent/audit closure
- Cluster D CI/deployment/environment closure
- staging release gate

## Verification

```bash
pytest -c pytest.ini tests/unit/test_release_evidence_artifacts.py -q --no-cov
```
