---
title: "POPIA Correction Request Authorization Wiring"
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

# POPIA Correction Request Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/popia/correction-request/{learner_id}
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

A correction request changes learner personal information and is treated as a
write-sensitive learner-data rights operation.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_popia_correction_request_authorization_wiring.py \
  tests/integration/test_popia_correction_request_authorization.py \
  -q --no-cov
```
