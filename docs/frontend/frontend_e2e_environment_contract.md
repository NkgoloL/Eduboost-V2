# Frontend E2E Environment Contract

## Purpose

Cluster G Playwright execution must have explicit environment variables for
frontend runtime, journey entrypoints, and mocked API execution.

## Required Environment Variables

- `FRONTEND_BASE_URL`
- `PLAYWRIGHT_WEB_SERVER_COMMAND`
- `LEARNER_JOURNEY_PATH`
- `PARENT_JOURNEY_PATH`
- `PLAYWRIGHT_MOCK_API`
- `CI`

## Runtime Requirements

- frontend base URL must point to a running frontend server
- web server command must start the frontend in test mode when provided
- learner journey path must route to the learner-facing entrypoint
- parent journey path must route to the parent-facing entrypoint
- mocked API mode must not call production backend services
- runtime E2E must not require live learner or parent data
- traces and screenshots must be retained on failure

## Command

```bash
make frontend-e2e-env-contract-check
```
