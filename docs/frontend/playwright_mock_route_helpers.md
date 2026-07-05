---
title: "Playwright Mock Route Helpers"
status: "active"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

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
