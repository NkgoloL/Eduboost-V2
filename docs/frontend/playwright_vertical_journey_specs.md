# Playwright Vertical Journey Specs

## Purpose

These specs provide the first runtime-browser smoke layer for Cluster G.

## Specs

- `tests/e2e/learner-vertical-journey.spec.ts`
- `tests/e2e/parent-vertical-journey.spec.ts`

## Runtime Inputs

- `FRONTEND_BASE_URL`
- `LEARNER_JOURNEY_PATH`
- `PARENT_JOURNEY_PATH`
- `PLAYWRIGHT_WEB_SERVER_COMMAND`

## Required Coverage

- learner journey entrypoint loads
- parent journey entrypoint loads
- frontend shell is not blank
- body content is visible
- browser trace is retained on failure

## Command

```bash
make frontend-e2e
```
