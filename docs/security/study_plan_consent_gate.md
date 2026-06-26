---
title: "Study Plan Consent Gate"
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

# Study Plan Consent Gate

## Routes

```text
POST /api/v2/study-plans/{learner_id}
POST /api/v2/study-plans/generate/{learner_id}
```

## Policy

Study-plan generation processes learner data and must pass:

1. learner write authorization
2. active POPIA consent

The consent gate runs before the background job is enqueued.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_study_plan_consent_gate_wiring.py -q --no-cov
```
