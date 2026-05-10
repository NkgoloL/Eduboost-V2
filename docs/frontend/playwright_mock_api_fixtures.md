# Playwright Mock API Fixtures

## Purpose

Mock API fixtures let Playwright journey specs exercise learner and parent UI
states without a deployed backend.

## Success Fixtures

- `tests/fixtures/frontend/api/learner_dashboard_success.json`
- `tests/fixtures/frontend/api/diagnostic_submit_success.json`
- `tests/fixtures/frontend/api/lesson_generation_success.json`
- `tests/fixtures/frontend/api/parent_dashboard_success.json`

## Denial Fixtures

- `tests/fixtures/frontend/api/consent_denied_error.json`
- `tests/fixtures/frontend/api/authorization_denied_error.json`

## Required Envelope Fields

- `ok`
- `data` for success responses
- `error.code` for denial responses
- `error.message` for denial responses
- `error.safe_next_action` for denial responses
- `meta.request_id`

## Command

```bash
make frontend-mock-api-fixture-check
```
