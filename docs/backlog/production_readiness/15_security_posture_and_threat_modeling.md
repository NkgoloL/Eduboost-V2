# 15. Security posture and threat modeling

## 15.1 Security headers, CORS, and CSRF

- [verify] `P0` Verify security headers in staging.
- [verify] `P0` Verify HSTS where TLS is terminated.
- [verify] `P0` Verify `X-Content-Type-Options`.
- [verify] `P0` Verify frame-ancestors or X-Frame-Options.
- [verify] `P0` Verify CSP if feasible.
- [verify] `P0` Verify production CORS allowlist.
- [verify] `P0` Remove wildcard origins in production.
- [verify] `P0` Define CSRF strategy for cookie-based auth.
- [verify] `P0` Add CSRF tests.
- [verify] `P1` Add security-header tests.
- [verify] `P1` Document browser security model.

## 15.2 Secrets

- [verify] `P0` Run gitleaks on full history.
- [verify] `P0` Run detect-secrets or equivalent.
- [verify] `P0` Verify no real secrets remain active from git history.
- [verify] `P0` Rotate any exposed or possibly exposed secrets.
- [verify] `P0` Store production secrets in Key Vault or equivalent.
- [verify] `P0` Ensure local `.env` is ignored.
- [verify] `P0` Ensure `.env.example` has no real secrets.
- [verify] `P1` Add secret rotation schedule.
- [verify] `P1` Add secret access audit.
- [verify] `P1` Add emergency secret rotation runbook.

## 15.3 Threat model

- [verify] `P1` Create `docs/threat_model.md`.
- [verify] `P1` Model learner data exposure.
- [verify] `P1` Model consent bypass.
- [verify] `P1` Model account takeover.
- [verify] `P1` Model prompt injection.
- [verify] `P1` Model LLM PII leakage.
- [verify] `P1` Model billing webhook replay.
- [verify] `P1` Model data export abuse.
- [verify] `P1` Model admin misuse.
- [verify] `P1` Model audit tampering.
- [verify] `P1` Model dependency supply-chain compromise.
- [verify] `P1` Add mitigations for each threat.
- [verify] `P1` Add tests or controls for high-risk threats.
- [verify] `P2` Review threat model every release.

## 15.4 Pen-test readiness

- [verify] `P1` Finalize penetration-test checklist.
- [verify] `P1` Run auth pen-test checks.
- [verify] `P1` Run authorization pen-test checks.
- [verify] `P1` Run POPIA workflow abuse checks.
- [verify] `P1` Run API input validation checks.
- [verify] `P1` Run rate-limit abuse checks.
- [verify] `P1` Run LLM prompt-injection checks.
- [verify] `P1` Run file/export abuse checks.
- [verify] `P1` Run admin access checks.
- [verify] `P1` Record findings.
- [verify] `P1` Fix critical/high findings before beta.
- [verify] `P2` Schedule recurring security scans.

---



## 15.6 Repository-side implementation evidence

- [verify] Security posture decision is documented in `docs/adr/ADR-015-security-posture-threat-modeling.md`.
- [verify] Security posture architecture is documented in `docs/security/security_posture_architecture_contract.md`.
- [verify] Threat model register is documented in `docs/security/threat_model_register.md`.
- [verify] Security control register is documented in `docs/security/security_control_register.md`.
- [verify] Vulnerability management policy is documented in `docs/security/vulnerability_management_policy.md`.
- [verify] Security test strategy is documented in `docs/security/security_test_strategy_contract.md`.
- [verify] Secret hygiene controls are documented in `docs/security/secret_hygiene_contract.md`.
- [verify] Supply-chain controls are documented in `docs/security/supply_chain_security_contract.md`.
- [verify] Security header policy is documented in `docs/security/security_headers_policy.md`.
- [verify] PII/secret redaction contract is documented in `docs/security/pii_secret_redaction_contract.md`.
- [verify] Risk acceptance register is documented in `docs/security/risk_acceptance_register.md`.
- [verify] Security incident response runbook is documented in `docs/security/runbooks/security_incident_response.md`.
- [verify] Deterministic repository contracts live in `app/modules/security_posture/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_security_posture_threat_modeling_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_15_security_posture_threat_modeling_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_security_posture_threat_modeling_production_readiness.py`.
- [verify] Make target is `make security-posture-threat-modeling-production-readiness-check`.

### Verification boundary

This implementation provides repository-side security posture, threat-modeling, vulnerability-management, secret-hygiene, supply-chain, incident-response, risk-acceptance, and security-header readiness evidence. It does not execute a live penetration test, configure cloud security posture, rotate secrets, or authorize production launch.
