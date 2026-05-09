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

- [`docs/security/study_plan_authorization_wiring.md`](security/study_plan_authorization_wiring.md)
- [`docs/security/learner_mastery_authorization_wiring.md`](security/learner_mastery_authorization_wiring.md)
- [`docs/security/learner_read_authorization_http_tests.md`](security/learner_read_authorization_http_tests.md)
- [`docs/security/learner_route_authorization_wiring.md`](security/learner_route_authorization_wiring.md)
- [`docs/security/learner_route_authorization_inspection.md`](security/learner_route_authorization_inspection.md)
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

## Lesson Generation Authorization

- [`docs/security/lesson_generation_authorization_wiring.md`](security/lesson_generation_authorization_wiring.md)

## Diagnostic Items Authorization

- [`docs/security/diagnostic_items_authorization_wiring.md`](security/diagnostic_items_authorization_wiring.md)

## Phase 2 Authorization Evidence

- [`docs/security/phase2_authorization_evidence_check.md`](security/phase2_authorization_evidence_check.md)

## Diagnostic Submit Authorization

- [`docs/security/diagnostic_submit_authorization_wiring.md`](security/diagnostic_submit_authorization_wiring.md)

## POPIA Data Export Authorization

- [`docs/security/popia_data_export_authorization_wiring.md`](security/popia_data_export_authorization_wiring.md)

## Parent Progress Authorization

- [`docs/security/parent_progress_authorization_wiring.md`](security/parent_progress_authorization_wiring.md)

## POPIA Deletion Request Authorization

- [`docs/security/popia_deletion_request_authorization_wiring.md`](security/popia_deletion_request_authorization_wiring.md)

## POPIA Deletion Cancel Authorization

- [`docs/security/popia_deletion_cancel_authorization_wiring.md`](security/popia_deletion_cancel_authorization_wiring.md)

## POPIA Correction Request Authorization

- [`docs/security/popia_correction_request_authorization_wiring.md`](security/popia_correction_request_authorization_wiring.md)

## POPIA Restriction Request Authorization

- [`docs/security/popia_restriction_request_authorization_wiring.md`](security/popia_restriction_request_authorization_wiring.md)

## POPIA Deletion Status Authorization

- [`docs/security/popia_deletion_status_authorization_wiring.md`](security/popia_deletion_status_authorization_wiring.md)

## Parent Erasure Authorization

- [`docs/security/parent_erasure_authorization_wiring.md`](security/parent_erasure_authorization_wiring.md)

## POPIA Deletion Execute Authorization

- [`docs/security/popia_deletion_execute_authorization_wiring.md`](security/popia_deletion_execute_authorization_wiring.md)

## Parent Export Authorization

- [`docs/security/parent_export_authorization_wiring.md`](security/parent_export_authorization_wiring.md)

## Consent Status Authorization

- [`docs/security/consent_status_authorization_wiring.md`](security/consent_status_authorization_wiring.md)

## Parent Trust Dashboard Authorization

- [`docs/security/parent_trust_dashboard_authorization_wiring.md`](security/parent_trust_dashboard_authorization_wiring.md)

## Parent Dashboard Authorization

- [`docs/security/parent_dashboard_authorization_wiring.md`](security/parent_dashboard_authorization_wiring.md)

## Consent Grant Authorization

- [`docs/security/consent_grant_authorization_wiring.md`](security/consent_grant_authorization_wiring.md)

## Consent Revoke Authorization

- [`docs/security/consent_revoke_authorization_wiring.md`](security/consent_revoke_authorization_wiring.md)

## Gamification Profile Authorization

- [`docs/security/gamification_profile_authorization_wiring.md`](security/gamification_profile_authorization_wiring.md)

## Gamification Award XP Authorization

- [`docs/security/gamification_award_xp_authorization_wiring.md`](security/gamification_award_xp_authorization_wiring.md)

## Lesson Stream Authorization

- [`docs/security/lesson_stream_authorization_wiring.md`](security/lesson_stream_authorization_wiring.md)

## Assessment Attempt Authorization

- [`docs/security/assessment_attempt_authorization_wiring.md`](security/assessment_attempt_authorization_wiring.md)

## Onboarding Authorization

- [`docs/security/onboarding_authorization_wiring.md`](security/onboarding_authorization_wiring.md)

## Assessment List Authentication Boundary

- [`docs/security/assessment_list_auth_boundary.md`](security/assessment_list_auth_boundary.md)

## Onboarding Questions Authentication Boundary

- [`docs/security/onboarding_questions_auth_boundary.md`](security/onboarding_questions_auth_boundary.md)

## Assessment Attempt Model Contract

- [`docs/security/assessment_attempt_model_contract.md`](security/assessment_attempt_model_contract.md)

## Phase 2 Router Import Smoke

- [`docs/security/phase2_router_import_smoke.md`](security/phase2_router_import_smoke.md)

## Learner Authorization Matrix

- [`docs/security/learner_authz_matrix.md`](security/learner_authz_matrix.md)

## Learner Authorization Coverage Check

- [`docs/security/learner_authz_coverage_check.md`](security/learner_authz_coverage_check.md)

## Learner Authorization Coverage CI

- [`docs/security/learner_authz_ci.md`](security/learner_authz_ci.md)

## Phase 2 Authorization Closure Report

- [`docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`](security/PHASE2_AUTHORIZATION_CLOSURE.md)

## Phase 2 Authorization Closure Check

- [`docs/security/phase2_authorization_closure_check.md`](security/phase2_authorization_closure_check.md)

## Dev Session Environment Gate

- [`docs/security/dev_session_environment_gate.md`](security/dev_session_environment_gate.md)

## Consent Renewal Admin Authorization Boundary

- [`docs/security/consent_renewal_admin_auth_boundary.md`](security/consent_renewal_admin_auth_boundary.md)

## Ether Onboarding Questions Authentication Boundary

- [`docs/security/ether_onboarding_questions_auth_boundary.md`](security/ether_onboarding_questions_auth_boundary.md)

## Operational Auth Boundaries

- [`docs/security/operational_auth_boundaries.md`](security/operational_auth_boundaries.md)

## POPIA Consent and Audit Baseline

- [`docs/security/POPIA_CONSENT_AUDIT_BASELINE.md`](security/POPIA_CONSENT_AUDIT_BASELINE.md)
