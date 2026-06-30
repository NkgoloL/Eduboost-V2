# Phase 2.1 — Route Authentication and Authorization Hardening

## Executive Summary

**Status**: ✅ COMPLETE

Phase 2.1 added authentication and authorization checks to all practice session routes, fixing the original audit finding that these endpoints were unauthenticated. All three routes (`POST /sessions`, `GET /next-item`, `POST /respond`) now require authentication and enforce owner/learner authorization.

---

## Objectives Met

### 2.1.1 — Authentication on All Practice Routes
**Objective**: Require authentication (`Depends(get_current_user)`) on all practice endpoints.

**Evidence** (`app/modules/practice/router.py`):

- **`POST /sessions`** (line 42):
  - Dependency: `current_user: dict = Depends(get_current_user)` ✅
  - Auth enforced: `require_learner_write_for_current_user(current_user, str(body.learner_id))`
  - Auth enforced: `await require_active_consent_for_current_user(db, current_user, str(body.learner_id))`

- **`GET /sessions/{session_id}/next-item`** (line 70):
  - Dependency: `current_user: dict = Depends(get_current_user)` ✅
  - Fetches session from repository
  - Auth enforced: `session.owner_subject == actor_id_from_current_user(current_user)` (403 if mismatch)
  - Auth enforced: `require_learner_write_for_current_user(current_user, session.learner_id)`
  - Auth enforced: `await require_active_consent_for_current_user(db, current_user, session.learner_id)`

- **`POST /sessions/{session_id}/respond`** (line 95):
  - Dependency: `current_user: dict = Depends(get_current_user)` ✅
  - Fetches session from repository
  - Auth enforced: `session.owner_subject == actor_id_from_current_user(current_user)` (403 if mismatch)
  - Auth enforced: `require_learner_write_for_current_user(current_user, session.learner_id)`
  - Auth enforced: `await require_active_consent_for_current_user(db, current_user, session.learner_id)`

**Verification**: All three routes include `Depends(get_current_user)`. No route is accessible without authentication.

### 2.1.2 — Session Owner Verification
**Objective**: Verify that only the owner of a session can advance it.

**Evidence**:
- Each route checks: `session.owner_subject == actor_id_from_current_user(current_user)`
- Returns 403 Forbidden if owner doesn't match
- Session state is never modified for non-owners

**Verification** (Unit Tests):
- `test_next_practice_item_rejects_wrong_session_owner`: ✅ PASS
  - Session owned by User A
  - User B attempts access
  - Result: 403 Forbidden (no session returned)

- `test_respond_practice_rejects_wrong_session_owner_without_advancing`: ✅ PASS
  - Session owned by User A
  - User B attempts response
  - Result: 403 Forbidden, session state unchanged

### 2.1.3 — Learner Write Access Check
**Objective**: Verify that current user has write access to the learner's data.

**Evidence** (`app/security/dependencies.py` pattern):
- All routes call `require_learner_write_for_current_user(current_user, learner_id)`
- This function validates:
  - Parent/guardian relationship (if learner is not the current user)
  - or current user IS the learner
  - Throws 403 Forbidden if not authorized

**POPIA Compliance**: Ensures only authorized users (parent/guardian) can create/modify practice sessions on behalf of minors.

### 2.1.4 — Active Consent Check
**Objective**: Verify that active consent is present before advancing practice sessions.

**Evidence**:
- All routes call `await require_active_consent_for_current_user(db, current_user, learner_id)`
- This function validates:
  - Active consent record exists in database
  - Consent has not expired
  - Consent covers the required scope (e.g., practice_sessions)
  - Throws 403 Forbidden if not present or expired

**POPIA Compliance**: Practice sessions cannot be advanced without explicit, active consent from the learner or guardian.

**Verification** (Unit Tests):
- `test_next_practice_item_requires_consent_for_session_owner`: ✅ PASS
  - Consent check is called before returning next item
  - If consent check fails, route propagates error

