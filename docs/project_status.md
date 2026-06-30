# Project Status

This page is a project-status index. The canonical current-state source of truth is docs/current_state.md, which is generated from live checks by scripts/refresh_current_state_doc.py.

## Current Verified Baseline

EduBoost V2 is in a release-candidate hardening phase, not a release-ready or public-beta-ready phase.

The latest local refresh on 2026-05-17 assessed commit 859695dac818 and reports RED quality status: 9 of 11 required checks passed. The live API contract checks now pass after regenerating docs/openapi.json and docs/route_inventory.md, but two required gates remain open:

- Architecture import boundaries fail. Import Linter now runs against the actual V2 packages and exposes real boundary violations between routers, modules, services, repositories, domain, and core.
- Backend unit gate did not complete inside the 300-second current-state timeout. The previous documented 1702 passed, 29 skipped result is historical until a fresh run is captured.

Recently reconciled checks that now agree with the live runtime:

- app.api_v2:app imports successfully.
- OpenAPI drift check passes.
- Route inventory drift check passes.
- Frontend lint, type-check, and Vitest unit checks pass.
- PR-002R evidence, E2E opt-in workflow, Makefile deduplication, staging release gate, and POPIA legal evidence checks pass locally.

New operating controls added on 2026-05-22:

- `docs/operations/recommended_operating_model.md` defines the day-to-day source-of-truth, evidence, protected-change, release-control, and accountability rules.
- `docs/operations/project_assistance_status.md` implements the five assistance lanes: current-state triage, verification and repair, release evidence and governance, architecture/security/compliance hardening, and staging/beta/operational readiness.
- `make recommended-operating-model-check` and `make project-assistance-status-check` provide local and CI-checkable guardrails for those controls.

## Content Factory Refreshed Implementation

Status: implemented and locally tested on branch `feature/content-factory-refreshed`; not CI, staging, or production verified.

The refreshed Content Factory plan from `temp/EduBoost_Content_Factory_Refreshed_Plan_25-May-2026.md` and the accompanying `temp/etl/` assets have been integrated into the repository. Evidence is tracked in [`docs/release/content_factory_refreshed_status.md`](release/content_factory_refreshed_status.md).

Implemented scope includes Content Factory ORM tables and migration, ETL service assets under `app/services/etl/`, optional MCP wrappers isolated under `tools/etl/`, admin-only `/api/v2/admin/content-factory` routes, provenance and validation gates, a file-backed `grade4_mathematics_en` scope/coverage registry, registry-backed coverage calculations, `/admin/content-factory` frontend entry point, and focused local tests.

Remaining proof required: CI run, disposable PostgreSQL migration evidence, staging seed/promotion proof, educator review evidence, and production rollback evidence.`n`nPR-CF-005 control-plane foundation is implemented locally: provenance expansion, lifecycle transitions, generation run/task ledger, dry-run orchestrator, seed/promotion gates, admin ETL visibility, and live dashboard reads are present behind admin-only routes and feature flags.
## Release Readiness

Status: blocked. Do not describe the repository as production-ready, release-ready, or public-beta-ready until docs/current_state.md is green and the release evidence bundle has current CI, staging, backup, restore, rollback, branch-protection, and sign-off evidence.

The root TODO.md remains the North Star tracker for work that is implemented but still needs CI, runtime, external, legal, security, product, or beta-launch proof.

## Claim Discipline

Do not describe the repository as production-ready until the release-blocker checklist is complete.

Claims must be phrased according to evidence:

| Claim type | Meaning |
| --- | --- |
| implemented | Source code exists. |
| tested | Targeted tests pass locally or in CI. |
| CI verified | Required workflow passed on the relevant branch or PR. |
| staging verified | Evidence exists from the staging environment. |
| production verified | Evidence exists from the production environment. |
| planned | Work is accepted but not implemented. |
| blocked | Work cannot proceed without an explicit blocker being resolved. |

## Compatibility Boundary

EduBoost is V2-first, but not every historical surface has disappeared:

- Archived legacy code is kept under app/legacy.
- app.legacy.api.main:app is retained as a compatibility shim.
- The legacy shim may expose a 410 Gone response for /api/v1/lessons/generate when explicitly imported.
- The canonical production runtime remains app.api_v2:app.
- Legacy compatibility routes must not appear in the canonical V2 OpenAPI schema.

