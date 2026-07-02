---
title: "Playwright Journey Fixture Contract"
status: active
owner: frontend
reviewers: [frontend, product, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/frontend, docs/frontend/README.md]
---

# Playwright Journey Fixture Contract

## Purpose

Playwright fixtures must describe learner and parent vertical journeys before
runtime browser tests are wired.

## Required Fixture Coverage

- learner vertical journey fixture
- parent vertical journey fixture
- authenticated session state
- learner and parent actor roles
- diagnostic start and submit
- lesson view
- progress/mastery feedback
- consent and authorization denial states
- API domains needed by the journey

## Required Fixtures

- `tests/fixtures/frontend/learner_journey_fixture.json`
- `tests/fixtures/frontend/parent_journey_fixture.json`

## Command

```bash
make frontend-journey-fixture-check
```
