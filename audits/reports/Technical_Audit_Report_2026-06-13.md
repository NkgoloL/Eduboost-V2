# EduBoost V2 Technical Audit Report

Generated: 2026-06-13  
Workspace audited: `/home/nkgolol/Dev/Development/Eduboost-V2`  
Branch observed: `master...origin/master`  
Audit mode: static source review, local WSL verification, targeted runtime reproduction, and CI/deployment review.

## Executive Summary

EduBoost V2 is a substantial modular monolith with a FastAPI backend, Next.js frontend, PostgreSQL/Alembic persistence, Redis-backed sessions/jobs, Content Factory curriculum tooling, and extensive governance/evidence automation. The project has several strong foundations: the canonical FastAPI runtime imports, Alembic has a single head, selected Python syntax/static gates pass, import-boundary contracts are kept, security/privacy documentation gates exist, and frontend TypeScript plus Vitest checks are currently green locally.

The repository is not release-ready as checked out. The broad backend fast gate fails with 89 failing unit tests, mostly because the authoritative Content Factory registry files are required by runtime code but `data/content_factory/` is absent and gitignored. POPIA data-rights endpoints have a confirmed runtime failure because the router injects `AuthContext` while the service calls `current_user.get(...)`. The frontend data-rights client points at route aliases that the active backend router does not expose. The main CI workflow has a duplicate `schema-drift` job id and uses `npm ci` against a pnpm frontend with no `package-lock.json`, so CI is likely brittle or broken even before product tests run.

Priority should be: restore or relocate the Content Factory registry artifacts, fix POPIA auth-context normalization and route aliases, repair CI package-manager/job definitions, regenerate or intentionally reconcile OpenAPI drift, then rerun full backend, frontend, migration, and E2E gates.

## Scope and Method

The audit covered:

- Repository structure, stack, entrypoints, and dependency layout.
- Backend runtime wiring, authentication, authorization, POPIA, billing, diagnostics, lessons, and Content Factory surfaces.
- Database migration graph and schema integrity scripts.
- Frontend package/tooling, API client contract, environment checks, type-checking, and unit tests.
- Docker Compose, Dockerfiles, GitHub Actions, security scans, and deployment-related scripts.
- Existing reports and docs as context, but findings below are based on current source and local verification.

Limitation: the project skill points to the canonical remote workspace at `azureuser@135.119.52.214:~/Dev/Eduboost-V2`, but SSH timed out on port 22. I therefore audited the mounted WSL workspace provided by the Codex app.

## Repository Snapshot

- Tracked files: 4,217.
- Main line count across tracked `.py`, `.ts`, `.tsx`, `.js`, `.md`, `.yml`, `.yaml`, and `.json`: about 114,527 lines.
- Backend application Python files under `app`: 335.
- Backend test files matching `tests/**/test_*.py`: 724.
- Frontend test files under `app/frontend`: 395.
- Playwright E2E specs under `tests/e2e`: 14.
- Alembic revision files: 34.
- GitHub Actions workflow files: 44.
- Worktree note: the checkout was already dirty with many generated documentation/evidence files before this report was added. A test run also produced `logs/seed_run_20260613_134910.json`.

## Architecture Overview

### Backend

The active backend entrypoint is `app/api_v2.py`. It configures FastAPI, request logging/timing/id middleware, security headers, CORS, rate limiting, health/readiness, Prometheus metrics, and registers routers under both `/api/v2` and `/v2`.

Core backend layers:

- `app/api_v2_routers/`: HTTP route layer.
- `app/api_v2_deps/`: dependency adapters for auth, runtime repositories, POPIA lifecycle, and route wiring.
- `app/services/`: application workflows, Content Factory, auth lifecycle, POPIA, billing, lessons, diagnostics, and operational proof helpers.
- `app/repositories/`: SQLAlchemy persistence adapters.
- `app/domain/`: schemas and domain contracts.
- `app/modules/`: bounded modules for lessons, diagnostics, practice, consent, jobs, progress, and auth.
- `app/security/`: object-level authorization dependencies and policy helpers.

Strengths:

- Runtime entrypoint import passes: `app.api_v2:app` reports route count 347.
- Admin Content Factory router is protected at router level with `Depends(require_admin)`.
- Learner/diagnostic/lesson paths generally apply object-level authorization and active-consent gates.
- JWT helper includes `kid` support and production placeholder-secret checks.
- Security headers middleware sets CSP, frame denial, nosniff, referrer policy, permissions policy, and production HSTS.
- Import-linter contracts are green.

