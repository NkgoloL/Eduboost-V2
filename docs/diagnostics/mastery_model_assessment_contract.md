---
title: "Mastery Model Assessment Contract"
status: active
owner: diagnostics
reviewers: [diagnostics, learning-science, backend]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/modules/diagnostics, docs/diagnostics]
---

# Mastery Model Assessment Contract

## Purpose

This contract records the diagnostics-to-mastery evidence chain for learner progress and remediation.

## Required Mastery Signals

- diagnostic estimate
- practice performance
- recency
- consistency
- confidence
- topic-level mastery
- subject-level mastery
- progress timelines
- adaptive practice generator
- remediation based on misconception
- spaced repetition
- retrieval practice
- learning velocity
- risk-of-falling-behind signal
- next-best-activity recommendation

## Repository Evidence

- `app/modules/progress/mastery_model.py`
- `app/modules/progress/progress_timeline_service.py`
- `app/modules/progress/learning_velocity_service.py`
- `app/modules/practice/practice_generator.py`
- `app/modules/practice/spaced_repetition_scheduler.py`
- `app/modules/diagnostics/production_readiness_contracts.py`
- `tests/unit/modules/progress/test_mastery_model.py`
- `tests/unit/modules/practice/test_practice_and_calibration.py`

## Research Boundary

Bayesian Knowledge Tracing and Deep Knowledge Tracing remain post-launch research tracks that require sufficient usage data before implementation can be responsibly evaluated.
