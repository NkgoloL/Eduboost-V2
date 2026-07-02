---
title: "Playwright Vertical Journey Specs"
status: "active"
owner: "frontend"
reviewers: "[frontend, product, privacy]"
audience: "developer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

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
