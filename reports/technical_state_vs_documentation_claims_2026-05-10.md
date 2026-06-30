# EduBoost V2 Technical State vs Documentation Claims

Date: 2026-05-10
Audited commit: f57d6d1 docs: add cluster h post-merge release governance
Audit method: clean detached worktree at `/tmp/eduboost-v2-state-audit`, excluding the active dirty worktree changes on `codex/cluster-c-popia-consent-audi`.

## Executive summary

The repository is an active V2 FastAPI + Next.js modular-monolith codebase with a substantial amount of real implementation: 123 FastAPI routes, PostgreSQL/Redis-aware readiness code, Prometheus metrics, POPIA/data-rights routes, diagnostics, lessons, billing, frontend sources, Docker Compose assets, and many governance/evidence documents.

The true project state is not production-ready and not fully beta-release-ready. The most accurate top-level claim is the cautious README statement that production readiness still depends on remaining security, POPIA, CI/CD, backup/restore, AI-safety, frontend, staging, and release-evidence gates. Several other documents overclaim maturity by saying all major systems are implemented and tested, or that release gates are complete. Clean-HEAD verification contradicts those stronger claims.

## Evidence gathered

- Clean worktree created with `git worktree add --detach /tmp/eduboost-v2-state-audit HEAD`.
- Current active branch was not used for evidence because it contains uncommitted/untracked work.
- Imported `app.api_v2:app` successfully and counted 123 routes.
- Ran selected runtime tests:
  - `python -m pytest tests/test_entrypoints.py tests/test_health_checks.py -q --no-cov`: 15 passed, 4 skipped.
  - `python -m pytest tests/smoke tests/test_entrypoints.py tests/test_health_checks.py -q`: 4 failed, 31 passed, 4 skipped; coverage 36.13%, below the configured 80% gate.
- Ran project contract commands:
  - `make runtime-check`: failed because `scripts/check_runtime_entrypoints.py` is missing at `HEAD`.
  - `make openapi-check`: failed with OpenAPI drift.
  - `make beta-release-readiness-contract-check`: passed, but it only checks wording/evidence-document presence, not the runtime readiness gates themselves.
- Frontend test command from `app/frontend` failed locally because `vitest` was not installed in the clean worktree dependency set.
- Parsed GitHub workflow YAML with Python `yaml.safe_load`; `.github/workflows/db-backup-matrix.yml` failed to parse.

## Claim vs true state

| Area | Documentation claim | True state at clean HEAD | Assessment |
|---|---|---|---|
| Overall readiness | `EduBoost_Technical_Status_Report.md` says the project is in a "mature pre-production state" and that auth, consent, diagnostics, gamification, observability, CI/CD are "implemented and tested". | Smoke tests fail, coverage is 36.13%, OpenAPI drift exists, `runtime-check` is broken, at least one workflow is invalid. | Overclaimed. |
| README current state | README says production readiness still depends on remaining gates and warns not to claim beyond what checks prove. | This matches the evidence. | Mostly accurate. |
| Runtime entrypoint | Docs and Makefile refer to `make runtime-check` and `scripts/check_runtime_entrypoints.py`. | Make target exists, but the script is absent at clean `HEAD`; the active dirty worktree has it untracked, so it is not part of the audited committed state. | Broken at committed state. |
| Legacy shim | README links `app/api/main.py` as a compatibility shim. | No `app/api/main.py` exists. The actual shim is `app/legacy/api/main.py`. A smoke test still imports `app.api.main` and fails. | Stale documentation and stale test. |
| OpenAPI | TODO marks schema generation/publishing as done; workflow exists for OpenAPI drift. | `make openapi-check` reports drift and asks to regenerate `docs/openapi.json`. | Gate exists but is failing. |
| Coverage | README badge claims 80%+ coverage; TODO requires 80% backend coverage. | Selected smoke/runtime run reported total backend coverage of 36.13% and failed the 80% threshold. | Badge/status overclaims current verified state. |
| Release readiness | TODO marks non-negotiable production gate items complete; Cluster H docs assert release-readiness evidence. | Some checks are document-contract checks. Runtime/openapi/smoke evidence is not green. | Release evidence is ahead of runtime proof. |
| CI workflows | TODO says workflow inconsistencies are fixed and docs mention release blockers. | `.github/workflows/db-backup-matrix.yml` failed YAML parsing. Release workflow references `app/api/version.py`, which is absent. Several workflows use `requirements/dev.txt`, which exists, but some docs also mention root alias files. | CI/CD not fully trustworthy. |
| Frontend | Integration docs claim frontend core flows/accessibility complete and ready for staging validation. | Frontend sources and tests exist, but local clean-HEAD test execution was not verifiable without installing Node deps; workflow path assumptions are mixed (`frontend/` vs `app/frontend/`). | Partially implemented, not independently verified in this audit. |
| Readiness endpoint | TODO marks `/ready` dependency-aware behavior complete. | Code checks secrets, PostgreSQL, Redis, migrations, and audit repository as critical; optional LLM/judiciary degrade status. Targeted health tests passed. | Substantially true locally, subject to environment validation. |
| Docker Compose map | README lists `docker-compose.v2.yml` and `docker-compose.aca.yml`. | Only `docker-compose.yml` and `docker-compose.prod.yml` were present at clean `HEAD`. | README stale. |
| Production secrets | Docs claim Key Vault production path exists. | `app/core/config.py` requires Key Vault URL in production and fetches secrets; default dev placeholders still exist for local mode. | Implementation exists, production deployment unverified. |
| CAPS item bank | README says 14 approved starter items against 120 production target. | This is consistent with the cautious item-bank docs. | Accurate and appropriately scoped. |

