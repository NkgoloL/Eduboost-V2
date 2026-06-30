# Frontend Verification Evidence

Date: 2026-05-11
Branch: `codex/pr18-frontend-verification`
Base: `codex/pr17-rc-evidence-sweep`

## Purpose

This document records the fresh frontend install, test, accessibility, type, and
build verification pass for the production-readiness PR series.

## Dependency Corrections

The clean frontend install initially failed because `eslint-config-next@16.2.4`
requires ESLint 9 while the project pins ESLint 8. The frontend package now
uses `eslint-config-next@14.2.35`, aligned with the Next.js 14 runtime already
used by the app.

The test runner also failed under the available WSL Node.js 18 runtime because
Vitest 4 pulled newer Vite/Rolldown APIs. The frontend package now uses
`vitest@^1.6.1` and `@vitest/coverage-v8@^1.6.1`, which run successfully in the
current local verification environment.

The tracked `tsconfig.tsbuildinfo` file was removed and ignored. It is a
generated incremental TypeScript artifact and was holding stale `.next/types`
paths that broke clean `npm run type-check` runs.

## Commands Run

```bash
cd app/frontend
npm ci
npm run type-check
npm run test
npm run a11y-check
npm run build
```

## Observed Results

- `npm ci` passed.
- `npm run type-check` passed.
- `npm run test` passed with 10 test files and 41 tests.
- `npm run a11y-check` passed with 1 test file and 6 tests.
- `npm run build` passed with Next.js 14.2.35 and generated 14 static pages.

## Remaining Frontend Release Risks

- `npm ci` reports 10 vulnerabilities: 6 moderate and 4 high.
- Several Supabase packages warn that they require Node.js `>=20.0.0`; the
  local verification environment is Node.js `v18.19.1`.
- This PR verifies local unit/component/build evidence only. Browser E2E against staging remains part of the staging and operations PR.

## Release Claim

This PR establishes a fresh local frontend verification baseline. It does not
claim browser-level staging readiness, dependency-audit closure, or production
frontend readiness.