Concerns:

- Authentication code is duplicated across `app/core/security.py`, `app/core/token_config.py`, `app/services/auth_lifecycle_impl.py`, and legacy-compatible `app/services/auth_service.py`.
- Several routers still use compatibility imports and dict-style auth dependencies alongside `AuthContext`.
- Some service methods are test-oriented or generated/migration-era and increase maintenance risk.

### Frontend

The frontend lives in `app/frontend` and declares `pnpm@9.14.4`, Next.js, React, Vitest, TypeScript, Serwist PWA support, shadcn/Radix UI components, and API service clients.

Strengths:

- `npm run type-check` passes locally.
- `npm run test -- --run` passes locally: 43 files, 147 tests.
- Frontend has accessibility, route, tutor, voice, offline sync, and API-layer tests.

Concerns:

- Main CI uses npm even though the app declares pnpm and only has `pnpm-lock.yaml`.
- `npm run lint` fails locally because `next lint --no-cache` is not accepted by the installed Next CLI.
- `npm run env-check` fails locally because the script calls `python`, which is not available in this WSL environment.
- Frontend data-rights routes do not match the active backend POPIA router.

### Data and Migrations

Alembic is configured and has a single head:

- `alembic heads`: `20260609_0800_practice_sessions (head)`.
- `scripts/verify_migration_graph.py`: pass.
- `scripts/validate_schema_integrity.py`: pass.

The largest data risk is outside Alembic: Content Factory registry files are runtime inputs but are missing from the checkout.

## Verification Evidence

| Check | Result | Notes |
| --- | --- | --- |
| SSH to canonical remote | Fail | `ssh: connect to host 135.119.52.214 port 22: Connection timed out`; audited WSL workspace instead. |
| `python -m compileall -q app scripts` | Pass | Python source compiles. |
| `ruff check app tests scripts --select E9,F63,F7,F82,F821` | Pass | Release-blocking syntax/name checks pass. |
| `scripts/verify_migration_graph.py` | Pass | 34 revisions, single head. |
| `scripts/validate_schema_integrity.py` | Pass | Schema integrity OK. |
| `alembic heads` | Pass | Single head: `20260609_0800_practice_sessions`. |
| Focused backend tests | Pass with warnings | 38 passed; POPIA tests emitted unawaited `AsyncMock` warnings. |
| POPIA `AuthContext` reproduction | Fail confirmed | `AttributeError: 'AuthContext' object has no attribute 'get'`. |
| `make test-fast` | Fail | 89 failed, 2056 passed, 12 skipped, 1 xfailed. Major cluster: missing `data/content_factory/scopes.json`. |
| `lint-imports` | Pass | 3 contracts kept, 0 broken. |
| Runtime entrypoint check | Pass | `app.api_v2:app` and legacy shim import. |
| `generate_openapi.py --check` | Fail | OpenAPI drift detected. |
| Environment security contract | Pass | Config and Key Vault contract checks pass. |
| Privacy boundary evidence check | Pass | Required docs/scripts/check wiring present. |
| Frontend type-check | Pass | `tsc --noEmit` passes. |
| Frontend Vitest | Pass with warnings | 43 files, 147 tests passed; React `act(...)` warnings remain. |
| Frontend env-check | Fail | `python: not found`. |
| Frontend lint | Fail | `next lint --no-cache`: unknown option. |

## Critical and High Findings

### 1. Backend fast gate is red because required Content Factory registry files are missing

Severity: Critical  
Evidence:

- `make test-fast`: 89 failed, 2056 passed, 12 skipped, 1 xfailed.
- Repeated exception: `FileNotFoundError: data/content_factory/scopes.json`.
- Runtime registry defaults to `data/content_factory/scopes.json` and `coverage_targets.json` in `app/services/content_scope_registry.py:11-13`.
- The registry is read directly without fallback in `app/services/content_scope_registry.py:31-42`.
- `.gitignore:51-56` ignores `data/content_factory/`.
- `find` found no checked-out `data/content_factory/scopes.json` or `coverage_targets.json`.

Impact:

- Content Factory APIs, launch content seeding, coverage reports, staging readiness, generated lesson quality checks, item-bank readiness, and many CI/unit tests cannot run from a clean checkout.
- Release evidence cannot be trusted if required runtime data lives only on an untracked local disk.

