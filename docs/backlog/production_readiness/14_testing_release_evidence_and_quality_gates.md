# 14. Testing, release evidence, and quality gates

## 14.1 Backend tests

- [verify] `P0` Maintain backend unit coverage at or above 80%.
- [verify] `P0` Add unit tests for API envelope.
- [verify] `P0` Add unit tests for error contract.
- [verify] `P0` Add unit tests for auth security helpers.
- [verify] `P0` Add unit tests for token revocation.
- [verify] `P0` Add unit tests for consent policy.
- [verify] `P0` Add unit tests for LLM PII redaction.
- [verify] `P0` Add unit tests for CAPS validator.
- [verify] `P0` Add unit tests for IRT engine.
- [verify] `P0` Add unit tests for repository layer.
- [verify] `P0` Add integration tests for auth flows.
- [verify] `P0` Add integration tests for consent flows.
- [verify] `P0` Add integration tests for POPIA workflows.
- [verify] `P0` Add integration tests for diagnostics.
- [verify] `P0` Add integration tests for lesson generation.
- [verify] `P0` Add integration tests for billing webhooks.
- [verify] `P0` Add integration tests for audit trail.
- [verify] `P0` Add smoke tests for `/health`.
- [verify] `P0` Add smoke tests for `/ready`.
- [verify] `P0` Add smoke tests for `/metrics`.
- [verify] `P0` Add smoke tests for `/docs`.
- [verify] `P0` Add smoke tests for `/openapi.json`.

## 14.2 Frontend tests

- [verify] `P0` Maintain frontend coverage at or above agreed threshold.
- [verify] `P0` Add component tests for signup.
- [verify] `P0` Add component tests for login.
- [verify] `P0` Add component tests for consent.
- [verify] `P0` Add component tests for diagnostic.
- [verify] `P0` Add component tests for lesson view.
- [verify] `P0` Add component tests for parent dashboard.
- [verify] `P0` Add tests for API client envelope parsing.
- [verify] `P0` Add tests for API client error parsing.
- [verify] `P0` Add tests for route guards.
- [verify] `P1` Add tests for loading states.
- [verify] `P1` Add tests for empty states.
- [verify] `P1` Add tests for failure states.
- [verify] `P1` Add tests for retry states.
- [verify] `P1` Add mobile viewport tests.
- [verify] `P1` Add accessibility tests.
- [verify] `P1` Add PWA/offline tests.

## 14.3 E2E tests

- [verify] `P0` Add Playwright E2E for guardian signup.
- [verify] `P0` Add Playwright E2E for learner profile creation.
- [verify] `P0` Add Playwright E2E for consent capture.
- [verify] `P0` Add Playwright E2E for diagnostic session.
- [verify] `P0` Add Playwright E2E for study plan.
- [verify] `P0` Add Playwright E2E for lesson completion.
- [verify] `P0` Add Playwright E2E for parent report.
- [verify] `P0` Add Playwright E2E for POPIA export request.
- [verify] `P0` Add Playwright E2E for erasure request.
- [verify] `P1` Add Playwright E2E for billing subscription if billing in beta scope.
- [verify] `P1` Add Playwright E2E for password reset.
- [verify] `P1` Add Playwright E2E for session expiry.
- [verify] `P1` Add Playwright E2E for mobile viewport.

## 14.4 Security tests

- [verify] `P0` Run SAST.
- [verify] `P0` Run Python dependency audit.
- [verify] `P0` Run npm dependency audit.
- [verify] `P0` Run Docker image scan.
- [verify] `P0` Run secrets scan.
- [verify] `P0` Add CORS tests.
- [verify] `P0` Add CSRF tests.
- [verify] `P0` Add cookie policy tests.
- [verify] `P0` Add rate-limit tests.
- [verify] `P0` Add object-authorization tests.
- [verify] `P0` Add consent-bypass tests.
- [verify] `P1` Run penetration-test checklist.
- [verify] `P1` Add abuse-case tests.

## 14.5 Release evidence

- [verify] `P0` Generate backend image digest.
- [verify] `P0` Generate frontend build/image digest.
- [verify] `P0` Record migration revision.
- [verify] `P0` Generate changelog entry.
- [verify] `P0` Generate SBOM.
- [verify] `P0` Attach backend test reports.
- [verify] `P0` Attach frontend test reports.
- [verify] `P0` Attach coverage reports.
- [verify] `P0` Attach security scan reports.
- [verify] `P0` Attach OpenAPI schema hash.
- [verify] `P0` Attach deployment manifest.
- [verify] `P0` Attach rollback plan.
- [verify] `P0` Attach repo-state verification.
- [verify] `P0` Attach staging acceptance report.
- [verify] `P0` Block production promotion if evidence bundle missing.
- [verify] `P1` Add `scripts/build_release_evidence.py` if not complete.
- [verify] `P1` Add release evidence validation script.

---



## 14.6 Repository-side implementation evidence

- [verify] Testing/release quality-gate decision is documented in `docs/adr/ADR-014-testing-release-evidence-quality-gates.md`.
- [verify] Testing release evidence architecture is documented in `docs/testing/testing_release_evidence_architecture_contract.md`.
- [verify] Test strategy matrix is documented in `docs/testing/test_strategy_matrix_contract.md`.
- [verify] Coverage quality thresholds are documented in `docs/testing/coverage_quality_threshold_contract.md`.
- [verify] Quality gate waiver policy is documented in `docs/testing/quality_gate_waiver_policy.md`.
- [verify] Release evidence bundle requirements are documented in `docs/testing/release_evidence_bundle_contract.md`.
- [verify] Defect triage and release blocker rules are documented in `docs/testing/defect_triage_release_blocker_contract.md`.
- [verify] Beta and production release quality-gate checklists are documented under `docs/testing/`.
- [verify] Known issues release register template exists at `docs/testing/known_issues_release_register.md`.
- [verify] Deterministic repository contracts live in `app/modules/quality_gates/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_testing_release_quality_gates_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_14_testing_release_quality_gates_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_testing_release_quality_gates_production_readiness.py`.
- [verify] Make target is `make testing-release-quality-gates-production-readiness-check`.

### Verification boundary

This implementation provides repository-side testing, release evidence, coverage, defect triage, known-issues, waiver, and quality-gate readiness evidence. It does not configure external branch protection, run CI, approve releases, or authorize production launch.
