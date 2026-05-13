# 17. Documentation, ADRs, and claim discipline

## 17.1 Required production docs

- [verify] `P0` Update `README.md`.
- [verify] `P0` Update `docs/project_status.md`.
- [verify] `P0` Add or update `docs/api_v2.md`.
- [verify] `P0` Commit `docs/openapi.json`.
- [verify] `P0` Add or update `docs/environment_variables.md`.
- [verify] `P0` Add or update `docs/release_checklist.md`.
- [verify] `P0` Add or update `docs/repository_governance.md`.
- [verify] `P0` Add or update `SECURITY.md`.
- [x] `P0` Add or update `docs/incident_response.md`. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Add or update `docs/disaster_recovery.md`. Evidence: `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Add or update `docs/popia_compliance.md`. Evidence: `docs/legal/privacy_legal_evidence_2026-05-11.md`.
- [verify] `P0` Add or update `docs/data_inventory.md`.
- [verify] `P0` Add or update `docs/data_retention_policy.md`.
- [verify] `P0` Add or update `docs/subprocessor_register.md`.
- [verify] `P1` Add or update `docs/testing_strategy.md`.
- [verify] `P1` Add or update `docs/deployment.md`.
- [verify] `P1` Add or update `docs/observability.md`.

## 17.2 ADRs

- [verify] `P1` Write ADR for modular monolith.
- [verify] `P1` Write ADR for FastAPI V2.
- [verify] `P1` Write ADR for Next.js frontend.
- [verify] `P1` Write ADR for PostgreSQL audit ledger.
- [verify] `P1` Write ADR for Redis revocation/job state.
- [verify] `P1` Write ADR for LLM provider abstraction.
- [verify] `P1` Write ADR for POPIA-first design.
- [verify] `P1` Write ADR for CAPS alignment.
- [verify] `P1` Write ADR for production deployment target.
- [verify] `P1` Write ADR for billing provider.
- [verify] `P1` Write ADR for notification provider.
- [verify] `P1` Write ADR for observability stack.
- [verify] `P1` Write ADR for business-logic location.
- [verify] `P1` Write ADR for API envelope.
- [verify] `P1` Write ADR for OpenAPI contract governance.

## 17.3 Claim discipline

- [verify] `P0` Remove or correct “V1 fully deleted” if legacy shims/archive remain.
- [verify] `P0` Remove or correct “no microservices” if inference sidecar remains.
- [verify] `P0` Remove or correct “ACA target” vs Kubernetes deployment mismatch.
- [verify] `P0` Remove or correct “production-ready” unless all release gates pass.
- [verify] `P0` Avoid claiming full CAPS coverage until validated.
- [verify] `P0` Avoid claiming full POPIA compliance until tests/legal docs pass.
- [verify] `P0` Label claims as `implemented`.
- [verify] `P0` Label claims as `tested`.
- [verify] `P0` Label claims as `CI verified`.
- [verify] `P0` Label claims as `staging verified`.
- [verify] `P0` Label claims as `production verified`.
- [verify] `P0` Label claims as `planned`.
- [verify] `P0` Label claims as `blocked`.
- [verify] `P1` Add docs linting to CI.
- [verify] `P1` Add docs link checker to CI.
- [verify] `P1` Add docs owner review requirement.

---



## 17.6 Repository-side implementation evidence

- [verify] Documentation/ADR/claim-discipline decision is documented in `docs/adr/ADR-017-documentation-adrs-claim-discipline.md`.
- [verify] Documentation governance architecture is documented in `docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md`.
- [verify] ADR lifecycle controls are documented in `docs/documentation/adr_lifecycle_contract.md`.
- [verify] Claim discipline controls are documented in `docs/documentation/claim_discipline_contract.md`.
- [verify] Documentation inventory controls are documented in `docs/documentation/documentation_inventory_contract.md`.
- [verify] Stale documentation review is documented in `docs/documentation/stale_documentation_review_register.md`.
- [verify] Release-note discipline is documented in `docs/documentation/release_notes_discipline_contract.md`.
- [verify] Documentation review gate is documented in `docs/documentation/documentation_review_gate_contract.md`.
- [verify] Production claim boundary policy is documented in `docs/documentation/production_claim_boundary_policy.md`.
- [verify] Deterministic repository contracts live in `app/modules/documentation_governance/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_documentation_adrs_claim_discipline_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_17_documentation_adrs_claim_discipline_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_documentation_adrs_claim_discipline_production_readiness.py`.
- [verify] Make target is `make documentation-adrs-claim-discipline-production-readiness-check`.

### Verification boundary

This implementation provides repository-side documentation governance, ADR lifecycle, stale-doc review, release-note discipline, documentation review-gate, and claim-boundary readiness evidence. It does not approve external repository settings, human signoff, legal approval, security approval, or production launch.
