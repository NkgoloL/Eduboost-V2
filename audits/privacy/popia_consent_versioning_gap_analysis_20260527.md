# POPIA Consent Versioning Implementation Gap Analysis

**Date**: 2026-05-27
**Task**: T112B - POPIA consent versioning implementation gap analysis
**Source of Truth**: `docs/popia_consent_versioning_design.md`
**Current Implementation**: `app/models/__init__.py` (ParentalConsent), `app/repositories/consent_repository.py`

## Executive Summary

The current POPIA consent versioning implementation is **partially implemented**. The model has a `policy_version` field, but semantic versioning logic, migration detection, auto-renewal, and version history tracking are entirely missing.

**Overall Status**: `partially implemented`

**Release Blockers**: Version comparison utility, migration detection, version history table

## Gap Analysis by Component

### 1. Version Format

**Status**: `partially implemented`

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Semantic versioning (MAJOR.MINOR.PATCH) | Yes | No validation | ❌ Missing |
| policy_version field | Yes | Yes (String) | ✅ Implemented |
| Version parsing | Yes | No parser | ❌ Missing |
| Version comparison | Yes | No comparison logic | ❌ Missing |

**Gap Count**: 3 missing features (validation, parsing, comparison)

**Action Required**: Implement semantic versioning utility

---

### 2. Version Storage

**Status**: `partially implemented`

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| policy_version field | Yes | Yes | ✅ Implemented |
| granted_at | Yes | Yes | ✅ Implemented |
| expires_at | Yes | Yes | ✅ Implemented |
| revoked_at | Yes | Yes | ✅ Implemented |
| status enum | Yes | No (uses is_active) | ⚠️ Partial |
| 365-day default expiry | Yes | No default | ❌ Missing |

**Gap Count**: 2 missing features (status enum, default expiry)

**Action Required**: Add status enum, set default expiry to 365 days

---

### 3. Version Migration Rules

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Automatic renewal (same MAJOR.MINOR) | Yes | No logic | ❌ Missing |
| Manual renewal required (version change) | Yes | No logic | ❌ Missing |
| MAJOR change detection | Yes | No detection | ❌ Missing |
| MINOR change detection | Yes | No detection | ❌ Missing |
| PATCH change detection | Yes | No detection | ❌ Missing |
| Renewal window (30 days before expiry) | Yes | No logic | ❌ Missing |
| Grace period (30 days after expiry) | Yes | No logic | ❌ Missing |
| Hard deadline (60 days after expiry) | Yes | No logic | ❌ Missing |

**Gap Count**: 8 missing features

**Action Required**: Implement migration detection and renewal logic

---

### 4. Migration Paths

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Path 1: 1.0.0 → 1.1.0 (MINOR) | Yes | No implementation | ❌ Missing |
| Path 2: 1.1.0 → 2.0.0 (MAJOR) | Yes | No implementation | ❌ Missing |
| Path 3: 1.0.0 → 1.0.1 (PATCH) | Yes | No implementation | ❌ Missing |
| Identify consents requiring renewal | Yes | No query | ❌ Missing |
| Mark consents for renewal | Yes | No update | ❌ Missing |
| Auto-upgrade consents (PATCH) | Yes | No logic | ❌ Missing |

**Gap Count**: 6 missing features

**Action Required**: Implement migration path logic

---

### 5. Backward Compatibility

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Data processing rules by version | Yes | No rules | ❌ Missing |
| Fallback behavior for unknown versions | Yes | No fallback | ❌ Missing |
| Audit log for version mismatch | Yes | No audit | ❌ Missing |
| Notification for version mismatch | Yes | No notification | ❌ Missing |

**Gap Count**: 4 missing features

**Action Required**: Implement backward compatibility rules

---

### 6. Audit Trail

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| consent.granted event | Yes | No audit | ❌ Missing |
| consent.denied event | Yes | No audit | ❌ Missing |
| consent.withdrawn event | Yes | No audit | ❌ Missing |
| consent.renewed event | Yes | No audit | ❌ Missing |
| consent.expired event | Yes | No audit | ❌ Missing |
| consent.renewal_required event | Yes | No audit | ❌ Missing |
| Version history table | Yes | No table | ❌ Missing |

**Gap Count**: 7 missing features (6 events + history table)

**Action Required**: Implement audit events and version history table

---

### 7. Version History Table

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| consent_version_history table | Yes | No table | ❌ Missing |
| consent_id FK | Yes | N/A | ❌ Missing |
| policy_version | Yes | N/A | ❌ Missing |
| status | Yes | N/A | ❌ Missing |
| granted_at | Yes | N/A | ❌ Missing |
| expires_at | Yes | N/A | ❌ Missing |
| revoked_at | Yes | N/A | ❌ Missing |
| transition_reason | Yes | N/A | ❌ Missing |
| created_at | Yes | N/A | ❌ Missing |

**Gap Count**: 9 missing fields (entire table)

**Action Required**: Create migration for version history table

---

### 8. ConsentRepository

