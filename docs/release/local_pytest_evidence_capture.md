---
title: Local Pytest Evidence Capture
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Local Pytest Evidence Capture

This document defines how EduBoost captures repository-local pytest evidence for release readiness.

## Commands

Capture all local pytest release evidence:

```bash
make capture-pytest-release-evidence
```

Validate captured evidence files:

```bash
make pytest-release-evidence-check
```

Capture individual scopes:

```bash
PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py unit
PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py integration
PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py full
```

## Evidence files

| Scope | File |
|---|---|
| Unit | `docs/release/unit_latest_green.txt` |
| Integration | `docs/release/integration_latest_green.txt` |
| Full pytest discovery | `docs/release/full_pytest_latest_green.txt` |

## Rules

- Local pytest evidence proves repository-local health only.
- It does not replace CI, staging smoke, migration proof, backup/restore drill, or human release signoff.
- Evidence files must include command, timestamp, return code, and passing summary.
