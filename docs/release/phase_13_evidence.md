# Phase 13 Evidence - Frontend and Product Completeness

**Evidence date:** 2026-06-14
**Status:** Substantially remediated with local WSL proof; live full-stack CI proof still pending

## Evidence Sources

- `docs/roadmap/execution/phase_13_execution_plan.md`
- `docs/roadmap/execution/phase_13_implementation_report.md`
- `.github/workflows/e2e.yml`
- `.github/workflows/frontend-e2e.yml`
- `playwright.config.ts`
- `Makefile`
- `pnpm-lock.yaml`
- `locust/locustfile.py`
- `locust/README.md`
- `docs/caps/content_expansion_roadmap.md`
- `docs/caps/multilingual_status.md`
- `docs/development/e2e_testing.md`
- `docs/development/pwa_offline_plan.md`
- `docs/adr/ADR-029-supabase-auth-strategy.md`

## Remediation Completed on 2026-06-14

- Installed a WSL user-local `pnpm` shim pinned to `9.14.4`.
- Installed root Node dependencies and committed the root `pnpm-lock.yaml` so root Playwright dependencies are reproducible.
- Installed Playwright Chromium, Firefox, and WebKit browser bundles plus required WSL browser libraries.
- Repaired root Playwright execution:
  - `playwright.config.ts` now starts the frontend with `pnpm --dir app/frontend exec next dev --webpack -p 3050`.
  - Default base URL is `http://localhost:3050`, avoiding Next dev cross-origin warnings for `127.0.0.1`.
  - `PLAYWRIGHT_SKIP_WEB_SERVER=1` remains available for externally managed stacks.
- Repaired E2E command wiring:
  - `make frontend-e2e`
  - `make frontend-e2e-smoke`
  - `make frontend-e2e-mocked`
  now run `pnpm exec playwright test` from the repository root, where `tests/e2e/` actually lives.
- Repaired `.github/workflows/frontend-e2e.yml` to install root and frontend dependencies, then run `pnpm exec playwright test` from the repo root.
- Repaired `.github/workflows/e2e.yml` to use the root lockfile and `pnpm exec playwright`.
- Added unit smoke coverage proving deterministic lesson generation preserves supported language codes: `en`, `zu`, `af`, `xh`.

## Current Verification

```text
pnpm install --frozen-lockfile
# passed

cd app/frontend && pnpm install --frozen-lockfile
# passed

cd app/frontend && pnpm run env-check
# Frontend environment exposure OK

cd app/frontend && pnpm run lint
# passed with 75 warnings, 0 errors

cd app/frontend && pnpm run a11y-check
# 1 file, 6 tests passed

cd app/frontend && pnpm run type-check
# passed

cd app/frontend && pnpm run test -- --run
# 43 files, 147 tests passed

cd app/frontend && pnpm run build
# passed; service worker bundled

python3 -m py_compile locust/locustfile.py
# passed

make frontend-e2e-env-contract-check frontend-e2e-runtime-command-check frontend-e2e-opt-in-workflow-check frontend-playwright-scaffold-check frontend-playwright-specs-check frontend-playwright-mocked-specs-check frontend-playwright-mock-helper-check frontend-mock-api-fixture-check frontend-journey-fixture-check accessibility-pwa-e2e-check
# passed

python3 -m pytest --no-cov -q tests/unit/test_frontend_e2e_opt_in_workflow.py
# 8 passed

make frontend-e2e-mocked
# 20 passed across chromium, firefox, webkit, Mobile Chrome, Mobile Safari

make frontend-e2e-smoke
# 10 passed across chromium, firefox, webkit, Mobile Chrome, Mobile Safari

python3 -m pytest --no-cov -q tests/unit/test_content_generation_executor.py tests/unit/test_content_generation_provider_factory.py tests/unit/test_lesson_service_v2.py
# 20 passed
```

## Acceptance Criteria Status

| Criterion | Current evidence | Verdict |
|---|---|---|
| Playwright E2E suite runs locally | Mocked and smoke E2E targets pass across all configured projects | Pass for scaffold/smoke; full backend-backed suite still pending |
| Playwright CI job exists | `.github/workflows/e2e.yml` repaired to use root lockfile and `pnpm exec playwright` | Static pass; live Actions run pending |
| E2E docs exist | `docs/development/e2e_testing.md` | Pass after command refresh |
| Content expansion roadmap exists | `docs/caps/content_expansion_roadmap.md` | Pass |
| Locust scenario exists | `locust/locustfile.py` compiles | Pass for scaffold; live load run pending |
| A11y assertions/checks exist | `pnpm run a11y-check` passes 6 tests; static evidence gates pass | Pass for contract checks; Lighthouse score pending |
| PWA offline behavior documented | `docs/development/pwa_offline_plan.md`; build bundles service worker; offline sync tests included in 147 frontend tests | Partial; full cached-lesson offline browser proof pending |
| Multilingual lesson generation smoke | Deterministic provider generates one lesson per `en`, `zu`, `af`, `xh` | Pass for mock/fixture smoke; native-speaker quality review pending |
| Supabase ADR exists | `docs/adr/ADR-029-supabase-auth-strategy.md` | Pass |

## Remaining Limits

- No live GitHub Actions run was captured in this audit turn.
- Full backend-backed E2E suite was not run because it requires the complete backend/database stack and seeded data.
- Lighthouse numeric accessibility/PWA score remains uncaptured.
- PWA cached-lesson behavior still needs browser proof with a real cached lesson.
- Afrikaans and isiXhosa language quality still needs human/native-speaker review.
