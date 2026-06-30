---
title: "Consent Revoke Authorization Wiring"
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

# Consent Revoke Authorization Wiring

## Endpoint

This slice enforces learner write authorization on:

```text
POST /api/v2/consent/revoke
```

## Policy Function

```python
require_learner_write_for_current_user(current_user, learner_id)
```

Revoking consent changes learner processing state and is treated as a
write-sensitive learner-data operation.

## Verification

```bash
pytest -c pytest.ini \
  tests/unit/test_consent_revoke_authorization_wiring.py \
  tests/integration/test_consent_revoke_authorization.py \
  -q --no-cov
```
