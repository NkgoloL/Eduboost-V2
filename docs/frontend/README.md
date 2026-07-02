---
title: "Frontend"
status: active
owner: frontend
reviewers: [frontend, product, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/frontend, docs/frontend/README.md]
---

# Frontend

The frontend is a Next.js app in `app/frontend` serving learner, parent, auth, and admin experiences.

## Runtime map

- App routes: `app/frontend/src/app/`
- Shared components: `app/frontend/src/components/`
- API client and services: `app/frontend/src/lib/api/`
- Frontend tests: `app/frontend/src/__tests__/` and `app/frontend/__tests__/`

## Current implementation notes

- API calls should go through the typed service/client layer in `src/lib/api`.
- Mocked Playwright or mock dashboard modes are test/local only.
- `NEXT_PUBLIC_CONTENT_FACTORY_MOCK=true` is ignored in production by design.
- Learner-facing pages must not render misleading success/fallback content after API failures.

## Verification

From `app/frontend`:

```bash
npm run type-check
npm test
npm run lint
npm run build
```

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
