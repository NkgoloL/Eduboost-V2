---
title: "Onboarding Consent Gate"
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

# Onboarding Consent Gate

## Learner-Scoped Routes

```text
POST /api/v2/onboarding/submit
POST /api/v2/onboarding/archetype
```

Onboarding submission updates learner archetype data and must pass:

1. learner write authorization
2. active POPIA consent

## Non-Learner-Scoped Boundary

```text
GET /api/v2/onboarding/questions
```

The questions endpoint remains an authenticated catalog boundary. It has no
learner identifier and does not process a learner record.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_onboarding_consent_gate_wiring.py -q --no-cov
```
