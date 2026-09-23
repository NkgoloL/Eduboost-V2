---
title: "Frontend Architecture & Client Operations"
status: "active"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---
# Frontend Architecture & Client Operations

The frontend is a Next.js web application located in `app/frontend`, built with Next.js 16.3.3 (`@next/swc`) and managed via `pnpm@9.14.4`. It serves learner, parent, auth, and administrative experiences, with PWA offline caching via Serwist.

## Toolchain & Runtime Contracts

- **Framework**: Next.js 16.3.3 with React 18.3.1 and `@next/swc`.
- **Package Manager**: `pnpm@9.14.4` (`pnpm-lock.yaml` enforced).
- **Build Mode**: Webpack-compatible hermetic offline build (`next build --webpack`).
- **Dev Port**: `3050` (`http://localhost:3050`).
- **E2E Testing**: Root Playwright test suite (`tests/e2e/`) auto-spawns Next in webpack mode via `pnpm --dir app/frontend exec next dev --webpack -p 3050`.

## Runtime Map

- App Routes: `app/frontend/src/app/`
- Shared UI Components: `app/frontend/src/components/`
- API Client and Typed Services: `app/frontend/src/lib/api/`
- Offline / PWA Service Worker: `app/frontend/public/sw.js` and Serwist config
- Unit & Component Tests: `app/frontend/src/__tests__/` and `app/frontend/__tests__/`
- End-to-End Tests: `tests/e2e/` (root-level Playwright)

## Current Implementation Invariants

- **Typed API Access**: All backend communication must route through typed services in `src/lib/api`.
- **Mock Separation**: `NEXT_PUBLIC_CONTENT_FACTORY_MOCK=true` and mocked dashboard flows are test-only and strictly ignored in production.
- **Fail-Closed Presentation**: Learner-facing components must never render artificial fallback or unearned completion states upon API failures.
- **Offline Integrity**: Cached lessons must indicate offline state clearly without fabricating sync confirmations.

## Verification Commands

From `app/frontend`:

```bash
pnpm run type-check
pnpm run lint
pnpm run test
pnpm run build
```

From repo root (E2E and Integration):

```bash
make frontend-e2e-mocked
make frontend-e2e-smoke
```

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).

