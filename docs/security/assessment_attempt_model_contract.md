---
title: "Assessment Attempt Model Contract"
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

# Assessment Attempt Model Contract

## Purpose

`AssessmentAttemptRequest` and `AssessmentAttemptResponseItem` are centralized in:

```text
app/domain/api_v2_models.py
```

The assessment router imports the shared model directly. This replaces the
temporary local fallback used to keep the route importable while the missing
model was discovered.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_assessment_attempt_model_contract.py -q --no-cov
```
