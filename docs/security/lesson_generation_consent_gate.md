---
title: "Lesson Generation Consent Gate"
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

# Lesson Generation Consent Gate

## Routes

```text
POST /api/v2/lessons/generate
POST /api/v2/lessons/
POST /api/v2/lessons/generate/stream
```

## Policy

Lesson generation processes learner data and must pass both gates:

1. object authorization via `require_learner_write_for_current_user`
2. active POPIA consent via `require_active_consent_for_current_user`

## Verification

```bash
pytest -c pytest.ini tests/unit/test_lesson_generation_consent_gate_wiring.py -q --no-cov
```
