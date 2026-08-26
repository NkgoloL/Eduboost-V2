# EduBoost V2 Authentication, Authorization, and Session Security

Maps registration, login, refresh rotation, key management, revocation, RBAC, and object-level authorization.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/api_v2_routers/auth*.py`
- `app/services/auth*`
- `app/core/security.py`
- `app/core/authorization.py`
- `app/core/rbac.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Registration and login transaction

**Description:** Follows credential intake through validation, user persistence, audit recording, and access/refresh token issuance.

**Motivation:**
Authentication is the root trust boundary for learner, guardian, administrator, and service actions.

**Details:**

**Execution path**

1. Validate registration or login payload.
2. Normalize identity and enforce password policy.
3. Open an atomic user or session transaction.
4. Verify password and lockout state.
5. Build canonical token claims.
6. Issue tokens and record the security event.

**State and ownership boundaries**

User records, password hashes, lockout counters, and refresh-token families are authoritative server state.

**Failure, privacy, and control points**

Registration is atomic, passwords are never logged, failure messages resist account enumeration, and audit writes accompany state changes.

**Verification signals**

Run transactional registration, login, lockout, token-claim, and auth-boundary tests.

**Trace text diagram:**
```text
1. Validate registration or login payload [1a]
   |
   v
2. Normalize identity and enforce password policy [1b]
   |
   v
3. Open an atomic user or session transaction [1c]
   |
   v
4. Verify password and lockout state [1d]
   |
   v
5. Build canonical token claims [1d]
   |
   v
6. Issue tokens and record the security event [1d]
```

**Location ID: 1a**
- **Title:** Auth endpoints
- **Description:** Public registration and login entry points.
- **Path:LineNumber:** app/api_v2_routers/auth.py:84

**Location ID: 1b**
- **Title:** Transactional registration
- **Description:** Atomic identity creation.
- **Path:LineNumber:** app/services/auth_transactional_registration.py:10

**Location ID: 1c**
- **Title:** Authentication application service
- **Description:** Use-case orchestration.
- **Path:LineNumber:** app/services/auth_application_service.py:42

**Location ID: 1d**
- **Title:** Password policy
- **Description:** Credential-strength enforcement.
- **Path:LineNumber:** app/core/password_policy.py:25

### AI Guide: Registration and login transaction

**Motivation:**
Authentication is the root trust boundary for learner, guardian, administrator, and service actions.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors auth endpoints. [1b] anchors transactional registration. [1c] anchors authentication application service. [1d] anchors password policy.

**Safe change boundary.** User records, password hashes, lockout counters, and refresh-token families are authoritative server state. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Registration is atomic, passwords are never logged, failure messages resist account enumeration, and audit writes accompany state changes.

**How to verify the change.** Run transactional registration, login, lockout, token-claim, and auth-boundary tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Access token verification and refresh rotation

**Description:** Maps JWT creation, key selection, request verification, single-use refresh rotation, and revocation.

**Motivation:**
Short-lived access tokens and controlled refresh rotation reduce replay risk while preserving usable sessions.

**Details:**

**Execution path**

1. Create access token with canonical claims and active key ID.
2. Verify signature, issuer, audience, expiry, and token type.
3. Check token and subject revocation state.
4. Accept a valid refresh token family member.
5. Rotate refresh token and invalidate the predecessor.
6. Return a new token pair or fail closed.

**State and ownership boundaries**

Key rings, refresh-token family state, and revocation entries are separate security authorities.

**Failure, privacy, and control points**

Unknown keys, reused refresh tokens, expired families, and revoked subjects fail closed; rotation is transactionally consistent.

**Verification signals**

Run keyring, token verification, refresh reuse, family revocation, and production guard tests.

**Trace text diagram:**
```text
1. Create access token with canonical claims and active key ID [2a]
   |
   v
2. Verify signature, issuer, audience, expiry, and token type [2b]
   |
   v
3. Check token and subject revocation state [2c]
   |
   v
4. Accept a valid refresh token family member [2d]
   |
   v
5. Rotate refresh token and invalidate the predecessor [2d]
   |
   v
6. Return a new token pair or fail closed [2d]
```

