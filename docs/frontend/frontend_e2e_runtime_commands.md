# Frontend E2E Runtime Commands

## Purpose

Cluster G separates scaffold checks from runtime browser execution.

## Commands

```bash
make frontend-e2e-smoke
make frontend-e2e-mocked
make frontend-e2e
```

## Mocked Runtime

`make frontend-e2e-mocked` runs the learner and parent mocked API journey specs
with `PLAYWRIGHT_MOCK_API=1`.

## Smoke Runtime

`make frontend-e2e-smoke` runs the learner and parent basic journey smoke specs
against `FRONTEND_BASE_URL`.

## Safety Boundary

Runtime E2E commands must not require production credentials, live learner data,
live parent data, or direct production backend access.

## Expected Specs

- `tests/e2e/learner-vertical-journey.spec.ts`
- `tests/e2e/parent-vertical-journey.spec.ts`
- `tests/e2e/learner-mocked-api-journey.spec.ts`
- `tests/e2e/parent-mocked-api-journey.spec.ts`
