# 20. Final release-blocker checklist

All items below must be complete before public beta or production use with real learner data.

```text
[x] Latest repo head verified by merge marker and SHA
[x] Canonical repo/branch/release authority documented
[ ] PR-002R implemented and verified
[ ] app.api_v2 imports cleanly
[ ] app/api_v2.py router-registration defect fixed
[ ] /health passes
[ ] /ready passes with real dependencies
[ ] /metrics exposes Prometheus metrics
[ ] /docs loads
[ ] /openapi.json loads
[ ] OpenAPI schema committed
[ ] OpenAPI drift check passes
[ ] API response envelope standardized
[ ] API error envelope standardized
[ ] Legacy routes excluded
[ ] Auth flows pass
[ ] Token rotation/revocation verified
[ ] Cookie policy verified
[ ] Object-level authorization tests pass
[ ] Consent gate check script passes
[ ] Consent bypass negative tests pass
[x] POPIA export workflow tested
[x] POPIA erasure workflow tested
[x] POPIA correction workflow tested
[x] POPIA restriction workflow tested
[ ] Backend consolidation diagnostics green
[ ] Audit call-site inventory reviewed
[ ] Consent call-site inventory reviewed
[ ] Runtime compatibility probes pass
[ ] Audit chain verified
[ ] Audit completeness tests pass
[ ] LLM PII sweep passes
[ ] AI output validators pass
[ ] Independent answer-key checking implemented
[x] CAPS topic map MVP validated
[x] CAPS claims reviewed and limited to evidence
[ ] Diagnostic IRT tests pass
[ ] Minimum item bank exists for launch scope
[ ] Database migrations pass from empty DB
[ ] Schema integrity validation passes
[x] Backup/restore drill completed
[x] RPO/RTO documented
[ ] CI branch/deployment contradictions resolved
[x] Docker images build cleanly
[ ] Docker images run as non-root
[ ] Production secrets stored outside repo
[x] Security scans pass or have accepted risk records
[x] Staging deployment completed
[x] Staging smoke tests pass
[x] Playwright E2E passes against staging
[x] Dashboards live
[x] Alerts live
[x] Incident response runbook complete
[ ] Tabletop exercise completed
[x] Privacy Policy drafted and reviewed
[x] Terms of Service drafted and reviewed
[x] Parent Consent Notice drafted and reviewed
[x] Child-friendly Privacy Notice drafted and reviewed
[x] Release evidence bundle generated
[ ] Rollback tested
[ ] Go/no-go review completed
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
