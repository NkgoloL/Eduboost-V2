# V2 Pen-Test Checklist

**Status:** RR-006 required checklist  
**Scope:** EduBoost V2 controlled-beta and release-readiness surfaces.  
**Boundary:** checklist only; no public beta or production release authority.

## 1. Authentication and session management

- [ ] Verify login/session cookie flags: HttpOnly, Secure, SameSite.
- [ ] Attempt refresh-token replay.
- [ ] Attempt expired-token access.
- [ ] Attempt logout/revocation bypass.
- [ ] Attempt role-claim tampering.

## 2. Authorization and IDOR

- [ ] Learner cannot access another learner's diagnostics.
- [ ] Parent cannot access unrelated learner reports.
- [ ] Learner cannot call parent-only endpoints.
- [ ] Parent cannot bypass consent or export/erasure ownership checks.
- [ ] Route aliases preserve the same authorization dependency as canonical routes.

## 3. POPIA and learner data handling

- [ ] Export requires active authorization and active consent where applicable.
- [ ] Erasure preflight blocks legal-hold cases.
- [ ] Erasure requires export-offered state before execution.
- [ ] Audit records are preserved and not destructively rewritten.
- [ ] Logs do not expose learner PII.

## 4. API, input validation, and rate limiting

- [ ] Attempt malformed JSON and overlong payloads.
- [ ] Attempt path traversal and route confusion between `/api/v2` and `/v2`.
- [ ] Attempt repeated auth and diagnostic calls for rate-limit bypass.
- [ ] Confirm OpenAPI routes match implemented authorization expectations.

## 5. LLM and content safety

- [ ] Prompt-injection attempts cannot exfiltrate system prompts or PII.
- [ ] LLM context excludes direct learner PII.
- [ ] Output is checked for unsafe or PII-like content before learner display.
- [ ] Content review paths exist for questionable generated content.

## 6. Frontend and browser security

- [ ] Check CSP/security headers.
- [ ] Check XSS handling in generated lesson and feedback surfaces.
- [ ] Check CSRF-sensitive flows if cookie auth is used.
- [ ] Check no secrets appear in client bundle or frontend env exposure.

## 7. Infrastructure and CI/CD

- [ ] Dependency vulnerability scans run in CI.
- [ ] Secrets scanning runs in pre-commit and CI.
- [ ] Required release checks are visible in GitHub branch protection.
- [ ] Deployment credentials are not available to PRs from forks.

## 8. Observability and incident response

- [ ] Security incidents are classifiable by severity.
- [ ] Logs contain trace IDs without leaking PII.
- [ ] Alert/runbook linkage exists for auth, privacy, and availability incidents.
- [ ] Rollback decision process is documented.

## Exit criterion

Pen-test checklist prepared: true  
Production release authorised: false  
Public beta authorised: false  
Runtime KG implementation claimed: false
