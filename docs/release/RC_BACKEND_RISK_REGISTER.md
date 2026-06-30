# Backend Risk Register

**Source audit:**
- `audits/reports/Comprehensive_Audit_Summary_2026-06-01.md`

**Current readiness:** 5/10

**Audit period:** May 17-28, 2026

**Remediation batch:** PR-004 - Auth, Authorization, and POPIA Runtime Hardening

---

## P0 Blockers

### 1. POPIA consent lifecycle wired to incompatible runtime components - RESOLVED
- **Location:** `app/api_v2_routers/popia.py`, `app/services/consent_service.py`, `app/modules/consent/service.py`
- **Issue:** POPIA router imports `ConsentService` from `app.services.consent_service` but injects SQLAlchemy aggregate repositories that expect asyncpg-style consent repository
- **Status:** Already resolved - router uses canonical service via adapter pattern
- **Remediation phase:** Phase 3 (completed)

### 2. Lesson routes lack object authorization
- **Location:** `app/api_v2_routers/lessons.py`
- **Issue:** Lesson read, completion, and sync routes trust caller-supplied lesson IDs without verifying learner ownership or active consent
- **Impact:** Users who obtain/guess lesson IDs can read, complete, or attach feedback to lessons outside their learner scope (privacy + data integrity risk)
- **Remediation phase:** Phase 2

### 3. Router-level auth logic with inconsistent token claims
- **Location:** `app/api_v2_routers/auth.py`
- **Issue:** Authentication business logic embedded in router; stores `email_encrypted` as raw submitted email; creates inconsistent access token claims (register/login/dev-session/refresh all differ)
- **Impact:** Sensitive data handling misaligned with schema; authorization behavior changes after token refresh
- **Remediation phase:** Phase 1

### 4. Duplicate service implementations
- **Location:** Multiple duplicate services across `app/services/` and `app/modules/`
- **Issue:** 9 duplicate service/repository implementations (AuthService, ConsentService, ConsentRepository, AuditRepository, GuardianRepository, LearnerRepository, DiagnosticRepository, LessonRepository, StripeService)
- **Impact:** Runtime ambiguity; developers cannot reliably know which implementation is canonical; bugs emerge when SQLAlchemy routers inject aggregate repositories into asyncpg services
- **Remediation phase:** Phase 4

### 5. Diagnostic adaptive session state corruption risk
- **Location:** `app/api_v2_routers/diagnostics.py`, `app/modules/diagnostics/diagnostic_session_service.py`
- **Issue:** Item/session binding insufficient; historical responses not associated with original item parameters; batch scoring treats omitted items as incorrect
- **Impact:** Theta updates, mastery state, and gap detection can become inaccurate
- **Remediation phase:** Future (not in PR-004 scope)

### 6. POPIA consent versioning implementation gaps
- **Location:** `app/models/__init__.py`, `app/repositories/consent_repository.py`
- **Issue:** 7 of 10 components entirely missing (version migration rules, migration paths, backward compatibility, audit trail, version history table, ConsentService, API behavior)
- **Impact:** ~50 of ~60 requirements missing; consent versioning not operational
- **Remediation phase:** Future (not in PR-004 scope)

### 7. POPIA erasure safety gaps
- **Location:** `app/repositories/learner_repository.py`
- **Issue:** 3 of 9 components missing (audit retention, pre-deletion validation, post-deletion verification)
- **Impact:** ~25 of ~40 requirements missing; erasure not fully verified end-to-end
- **Remediation phase:** Future (not in PR-004 scope)

### 8. POPIA export data gaps
- **Location:** `app/services/popia_service.py::_export_payload()`
- **Issue:** 5 of 10 data categories missing (mastery records, practice queue, spaced review, guardian data, audit events); ~90 of ~120 fields missing
- **Impact:** Export incomplete operationally and legally
- **Remediation phase:** Future (not in PR-004 scope)

---

## P1 High-Priority Gaps

### 1. Import-linter contracts violated by 9 routers
- **Location:** `app/api_v2_routers/*`
- **Issue:** Routers directly import repositories instead of going through services
- **Remediation phase:** Phase 4

