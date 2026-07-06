---
title: Release Evidence Artifacts Check
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
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
