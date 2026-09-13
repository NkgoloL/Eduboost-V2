---
title: "Operations — Database Restore Integrity Check"
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
# Database Restore Integrity Check

## Purpose

This check validates that restore evidence records the minimum status fields
needed before release promotion.

## Required Evidence

- backup artifact ID
- target environment
- restore integrity status
- learner count status
- consent count status
- audit count status
- restore dry-run command reference
- POPIA consent closure command reference

## Command

```bash
make database-restore-integrity-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_database_restore_integrity.py -q --no-cov
```
