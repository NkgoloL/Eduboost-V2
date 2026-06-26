---
title: "POPIA Consent Closure CI"
status: current-evidence
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# POPIA Consent Closure CI

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
