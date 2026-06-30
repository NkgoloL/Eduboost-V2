# FE-PR-003 Handover Report

**Branch:** `fe-pr-003-typescript-strictness`
**Date:** 2026-05-29
**Scope:** TypeScript strictness, ESLint enforcement, PII logging guard, React Hooks compliance, evidence + verification logs

---

## Commit command

```bash
git checkout -b fe-pr-003-typescript-strictness

git add \
  app/frontend \
  docs/frontend/FE-PR-003-handover.md

git commit -m "FE-PR-003 enforce frontend TypeScript and lint strictness"
```

---

## Area 1 — ESLint + lint governance

- Added `app/frontend/.eslintrc.js` to pin the TS parser/plugin, enforce `@typescript-eslint/no-explicit-any` as an error, and wire the new console/PII guardrails.
- Introduced `no-console` policy (warn/error only) plus `no-restricted-syntax` selectors that block logging of IDs, guardian/learner references, POPIA identifiers, or raw API payloads.
- Updated monitoring fallback logging (`src/lib/monitoring.ts`) to use `console.warn`/`console.error` so it passes the stricter lint rules while still emitting synthetic events during development.

**Result:** ESLint now fails any new `any`, disallows unsafe console usage, and runs with the exact parser/plugins required for TS-aware rules.

---

## Area 2 — React Hooks + async panel hygiene

Stabilized callback dependencies and data loaders across admin content-factory panels to clear the React Hooks lint warnings and prevent accidental refetch storms:

- `ProductionPromotionPanel`, `ReviewQueuePanel`, `StagingProductionPreviewPanel`, `StagingSeedPanel`, and `GenerationRunsPanel` now wrap async loaders in `useCallback`, guard queued-task indexing, and ensure catch branches never set state after unmount.

**Result:** `eslint --rule 'react-hooks/rules-of-hooks:error' --rule 'react-hooks/exhaustive-deps:error'` is clean across the admin surface.

---

## Area 3 — TypeScript strictness stages

| Flag | Status | Key fallout handled |
| --- | --- | --- |
| `noUncheckedIndexedAccess` | ✅ Enabled | Guarded onboarding steps, queued task peeks, course-card subject colors, metric-card sparkline math, and Vitest array index assertions. |
| `noImplicitOverride` | ✅ Enabled | Added `override` markers to the class-based `ErrorBoundary`. |
| `noFallthroughCasesInSwitch` | ✅ Enabled | No code changes required; entire repo compiles under the flag. |
| `noImplicitReturns` | ✅ Enabled | No new fallout; existing functions already returned explicitly. |
| `exactOptionalPropertyTypes` | ⏸️ Deferred | Flagged broad churn across API DTOs/monitoring/UI wrappers. Documented follow-up ticket **FE-TS-EXACT-OPTIONAL-001**. |

`tsconfig.json` now records the accepted strict flag set; the deferred flag was evaluated and explicitly removed with justification.

---

## Area 4 — API client + monitoring hardening

- `src/lib/api/client.ts` replaces the remaining `any` casts with type guards, normalizes `NormalizedApiError` envelopes, and ensures `ApiError` instances inherit typed metadata.
- `src/lib/monitoring.ts` logs scrubbed events only via warn/error, ensuring lint compliance and maintaining PII guards.

---

## Area 5 — Component/test fixes for strict indexing

- `src/app/onboarding/page.tsx`: `currentStep` now always resolves to a valid entry even when `activeStep` drifts.
- Dashboard components now enforce typed fallback tokens and safe sparkline math.
- Vitest suites (`ApiLayer`, `DiagnosticContract`, `LearnerJourneys`) assert array lengths or capture first elements defensively before dereferencing.

These changes eliminate the undefined-index assumptions exposed by `noUncheckedIndexedAccess`.

---

## Verification record

All checks below ran on the branch after the strictness work:

| Check | Result |
| --- | --- |
| `pnpm run type-check` | ✅ (`tsc --noEmit`) |
| `pnpm run lint` | ✅ (`next lint --no-cache`) |
| `pnpm test` | ✅ (22 files / 96 tests) |
| `pnpm run build` | ✅ (Next 15 production build) |
| `ANALYZE=true pnpm run build` | ✅ (bundle analyzer reports written to `.next/analyze/`) |

Artifacts: see `.next/analyze/{client,edge,nodejs}.html` for analyzer outputs.

---

## Deferred follow-up

- **Ticket:** `FE-TS-EXACT-OPTIONAL-001 — Migrate to exactOptionalPropertyTypes`
- **Reason:** Enabling the flag forced DTO/API/UI prop churn across `NormalizedApiError`, `FieldError`, learner DTOs, ShadCN wrappers, and monitoring events. Requires coordinated schema updates before re-attempting the flag.

---

## Carry-forward to FE-PR-004

```text
- Keep PPR disabled (per FE-SPIKE-003).
- Use synthetic monitoring payloads only.
- Re-run `ANALYZE=true pnpm run build` after dependency-heavy changes.
- Honor the strict TypeScript baseline recorded above.
- exactOptionalPropertyTypes remains deferred to FE-TS-EXACT-OPTIONAL-001.
```
