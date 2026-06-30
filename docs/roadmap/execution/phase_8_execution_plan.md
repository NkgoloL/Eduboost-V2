# Phase 8 Execution Plan — Privacy and Authorization Completion

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: Implemented with 2026-06-14 remediation evidence
**Branch**: `phase-8/privacy-and-authorization-completion`
**Base**: `origin/master`
**Priority**: P1 (per [roadmap.md](../roadmap.md#L328-L355))
**Scope**: Close all remaining P0 and P1 gaps in the authentication/authorization (PR-003) and POPIA/privacy/audit (PR-004) production-readiness domains.

---

## 2026-06-14 Audit Note

The original execution plan is broader than the work that was merged in PR #228.
The current completion claim is limited to the implemented Phase 8
authorization/privacy evidence set plus the 2026-06-14 remediation of the POPIA
`AuthContext` runtime mismatch. Unchecked aspirational PR-004 items in this plan
remain backlog candidates unless separately proven by code and tests.

Fresh local evidence is recorded in:

- `docs/release/phase_8_evidence.md`
- `docs/release/phase_8_implementation_audit.md`
- `docs/roadmap/execution/phase_8_implementation_report.md`

## Pre-Conditions

- [x] Phase 7 merged to `master` (PR #227).
- [x] Roadmap Phase 8 requirements documented in `docs/roadmap/roadmap.md`.
- [x] Preliminary phase plan exists in `phases/phase_8_privacy_and_authorization_completion.md`.
- [x] Backlog inventory exists: `docs/backlog/production_readiness/03_authentication_sessions_rbac_and_object-level_authorization.md` (PR-003) and `docs/backlog/production_readiness/04_popia_consent_privacy_data-subject_rights_and_audit.md` (PR-004).
- [x] Branch `phase-8/privacy-and-authorization-completion` created from `master`.

---

## Pre-Execution Baseline (Audit Results)

### Existing Infrastructure (already built)

**Authorization** (`app/core/authorization.py`, `app/security/`):
- Roles defined: `LEARNER`, `GUARDIAN`, `TEACHER`, `ADMIN`, `SUPPORT_OPERATOR`, `CONTENT_REVIEWER`, `COMPLIANCE_AUDITOR`
- Policy helpers: `can_view_learner`, `can_update_learner`, `can_generate_lesson_for_learner`, `can_start_diagnostic_for_learner`, `can_view_study_plan`, `can_view_parent_report`, `can_export_learner_data`, `can_request_erasure`, `can_view_billing`
- Object-level authorization with audit events for privileged access
- Rate limiting on login, signup, refresh, password reset, email verification, LLM, data export, billing webhook endpoints
- JWT signing-key rotation with `kid`, emergency revoke-all, persistent revocation fallback

**Consent/POPIA** (`app/services/`, `app/core/consent_gate.py`, `app/modules/consent/`):
- Consent gate middleware and policy framework
- Consent repository and renewal job
- POPIA service with data subject rights scaffolding
- Consent lifecycle adapters and runtime orchestrators
- Consent expiry service (background loop)
- Consent gate inventory and boundary matrix docs

**Audit** (`app/core/audit.py`, `app/repositories/repositories.py`):
- `FourthEstateService` with append-only audit trail
- Audit repository using PostgreSQL
- Backend consolidation diagnostics complete
- Audit callsite inventory and compatibility adapter

**Tests already in place**:
- `tests/unit/test_audit_integrity.py`
- `tests/unit/test_consent_lifecycle.py`
- `tests/unit/test_object_authorization.py`
- `tests/unit/test_authorization_policy.py`
- `tests/unit/test_refresh_token_rotation.py`
- `tests/unit/test_auth_cookie_policy.py`
- `tests/integration/test_rate_limits.py`
- `tests/unit/test_guardian_consent_withdrawal.py`
- `tests/unit/test_popia_erasure_safety.py`
- `tests/popia/test_right_to_erasure.py`
- `tests/popia/test_consent_audit_trail.py`
- Plus many integration tests for POPIA workflows

### Remaining Gaps (from backlog docs)

**PR-003 (Auth/Authorization)** — Unchecked items:
| Item | Priority | Area |
|------|----------|------|
| Auth abuse-path tests (lockout, cooldown, security alerts) | P1 | 3.1 |
| `kid` rotation tests | P1 | 3.3 |
| Emergency revoke-all tests | P1 | 3.3 |
| Frontend token-storage audit (access token in localStorage?) | P0 | 3.4 |
| Cookie policy tests (HttpOnly, Secure, SameSite, Path) | P1 | 3.4 |
| Route policy matrix (every route's auth/role/consent requirements) | P1 | 3.5 |
| Teacher authorization tests (assigned learners only) | P0 | 3.6 |
| Support-operator PII boundary tests | P0 | 3.6 |
| Compliance-auditor boundary tests | P0 | 3.6 |
| Policy-based authorization for sensitive workflows | P1 | 3.6 |
| Rate-limit tests | P1 | 3.7 |

**PR-004 (POPIA/Privacy)** — Unchecked items:
| Item | Priority | Area |
|------|----------|------|
| Consent lifecycle flows (grant, deny, withdraw, renew, expiry states) | P0 | 4.1 |
| Consent state machine (pending/granted/denied/expired/withdrawn/renewal_required) | P0 | 4.1 |
| Consent enforcement for analytics, RLHF, parent reports, data export, erasure | P0 | 4.2 |
| Data subject rights: export (create, status, download, JSON, CSV) | P0 | 4.3 |
| Data subject rights: erasure (request, status, approval, execution with audit retention) | P0 | 4.3 |
| Data subject rights: correction/update workflow | P0 | 4.3 |
| Data subject rights: processing restriction workflow | P0 | 4.3 |
| Data subject rights: SLA tracking for export/erasure | P0 | 4.3 |
| Data minimization & inventory (`docs/data_inventory.md`) | P0 | 4.4 |
| Data retention policy (`docs/data_retention_policy.md`) | P1 | 4.4 |
| Subprocessor register (`docs/subprocessor_register.md`) | P1 | 4.4 |
| Audit integrity: event hash + previous hash + HMAC chain | P0 | 4.5 |
| Audit integrity: append-only enforcement (DB-level) | P0 | 4.5 |
| Audit events: missing event types (consent, learner CRUD, diagnostic, lesson, LLM, export, erasure, admin access, billing) | P0 | 4.5 |
| Audit-chain verification script | P0 | 4.5 |
| Immutable retention rules (legal hold, purge-after-TTL) | P1 | 4.5 |
| Security Disclosure Policy (`SECURITY.md` review) | P0 | 4.6 |
| DPIA-style privacy impact assessment | P1 | 4.6 |
| Legal review status markers | P1 | 4.6 |
| CI gates for authorization and privacy boundaries | P1 | C.1/C.2 |
| Coverage gates (80%+ on authorization, consent, audit modules) | P1 | C.3 |

---

## Execution Plan

The work splits into three tracks that can proceed partly in parallel:

### Track A — Authorization Completion (PR-003 gaps)

#### A.1 — Auth Abuse-Path Tests [P1]
- [ ] Write test: account lockout after `_MAX_FAILED_ATTEMPTS` consecutive failures
- [ ] Write test: lockout resets after cooldown or admin unlock
- [ ] Write test: security alert event emitted on suspicious auth patterns
- **Evidence:** `tests/unit/test_auth_abuse_paths.py`
- **Files:** `app/services/auth_service.py`

#### A.2 — JWT `kid` Rotation Tests [P1]
- [ ] Write test: token signed with `CURRENT_KID` verifies under current key
- [ ] Write test: token signed with `PREVIOUS_KID` verifies during overlap window
- [ ] Write test: unknown `kid` in token header raises appropriate error
- [ ] Write test: after rotation, new tokens use the new `kid`
- **Evidence:** `tests/unit/test_token_rotation.py`
- **Files:** `app/core/token_config.py`

#### A.3 — Emergency Revoke-All Tests [P1]
- [ ] Write test: `emergency_revoke_all` invalidates all existing tokens
- [ ] Write test: tokens created after revoke-all are not pre-emptively invalidated
- [ ] Write test: revoke-all is idempotent
- **Evidence:** `tests/unit/test_emergency_revocation.py`
- **Files:** `app/core/token_config.py`

#### A.4 — Cookie Policy Tests [P1]
- [ ] Write test: refresh cookie is `HttpOnly`
- [ ] Write test: refresh cookie is `Secure` in production context
- [ ] Write test: refresh cookie has correct `SameSite` value
- [ ] Write test: cookie `Path` is scoped to `/api/auth`
- [ ] Write test: no access token stored in JavaScript-accessible storage (backend response verification)
- **Evidence:** `tests/unit/test_cookie_policy.py` (extends existing `test_auth_cookie_policy.py`)
- **Files:** `app/core/cookies.py`

#### A.5 — Frontend Token-Storage Audit [P0]
- [ ] Audit frontend code for insecure access-token storage
- [ ] Ensure access tokens are never stored in `localStorage` or `sessionStorage` directly readable by JS
- [ ] Fix any violations (move to `httpOnly` cookie or in-memory only)
- **Evidence:** `docs/security/frontend_token_storage_audit.md`

#### A.6 — Route Policy Matrix [P1]
- [ ] Generate a complete route-policy matrix documenting:
  - Every public route
  - Every authenticated route
  - Required role for each route
  - Required consent gate for each route
  - Object-level authorization helper for each learner-data route
- [ ] Add CI check that matrix stays in sync with router registration
- **Evidence:** `docs/security/route_policy_matrix.md`

#### A.7 — Missing Authorization Tests [P0/P1]
- [ ] Test: teacher can access only assigned learners/classes
- [ ] Test: support operator cannot view unnecessary PII
- [ ] Test: compliance auditor can view audit records without broad data mutation rights
- [ ] Item-level reconciliation: ensure every learner-data router calls the correct `can_*` policy helper
- [ ] Consolidate existing wiring tests into a single self-auditing registry
- **Evidence:** `tests/unit/test_teacher_authorization.py`, `tests/unit/test_support_pii_boundary.py`, `tests/unit/test_compliance_auditor_boundary.py`

#### A.8 — Rate-Limit Tests [P1]
- [ ] Test: login rate limit enforced after N rapid attempts
- [ ] Test: signup rate limit enforced
- [ ] Test: refresh rate limit enforced
- [ ] Test: password reset rate limit enforced
- [ ] Test: account-level throttling activates after repeated failures
- **Evidence:** Extend `tests/integration/test_rate_limits.py`

---

### Track B — POPIA/Privacy Completion (PR-004 gaps)

#### B.1 — Consent Lifecycle State Machine [P0]
- [ ] Implement consent state machine: `pending → granted/denied → withdrawn/expired/renewal_required`
- [ ] Tie consent to privacy notice version and guardian identity
- [ ] Implement consent denial flow: create `denied` record with reason
- [ ] Implement consent withdrawal flow: state transition with audit
- [ ] Implement consent renewal flow: re-grant with new version
- [ ] Implement restricted mode after consent expiry
- [ ] Add tests for every state transition
- **Files:** `app/domain/consent.py`, `app/services/consent_service.py`, `app/repositories/consent_repository.py`
- **Evidence:** `tests/unit/test_consent_lifecycle.py` (extend)

#### B.2 — Missing Consent Enforcement Tests [P0]
- [ ] Negative test: analytics processing without consent
- [ ] Negative test: RLHF feedback without consent
- [ ] Negative test: parent reports without consent
- [ ] Negative test: data export without consent/authority
- [ ] Negative test: erasure request without authority
- **Evidence:** Extend `tests/unit/` with consent-gate wiring tests

#### B.3 — Data Subject Rights: Export [P0]
- [ ] Implement data export request creation endpoint
- [ ] Implement data export status endpoint
- [ ] Implement data export download endpoint
- [ ] Machine-readable JSON export format
- [ ] Machine-readable CSV export format
- [ ] Guardian-friendly PDF export summary [P1]
- [ ] SLA tracking for export requests
- [ ] Notification to guardian when export is ready [P1]
- **Files:** `app/api_v2_routers/popia.py`, `app/services/popia_service.py`, `app/repositories/`
- **Evidence:** `tests/integration/test_data_export_lifecycle.py`

#### B.4 — Data Subject Rights: Erasure [P0]
- [ ] Implement erasure request creation endpoint
- [ ] Implement erasure status endpoint
- [ ] Implement erasure approval/review queue
- [ ] Implement erasure execution with audit-retention exceptions
- [ ] Legal-hold check before erasure
- [ ] SLA tracking for erasure requests
- [ ] Admin review queue for billing/school/legal-retention conflicts [P1]
- [ ] Notification to guardian when erasure completes [P1]
- **Files:** `app/api_v2_routers/popia.py`, `app/services/popia_service.py`
- **Evidence:** `tests/integration/test_erasure_lifecycle.py`

#### B.5 — Data Subject Rights: Correction and Restriction [P0]
- [ ] Implement correction/update workflow endpoint
- [ ] Implement processing restriction workflow endpoint
- [ ] Tests for both workflows
- **Files:** `app/api_v2_routers/popia.py`
- **Evidence:** Extend existing `tests/integration/test_popia_correction_request_authorization.py`, `tests/integration/test_popia_restriction_request_authorization.py`

#### B.6 — Data Inventory and Minimization [P0]
- [ ] Create `docs/data_inventory.md` listing:
  - Every collected learner, guardian, diagnostic, lesson/AI, billing field
  - Purpose, lawful/consent basis, retention period, access roles, third-party exposure
- [ ] Review and remove non-essential data fields
- [ ] Hash or tokenize identifiers where raw values are unnecessary
- [ ] Separate identifiable operational data from analytics data
- [ ] Ensure no names/emails/phone numbers/raw identifiers reach LLM prompts
- **Files:** `docs/data_inventory.md`, `docs/data_retention_policy.md`, `docs/subprocessor_register.md`

#### B.7 — Audit Integrity [P0]
- [ ] Confirm sensitive events write to append-only PostgreSQL audit repository (verify `audit_log` table has no UPDATE/DELETE from application role)
- [ ] Prevent application update/delete operations on audit records (DB-level permissions or `BEFORE` trigger that rejects writes)
- [ ] Add `event_hash` column to audit records (SHA-256 of concatenated event fields)
- [ ] Add `previous_event_hash` column to audit records (chained hash)
- [ ] Add HMAC/signature over `event_hash` with server-side secret
- [ ] Add audit-chain verification script (`scripts/verify_audit_chain.py`)
- [ ] Implement missing audit events:
  - [ ] Login success / failure
  - [ ] Token refresh
  - [ ] Logout
  - [ ] Consent grant / renewal / withdrawal / expiry
  - [ ] Learner profile create / update / delete
  - [ ] Diagnostic start / answer submission / completion
  - [ ] Lesson generation / LLM provider call
  - [ ] Parent report generation
  - [ ] Data export request / download
  - [ ] Erasure request / execution
  - [ ] Admin access (privileged read of learner data)
  - [ ] Billing changes
- [ ] Add immutable retention rules (legal hold flag, purge-after-TTL only via admin script)
- **Files:** `app/core/audit.py`, `app/models/audit.py`, `scripts/verify_audit_chain.py`
- **Evidence:** `tests/unit/test_audit_integrity.py` (extend), Alembic migration for new columns

#### B.8 — Legal / Privacy Documentation [P0/P1]
- [ ] Review `SECURITY.md` — verify it covers disclosure expectations
- [ ] Complete DPIA-style privacy impact assessment (`docs/legal/privacy_impact_assessment.md`) [P1]
- [ ] Add legal review-status section to each privacy doc [P1]
- **Files:** `SECURITY.md`, `docs/legal/privacy_impact_assessment.md`

---

### Track C — CI / Evidence Gates

#### C.1 — Authorization Boundary CI [P1]
- [ ] Add/update `.github/workflows/auth-boundary.yml` to run new authorization tests
- [ ] Add route-policy-matrix staleness check to CI

#### C.2 — Privacy Boundary CI [P1]
- [ ] Update `.github/workflows/privacy-boundary.yml` to run consent-lifecycle and audit-integrity tests
- [ ] Add data-inventory staleness check

#### C.3 — Coverage Gates [P1]
- [ ] Verify 80%+ unit-test coverage on `app/core/authorization.py`
- [ ] Verify 80%+ unit-test coverage on `app/modules/consent/`
- [ ] Verify 80%+ unit-test coverage on `app/core/audit.py`

---

## Execution Order

1. **A.1–A.4, A.8** (auth tests) — isolated, low-risk, fast to write
2. **A.5** (frontend token audit) — quick audit + potential fix
3. **A.7** (missing authorization tests) — broadens existing test matrix
4. **A.6** (route policy matrix) — depends on understanding all routes
5. **B.1** (consent lifecycle) — core privacy domain, high priority
6. **B.2** (consent enforcement tests) — depends on B.1
7. **B.3–B.5** (data subject rights APIs) — new endpoints, moderate scope
8. **B.7** (audit integrity) — foundational, do before B.3–B.5 if possible
9. **B.6** (data inventory) — documentation, iterative across tracks
10. **B.8** (legal docs) — documentation, iterative
11. **C.1–C.3** (CI gates) — after all code changes

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 8 execution plan | `docs/roadmap/execution/phase_8_execution_plan.md` | ✅ (this file) |
| Phase 8 implementation report | `docs/roadmap/execution/phase_8_implementation_report.md` | ✅ Present; refreshed 2026-06-14 |
| Phase 8 evidence | `docs/release/phase_8_evidence.md` | ✅ Present; refreshed 2026-06-14 |
| Phase 8 implementation audit | `docs/release/phase_8_implementation_audit.md` | ✅ Present; refreshed 2026-06-14 |
| Route policy matrix | `docs/security/route_policy_matrix.md` | ✅ Present |
| Frontend token-storage audit | `docs/security/frontend_token_storage_audit.md` | ✅ Present |
| Data inventory | `docs/data_inventory.md` | ❌ Pending |
| Data retention policy | `docs/data_retention_policy.md` | ❌ Pending |
| Subprocessor register | `docs/subprocessor_register.md` | ❌ Pending |
| Privacy impact assessment | `docs/legal/privacy_impact_assessment.md` | ❌ Pending |

---

## Success Criteria

**Phase 8 is complete when:**

### Track A (Authorization)
- [ ] Auth abuse-path tests pass: lockout, cooldown, security alerts
- [ ] `kid` rotation tests pass: CURRENT, PREVIOUS, unknown
- [ ] Emergency revoke-all tests pass: invalidation, new-token, idempotency
- [ ] Cookie policy tests pass: HttpOnly, Secure, SameSite, Path, JS-inaccessibility
- [ ] Frontend token-storage audit committed, no violations found or all fixed
- [ ] Route policy matrix generated and CI-staleness-checked
- [ ] Teacher, support-operator, and compliance-auditor boundary tests pass
- [ ] Rate-limit tests pass for all auth endpoints

### Track B (POPIA/Privacy)
- [ ] Consent state machine fully implemented with tests for all transitions
- [ ] Consent enforcement tests cover analytics, RLHF, parent reports, data export, erasure
- [ ] Data subject rights APIs implemented: export (create/status/download JSON+CSV), erasure (request/status/execution), correction, restriction
- [ ] Data inventory, retention policy, and subprocessor register committed
- [ ] Audit integrity: event hash chain, append-only enforcement, HMAC, verification script
- [ ] All missing audit events implemented (login, consent, learner CRUD, diagnostic, lesson, LLM, export, erasure, admin, billing)
- [ ] Legal docs reviewed and DPIA drafted

### Track C (CI)
- [ ] Authorization boundary CI job runs new auth tests
- [ ] Privacy boundary CI job runs consent and audit tests
- [ ] 80%+ coverage on authorization, consent, and audit modules

### RoadMap alignment (from [roadmap.md](../roadmap.md#L328-L355))
- [ ] POPIA workflows enforce legal hold and export preconditions
- [ ] Erasure/export requests create auditable state transitions
- [ ] Authorization tests fail closed when repository checks deny access

---

## Known Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Consent lifecycle changes may affect existing data | Write additive migration; backfill missing states via script |
| Audit hash chain requires schema migration | Use Alembic with nullable new columns; backfill after deploy |
| Frontend token audit may reveal violations | Fix immediately; document rationale in audit report |
| Legal review is external dependency | Draft docs first; mark review status clearly |
| Data inventory is large (many fields) | Start with high-risk categories (PII, health, minors) |

---

## Close Checklist

- [x] Execution plan exists: `docs/roadmap/execution/phase_8_execution_plan.md` (this file)
- [x] Implementation report exists: `docs/roadmap/execution/phase_8_implementation_report.md`
- [x] Audit report exists: `docs/release/phase_8_implementation_audit.md`
- [x] Evidence files committed and accurate for implemented scope
- [ ] `roadmap.md` Phase 8 status updated to "Complete (YYYY-MM-DD)"
- [ ] `context/build-plan.md` Phase 8 status updated
- [ ] `context/progress-tracker.md` updated
- [ ] `docs/todos/todo.md` updated
- [x] Branch merged to `master` via PR
- [ ] Remote branch deleted after merge

---

## Next Phase

**Phase 9: Coverage, CI, and Evidence Renewal** — Regenerate coverage, enforce release checks, consolidate route registration to single prefix, clean dormant routers.
