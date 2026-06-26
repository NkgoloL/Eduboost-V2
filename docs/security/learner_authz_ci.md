---
title: "Learner Authorization Coverage CI"
status: active
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

# Learner Authorization Coverage CI

## Workflow

```text
.github/workflows/learner-authz-coverage.yml
```

## Guard

The workflow runs:

```bash
make learner-authz-check
```

on pull requests and pushes targeting `master` and `release/**`.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_learner_authz_ci_contract.py -q --no-cov
```