Recommended remediation:

- Decide whether `data/content_factory/scopes.json` and `data/content_factory/coverage_targets.json` are source-controlled product configuration or generated artifacts.
- If source-controlled: unignore just the required registry files and commit them with deterministic generation provenance.
- If generated: add a deterministic bootstrap step to `make test-fast`, CI, Docker builds, and local setup; fail with a clear setup message if generation is skipped.
- Add a small startup/CI preflight that checks both files before importing Content Factory services.

### 2. POPIA data-rights endpoints fail with injected `AuthContext`

Severity: Critical  
Evidence:

- POPIA router injects `current_user: Any = Depends(require_auth_context)` and passes it directly to `POPIADataRightsService` in `app/api_v2_routers/popia.py:172-248`.
- `POPIADataRightsService` methods call `current_user.get(...)` in `app/services/popia_service.py:99-140`, `213-217`, `263-307`, and `329-332`.
- Direct reproduction with an `AuthContext` raised: `AttributeError: 'AuthContext' object has no attribute 'get'`.

Impact:

- Authenticated export, erasure, cancellation, correction, restriction, and erasure execution paths can fail with 500-class behavior before authorization/persistence is reached.
- These are POPIA-critical workflows, so failure affects compliance posture and user trust.

Recommended remediation:

- Normalize actor access in one helper, for example `actor_id_from_current_user` plus role extraction that accepts both `AuthContext` and `dict`.
- Update `POPIADataRightsService` type hints to accept `dict[str, Any] | AuthContext`, or convert to `current_user.raw_claims` at the router boundary consistently.
- Add regression tests that call the actual FastAPI router with real `require_auth_context` semantics, not only mocked dict claims.

### 3. Frontend data-rights client points to routes the backend does not expose

Severity: High  
Evidence:

- Frontend calls `/popia/data-export/{learnerId}`, `/popia/deletion-request/{learnerId}`, `/popia/deletion-cancel/{learnerId}`, `/popia/restriction-request/{learnerId}`, and `/popia/deletion-status/{learnerId}` in `app/frontend/src/lib/api/services.ts:159-173`.
- Active backend POPIA router exposes `/popia/exports`, `/popia/erasure`, `/popia/erasure/{learner_id}/cancel`, `/popia/correction`, and `/popia/restriction` in `app/api_v2_routers/popia.py:172-248`.
- Parent dashboard export URLs still emit `/api/v2/popia/data-export/{learner.id}` in `app/api_v2_routers/parents.py`.

Impact:

- Parent dashboard privacy actions can 404 even after the `AuthContext` service bug is fixed.
- Frontend tests currently mock API calls and do not prove backend route compatibility.

Recommended remediation:

- Either add backend aliases for the frontend route contract or update frontend calls and parent-export URLs to the canonical backend routes.
- Add an OpenAPI-driven frontend route-contract test that fails when client service paths are not present in backend OpenAPI.

### 4. Main CI workflow is internally inconsistent and likely brittle

Severity: High  
Evidence:

- Duplicate `schema-drift` job id appears at `.github/workflows/ci-cd.yml:71` and `.github/workflows/ci-cd.yml:443`.
- Frontend package declares `pnpm@9.14.4` in `app/frontend/package.json:5-8`.
- `ci-cd.yml` frontend job uses npm cache and `app/frontend/package-lock.json`, then runs `npm ci` in `.github/workflows/ci-cd.yml:389-396`.
- The checkout has `app/frontend/pnpm-lock.yaml` and no `package-lock.json`.
- E2E job runs root-level `npm ci` in `.github/workflows/ci-cd.yml:428-433`; no root lockfile was found.

Impact:

- CI can fail before running tests, or silently skip/overwrite one schema-drift job depending on YAML parsing behavior.
- Production promotion `needs` can reference an ambiguous or overwritten job.

Recommended remediation:

- Rename one schema job id, for example `schema-integrity` and `schema-drift-live`.
- Convert frontend and E2E jobs to pnpm with `pnpm/action-setup`, `cache: pnpm`, and `app/frontend/pnpm-lock.yaml`.
- If root Playwright dependencies are intentional, add a root lockfile and package manifest that reflect that; otherwise run Playwright from `app/frontend` or the proper package directory.

### 5. OpenAPI contract is stale

Severity: High  
Evidence:

