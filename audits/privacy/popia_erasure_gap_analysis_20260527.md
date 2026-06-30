# POPIA Erasure Implementation Gap Analysis

**Date**: 2026-05-27
**Task**: T111B - POPIA erasure implementation gap analysis
**Source of Truth**: `docs/popia_erasure_cascade_matrix.md`
**Current Implementation**: `app/repositories/learner_repository.py`

## Executive Summary

The current POPIA erasure implementation is **partially implemented**. The repository layer provides soft delete and physical delete methods, but critical safety checks, grace period enforcement, and audit integration are missing.

**Overall Status**: `partially implemented`

**Release Blockers**: Pre-deletion validation, grace period enforcement, audit integration

## Gap Analysis by Component

### 1. Soft Delete (Grace Period)

**Status**: `partially implemented`

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Set is_deleted flag | Yes | Yes | ✅ Implemented |
| Set display_name to "[erased]" | Yes | Yes | ✅ Implemented |
| Set deletion_requested_at timestamp | Yes | Yes | ✅ Implemented |
| Retain dependent records (30 days) | Yes | Yes (no cascade) | ✅ Implemented |
| Grace period: 30 days | Yes | No enforcement | ❌ Missing |
| Recovery within grace period | Yes | No recovery method | ❌ Missing |
| Audit event: erasure.requested | Yes | No audit integration | ❌ Missing |

**Gap Count**: 3 missing features (grace enforcement, recovery, audit)

**Action Required**: Add grace period enforcement, recovery method, audit integration

---

### 2. Physical Delete (Right to Erasure)

**Status**: `partially implemented`

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Use DELETE SQL statement | Yes | Yes | ✅ Implemented |
| CASCADE delete dependent records | Yes | Yes (DB-enforced) | ✅ Implemented |
| Return success/failure | Yes | Yes | ✅ Implemented |
| Pre-deletion validation | Yes | No validation | ❌ Missing |
| Consent status check | Yes | No check | ❌ Missing |
| Grace period check (30 days) | Yes | No check | ❌ Missing |
| Legal hold check | Yes | No check | ❌ Missing |
| Audit event: erasure.requested | Yes | No audit integration | ❌ Missing |
| Audit event: erasure.executed | Yes | No audit integration | ❌ Missing |
| Post-deletion verification | Yes | No verification | ❌ Missing |

**Gap Count**: 7 missing features (validation, consent check, grace check, legal hold, 2 audit events, verification)

**Action Required**: Add pre-deletion validation, consent/grace/legal checks, audit integration, post-deletion verification

---

### 3. Purge Personal Data (Emergency)

**Status**: `partially implemented`

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Use DELETE SQL statement | Yes | Yes | ✅ Implemented |
| CASCADE delete dependent records | Yes | Yes (DB-enforced) | ✅ Implemented |
| Admin authorization required | Yes | No authorization | ❌ Missing |
| Audit event: erasure.executed | Yes | No audit integration | ❌ Missing |
| Override reason logging | Yes | No reason logging | ❌ Missing |

**Gap Count**: 3 missing features (authorization, audit, reason logging)

**Action Required**: Add admin authorization, audit integration, reason logging

---

### 4. Cascade Behavior

**Status**: `implemented` (database-enforced)

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| CASCADE delete diagnostic_sessions | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete knowledge_gaps | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete lessons | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete parental_consents | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete subject_mastery | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete topic_mastery | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete mastery_snapshots | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete practice_queue | Yes | Yes (DB FK) | ✅ Implemented |
| CASCADE delete spaced_review_schedule | Yes | Yes (DB FK) | ✅ Implemented |

**Gap Count**: 0 missing features

**Action Required**: None (database handles cascade)

---

### 5. Audit Retention

**Status**: `missing` (no integration)

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Audit events never deleted | Yes | N/A (no integration) | ❌ Missing |
| Audit logs never deleted | Yes | N/A (no integration) | ❌ Missing |
| Append-only audit trail | Yes | N/A (no integration) | ❌ Missing |

**Gap Count**: 3 missing features (audit integration)

**Action Required**: Integrate with audit service, ensure append-only behavior

---

### 6. Guardian Data Retention

**Status**: `implemented` (correct behavior)

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Guardian not deleted with learner | Yes | Yes (no cascade) | ✅ Implemented |
| Guardian email_hash retained | Yes | Yes (not deleted) | ✅ Implemented |
| Guardian email_encrypted retained | Yes | Yes (not deleted) | ✅ Implemented |
| Guardian stripe_customer_id retained | Yes | Yes (not deleted) | ✅ Implemented |