## Remaining Release Blockers

Current blockers are evidence-backed, not inferred:

- [ ] Resolve architecture import-boundary violations or deliberately revise the contracts with documented rationale.
- [ ] Capture a fresh full backend unit-suite result outside the 300-second current-state timeout.
- [ ] Capture authoritative remote CI evidence for the target branch.
- [ ] Verify branch protection and required checks.
- [ ] Execute and capture staging smoke evidence against a real deployed environment.
- [ ] Execute and capture backup, restore, and rollback drill evidence.
- [ ] Complete external legal/security/product sign-offs before real learner data or public beta.
- [ ] Resolve the CAPS content gate: current approved item count is below beta and production thresholds.

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

The root [`TODO.md`](/TODO.md) is the live production-readiness tracker and current North Star execution plan for the repository. Operational workflow is documented in [`docs/operations/recommended_operating_model.md`](operations/recommended_operating_model.md), the five project assistance lanes are tracked in [`docs/operations/project_assistance_status.md`](operations/project_assistance_status.md), and the outstanding TODO execution plan is compiled in [`docs/operations/todo_implementation_plan.md`](operations/todo_implementation_plan.md).

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

- Evidence pending: `docs/security/popia_deletion_status_authorization_wiring.md`

## Parent Erasure Authorization

- [`docs/security/parent_erasure_authorization_wiring.md`](security/parent_erasure_authorization_wiring.md)

## POPIA Deletion Execute Authorization

- Evidence pending: `docs/security/popia_deletion_execute_authorization_wiring.md`

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

## POPIA Consent Gate Check

- [`docs/security/popia_consent_gate_check.md`](security/popia_consent_gate_check.md)

## POPIA Consent Audit CI

- [`docs/security/popia_consent_audit_ci.md`](security/popia_consent_audit_ci.md)

## POPIA Consent Dependency Adapter

- [`docs/security/consent_dependency_adapter.md`](security/consent_dependency_adapter.md)

## Study Plan Consent Gate

- [`docs/security/study_plan_consent_gate.md`](security/study_plan_consent_gate.md)

## Learner Read Consent Gate

- [`docs/security/learner_read_consent_gate.md`](security/learner_read_consent_gate.md)

## Gamification Consent Gate

- [`docs/security/gamification_consent_gate.md`](security/gamification_consent_gate.md)

## Parent Routes Consent Gate

- [`docs/security/parent_routes_consent_gate.md`](security/parent_routes_consent_gate.md)

## POPIA Data-Rights Consent Boundary

- [`docs/security/popia_data_rights_consent_boundary.md`](security/popia_data_rights_consent_boundary.md)

## Assessment Consent Gate

- [`docs/security/assessment_consent_gate.md`](security/assessment_consent_gate.md)

## Onboarding Consent Gate

- [`docs/security/onboarding_consent_gate.md`](security/onboarding_consent_gate.md)

## Ether Onboarding Consent Gate

- [`docs/security/ether_onboarding_consent_gate.md`](security/ether_onboarding_consent_gate.md)

## Ether Onboarding Consent Boundary

- [`docs/security/ether_onboarding_consent_gate.md`](security/ether_onboarding_consent_gate.md)

## POPIA Consent Gate Closure

- [`docs/security/POPIA_CONSENT_GATE_CLOSURE.md`](security/POPIA_CONSENT_GATE_CLOSURE.md)

## Ether Onboarding Consent Boundary

- [`docs/security/ether_onboarding_consent_gate.md`](security/ether_onboarding_consent_gate.md)

## POPIA Consent CI Closure

- POPIA consent CI closure includes boundary, order, and rejection-audit checks.

## Diagnostics Central Consent Source

- [`docs/security/diagnostics_central_consent_source.md`](security/diagnostics_central_consent_source.md)

## POPIA Negative Consent Evidence

- POPIA negative-consent evidence includes adapter denial paths and central route-source checks.

## Cluster C Closure Stamp

- Cluster C POPIA consent/audit closure stamp recorded.

## Cluster D CI Deployment Evidence

- Cluster D CI/deployment/environment evidence checks added.

