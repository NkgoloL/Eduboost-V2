---
title: "Phase 2 Authorization Closure Check"
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

# Phase 2 Authorization Closure Check

## Make Target

```bash
make phase2-authz-closure
```

## Script

```text
scripts/check_phase2_authorization_closure.py
```

## Included Guards

```text
make runtime-check
make openapi-check
make route-inventory-check
make pr002r-check
make phase2-authz-check
make learner-authz-check
```

The script also runs the key Phase 2 evidence and import-smoke pytest files.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_phase2_authorization_closure_script.py -q --no-cov
make phase2-authz-closure
```
