# Project Status

This page summarizes the verified repository state as of **2026-05-08**.

## Current Verified Baseline

EduBoost V2 is in a **production-readiness implementation phase**, not a public-beta-ready state.

The current PR-002R work establishes the backend runtime and API contract baseline:

- Canonical production branch: `master`.
- Canonical backend runtime: `app.api_v2:app`.
- Freshness marker for the baseline that started this work: `Merge pull request #52 from NkgoloL/chore/slow-query-logging`.
- The V2 runtime imports cleanly from `app.api_v2:app`.
- Production routers are registered under both `/api/v2` and `/v2`.
- `system.router` is registered under both supported V2 prefixes.
- The legacy V1 lesson-generation compatibility route is excluded from the canonical `app.api_v2:app` route surface.
- Canonical response helpers now exist for V2 success, error, and paginated envelopes.
- Global exception handlers emit the V2 error envelope.
- `docs/openapi.json` is generated from `app.api_v2:app`.
- `make openapi-check` verifies the committed OpenAPI schema has not drifted.
- The OpenAPI drift workflow targets `master` and `release/**`, not `main`.

## Claim Discipline

Do not describe the repository as production-ready until the release-blocker checklist is complete.

Claims must be phrased according to evidence:

| Claim type | Meaning |
| --- | --- |
| `implemented` | Source code exists. |
| `tested` | Targeted tests pass locally or in CI. |
| `CI verified` | Required workflow passed on the relevant branch or PR. |
| `staging verified` | Evidence exists from the staging environment. |
| `production verified` | Evidence exists from the production environment. |
| `planned` | Work is accepted but not implemented. |
| `blocked` | Work cannot proceed without an explicit blocker being resolved. |

## Compatibility Boundary

EduBoost is V2-first, but not every historical surface has disappeared:

- Archived legacy code is kept under `app/legacy`.
- `app.legacy.api.main:app` is retained as a compatibility shim.
- The legacy shim may expose a 410 Gone response for `/api/v1/lessons/generate` when explicitly imported.
- The canonical production runtime remains `app.api_v2:app`.
- Legacy compatibility routes must not appear in the canonical V2 OpenAPI schema.

## Remaining Release Blockers

The following categories remain release blockers before real learner data or public beta use:

- Security and object-level authorization.
- POPIA consent enforcement and negative tests.
- Data-subject rights workflows.
- Audit integrity and audit-chain verification.
- Database migration proof from an empty database.
- Backup/restore drill evidence.
- AI prompt PII safety, lesson validators, and CAPS validation.
- Diagnostic item-bank and IRT validation.
- Frontend API-envelope adoption and learner/guardian journeys.
- Staging acceptance evidence.
- Incident response and release evidence bundle.

## Evidence Documents

- [`docs/security/authorization_dependencies.md`](security/authorization_dependencies.md)
- [`docs/security/object_authorization.md`](security/object_authorization.md)
- [`docs/testing/pr002r_evidence_check.md`](testing/pr002r_evidence_check.md)
- [`docs/testing/pytest_import_path.md`](testing/pytest_import_path.md)
- [`docs/release/PR-002R_EVIDENCE.md`](release/PR-002R_EVIDENCE.md)
- [`docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md`](pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md)
- [`docs/route_inventory.md`](route_inventory.md)
- [`docs/error_contract.md`](error_contract.md)
- [`docs/api_versioning_policy.md`](api_versioning_policy.md)
- [`PR_INTEGRATION_SUMMARY.md`](/PR_INTEGRATION_SUMMARY.md)

## Audit Tracker

The root [`TODO.md`](/TODO.md) remains the live production-readiness backlog.
