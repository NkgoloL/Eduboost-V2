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
