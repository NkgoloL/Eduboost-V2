# PR-004 Summary: Auth, Authorization, and POPIA Runtime Hardening

**Date:** 2026-06-01
**Branch:** `pr-004-auth-authorization-popia-hardening`
**Status:** Phases 0-4 Complete, Phase 5 Pending

---

## Objective

Address P0 and P1 blockers identified in the May 2026 audit:
- POPIA consent lifecycle runtime alignment
- Lesson object authorization gaps
- Router-level auth logic with inconsistent token claims
- Duplicate service implementations
- Test coverage below CI threshold

---

## Completed Work

### Phase 0: Audit Evidence Lock ✅
- **Commit:** `3e9ae461` - Audit summary committed
- **Commit:** `5b8b5dbe` - Risk register and inventory docs added
- **Deliverables:**
  - `audits/reports/Comprehensive_Audit_Summary_2026-06-01.md`
  - `docs/release/RC_BACKEND_RISK_REGISTER.md`
  - `docs/release/PR-004_auth_inventory.md`
  - `docs/release/PR-004_lesson_inventory.md`
  - `docs/release/PR-004_consent_inventory.md`

### Phase 1: Auth Claim Normalization ✅
- **Commit:** `c1372c2a` - AuthContext and lesson authorization policies
- **Deliverables:**
  - `app/api_v2_deps/auth.py` - Canonical AuthContext dependency
  - `tests/unit/test_auth_context_claims.py` - Auth context tests
- **Features:**
  - Typed `AuthContext` with normalized JWT claims
  - Role parsing (single/multiple, string/enum)
  - Issuer and audience validation
  - Token type validation
  - Convenience properties (is_admin, is_parent, etc.)
  - Backward compatibility layer (`get_current_user_compat`)
  - Role-based dependencies (`require_admin`, `require_parent_or_admin`, etc.)

### Phase 2: Lesson Object-Level Authorization ✅
- **Commit:** `c1372c2a` - AuthContext and lesson authorization policies
- **Deliverables:**
  - `app/security/authorization.py` - Authorization policy functions
  - `tests/unit/test_lesson_object_authorization.py` - Authorization tests
- **Features:**
  - `can_access_lesson()` - Lesson read access policy
  - `can_write_lesson()` - Lesson write access policy
  - `can_access_learner()` - Learner read access policy
  - `can_write_learner()` - Learner write access policy
  - `require_*()` helpers for route-level enforcement
  - Admin bypass for all operations
  - Guardian relationship checks (placeholder for repository)
  - Teacher assignment checks (placeholder for repository)

### Phase 3: POPIA Consent Lifecycle Runtime Alignment ✅
- **Commit:** `f22e7b13` - Consent lifecycle already resolved
- **Finding:** Already resolved in current codebase
- **Evidence:**
  - Router uses `app.api_v2_deps.consent_lifecycle.get_canonical_consent_service`
  - Returns `POPIAConsentLifecycleAdapter` wrapping canonical service
  - Canonical service uses SQLAlchemy aggregate repository
  - ARQ job uses `app.services.job_dependency_factory.build_consent_service_for_job`
  - Versioning logic already present in canonical service
  - Audit events already integrated
- **Action:** Updated documentation to reflect resolved status

### Phase 4: Duplicate Service Cleanup ✅
- **Commit:** `5bf69d10` - Duplicate service inventory
- **Deliverables:**
  - `docs/release/PR-004_duplicate_service_inventory.md`
- **Inventory:**
  - 8 duplicate service/repository pairs identified
  - Canonical selections documented
  - Migration plan outlined (archiving, not deletion)
- **Duplicates to Archive:**
  1. `app/services/auth_service.py` → `app/services/archived/auth_service.py`
  2. `app/services/consent_service.py` → `app/services/archived/consent_service.py`
  3. `app/services/lesson_service_v2.py` → `app/services/archived/lesson_service_v2.py`
  4. `app/services/diagnostic_session_service.py` → `app/services/archived/diagnostic_session_service.py`
  5. `app/services/ether_service.py` → `app/services/archived/ether_service.py`
  6. `app/services/stripe_service.py` → `app/services/archived/stripe_service.py`
  7. `app/repositories/audit_repository.py` → `app/repositories/archived/audit_repository.py`
  8. `app/repositories/consent_repository.py` → `app/repositories/archived/consent_repository.py`

---

## Pending Work

### Phase 5: Coverage Recovery (60%+) ⏳
- **Current Coverage:** 57.5% (below 60% CI threshold)
- **Target:** 60% minimum, 62-65% preferred
- **Strategy:**
  - Run new tests for AuthContext and authorization
  - Target high-yield files with business risk
  - Focus on blocker-related code paths
- **Blocker:** Test environment not configured in current session

---

## Risk Register Updates

### P0 Blockers Resolved
1. ✅ POPIA consent lifecycle runtime alignment (already resolved)
2. ⏳ Lesson object authorization (policies created, integration pending)
3. ⏳ Router-level auth logic (AuthContext created, migration pending)
4. ⏳ Duplicate services (inventory complete, migration pending)

### P1 Gaps Addressed
1. ✅ JWT iss/aud claims (added to AuthContext validation)
2. ⏳ Minimum key length enforcement (not yet implemented)
3. ⏳ Test coverage below threshold (Phase 5 pending)

---

## Next Steps

### Immediate (Requires Test Environment)
1. Run test suite to verify new tests pass
2. Check coverage impact of new tests
3. Add additional tests to reach 60% threshold

### Short-term (Code Integration)
1. Migrate lesson routes to use new authorization policies
2. Migrate auth routes to use AuthContext
3. Archive duplicate services per inventory
4. Update imports to use canonical services

### Medium-term (Future PRs)
1. Implement guardian relationship repository checks
2. Implement teacher assignment repository checks
3. Add minimum key length enforcement
4. Migrate remaining V2 services to module pattern

---

## Files Modified

### New Files
- `app/api_v2_deps/auth.py` (210 lines)
- `app/security/authorization.py` (210 lines)
- `tests/unit/test_auth_context_claims.py` (280 lines)
- `tests/unit/test_lesson_object_authorization.py` (350 lines)
- `docs/release/RC_BACKEND_RISK_REGISTER.md` (140 lines)
- `docs/release/PR-004_auth_inventory.md` (180 lines)
- `docs/release/PR-004_lesson_inventory.md` (200 lines)
- `docs/release/PR-004_consent_inventory.md` (350 lines)
- `docs/release/PR-004_duplicate_service_inventory.md` (210 lines)

### Updated Files
- `audits/reports/Comprehensive_Audit_Summary_2026-06-01.md` (committed)

---

## Commits

1. `3e9ae461` - Audit: summarize May 2026 readiness findings
2. `5b8b5dbe` - PR-004 Phase 0-3: add risk register and inventory docs
3. `c1372c2a` - PR-004 Phase 1-2: add AuthContext and lesson authorization policies
4. `f22e7b13` - PR-004 Phase 3: consent lifecycle already resolved, update docs
5. `5bf69d10` - PR-004 Phase 4: add duplicate service inventory

---

## Success Criteria

- ✅ Audit summary committed and risk register created
- ✅ Auth context dependency created with tests
- ✅ Lesson authorization policies created with tests
- ✅ POPIA consent lifecycle verified as resolved
- ✅ Duplicate services inventoried with migration plan
- ⏳ Coverage raised to 60%+ (pending test environment)
- ⏳ Routes migrated to use new dependencies (pending)
- ⏳ Duplicate services archived (pending)

---

**Last Updated:** 2026-06-01
**Ready for Review:** Phases 0-4 complete, Phase 5 requires test environment
