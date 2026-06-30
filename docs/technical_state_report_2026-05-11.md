# EduBoost V2 Technical State Report

Date refreshed: 2026-05-11
Branch assessed: `master`
Latest merge assessed: `c9a69b2` (`Merge pull request #89 from NkgoloL/codex/cluster-c-popia-consent-audi`)
Runtime version observed: `1.0.0-rc1`

## Executive Summary

EduBoost V2 is in production-readiness hardening. It is not public-beta-ready
or production-ready yet, but the local `master` branch is materially ahead of
the earlier snapshot: the PR1 through PR16 evidence train has been merged into
`master`, the runtime/OpenAPI/route inventory checks are green, the migration
graph and schema-integrity checks now pass, and the POPIA consent-gate
inventory has no new unallowlisted findings.

The remaining release risk is no longer "the evidence branches are pending."
The risk is that many controls are still documentation or local-evidence gates
rather than fresh staging, legal, operational, data, and browser evidence
against a release candidate.

## Current Repository Truth

The current `master` first-parent history includes these recent production
readiness merges:

| PR | Branch | Scope |
| --- | --- | --- |
| #72 | `codex/pr1-repo-truth` | Repository governance and repo-state verification |
| #74 | `codex/pr2-runtime-contract` | Runtime contract, router registration, legacy exclusion, route inventory, OpenAPI |
| #75 | `codex/pr3-privacy-boundary` | Privacy-boundary evidence gate |
| #76 | `codex/pr4-persistence-resilience` | Persistence evidence gate and schema-integrity import fix |
| #77 | `codex/pr5-learning-evidence` | Learning evidence gate |
| #78 | `codex/pr6-api-envelope-error-contract` | API envelope and error-contract evidence |
| #79 | `codex/pr7-auth-boundary` | Auth/token/cookie/RBAC/object-auth evidence |
| #80 | `codex/pr8-popia-legal` | POPIA/legal evidence |
| #81 | `codex/pr9-db-repositories` | DB/repository evidence |
| #82 | `codex/pr10-backup-redis-dr` | Backup/Redis/DR evidence |
| #83 | `codex/pr11-ai-safety` | AI safety release evidence |
| #84 | `codex/pr12-caps-learning-proof` | CAPS/learning proof |
| #85 | `codex/pr13-frontend-journeys` | Frontend journey evidence |
| #86 | `codex/pr14-accessibility-pwa-e2e` | Accessibility/PWA/E2E evidence |
| #87 | `codex/pr15-cicd-staging` | CI/CD and staging evidence |
| #88 | `codex/pr16-observability-ops` | Observability/ops evidence |
| #89 | `codex/cluster-c-popia-consent-audi` | Cluster C POPIA/consent/audit continuation |

Current backlog counters from `TODO.md`:

- Checked `[x]`: 16
- Verification `[verify]`: 183
- Open `[ ]`: 1316
- Python test files under `tests`: 439

The repository contains:

- FastAPI V2 runtime: `app.api_v2:app`.
- Legacy compatibility shim: `app.legacy.api.main:app`.
- Canonical V2 routes mounted under `/api/v2` and `/v2`.
- Operational routes: `/`, `/health`, `/ready`, `/metrics`,
  `/v2/health/deep`, `/docs`, `/redoc`, and `/openapi.json`.
- Deterministic OpenAPI and route inventory generation.
- Runtime, repository-state, migration, POPIA, authorization, API-envelope,
  data-resilience, AI-safety, frontend, staging, observability, and release
  evidence checks.
- Grade 4 Mathematics item-bank work with 14 approved starter items plus
  generated candidate content that still needs human curriculum approval before
  production CAPS coverage can be claimed.

## Verified Locally On 2026-05-11

These checks passed in the WSL workspace:

```bash
make runtime-check openapi-check route-inventory-check beta-release-readiness-contract-check diagnostics-assessment-check
make migration-check
make popia-consent-gate-check
```

Observed results:

- `app.api_v2:app` imports with 143 routes.
- `app.legacy.api.main:app` imports with 144 routes because it explicitly adds
  the hidden legacy `410 Gone` compatibility route.
- OpenAPI and route inventory drift checks pass.
- Beta release readiness contract check passes as a documentation-contract
  check only; it is not a go/no-go release decision.
- Diagnostics assessment check passes, including 12 targeted diagnostics,
  mastery, and practice tests.
- Schema integrity passes.
- Migration graph passes with 19 revisions and head `20260510_0200`.
- POPIA consent-gate inventory reports 190 learner-related missing local
  consent markers, all covered by the baseline allowlist, with 0 new
  unallowlisted missing markers and 0 stale allowlist entries.

Focused legacy route tests were also run:

```bash
python3 -m pytest tests/test_legacy_route_exclusion.py tests/test_entrypoints.py tests/unit/test_generate_route_inventory.py -q
```

The assertions passed (`15 passed`), but the narrow test slice failed the
repository-wide coverage gate because total coverage for that slice was 35%,
below the configured 80% threshold. This is a coverage-scope issue for the
targeted command, not a failing assertion in the legacy route behavior.

## Architecture Assessment