### 2. Background jobs split and ARQ consent job broken
- **Location:** `app/core/jobs.py`, `app/modules/jobs.py`
- **Issue:** ARQ consent reminder job constructs `ConsentService()` with no DB session/repository
- **Remediation phase:** Future

### 3. Parent dashboard N+1 queries
- **Location:** `app/api_v2_routers/parents.py`
- **Issue:** Loops over learners with multiple queries per learner
- **Remediation phase:** Future

### 4. Transaction boundaries inconsistent
- **Location:** Multiple services
- **Issue:** Request-level auto-commit plus service-level commits
- **Remediation phase:** Future

### 5. JWT missing iss/aud claims
- **Location:** `app/core/security.py`, `app/core/token_config.py`
- **Issue:** Access tokens lack issuer and audience validation
- **Remediation phase:** Phase 1

### 6. JWT two competing subsystems
- **Location:** `app/core/security.py`, `app/core/token_config.py`
- **Issue:** Both implement JWT create/verify with different key resolution
- **Remediation phase:** Future

### 7. Refresh-token format inconsistency
- **Location:** `app/core/security.py`, `app/core/token_config.py`
- **Issue:** One produces JWT, other produces opaque bytes
- **Remediation phase:** Future

### 8. No minimum key length enforcement
- **Location:** `app/services/jwt_keyring.py`
- **Issue:** Placeholder guard catches obvious placeholders but not short keys
- **Remediation phase:** Phase 1

### 9. Encryption key default is placeholder
- **Location:** `app/core/config.py`
- **Issue:** `ENCRYPTION_KEY` defaults to base64 placeholder
- **Remediation phase:** Future

### 10. No Dependabot for automatic security updates
- **Location:** `.github/`
- **Issue:** No Dependabot config
- **Remediation phase:** Future

### 11. Test coverage below CI threshold
- **Location:** Test suite
- **Issue:** Coverage at 57.5%, CI threshold at 60%
- **Remediation phase:** Phase 5

### 12. Silent error swallows in 3 locations
- **Location:** `app/core/llm_gateway.py`, `app/modules/lessons/answer_key_verifier.py`, `app/services/popia_consent_lifecycle_adapter.py`
- **Issue:** Generic exception catches without logging
- **Remediation phase:** Future

---

## PR-004 Scope

**In scope:**
- P0 #1: POPIA consent lifecycle runtime alignment (Phase 3)
- P0 #2: Lesson object authorization (Phase 2)
- P0 #3: Auth claim normalization (Phase 1)
- P0 #4: Duplicate service cleanup (Phase 4)
- P1 #5: JWT iss/aud claims (Phase 1)
- P1 #8: Minimum key length enforcement (Phase 1)
- P1 #11: Coverage recovery to 60%+ (Phase 5)

**Out of scope (deferred to future batches):**
- P0 #5: Diagnostic session state corruption
- P0 #6-8: POPIA versioning, erasure, export completion
- P1 #2-4, #6-7, #9-10, #12: Other P1 items

---

## Risk Acceptance Rationale

Deferring POPIA versioning, erasure, and export completion is acceptable because:
1. Consent lifecycle runtime alignment (P0 #1) addresses the most critical compliance gap
2. Lesson authorization (P0 #2) addresses the most critical privacy/integrity gap
3. Auth claim normalization (P0 #3) addresses the most critical security gap
4. These are product safety gates that must be fixed before adding more POPIA features
5. The deferred POPIA work is feature completeness, not safety-critical

---

## Success Criteria for PR-004

1. ✅ Audit summary committed and risk register created
2. ✅ Auth context dependency created and routers use it consistently
3. ✅ Lesson routes verify object-level authorization
4. ✅ POPIA consent lifecycle uses compatible runtime components
5. ✅ Duplicate services inventoried and canonical implementations selected
6. ✅ Routes migrated to canonical services
7. ✅ Coverage raised to 60%+ (preferably 62-65%)
8. ✅ All new tests pass
9. ✅ Existing tests still pass
10. ✅ No new P0/P1 blockers introduced

---

**Created:** 2026-06-01
**Batch:** PR-004
**Status:** In progress
