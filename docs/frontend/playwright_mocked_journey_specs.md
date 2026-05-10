# Playwright Mocked Journey Specs

## Purpose

Mocked journey specs validate that learner and parent UI flows can run with
controlled API fixture envelopes.

## Specs

- `tests/e2e/learner-mocked-api-journey.spec.ts`
- `tests/e2e/parent-mocked-api-journey.spec.ts`

## Covered States

- learner success envelope
- learner consent denial envelope
- parent success envelope
- parent authorization denial envelope

## Safety Boundary

Mocked tests must not require live learner data, live parent data, production
credentials, or a deployed backend.

## Command

```bash
make frontend-playwright-mocked-specs-check
```