## Cluster D Runtime Environment Gates

- Cluster D runtime environment gates now cover production placeholders and dev-only endpoint exposure.

## Production Key Vault Behavior

- Production Key Vault behavior tests added for Cluster D.

## Cluster D Closure

- Cluster D closure command and production Key Vault behavior evidence added.

## Cluster D Release Evidence

- Release evidence manifest and staging release gate added to Cluster D.

## Project Evidence Index

- Project evidence index and Cluster D closure report added.

## Cluster E Data Resilience

- Cluster E data-resilience baseline added for backup/restore evidence.

## Cluster E Backup Restore Commands

- Cluster E backup/restore dry-run command contracts added.

## Cluster E Backup Restore Evidence Records

- Cluster E backup manifest and restore evidence records added.

## Cluster E Backup Restore Integrity

- Cluster E backup/restore integrity checks added.

## Cluster E Closure

- Cluster E closure command and report added.

## Cluster E Restore Readiness

- Cluster E restore-readiness guards added for env matrix and production approval.

## Cluster E Release Evidence Wiring

- Cluster E evidence index and release-gate wiring added.

## Cluster F AI Safety

- Cluster F AI/CAPS/safety evidence baseline added.

## Cluster F Prompt Diagnostic Safety

- Cluster F prompt input and diagnostic generation safety contracts added.

## Cluster F Provider Output Safety

- Cluster F LLM fallback and AI output schema contracts added.

## Cluster F Closure

- Cluster F lesson/remediation safety and closure aggregate check added.

## Cluster F Release Evidence Wiring

- Cluster F evidence index, closure report, and release-gate wiring added.

## Cluster F Fixture Validation

- Cluster F fixture-based AI output validation added.

## Cluster F Prompt Refusal Evidence

- Cluster F prompt surface inventory and refusal regression fixtures added.

## Cluster F Secret Fixture Coverage

- Cluster F prompt secret-leak and fixture coverage guards added.

## Cluster G Frontend Journey

- Cluster G frontend vertical journey evidence baseline added.

## Cluster G Parent Denial UX

- Cluster G parent journey and auth/consent denial UX contracts added.

## Cluster G API Fixture Evidence

- Cluster G frontend API inventory and journey fixtures added.

## Cluster G Playwright Evidence

- Cluster G Playwright scaffold and journey smoke specs added.

## Cluster G Accessibility Evidence

- Cluster G frontend accessibility contract and static scan added.

## Cluster G Runtime Mock Evidence

- Cluster G frontend runtime inventory and mock API fixtures added.

## Cluster G Mocked Playwright Evidence

- Cluster G mocked Playwright API route evidence added.

## Cluster G E2E Runtime Evidence

- Cluster G frontend E2E environment and runtime command evidence added.

## Cluster G Build E2E Workflow Evidence

- Cluster G frontend build/test/lint contract and opt-in E2E workflow added.

## Cluster G Closure Release Evidence

- Cluster G frontend closure and release-gate evidence wiring added.

## Cluster H — Beta Release Governance

Cluster H is consolidated as beta release governance, not release closure. Repository-side templates and indexes now exist, but they do not replace runtime execution, CI authority, branch protection, or external approval.

Repository-side governance artifacts:

- `docs/release/sign_off_manifest.md`
- `docs/release/rollback_runbook.md`
- `docs/release/post_deploy_smoke_checklist.md`
- `docs/release/release_bundle_v1.0.0-rc2.md`
- `docs/release/release_hygiene_checklist.md`
- `docs/release/release_state_snapshot.md`
- `docs/release/audit_trail_index.md`
- `docs/release/final_closure_certificate.md`

Still pending before controlled beta:

- CI evidence on the protected target branch.
- Branch protection evidence from a repository administrator.
- Staging smoke, migration, backup, restore, rollback, and telemetry evidence.
- POPIA/legal, security, product/content, and release-owner approvals.
- Formal beta go/no-go and final signatures.

No Cluster H document should be read as approving production launch or public beta with real learner data.


## Production-readiness implementation phase

EduBoost V2 remains in a production-readiness implementation phase: repository-side evidence is present, while runtime, legal, security, deployment, and human approval gates remain separate.