**Status**: `partially implemented`

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| get_active_for_learner | Yes | Yes | ✅ Implemented |
| get_by_id | Yes | Yes | ✅ Implemented |
| create | Yes | Yes | ✅ Implemented |
| update | Yes | Yes | ✅ Implemented |
| list_expiring_soon | Yes | Yes | ✅ Implemented |
| get_by_version | Yes | No method | ❌ Missing |
| get_version_history | Yes | No method | ❌ Missing |
| renew_consent | Yes | No method | ❌ Missing |
| revoke_consent | Yes | No method | ❌ Missing |

**Gap Count**: 4 missing methods

**Action Required**: Add version-aware repository methods

---

### 9. ConsentService

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Version comparison logic | Yes | No service | ❌ Missing |
| Migration detection | Yes | No service | ❌ Missing |
| Auto-renewal logic | Yes | No service | ❌ Missing |
| Manual renewal logic | Yes | No service | ❌ Missing |
| Grace period enforcement | Yes | No service | ❌ Missing |
| Notification triggering | Yes | No service | ❌ Missing |

**Gap Count**: 6 missing service methods

**Action Required**: Implement ConsentService with versioning logic

---

### 10. API Behavior

**Status**: `missing` (entire component)

| Requirement | Design Specification | Current Implementation | Gap Status |
|-------------|---------------------|----------------------|------------|
| Consent grant endpoint | Yes | No endpoint | ❌ Missing |
| Consent renewal endpoint | Yes | No endpoint | ❌ Missing |
| Consent withdrawal endpoint | Yes | No endpoint | ❌ Missing |
| Consent status endpoint | Yes | No endpoint | ❌ Missing |
| Version history endpoint | Yes | No endpoint | ❌ Missing |

**Gap Count**: 5 missing endpoints

**Action Required**: Implement consent versioning API endpoints

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total components required | 10 |
| Components fully implemented | 0 |
| Components partially implemented | 3 (version storage, repository, model) |
| Components entirely missing | 7 (migration rules, paths, compatibility, audit, history table, service, API) |
| Total requirements | ~60 |
| Requirements implemented | ~10 |
| Requirements missing | ~50 |

---

## Classification by Requirement

### Implemented (0 components)
- None

### Partially Implemented (3 components)
- ⚠️ Version format (policy_version field exists, no validation)
- ⚠️ Version storage (fields exist, no status enum, no default expiry)
- ⚠️ ConsentRepository (basic CRUD exists, no version-aware methods)

### Missing (7 components)
- ❌ Version migration rules (entire component)
- ❌ Migration paths (entire component)
- ❌ Backward compatibility (entire component)
- ❌ Audit trail (entire component)
- ❌ Version history table (entire component)
- ❌ ConsentService (entire component)
- ❌ API behavior (entire component)

### Release Blockers (3 components)
- 🚫 Version migration rules (critical for consent lifecycle)
- 🚫 Version history table (critical for audit)
- 🚫 ConsentService (critical for business logic)

---

## Implementation Priority

### Priority 1: Critical Foundation (Release Blockers)
1. Implement semantic versioning utility (parsing, comparison)
2. Create version history table migration
3. Implement ConsentService with versioning logic
4. Add version-aware repository methods

### Priority 2: Migration Logic
1. Implement version migration detection
2. Implement migration path logic (MAJOR/MINOR/PATCH)
3. Implement auto-renewal logic (same version)
4. Implement manual renewal logic (version change)

### Priority 3: Grace Period Enforcement
1. Implement renewal window detection (30 days before)
2. Implement grace period enforcement (30 days after)
3. Implement hard deadline (60 days after)
4. Implement processing restrictions on expiry

### Priority 4: Audit Integration
1. Implement consent lifecycle audit events
2. Integrate with version history table
3. Implement version mismatch audit logging

### Priority 5: API Layer
1. Implement consent grant endpoint
2. Implement consent renewal endpoint
3. Implement consent withdrawal endpoint
4. Implement consent status endpoint
5. Implement version history endpoint

### Priority 6: Backward Compatibility
1. Implement data processing rules by version
2. Implement fallback behavior for unknown versions
3. Implement notification for version mismatch

---

## Legal Rationale for Deferments

None currently. All missing components are required for POPIA compliance.

---

## Acceptance Criteria for T112B

- [x] Reconcile current consent implementation against versioning design
- [x] Classify each requirement (implemented/partial/missing/blocker)
- [x] Document version storage verification
- [x] Provide implementation priority order
- [ ] Every required component is either implemented, explicitly excluded with legal rationale, or tracked as a release blocker

**Remaining Work**: The acceptance criterion "every required component is either implemented, explicitly excluded with legal rationale, or tracked as a release blocker" is **not yet met**. The 7 missing components are tracked as release blockers, but no legal rationale exists for deferring them.

---

## Recommendations

1. **Immediate**: Implement Priority 1 components (versioning utility, history table, service)
2. **Short-term**: Implement Priority 2 (migration logic)
3. **Medium-term**: Implement Priority 3 (grace period enforcement)
4. **Long-term**: Implement Priority 4-6 (audit, API, compatibility)

---

## Next Steps

1. **T112C**: Implement consent versioning schema and migration
2. Add unit tests for semantic versioning utility
3. Add integration tests for consent lifecycle
4. Legal review of migration rules and grace periods
5. Privacy review of version history retention
