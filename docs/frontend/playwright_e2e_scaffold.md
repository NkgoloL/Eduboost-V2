---
title: "Playwright E2E Scaffold"
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

# Playwright E2E Scaffold

## Purpose

Cluster G uses Playwright to validate learner and parent frontend vertical
journeys against a running frontend application.

## Configuration

- `playwright.config.ts`
- `tests/e2e/`
- `FRONTEND_BASE_URL`
- `PLAYWRIGHT_WEB_SERVER_COMMAND`

## Execution Modes

### Scaffold validation

This mode checks that Playwright configuration and E2E specs exist without
requiring a live app.

```bash
make frontend-playwright-scaffold-check
```

### Runtime E2E

This mode runs browser tests against a running frontend.

```bash
make frontend-e2e
```

## CI Boundary

Browser execution is intentionally separate from the evidence scaffold. The
scaffold can run in standard CI; runtime browser tests should run in a frontend
or staging workflow with a live app.

Runtime boundary: runtime browser tests should run in a frontend or staging workflow with a live app.
