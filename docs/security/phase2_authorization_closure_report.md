---
title: "Phase 2 Authorization Closure Report Generator"
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

# Phase 2 Authorization Closure Report Generator

## Script

```text
scripts/generate_phase2_authorization_closure_report.py
```

## Output

```text
docs/security/PHASE2_AUTHORIZATION_CLOSURE.md
```

## Direct Execution

The script bootstraps the repository root onto `sys.path` so this command works
from the repository root:

```bash
python3 scripts/generate_phase2_authorization_closure_report.py
```

## Verification

```bash
python3 scripts/generate_phase2_authorization_closure_report.py
pytest -c pytest.ini tests/unit/test_generate_phase2_authorization_closure_report.py -q --no-cov
```