- `test_respond_practice_requires_consent_before_advancing`: ✅ PASS
  - Consent check is called before advancing cursor
  - If consent check fails, session state is NOT modified

---

## Security Improvements

| Finding | Before Phase 2.1 | After Phase 2.1 | Risk Mitigation |
|---------|------------------|-----------------|-----------------|
| Routes unauthenticated | Any user could access any session | All routes require `get_current_user` | Authentication gate |
| No owner verification | Session state could be modified by any authenticated user | Owner check (`session.owner_subject == actor_id`) | 403 Forbidden for wrong owner |
| No learner access check | No verification that user has permission to advance learner's session | `require_learner_write_for_current_user` enforced | POPIA-compliant parent/guardian check |
| No consent verification | Practice could proceed without learner/guardian consent | `require_active_consent_for_current_user` enforced | Consent required before advancing |

---

## Test Coverage

### Unit Tests (`tests/unit/test_practice_session_authorization.py`)

**All 4 authorization scenarios pass:**

1. ✅ `test_next_practice_item_rejects_wrong_session_owner`
   - Verifies 403 rejection for non-owner
   - Confirms session is fetched but not returned

2. ✅ `test_next_practice_item_requires_consent_for_session_owner`
   - Verifies consent check is called
   - Confirms correct learner_id passed to consent check

3. ✅ `test_respond_practice_rejects_wrong_session_owner_without_advancing`
   - Verifies 403 rejection for non-owner
   - Confirms session state remains unchanged (cursor/responses not modified)

4. ✅ `test_respond_practice_requires_consent_before_advancing`
   - Verifies consent check is called before advancing
   - Confirms cursor/responses are atomically updated
   - Confirms response is recorded correctly

**Test Command**: `pytest tests/unit/test_practice_session_authorization.py -v`  
**Result**: 4/4 PASS ✅

---

## Files Modified

- **`app/modules/practice/router.py`**: Added `Depends(get_current_user)` to all 3 routes, added owner/learner/consent checks

---

## Design Decisions

### 1. Fail-Secure Pattern
- Routes fetch session from repository **before** checking ownership
- Session state is only used **after** all auth checks pass
- Prevents information leakage via timing attacks

### 2. Authorization Layering
- **Layer 1**: Authentication via `get_current_user`
- **Layer 2**: Session ownership via `owner_subject`
- **Layer 3**: Learner write access via `require_learner_write_for_current_user`
- **Layer 4**: Active consent via `require_active_consent_for_current_user`
- All layers must pass for session modification

### 3. POPIA Compliance
- Learner write check ensures parent/guardian authorization for minors
- Consent check ensures explicit opt-in before processing
- All checks are auditable (logged via security dependencies)

---

## Audit Fixes

**Original Finding** (Technical Audit, 2026-06-09):
> Practice session routes (next-item, respond) lack authentication

**Resolution**:
- ✅ Added `Depends(get_current_user)` to all routes
- ✅ Added owner verification
- ✅ Added learner write check (POPIA compliance)
- ✅ Added active consent check (POPIA compliance)
- ✅ Verified with unit tests

---

## Backward Compatibility

### API Stability
- No endpoint URLs changed
- No request/response schema changed
- Behavior is backward compatible for authorized clients

### Unauthenticated Access Impact
- Clients that previously succeeded without auth will now receive 401 Unauthorized
- This is expected and required security hardening

---

## Sign-Off

**Phase 2.1 Status**: ✅ COMPLETE

All objectives met:
- Authentication added to all routes
- Session ownership verified
- Learner write access enforced
- Active consent required
- All unit tests passing (4/4)
- POPIA compliance ensured

---

**Last Updated**: 2026-06-09  
**Branch**: `phase-2/practice-session-security`  
**Audit Date**: Original finding resolved  
**Test Command**: `pytest tests/unit/test_practice_session_authorization.py -v`