## Key failing checks

### Backend smoke/runtime with coverage

Command:

```bash
python -m pytest tests/smoke tests/test_entrypoints.py tests/test_health_checks.py -q
```

Observed:

- 4 failed, 31 passed, 4 skipped.
- Coverage: 36.13%.
- Coverage gate failed: required 80%.

Notable failures:

- `tests/smoke/test_app_import.py::test_fastapi_app_imports` imports `app.api.main`, but that module is absent.
- `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_register_validates_email` expected 422, got 500.
- `tests/smoke/test_v2_smoke.py::TestConsentGate::test_lessons_endpoint_requires_auth` expected a protected route response, got 405.
- `tests/smoke/test_v2_smoke.py::TestErrorHandling::test_404_returns_json_error` expected 404, got 405.

### Runtime check

Command:

```bash
make runtime-check
```

Observed:

```text
python3: can't open file '/tmp/eduboost-v2-state-audit/scripts/check_runtime_entrypoints.py': [Errno 2] No such file or directory
```

### OpenAPI drift

Command:

```bash
make openapi-check
```

Observed:

```text
OpenAPI drift detected: regenerate /tmp/eduboost-v2-state-audit/docs/openapi.json with `python scripts/generate_openapi.py`.
```

### Workflow YAML

Python YAML parsing failed for:

```text
.github/workflows/db-backup-matrix.yml
```

Error:

```text
ScannerError mapping values are not allowed here
```

The problematic visible line is the unquoted `run: echo "Running scenario: ..."` command containing a colon.

## What is genuinely implemented

- `app/api_v2.py` is a real FastAPI app and imports successfully.
- The app exposes operational routes: `/`, `/health`, `/ready`, `/metrics`, `/docs`, `/redoc`, `/openapi.json`, `/v2/health/deep`.
- V2 routers are registered under both `/api/v2` and `/v2`.
- `app/legacy/api/main.py` reuses the canonical V2 app and adds a hidden 410 legacy route.
- Readiness checks include critical PostgreSQL, Redis, migrations, audit repository, and required-secret checks.
- Prometheus metrics exist for HTTP, LLM, IRT, item-bank coverage, learners, consent, DB, Redis, readiness, audit write failures, backups, and jobs.
- Docker Compose starts API, frontend, docs, PostgreSQL, Redis, Prometheus, Alertmanager, Grafana, and exporters.
- POPIA/data-rights route files and tests exist.
- Large volumes of governance, release, AI-safety, frontend, backup/restore, and evidence documentation exist.

## Main documentation drift

1. Some documents are honest about remaining work, especially `README.md`, `TODO.md` later milestone sections, and launch-scope docs.
2. Other documents read like completion certificates, especially `EduBoost_Technical_Status_Report.md`, `INTEGRATION_COMPLETE.md`, and parts of release-readiness evidence.
3. Evidence-contract tests often verify that documents contain required phrases. That is useful for governance, but it does not prove the product/runtime is deployable.
4. The docs are internally inconsistent: some sections say gates are done, while later TODO/milestone sections say beta/production prerequisites are still open.

## Risk assessment

| Risk | Severity | Why it matters |
|---|---|---|
| Release/readiness overclaim | High | A reader could believe the project is ready for staging or beta when basic clean-HEAD checks fail. |
| Broken runtime-check at committed state | High | Release evidence references a guard that does not exist in the committed tree. |
| OpenAPI drift | High | API docs/review artifacts are stale relative to the app. |
| Stale legacy import references | Medium | Tests/docs still point at removed `app.api.main` path. |
| Coverage badge mismatch | Medium | Public repo status claims are stronger than verified coverage. |
| Invalid workflow YAML | Medium | CI backup matrix cannot be trusted until syntax is fixed. |
| Document-contract checks mistaken for runtime checks | Medium | Governance tests can pass while runtime checks fail. |

## Recommended correction plan

1. Split documentation into two explicit categories:
   - "Implemented in code"
   - "Verified by green runtime/CI evidence"
2. Update `EduBoost_Technical_Status_Report.md` and `INTEGRATION_COMPLETE.md` to state that they are historical/integration snapshots, not current release truth.
3. Make `docs/project_status.md` or a new `docs/current_state.md` the single source of truth.
4. Commit or remove the `runtime-check` target. The committed state must not reference absent scripts.
5. Regenerate and commit `docs/openapi.json`, then keep `make openapi-check` green.
6. Fix stale legacy references:
   - Replace README `app/api/main.py` references with `app/legacy/api/main.py`, or add a real shim if that path is intentionally supported.
   - Update or remove `tests/smoke/test_app_import.py`.
7. Fix smoke failures before any release-readiness claim.
8. Replace static 80% coverage badge with a real CI-generated badge or remove it until the gate is green.
9. Validate every workflow with a YAML/GitHub Actions linter, starting with `db-backup-matrix.yml`.
10. Treat `beta-release-readiness-contract-check` as a docs-contract check, not a release go/no-go check, unless it also invokes runtime, OpenAPI, smoke, frontend, migration, backup/restore, and staging checks.

## Bottom line

The project is best described as a substantial pre-beta implementation with strong governance scaffolding and many real backend/frontend components, but with documentation and release evidence ahead of verified runtime truth. The safest public claim is:

> EduBoost V2 has an integrated V2 backend/frontend foundation and extensive production-hardening scaffolding. It is not yet production-ready or beta-release-ready until clean-HEAD smoke tests, OpenAPI drift, runtime contract checks, CI workflow validity, frontend verification, backup/restore evidence, and staging validation are green.