- `python scripts/generate_openapi.py --check` failed with: `OpenAPI drift detected: regenerate docs/openapi.json`.

Impact:

- Generated API docs, client contract checks, and route compatibility decisions may be based on stale data.
- This compounds the frontend/backend POPIA route mismatch.

Recommended remediation:

- Regenerate `docs/openapi.json` after fixing route contracts.
- Add OpenAPI drift to the same required CI path as frontend API contract tests.

### 6. Frontend lint and env-check scripts do not match the installed toolchain

Severity: High  
Evidence:

- `npm run env-check` fails: `sh: 1: python: not found`.
- `npm run lint` fails: `error: unknown option '--no-cache'`.
- Scripts are defined in `app/frontend/package.json:14-18`.

Impact:

- Frontend CI can be red even though type-check and Vitest are green.
- Local developers may skip lint/env validation because the commands are not runnable.

Recommended remediation:

- Change `env-check` to use an explicit interpreter path available in CI and dev, for example `python3` or a repo-level `make frontend-env-check`.
- Replace `next lint --no-cache` with a supported lint command for the installed Next/ESLint stack.
- Align the CI frontend job with the package manager before revalidating.

### 7. Dependency scanning workflow warns but does not fail on vulnerabilities

Severity: High  
Evidence:

- Python audit command suppresses failure with `|| true` in `.github/workflows/dependency-scan.yml:49-60`.
- pnpm audit also suppresses failure with `|| true` in `.github/workflows/dependency-scan.yml:95-106`.
- The SARIF upload step references `steps.publish.outputs.result_url`, but no `publish` step exists in `.github/workflows/dependency-scan.yml:62-69`.

Impact:

- Dependency scan results can appear as warnings rather than release-blocking failures.
- Security upload may be ineffective or broken, reducing visibility.

Recommended remediation:

- Define severity thresholds and fail on at least critical/high production vulnerabilities.
- Remove or justify `|| true`.
- Replace the upload step with a supported CodeQL/SARIF path or upload artifacts explicitly.

## Medium Findings

### 8. Authentication implementation is split across multiple active and compatibility paths

Severity: Medium  
Evidence:

- Active token creation in `app/core/security.py:57-68` includes `type=access`.
- Separate `app/core/token_config.py:109-127` creates access tokens without the same `type` claim.
- `app/services/auth_application_service.py:9-39` performs dynamic repository candidate resolution and delegates lifecycle methods in `app/services/auth_application_service.py:292-311`.
- `app/services/auth_service.py` retains legacy compatibility methods and monkey-patches `AuthService` at `app/services/auth_service.py:455-514`.

Impact:

- Auth behavior is harder to reason about and easier to regress.
- Tests can pass through compatibility paths while production paths drift.

Recommended remediation:

- Declare one canonical auth lifecycle and token module.
- Mark legacy classes as test-only or move them under a legacy namespace.
- Add token contract tests that assert issued login/register/refresh tokens work against all protected route dependencies.

### 9. Billing checkout uses placeholder email for Stripe customer creation

Severity: Medium  
Evidence:

- Billing router passes `email_plaintext="billing-placeholder"` in `app/api_v2_routers/billing.py:23-28`.
- Stripe customer creation uses that email in `app/core/stripe_client.py:29-39`.

Impact:

- Stripe customer records can be created with unusable placeholder email data.
- Receipts, billing communications, reconciliation, and support workflows can be degraded.

Recommended remediation:

- Decrypt guardian email at the service boundary, or omit email intentionally and document the downstream effect.
- Add a test that checkout creates Stripe customers with real, normalized guardian email when available.

### 10. Frontend has a production-looking API fallback

Severity: Medium  
Evidence:

- `app/frontend/next.config.js:12-18` defaults missing `NEXT_PUBLIC_API_URL` to `https://eduboost-api.onrender.com/api/v2`.
- Other frontend env utilities default to localhost.

Impact:

- A build missing `NEXT_PUBLIC_API_URL` can unintentionally target a hosted backend instead of failing closed or using environment-specific configuration.

Recommended remediation:

- Require `NEXT_PUBLIC_API_URL` for production builds.
- Keep localhost fallback only for explicit development mode.

### 11. Release provenance is obscured by many generated dirty files

Severity: Medium  
Evidence:

- `git status --short` showed many modified generated files under `docs/architecture`, `docs/release`, and `docs/security` before this report was added.

Impact:

- It is hard to distinguish fresh audit output from preexisting evidence churn.
- Release signoff and PR review become noisy.

Recommended remediation:

- Separate generated evidence outputs from source docs, or require a single command to regenerate and verify them deterministically.
- Keep release evidence changes in dedicated commits.

### 12. Test warnings indicate async mock hygiene issues

Severity: Medium  
Evidence:

- Focused POPIA tests passed but emitted unawaited `AsyncMock` warnings in `app/services/popia_service.py`.
- Full backend fast gate also emitted multiple unawaited coroutine warnings.

Impact:

- Tests can pass while hiding incorrect async behavior.

Recommended remediation:

- Treat `RuntimeWarning: coroutine ... was never awaited` as an error in focused suites.
- Replace async mocks used for synchronous SQLAlchemy methods such as `db.add` with regular `Mock`.

## Strengths to Preserve

- Runtime entrypoint check passes for canonical and legacy app imports.
- Alembic graph is currently linear with a single head.
- Schema integrity script passes.
- Import-linter contracts are green and enforce meaningful router/repository boundaries.
- Environment security contract and privacy-boundary evidence checks pass.
- Admin Content Factory routes use router-level admin dependency.
- Learner, diagnostics, lesson, and consent routes show broad adoption of object-level authorization and active-consent checks.
- Frontend TypeScript and Vitest suites are healthy locally.
- Security headers and production secret/key-vault checks are present.

## Recommended Remediation Plan

### Immediate release blockers

1. Restore Content Factory registry availability.
   - Commit required registry JSON files or generate them deterministically during setup/CI.
   - Remove broad `data/content_factory/` ignore or add precise unignore rules.
   - Rerun `make test-fast`.

2. Fix POPIA `AuthContext` handling.
   - Normalize all service actor extraction through a shared helper.
   - Add real router tests for `/v2/popia/exports`, `/v2/popia/erasure`, `/v2/popia/erasure/{learner_id}/cancel`, `/v2/popia/correction`, and `/v2/popia/restriction`.

3. Reconcile frontend/backend data-rights routes.
   - Choose canonical route shapes.
   - Update frontend services and parent export URLs, or add backend compatibility aliases.
   - Add OpenAPI/client path verification.

4. Repair CI workflow mechanics.
   - Remove duplicate job id.
   - Use pnpm consistently for frontend and E2E.
   - Fix lint/env scripts.

5. Regenerate OpenAPI.
   - Run `python scripts/generate_openapi.py` after route changes.
   - Commit the updated `docs/openapi.json`.

### Next hardening pass

6. Simplify auth lifecycle ownership.
   - Retire or isolate legacy `AuthService` monkey patches.
   - Keep one token issuance/verification contract.

7. Fix dependency scan enforcement.
   - Fail on configured severity.
   - Repair upload/reporting.

8. Fix billing identity data.
   - Use decrypted guardian email or a documented no-email Stripe strategy.

9. Tighten frontend production environment validation.
   - Remove hosted fallback for production builds.

10. Make generated evidence reproducible.
    - Use one command for evidence regeneration.
    - Keep generated outputs out of routine dev churn unless explicitly refreshed.

## Suggested Verification Gate After Fixes

Run these before claiming release readiness:

```bash
.venv/bin/python -m compileall -q app scripts
.venv/bin/ruff check app tests scripts --select E9,F63,F7,F82,F821
.venv/bin/lint-imports
.venv/bin/python scripts/verify_migration_graph.py
.venv/bin/python scripts/validate_schema_integrity.py
.venv/bin/alembic heads
.venv/bin/python scripts/check_runtime_entrypoints.py
.venv/bin/python scripts/generate_openapi.py --check
make test-fast
cd app/frontend && pnpm run env-check
cd app/frontend && pnpm run lint
cd app/frontend && pnpm run type-check
cd app/frontend && pnpm run test
```

For full release confidence, add:

```bash
make test-integration
docker compose config
docker compose -f docker-compose.prod.yml config
pnpm exec playwright test
```

## Overall Assessment

EduBoost V2 has strong architectural intent and unusually rich governance scaffolding, but the current checkout has release-blocking contract drift. The most serious problems are not broad architectural absence; they are broken source-of-truth wiring: missing Content Factory registry data, POPIA service/router auth-shape mismatch, frontend/backend route drift, and CI package-manager drift. Fixing those should unlock a much clearer view of the remaining product and quality risks.

