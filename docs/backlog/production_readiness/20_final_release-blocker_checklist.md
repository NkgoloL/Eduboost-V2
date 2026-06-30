# 20. Final release-blocker checklist

All items below must be complete before public beta or production use with real learner data.

```text
[x] Latest repo head verified by merge marker and SHA
[x] Canonical repo/branch/release authority documented
[x] PR-002R implemented and verified (Phase 9)
[x] app.api_v2 imports cleanly (Phase 9)
[x] app/api_v2.py router-registration defect fixed (Phase 9)
[x] /health passes (Phase 9 — scripts/verify_api_health.py)
[x] /ready passes with real dependencies (Phase 9 — scripts/verify_api_health.py)
[x] /metrics exposes Prometheus metrics (Phase 9 — scripts/verify_api_health.py)
[x] /docs loads (Phase 9 — scripts/verify_api_health.py)
[/] /openapi.json loads (CI workflow exists; generation requires full runtime deps)
[/] OpenAPI schema committed (run make openapi with full runtime)
[/] OpenAPI drift check passes (CI job: .github/workflows/openapi-drift.yml)
[x] API response envelope standardized (Phase 9 — tests/integration/test_api_envelope.py)
[x] API error envelope standardized (Phase 9 — tests/integration/test_api_envelope.py)
[x] Legacy routes excluded (Phase 9 — verified in envelope tests)
[x] Auth flows pass (Phase 8 — test_auth_abuse_paths.py)
[x] Token rotation/revocation verified (Phase 8 — test_token_rotation.py)
[x] Cookie policy verified (Phase 8 — test_cookie_policy.py)
[x] Object-level authorization tests pass (Phase 8 — test_role_authorization.py)
[x] Consent gate check script passes (Phase 8 — scripts/check_consent_gate_inventory.py)
[x] Consent bypass negative tests pass (Phase 8)
[x] POPIA export workflow tested
[x] POPIA erasure workflow tested
[x] POPIA correction workflow tested
[x] POPIA restriction workflow tested
[x] Backend consolidation diagnostics green (Phase 9)
[x] Audit call-site inventory reviewed (Phase 9)
[x] Consent call-site inventory reviewed (Phase 9)
[x] Runtime compatibility probes pass (Phase 9)
[x] Audit chain verified (Phase 9 — scripts/verify_audit_chain.py)
[x] Audit completeness tests pass (Phase 8 — test_audit_integrity.py)
[x] LLM PII sweep passes (Phase 9 — scripts/popia_sweep.py)
[x] AI output validators pass (Phase 9)
[x] Independent answer-key checking implemented (Phase 9 — scripts/check_answer_key_independence.py)
[x] CAPS topic map MVP validated
[x] CAPS claims reviewed and limited to evidence
[x] Diagnostic IRT tests pass (Phase 9)
[x] Minimum item bank exists for launch scope (Phase 9 — docs/release/item_bank_launch_scope.md)
[x] Database migrations pass from empty DB (Phase 9)
[x] Schema integrity validation passes (Phase 9)
[x] Backup/restore drill completed
[x] RPO/RTO documented
[x] CI branch/deployment contradictions resolved (Phase 9)
[x] Docker images build cleanly
[x] Docker images run as non-root (Phase 9 — docker/Dockerfile.v2 has USER eduboost)
[x] Production secrets stored outside repo (Phase 9 — docs/operations/production_secrets.md)
[x] Security scans pass or have accepted risk records
[x] Staging deployment completed
[x] Staging smoke tests pass
[x] Playwright E2E passes against staging
[x] Dashboards live
[x] Alerts live
[x] Incident response runbook complete
[x] Tabletop exercise completed (Phase 9 — docs/operations/tabletop_exercise_2026-06.md)
[x] Privacy Policy drafted and reviewed
[x] Terms of Service drafted and reviewed
[x] Parent Consent Notice drafted and reviewed
[x] Child-friendly Privacy Notice drafted and reviewed
[x] Release evidence bundle generated
[x] Rollback tested (Phase 9 — docs/release/go_no_go_review.md)
[x] Go/no-go review completed (Phase 9 — docs/release/go_no_go_review.md)
```

---

## Execution recommendation

Execute in this order:

1. **PR-002R runtime/API contract baseline**
2. **Security and POPIA negative tests**
3. **CI/CD and deployment target alignment**
4. **Database migration and backup/restore proof**
5. **AI/CAPS validation and diagnostic item-bank proof**
6. **Frontend E2E, accessibility, and parent/learner journeys**
7. **Staging acceptance, incident response, and release evidence**
8. **Controlled public beta**

This TODO intentionally favors evidence over optimism. EduBoost V2 should only claim production readiness where code, tests, CI, staging, and operational runbooks prove it.


## 20.6 Repository-side implementation evidence

- [verify] Final release-blocker decision is documented in `docs/adr/ADR-020-final-release-blocker-checklist.md`.
- [verify] Final release-blocker architecture is documented in `docs/release_blockers/final_release_blocker_architecture_contract.md`.
- [verify] Final release-blocker register is documented in `docs/release_blockers/final_release_blocker_register.md`.
- [verify] Release-blocker domain summary is documented in `docs/release_blockers/release_blocker_domain_summary.md`.
- [verify] Release-blocker waiver policy is documented in `docs/release_blockers/release_blocker_waiver_policy.md`.
- [verify] External/manual dependency register is documented in `docs/release_blockers/external_manual_dependency_register.md`.
- [verify] Final go/no-go checklist is documented in `docs/release_blockers/final_go_no_go_checklist.md`.
- [verify] Release-blocker closure register is documented in `docs/release_blockers/final_release_blocker_closure_register.md`.
- [verify] Final release-blocker evidence bundle is documented in `docs/release_blockers/final_release_blocker_evidence_bundle.md`.
- [verify] Final launch boundary statement is documented in `docs/release_blockers/final_launch_boundary_statement.md`.
- [verify] Deterministic repository contracts live in `app/modules/final_release_blockers/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_final_release_blocker_checklist.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_20_final_release_blocker_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_final_release_blocker_checklist.py`.
- [verify] Make target is `make final-release-blocker-checklist-check`.

### Verification boundary

This implementation provides repository-side final release-blocker checklist, blocker register, waiver, external/manual dependency, closure, evidence bundle, and final go/no-go readiness evidence. It does not approve external settings, legal signoff, security signoff, deployment, beta launch, general availability, or production launch.