### Backend Runtime And API

The backend runtime is coherent and testable. The canonical runtime is
`app.api_v2:app`; the archived legacy shim exists for compatibility and may
return `410 Gone` for `/api/v1/lessons/generate` only when the shim is imported
explicitly. The canonical OpenAPI schema and route inventory exclude V1 routes.

Remaining risks:

- Full router-by-router success-envelope proof is still incomplete.
- Abuse-path coverage for auth, RBAC, object authorization, and consent needs
  broader execution evidence.
- The legacy compatibility route must remain hidden from canonical OpenAPI and
  isolated from `app.api_v2:app`.

### Data And Persistence

Migration and schema tooling now pass locally. The repo contains migration graph
checks, schema integrity checks, repository evidence, backup/restore scripts,
and DR evidence documents.

Remaining risks:

- A disposable PostgreSQL migration run is still required before release.
- Backup/restore dry-run evidence must come from a separate environment.
- Transaction rollback and repository behavior are not yet proven for every
  sensitive workflow.

### Privacy, Security, And POPIA

POPIA, consent, audit, retention, data-rights, and authorization evidence is
substantial. The consent-gate inventory no longer reports new unallowlisted
findings.

Remaining risks:

- The current consent-gate state depends on an allowlist; release review still
  needs to decide which allowlisted learner-related functions are acceptable
  internal helpers and which should receive explicit local consent evidence.
- Legal documents still require external legal review and approval.
- Data-rights workflows need negative-path and staging evidence.
- Branch protection and release approval evidence is external to the repo.

### AI, CAPS, Diagnostics, And Learning

Diagnostics, IRT hardening, session lifecycle, mastery, practice, AI safety,
prompt/output contracts, and learning evidence gates are present. The targeted
diagnostics assessment check passes locally.

Remaining risks:

- Full CAPS coverage is not approved.
- Only 14 Grade 4 Mathematics starter items are approved.
- Generated candidate items cannot support production claims until reviewed and
  promoted.
- Live LLM provider safety, cost, refusal, and fallback behavior still requires
  environment-backed evidence.

### Frontend

The repo contains a Next.js frontend, API client, learner and parent journey
components, route guards, accessibility helpers, service worker/offline assets,
fixtures, and Playwright scaffolding.

Remaining risks:

- Frontend install/test/build evidence was not refreshed in this assessment.
- Browser E2E against staging is not verified.
- Real-device/mobile accessibility evidence is not present.

### Operations

The repo contains Prometheus, Grafana, Alertmanager, deployment runbooks,
staging gate docs, incident response docs, support model, beta monitoring, and
release evidence tooling.

Remaining risks:

- Staging deployment is not proven.
- Alert firing, dashboard screenshots, and incident tabletop evidence are
  missing.
- Rollback proof and final release evidence bundle are still absent.

## Overall Readiness Rating

Current status: production-readiness hardening, not public-beta-ready.

| Area | State |
| --- | --- |
| Backend runtime/API baseline | Mostly implemented; local runtime/OpenAPI/route checks pass |
| API envelope/error contract | Implemented as evidence gate; full router proof incomplete |
| Auth/object authorization | Substantial evidence; abuse-path and staging coverage incomplete |
| POPIA/consent/audit | Strong docs and gates; allowlist requires release review |
| Data/migrations/backup | Local migration/schema checks pass; live DB and restore evidence missing |
| AI/CAPS/diagnostics | Diagnostics check passes; item-bank approval and live AI evidence missing |
| Frontend | Implemented and documented; fresh build/E2E evidence missing |
| CI/CD/staging | Workflows/docs exist; live staging deployment missing |
| Observability/ops | Assets exist; live alert/dashboard/tabletop evidence missing |
| Release governance | Evidence gates exist; go/no-go package missing |

## Recommended Next PR Series

1. Release-candidate evidence sweep: rerun backend, frontend, OpenAPI, route
   inventory, migration, POPIA, and diagnostics checks from a clean branch and
   record exact outputs.
2. Frontend verification PR: fresh install, lint/typecheck/test/build, mocked
   Playwright, accessibility checks, and documented failures if any.
3. Database and resilience PR: disposable PostgreSQL migration run, backup,
   restore, Redis outage/recovery, and rollback evidence.
4. Privacy/legal PR: legal approval packet, POPIA negative paths, data export,
   erasure, correction, restriction, audit-chain verification, and consent
   allowlist review.
5. CAPS/AI safety PR: item-bank approval workflow, CAPS coverage claim cleanup,
   live provider safety/fallback/cost evidence, and educator review evidence.
6. Staging and operations PR: staging deploy, smoke tests, CORS/security
   headers, alert firing, dashboard screenshots, incident tabletop, rollback,
   and go/no-go record.

## Bottom Line

The earlier report understated the current state because it treated PR1 through
PR16 as pending. They are now merged. EduBoost V2 has a much stronger
production-readiness evidence foundation, and several previously reported local
failures now pass. The project should still be described as under production
hardening until release-candidate evidence exists for frontend, database,
backup/restore, staging, legal, privacy workflows, live AI behavior,
observability, rollback, and final go/no-go approval.
