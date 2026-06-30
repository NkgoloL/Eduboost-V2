---
title: "Parent Routes Consent Gate"
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

# Parent Routes Consent Gate

## Routes

```text
GET /api/v2/parents/dashboard
GET /api/v2/parents/{guardian_id}/dashboard
GET /api/v2/parents/{guardian_id}/export
GET /api/v2/parents/learners/{learner_id}/progress
```

## Policy

Parent portal learner-data reads must pass:

1. learner object authorization
2. active POPIA consent

The erasure route intentionally remains a rights-exercise workflow and continues
to use `ConsentService.execute_erasure`.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_parent_routes_consent_gate_wiring.py -q --no-cov
```