**Location ID: 2a**
- **Title:** JWT security
- **Description:** Access token construction and verification.
- **Path:LineNumber:** app/core/security.py:44

**Location ID: 2b**
- **Title:** JWT key ring
- **Description:** Active and historical signing-key selection.
- **Path:LineNumber:** app/services/jwt_keyring.py:25

**Location ID: 2c**
- **Title:** Refresh token lifecycle
- **Description:** Storage and rotation semantics.
- **Path:LineNumber:** app/core/refresh_tokens.py:24

**Location ID: 2d**
- **Title:** Revocation service
- **Description:** Token and subject invalidation.
- **Path:LineNumber:** app/core/token_revocation.py:27

### AI Guide: Access token verification and refresh rotation

**Motivation:**
Short-lived access tokens and controlled refresh rotation reduce replay risk while preserving usable sessions.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors jwt security. [2b] anchors jwt key ring. [2c] anchors refresh token lifecycle. [2d] anchors revocation service.

**Safe change boundary.** Key rings, refresh-token family state, and revocation entries are separate security authorities. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Unknown keys, reused refresh tokens, expired families, and revoked subjects fail closed; rotation is transactionally consistent.

**How to verify the change.** Run keyring, token verification, refresh reuse, family revocation, and production guard tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Role and object-level authorization

**Description:** Shows how authenticated identity is converted into role, ownership, relationship, and policy decisions.

**Motivation:**
EduBoost handles minors and guardian relationships, so broad role checks alone are insufficient for learner-specific data.

**Details:**

**Execution path**

1. Resolve actor identity and role.
2. Load target resource or relationship context.
3. Apply RBAC and object ownership policy.
4. Apply guardian/learner and consent constraints.
5. Allow the operation or return a non-enumerating denial.
6. Record sensitive decisions where required.

**State and ownership boundaries**

Authorization decisions are request-local but derive from persisted roles, learner relationships, and resource ownership.

**Failure, privacy, and control points**

Frontend guards are advisory only; every protected backend operation performs authoritative checks.

**Verification signals**

Run learner authorization coverage, parent access, cross-tenant denial, and security assurance tests.

**Trace text diagram:**
```text
1. Resolve actor identity and role [3a]
   |
   v
2. Load target resource or relationship context [3b]
   |
   v
3. Apply RBAC and object ownership policy [3c]
   |
   v
4. Apply guardian/learner and consent constraints [3d]
   |
   v
5. Allow the operation or return a non-enumerating denial [3d]
   |
   v
6. Record sensitive decisions where required [3d]
```

**Location ID: 3a**
- **Title:** Authorization policy
- **Description:** Object-level access decisions.
- **Path:LineNumber:** app/core/authorization.py:32

**Location ID: 3b**
- **Title:** RBAC primitives
- **Description:** Role and permission evaluation.
- **Path:LineNumber:** app/core/rbac.py:16

**Location ID: 3c**
- **Title:** Lesson authorization
- **Description:** Domain-specific learner access.
- **Path:LineNumber:** app/services/lesson_authorization.py:41

**Location ID: 3d**
- **Title:** Authorization coverage workflow
- **Description:** Hosted regression gate.
- **Path:LineNumber:** .github/workflows/learner-authz-coverage.yml:1

### AI Guide: Role and object-level authorization

**Motivation:**
EduBoost handles minors and guardian relationships, so broad role checks alone are insufficient for learner-specific data.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors authorization policy. [3b] anchors rbac primitives. [3c] anchors lesson authorization. [3d] anchors authorization coverage workflow.

**Safe change boundary.** Authorization decisions are request-local but derive from persisted roles, learner relationships, and resource ownership. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Frontend guards are advisory only; every protected backend operation performs authoritative checks.

**How to verify the change.** Run learner authorization coverage, parent access, cross-tenant denial, and security assurance tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
