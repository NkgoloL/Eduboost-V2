# Playwright Mock Route Helpers

## Purpose

Mock route helpers allow Playwright specs to exercise frontend learner and
parent states using canonical API fixture envelopes.

## Helper File

- `tests/e2e/support/mockApi.ts`

## Supported Fixture Groups

- learner dashboard success
- diagnostic submit success
- lesson generation success
- parent dashboard success
- consent denied error
- authorization denied error

## Required Helper Functions

- `loadApiFixture`
- `mockJson`
- `mockLearnerJourneyApi`
- `mockParentJourneyApi`
- `mockConsentDeniedApi`
- `mockAuthorizationDeniedApi`

## Command

```bash
make frontend-playwright-mock-helper-check
```
