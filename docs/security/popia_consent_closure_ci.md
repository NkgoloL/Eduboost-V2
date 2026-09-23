---
title: "POPIA Consent Closure CI"
status: archived
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: null
evidence_command: null
code_anchors: [docs/security/README.md, app/security]
archived_at: '2026-09-23'
---
# POPIA Consent Closure CI
> [!NOTE]
> **Status: ARCHIVED — 2026-09-23**
> Historical milestone evidence, review audit, or point-in-time record; retained for audit lineage.



## Purpose

The POPIA consent/audit CI workflow runs both component checks and the aggregate
closure command.

## Required CI Command

```bash
make popia-consent-closure-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_popia_consent_closure_ci_contract.py -q --no-cov
```
