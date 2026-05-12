# 15. Security posture and threat modeling

## 15.1 Security headers, CORS, and CSRF

- [ ] `P0` Verify security headers in staging.
- [ ] `P0` Verify HSTS where TLS is terminated.
- [ ] `P0` Verify `X-Content-Type-Options`.
- [ ] `P0` Verify frame-ancestors or X-Frame-Options.
- [ ] `P0` Verify CSP if feasible.
- [ ] `P0` Verify production CORS allowlist.
- [ ] `P0` Remove wildcard origins in production.
- [ ] `P0` Define CSRF strategy for cookie-based auth.
- [ ] `P0` Add CSRF tests.
- [ ] `P1` Add security-header tests.
- [ ] `P1` Document browser security model.

## 15.2 Secrets

- [ ] `P0` Run gitleaks on full history.
- [ ] `P0` Run detect-secrets or equivalent.
- [ ] `P0` Verify no real secrets remain active from git history.
- [ ] `P0` Rotate any exposed or possibly exposed secrets.
- [ ] `P0` Store production secrets in Key Vault or equivalent.
- [ ] `P0` Ensure local `.env` is ignored.
- [ ] `P0` Ensure `.env.example` has no real secrets.
- [ ] `P1` Add secret rotation schedule.
- [ ] `P1` Add secret access audit.
- [ ] `P1` Add emergency secret rotation runbook.

## 15.3 Threat model

- [ ] `P1` Create `docs/threat_model.md`.
- [ ] `P1` Model learner data exposure.
- [ ] `P1` Model consent bypass.
- [ ] `P1` Model account takeover.
- [ ] `P1` Model prompt injection.
- [ ] `P1` Model LLM PII leakage.
- [ ] `P1` Model billing webhook replay.
- [ ] `P1` Model data export abuse.
- [ ] `P1` Model admin misuse.
- [ ] `P1` Model audit tampering.
- [ ] `P1` Model dependency supply-chain compromise.
- [ ] `P1` Add mitigations for each threat.
- [ ] `P1` Add tests or controls for high-risk threats.
- [ ] `P2` Review threat model every release.

## 15.4 Pen-test readiness

- [ ] `P1` Finalize penetration-test checklist.
- [ ] `P1` Run auth pen-test checks.
- [ ] `P1` Run authorization pen-test checks.
- [ ] `P1` Run POPIA workflow abuse checks.
- [ ] `P1` Run API input validation checks.
- [ ] `P1` Run rate-limit abuse checks.
- [ ] `P1` Run LLM prompt-injection checks.
- [ ] `P1` Run file/export abuse checks.
- [ ] `P1` Run admin access checks.
- [ ] `P1` Record findings.
- [ ] `P1` Fix critical/high findings before beta.
- [ ] `P2` Schedule recurring security scans.

---

