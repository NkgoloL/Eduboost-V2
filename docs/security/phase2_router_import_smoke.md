---
title: "Phase 2 Router Import Smoke"
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

# Phase 2 Router Import Smoke

## Purpose

This test ensures the learner-data authorization work does not regress route
importability.

## Covered Routers

```text
assessments
onboarding
gamification
consent
parents
popia
diagnostics
lessons
learners
study_plans
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_phase2_router_import_smoke.py -q --no-cov
```
