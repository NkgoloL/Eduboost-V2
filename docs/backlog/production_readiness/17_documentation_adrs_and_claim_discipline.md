# 17. Documentation, ADRs, and claim discipline

## 17.1 Required production docs

- [ ] `P0` Update `README.md`.
- [ ] `P0` Update `docs/project_status.md`.
- [ ] `P0` Add or update `docs/api_v2.md`.
- [ ] `P0` Commit `docs/openapi.json`.
- [ ] `P0` Add or update `docs/environment_variables.md`.
- [ ] `P0` Add or update `docs/release_checklist.md`.
- [ ] `P0` Add or update `docs/repository_governance.md`.
- [ ] `P0` Add or update `SECURITY.md`.
- [x] `P0` Add or update `docs/incident_response.md`. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Add or update `docs/disaster_recovery.md`. Evidence: `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Add or update `docs/popia_compliance.md`. Evidence: `docs/legal/privacy_legal_evidence_2026-05-11.md`.
- [ ] `P0` Add or update `docs/data_inventory.md`.
- [ ] `P0` Add or update `docs/data_retention_policy.md`.
- [ ] `P0` Add or update `docs/subprocessor_register.md`.
- [ ] `P1` Add or update `docs/testing_strategy.md`.
- [ ] `P1` Add or update `docs/deployment.md`.
- [ ] `P1` Add or update `docs/observability.md`.

## 17.2 ADRs

- [ ] `P1` Write ADR for modular monolith.
- [ ] `P1` Write ADR for FastAPI V2.
- [ ] `P1` Write ADR for Next.js frontend.
- [ ] `P1` Write ADR for PostgreSQL audit ledger.
- [ ] `P1` Write ADR for Redis revocation/job state.
- [ ] `P1` Write ADR for LLM provider abstraction.
- [ ] `P1` Write ADR for POPIA-first design.
- [ ] `P1` Write ADR for CAPS alignment.
- [ ] `P1` Write ADR for production deployment target.
- [ ] `P1` Write ADR for billing provider.
- [ ] `P1` Write ADR for notification provider.
- [ ] `P1` Write ADR for observability stack.
- [ ] `P1` Write ADR for business-logic location.
- [ ] `P1` Write ADR for API envelope.
- [ ] `P1` Write ADR for OpenAPI contract governance.

## 17.3 Claim discipline

- [ ] `P0` Remove or correct “V1 fully deleted” if legacy shims/archive remain.
- [ ] `P0` Remove or correct “no microservices” if inference sidecar remains.
- [ ] `P0` Remove or correct “ACA target” vs Kubernetes deployment mismatch.
- [ ] `P0` Remove or correct “production-ready” unless all release gates pass.
- [ ] `P0` Avoid claiming full CAPS coverage until validated.
- [ ] `P0` Avoid claiming full POPIA compliance until tests/legal docs pass.
- [ ] `P0` Label claims as `implemented`.
- [ ] `P0` Label claims as `tested`.
- [ ] `P0` Label claims as `CI verified`.
- [ ] `P0` Label claims as `staging verified`.
- [ ] `P0` Label claims as `production verified`.
- [ ] `P0` Label claims as `planned`.
- [ ] `P0` Label claims as `blocked`.
- [ ] `P1` Add docs linting to CI.
- [ ] `P1` Add docs link checker to CI.
- [ ] `P1` Add docs owner review requirement.

---

