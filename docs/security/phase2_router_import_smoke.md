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
