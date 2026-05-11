# EduBoost V2 Current State

Date: 2026-05-11
Canonical current-state document: yes

This file is the single source of truth for current project status. Historical
reports, PR summaries, integration reports, and cluster evidence documents are
inputs, not release truth, unless this file points to their green evidence.

## Status Summary

EduBoost V2 is in production-readiness implementation. It is not yet
public-beta-ready and must not be described as production-ready.

The codebase contains a substantial V2 implementation: FastAPI backend, Next.js
frontend, PostgreSQL/Redis integration, POPIA/data-rights routes, diagnostics,
lesson generation scaffolding, billing routes, Prometheus metrics, Docker
Compose assets, governance scripts, and release-evidence documents.

The current verified truth is narrower: only the checks listed under
"Verified by green runtime/CI evidence" may be used as readiness claims.

## Implemented In Code

- Canonical backend runtime: `app.api_v2:app`.
- Compatibility shim: `app.legacy.api.main:app`.
- V2 routers are registered under `/api/v2` and `/v2`.
- Operational routes exist: `/`, `/health`, `/ready`, `/metrics`,
  `/v2/health/deep`, `/docs`, `/redoc`, and `/openapi.json`.
- Readiness code checks required secrets, PostgreSQL, Redis, migrations, and
  audit repository as critical dependencies.
- Optional LLM/judiciary checks may degrade readiness but do not block process
  liveness.
- Prometheus metrics are exposed for HTTP, LLM, diagnostic/item-bank, learner,
  consent, database, Redis, readiness, audit write failures, backup, and job
  surfaces.
- `scripts/check_runtime_entrypoints.py` and `make runtime-check` exist.
- `scripts/generate_openapi.py`, `make openapi`, and `make openapi-check`
  exist.
- Governance and evidence checks exist for release-readiness contracts, POPIA
  consent boundaries, route inventories, and PR-002R evidence.
- Repository provenance verification exists through
  `scripts/verify_repo_state.py`, `make verify-repo-state`, and the
  `.github/workflows/repo-state.yml` workflow.
- Grade 4 Mathematics item-bank implementation exists with 14 approved starter
  items plus generated candidate content that still requires approval before
  production coverage can be claimed.

## Verified By Green Runtime/CI Evidence

These checks passed locally on 2026-05-11 for the documentation-drift
correction commit:

- `make runtime-check`
- `make openapi-check`
- `pytest tests/smoke tests/test_entrypoints.py tests/test_health_checks.py -q --no-cov`
  with 35 passed and 4 skipped.
- YAML parsing for every `.github/workflows/*.yml` with PyYAML.
- `make beta-release-readiness-contract-check`, scoped to documentation
  contract wording only.
- `pytest tests/unit/test_verify_repo_state.py -q --no-cov` validates the
  repo-state checker contract.

These checks still require fresh verification before release promotion:

- Frontend install/test/build checks from `app/frontend`
- Migration checks against a disposable PostgreSQL database
- Backup and restore dry-run checks
- Staging smoke evidence

Any document that claims beta or production readiness must include the exact
passing command output or CI run URL for release-relevant checks.

## Not Yet Verified As Release-Ready

- Public beta launch.
- Production launch.
- 80% backend or frontend coverage.
- Staging deployment.
- Production CORS and security-header behavior.
- Backup/restore drill in a separate environment.
- Full frontend journey and Playwright verification.
- Full POPIA negative-path and data-rights verification.
- Full item-bank production coverage.
- Production billing/email/LLM provider readiness.

## Documentation Rules

- Use "implemented in code" when files exist but checks have not passed.
- Use "verified" only when a named local command, CI job, staging run, or
  release-evidence artifact passed for the current commit.
- Use "historical snapshot" for dated reports that describe an older branch,
  older commit, or integration event.
- Do not use "ready for staging", "beta-ready", "production-ready",
  "implemented and tested", or "complete" without a green evidence reference.

## Historical Snapshot Documents

These documents are retained for traceability but are not current-state truth:

- `EduBoost_Technical_Status_Report.md`
- `INTEGRATION_COMPLETE.md`
- `PR_INTEGRATION_SUMMARY.md`
- Cluster closure and release evidence files under `docs/operations/`
- Archived audit and roadmap files under `audits/`

## Live Backlog

The live implementation backlog is `TODO.md`. It must use the evidence-category
rule from this file: implemented code and verified evidence are separate.