**Gap Count**: 0 missing features

**Action Required**: None

---

### 7. Pre-Deletion Validation

**Status**: `missing` (entire component)

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Consent status check | Yes | No check | ❌ Missing |
| Grace period check (30 days) | Yes | No check | ❌ Missing |
| Legal hold check | Yes | No check | ❌ Missing |
| Erasure request audited | Yes | No audit | ❌ Missing |

**Gap Count**: 4 missing features

**Action Required**: Implement pre-deletion validation service

---

### 8. Post-Deletion Verification

**Status**: `missing` (entire component)

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Learner record no longer exists | Yes | No verification | ❌ Missing |
| Dependent records CASCADE deleted | Yes | No verification | ❌ Missing |
| Audit events remain intact | Yes | No verification | ❌ Missing |
| Guardian record still exists | Yes | No verification | ❌ Missing |

**Gap Count**: 4 missing features

**Action Required**: Implement post-deletion verification service

---

### 9. Deletion Order

**Status**: `implemented` (database-enforced)

| Requirement | Matrix Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Dependent records deleted first | Yes | Yes (DB CASCADE) | ✅ Implemented |
| Primary record deleted last | Yes | Yes (DB CASCADE) | ✅ Implemented |

**Gap Count**: 0 missing features

**Action Required**: None

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total components required | 9 |
| Components fully implemented | 3 (cascade, guardian retention, deletion order) |
| Components partially implemented | 3 (soft delete, physical delete, purge) |
| Components entirely missing | 3 (audit retention, pre-deletion validation, post-deletion verification) |
| Total requirements | ~40 |
| Requirements implemented | ~15 |
| Requirements missing | ~25 |

---

## Classification by Requirement

### Implemented (3 components)
- ✅ Cascade behavior (database-enforced)
- ✅ Guardian data retention
- ✅ Deletion order (database-enforced)

### Partially Implemented (3 components)
- ⚠️ Soft delete (3 missing: grace enforcement, recovery, audit)
- ⚠️ Physical delete (7 missing: validation, checks, audit, verification)
- ⚠️ Purge (3 missing: authorization, audit, reason logging)

### Missing (3 components)
- ❌ Audit retention (no integration)
- ❌ Pre-deletion validation (entire component)
- ❌ Post-deletion verification (entire component)

### Release Blockers (3 components)
- 🚫 Pre-deletion validation (critical for safety)
- 🚫 Grace period enforcement (critical for POPIA compliance)
- 🚫 Audit integration (critical for compliance)

---

## Implementation Priority

### Priority 1: Critical Safety (Release Blockers)
1. Implement pre-deletion validation service
   - Consent status check
   - Grace period check (30 days)
   - Legal hold check
2. Add grace period enforcement to soft delete
3. Integrate audit events for all deletion operations
   - erasure.requested
   - erasure.executed
   - erasure.cancelled

### Priority 2: Verification
1. Implement post-deletion verification service
   - Verify learner record deleted
   - Verify dependent records CASCADE deleted
   - Verify audit events remain
   - Verify guardian record retained

### Priority 3: Recovery
1. Add soft delete recovery method
   - Within 30-day grace period
   - Restore display_name
   - Clear is_deleted flag
   - Clear deletion_requested_at

### Priority 4: Authorization
1. Add admin authorization for purge
2. Add override reason logging for purge

---

## Legal Rationale for Deferments

None currently. All missing components are required for POPIA compliance.

---

## Acceptance Criteria for T111B

- [x] Reconcile current erasure implementation against cascade matrix
- [x] Classify each requirement (implemented/partial/missing/blocker)
- [x] Document cascade behavior verification
- [x] Provide implementation priority order
- [ ] Every required component is either implemented, explicitly excluded with legal rationale, or tracked as a release blocker

**Remaining Work**: The acceptance criterion "every required component is either implemented, explicitly excluded with legal rationale, or tracked as a release blocker" is **not yet met**. The 3 missing components are tracked as release blockers, but no legal rationale exists for deferring them.

---

## Recommendations

1. **Immediate**: Implement Priority 1 components (pre-deletion validation, grace enforcement, audit integration)
2. **Short-term**: Implement Priority 2 (post-deletion verification)
3. **Medium-term**: Implement Priority 3 (recovery method)
4. **Long-term**: Implement Priority 4 (authorization for purge)

---

## Next Steps

1. **T111C**: Implement erasure workflow with safety checks
2. Add integration tests for deletion with realistic data
3. Legal review of grace period and legal hold policies
4. Privacy review of audit retention strategy
