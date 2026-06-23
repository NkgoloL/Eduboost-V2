---
title: "Diagnostics Consent Gate"
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

# Diagnostics Consent Gate

## Routes

```text
GET /api/v2/diagnostics/items/{learner_id}
POST /api/v2/diagnostics/submit
```

## Policy

Diagnostic item retrieval and submission process learner data and must pass:

1. learner object authorization
2. active POPIA consent

## Verification

```bash
pytest -c pytest.ini tests/unit/test_diagnostics_consent_gate_wiring.py -q --no-cov
```
