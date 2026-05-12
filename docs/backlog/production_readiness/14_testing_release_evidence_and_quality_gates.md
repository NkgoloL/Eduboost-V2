# 14. Testing, release evidence, and quality gates

## 14.1 Backend tests

- [ ] `P0` Maintain backend unit coverage at or above 80%.
- [ ] `P0` Add unit tests for API envelope.
- [ ] `P0` Add unit tests for error contract.
- [ ] `P0` Add unit tests for auth security helpers.
- [ ] `P0` Add unit tests for token revocation.
- [ ] `P0` Add unit tests for consent policy.
- [ ] `P0` Add unit tests for LLM PII redaction.
- [ ] `P0` Add unit tests for CAPS validator.
- [ ] `P0` Add unit tests for IRT engine.
- [ ] `P0` Add unit tests for repository layer.
- [ ] `P0` Add integration tests for auth flows.
- [ ] `P0` Add integration tests for consent flows.
- [ ] `P0` Add integration tests for POPIA workflows.
- [ ] `P0` Add integration tests for diagnostics.
- [ ] `P0` Add integration tests for lesson generation.
- [ ] `P0` Add integration tests for billing webhooks.
- [ ] `P0` Add integration tests for audit trail.
- [ ] `P0` Add smoke tests for `/health`.
- [ ] `P0` Add smoke tests for `/ready`.
- [ ] `P0` Add smoke tests for `/metrics`.
- [ ] `P0` Add smoke tests for `/docs`.
- [ ] `P0` Add smoke tests for `/openapi.json`.

## 14.2 Frontend tests

- [ ] `P0` Maintain frontend coverage at or above agreed threshold.
- [ ] `P0` Add component tests for signup.
- [ ] `P0` Add component tests for login.
- [ ] `P0` Add component tests for consent.
- [ ] `P0` Add component tests for diagnostic.
- [ ] `P0` Add component tests for lesson view.
- [ ] `P0` Add component tests for parent dashboard.
- [ ] `P0` Add tests for API client envelope parsing.
- [ ] `P0` Add tests for API client error parsing.
- [ ] `P0` Add tests for route guards.
- [ ] `P1` Add tests for loading states.
- [ ] `P1` Add tests for empty states.
- [ ] `P1` Add tests for failure states.
- [ ] `P1` Add tests for retry states.
- [ ] `P1` Add mobile viewport tests.
- [ ] `P1` Add accessibility tests.
- [ ] `P1` Add PWA/offline tests.

## 14.3 E2E tests

- [ ] `P0` Add Playwright E2E for guardian signup.
- [ ] `P0` Add Playwright E2E for learner profile creation.
- [ ] `P0` Add Playwright E2E for consent capture.
- [ ] `P0` Add Playwright E2E for diagnostic session.
- [ ] `P0` Add Playwright E2E for study plan.
- [ ] `P0` Add Playwright E2E for lesson completion.
- [ ] `P0` Add Playwright E2E for parent report.
- [ ] `P0` Add Playwright E2E for POPIA export request.
- [ ] `P0` Add Playwright E2E for erasure request.
- [ ] `P1` Add Playwright E2E for billing subscription if billing in beta scope.
- [ ] `P1` Add Playwright E2E for password reset.
- [ ] `P1` Add Playwright E2E for session expiry.
- [ ] `P1` Add Playwright E2E for mobile viewport.

## 14.4 Security tests

- [ ] `P0` Run SAST.
- [ ] `P0` Run Python dependency audit.
- [ ] `P0` Run npm dependency audit.
- [ ] `P0` Run Docker image scan.
- [ ] `P0` Run secrets scan.
- [ ] `P0` Add CORS tests.
- [ ] `P0` Add CSRF tests.
- [ ] `P0` Add cookie policy tests.
- [ ] `P0` Add rate-limit tests.
- [ ] `P0` Add object-authorization tests.
- [ ] `P0` Add consent-bypass tests.
- [ ] `P1` Run penetration-test checklist.
- [ ] `P1` Add abuse-case tests.

## 14.5 Release evidence

- [ ] `P0` Generate backend image digest.
- [ ] `P0` Generate frontend build/image digest.
- [ ] `P0` Record migration revision.
- [ ] `P0` Generate changelog entry.
- [ ] `P0` Generate SBOM.
- [ ] `P0` Attach backend test reports.
- [ ] `P0` Attach frontend test reports.
- [ ] `P0` Attach coverage reports.
- [ ] `P0` Attach security scan reports.
- [ ] `P0` Attach OpenAPI schema hash.
- [ ] `P0` Attach deployment manifest.
- [ ] `P0` Attach rollback plan.
- [ ] `P0` Attach repo-state verification.
- [ ] `P0` Attach staging acceptance report.
- [ ] `P0` Block production promotion if evidence bundle missing.
- [ ] `P1` Add `scripts/build_release_evidence.py` if not complete.
- [ ] `P1` Add release evidence validation script.

---

