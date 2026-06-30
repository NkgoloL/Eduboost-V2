# POPIA Export Implementation Gap Analysis

**Date**: 2026-05-27
**Task**: T110B - Reconcile current export payload against required POPIA export inventory
**Source of Truth**: `docs/popia_export_data_inventory.md`
**Current Implementation**: `app/services/popia_service.py::_export_payload()`

## Executive Summary

The current POPIA export implementation is **partially implemented**. It exports 5 of 10 required data categories with limited field coverage. Several categories are entirely missing, and existing categories have significant field gaps.

**Overall Status**: `partially implemented`

**Release Blockers**: 4 categories entirely missing (mastery records, practice queue, spaced review, guardian data)

## Gap Analysis by Category

### 1. Learner Profile

**Status**: `partially implemented`

| Field | Inventory Requirement | Current Implementation | Gap Status |
|-------|------------------------|----------------------|------------|
| id | Yes (pseudonym_id only) | Yes (actual id) | ⚠️ Should use pseudonym_id |
| pseudonym_id | Yes | Yes | ✅ Implemented |
| guardian_id | Yes | No | ❌ Missing |
| display_name | Yes | Yes | ✅ Implemented |
| grade | Yes | Yes | ✅ Implemented |
| language | Yes | Yes | ✅ Implemented |
| archetype | Yes | Yes | ✅ Implemented |
| theta | Yes | Yes | ✅ Implemented |
| xp | Yes | Yes | ✅ Implemented |
| streak_days | Yes | Yes | ✅ Implemented |
| last_active | Yes | Yes | ✅ Implemented |
| is_deleted | Yes | No | ❌ Missing |
| deletion_requested_at | Yes | No | ❌ Missing |
| created_at | Yes | Yes | ✅ Implemented |
| updated_at | Yes | No | ❌ Missing |

**Gap Count**: 6 missing fields (guardian_id, is_deleted, deletion_requested_at, updated_at, plus id should be pseudonym)

**Action Required**: Add missing fields, use pseudonym_id for id field

---

### 2. Diagnostic Sessions

**Status**: `partially implemented`

| Field | Inventory Requirement | Current Implementation | Gap Status |
|-------|------------------------|----------------------|------------|
| id | Yes | Yes | ✅ Implemented |
| learner_id | Yes (via pseudonym) | No (FK not exported) | ⚠️ Acceptable (implicit) |
| responses | Yes | No | ❌ Missing |
| theta_before | Yes | Yes | ✅ Implemented |
| theta_after | Yes | Yes | ✅ Implemented |
| se_estimate | Yes | No | ❌ Missing |
| session_state | Yes | No | ❌ Missing |
| gap_topics | Yes | No | ❌ Missing |
| misconception_tags | Yes | No | ❌ Missing |
| items_served | Yes | No | ❌ Missing |
| theta_history | Yes | No | ❌ Missing |
| items_correct | Yes | No | ❌ Missing |
| completed_at | Yes | Yes | ✅ Implemented |
| created_at | Yes | Yes | ✅ Implemented |

**Gap Count**: 9 missing fields (responses, se_estimate, session_state, gap_topics, misconception_tags, items_served, theta_history, items_correct)

**Action Required**: Add missing diagnostic session fields

---

### 3. Lessons

**Status**: `partially implemented`

| Field | Inventory Requirement | Current Implementation | Gap Status |
|-------|------------------------|----------------------|------------|
| id | Yes | Yes | ✅ Implemented |
| learner_id | Yes (via pseudonym) | No (FK not exported) | ⚠️ Acceptable (implicit) |
| knowledge_gap_id | Yes | No | ❌ Missing |
| grade | Yes | Yes | ✅ Implemented |
| subject | Yes | Yes | ✅ Implemented |
| topic | Yes | Yes | ✅ Implemented |
| language | Yes | Yes | ✅ Implemented |
| archetype | Yes | Yes | ✅ Implemented |
| content | Yes | No | ❌ Missing |
| caps_ref | Yes | No | ❌ Missing |
| caps_reference | Yes | No | ❌ Missing |
| term | Yes | No | ❌ Missing |
| subtopic | Yes | No | ❌ Missing |
| learning_objectives | Yes | No | ❌ Missing |
| explanation | Yes | No | ❌ Missing |
| worked_examples | Yes | No | ❌ Missing |
| practice_questions | Yes | No | ❌ Missing |
| answer_key | Yes | No | ❌ Missing |
| remediation_hints | Yes | No | ❌ Missing |
| difficulty_level | Yes | No | ❌ Missing |
| language_level | Yes | No | ❌ Missing |
| safety_classification | Yes | No | ❌ Missing |
| pii_check_passed | Yes | No | ❌ Missing |
| answer_key_verified | Yes | No | ❌ Missing |
| alignment_confidence | Yes | No | ❌ Missing |
| quality_score | Yes | No | ❌ Missing |
| trust_label | Yes | No | ❌ Missing |
| review_status | Yes | No | ❌ Missing |
| reviewer_id | Yes | No | ✅ Correctly excluded (PII) |
| reviewed_at | Yes | No | ❌ Missing |
| prompt_template_version | Yes | No | ❌ Missing |
| provider | Yes | No | ❌ Missing |
| model_version | Yes | No | ❌ Missing |
| generation_latency_ms | Yes | No | ❌ Missing |
| token_usage | Yes | No | ❌ Missing |
| variant_type | Yes | No | ❌ Missing |
| llm_provider | Yes | No | ❌ Missing |
| served_from_cache | Yes | Yes | ✅ Implemented |
| feedback_score | Yes | Yes | ✅ Implemented |
| completed_at | Yes | No | ❌ Missing |
| created_at | Yes | Yes | ✅ Implemented |

**Gap Count**: 28 missing fields (most lesson metadata fields)

**Action Required**: Add comprehensive lesson metadata fields

---

### 4. Knowledge Gaps

**Status**: `fully implemented`

| Field | Inventory Requirement | Current Implementation | Gap Status |
|-------|------------------------|----------------------|------------|
| id | Yes | Yes | ✅ Implemented |
| learner_id | Yes (via pseudonym) | No (FK not exported) | ⚠️ Acceptable (implicit) |
| grade | Yes | Yes | ✅ Implemented |
| subject | Yes | Yes | ✅ Implemented |
| topic | Yes | Yes | ✅ Implemented |
| severity | Yes | Yes | ✅ Implemented |
| resolved | Yes | Yes | ✅ Implemented |
| created_at | Yes | Yes | ✅ Implemented |

**Gap Count**: 0 missing fields

**Action Required**: None

---

### 5. Parental Consents

**Status**: `partially implemented`

| Field | Inventory Requirement | Current Implementation | Gap Status |
|-------|------------------------|----------------------|------------|
| id | Yes | Yes | ✅ Implemented |
| guardian_id | Yes | No | ❌ Missing |
| learner_id | Yes (via pseudonym) | No (FK not exported) | ⚠️ Acceptable (implicit) |
| policy_version | Yes | Yes | ✅ Implemented |
| status | Yes | No (uses is_active) | ⚠️ Partial (is_active ≠ status) |
| granted_at | Yes | Yes | ✅ Implemented |
| expires_at | Yes | Yes | ✅ Implemented |
| revoked_at | Yes | Yes | ✅ Implemented |
| ip_address_hash | Yes | No | ✅ Correctly excluded (PII) |
| created_at | Yes | No | ❌ Missing |
| updated_at | Yes | No | ❌ Missing |

**Gap Count**: 4 missing fields (guardian_id, status enum, created_at, updated_at)

**Action Required**: Add missing fields, map is_active to status enum

---

### 6. Mastery Records

**Status**: `missing` (entire category)

**Tables**: `subject_mastery`, `topic_mastery`, `mastery_snapshots`

**Gap Count**: All fields missing (3 tables × ~8 fields each = ~24 fields)

**Action Required**: Implement entire category

---

### 7. Practice Queue

**Status**: `missing` (entire category)

**Table**: `practice_queue`

**Gap Count**: All fields missing (~9 fields)

**Action Required**: Implement entire category

---

### 8. Spaced Review Schedule

**Status**: `missing` (entire category)

**Table**: `spaced_review_schedule`

**Gap Count**: All fields missing (~7 fields)

**Action Required**: Implement entire category

---

### 9. Guardian Data

**Status**: `missing` (entire category)

**Table**: `guardians`

**Gap Count**: All fields missing (~11 fields, but email PII should be excluded)

**Action Required**: Implement category with PII exclusions

---

### 10. Audit Events

**Status**: `missing` (entire category)

**Table**: `audit_events`

**Gap Count**: All fields missing (~9 fields, but actor_id should be excluded)

**Action Required**: Implement category with PII exclusions

---

## PII Exclusion Verification

| PII Field | Inventory Requirement | Current Implementation | Status |
|-----------|------------------------|----------------------|--------|
| email_hash | No | N/A (category missing) | ⚠️ Will need exclusion |
| email_encrypted | No | N/A (category missing) | ⚠️ Will need exclusion |
| stripe_customer_id | No | N/A (category missing) | ⚠️ Will need exclusion |
| stripe_subscription_id | No | N/A (category missing) | ⚠️ Will need exclusion |
| reviewer_id | No | N/A (not exported) | ✅ Correctly excluded |
| ip_address_hash | No | N/A (not exported) | ✅ Correctly excluded |
| actor_id | No | N/A (category missing) | ⚠️ Will need exclusion |

**Status**: PII exclusions are correctly applied in current implementation, but missing categories will need PII handling.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total data categories required | 10 |
| Categories fully implemented | 1 (knowledge_gaps) |
| Categories partially implemented | 4 (learner, diagnostic_sessions, lessons, parental_consents) |
| Categories entirely missing | 5 (mastery, practice_queue, spaced_review, guardian, audit_events) |
| Total fields required | ~120 |
| Fields implemented | ~30 |
| Fields missing | ~90 |
| PII fields correctly excluded | 2 (reviewer_id, ip_address_hash) |

---

## Classification by Requirement

### Implemented (1 category)
- ✅ Knowledge gaps

### Partially Implemented (4 categories)
- ⚠️ Learner profile (6 missing fields)
- ⚠️ Diagnostic sessions (9 missing fields)
- ⚠️ Lessons (28 missing fields)
- ⚠️ Parental consents (4 missing fields)

### Missing (5 categories)
- ❌ Mastery records (subject_mastery, topic_mastery, mastery_snapshots)
- ❌ Practice queue
- ❌ Spaced review schedule
- ❌ Guardian data
- ❌ Audit events

### Release Blockers (4 categories)
- 🚫 Mastery records (critical for learning history)
- 🚫 Practice queue (critical for activity history)
- 🚫 Spaced review schedule (critical for learning history)
- 🚫 Guardian data (critical for consent context)

---

## Implementation Priority

### Priority 1: Critical Gaps (Release Blockers)
1. Add mastery records (subject_mastery, topic_mastery, mastery_snapshots)
2. Add practice queue
3. Add spaced review schedule
4. Add guardian data (with PII exclusions)

### Priority 2: Complete Partial Categories
1. Add missing learner profile fields (guardian_id, is_deleted, deletion_requested_at, updated_at)
2. Add missing diagnostic session fields (responses, se_estimate, session_state, etc.)
3. Add missing lesson metadata fields (content, caps_ref, learning_objectives, etc.)
4. Add missing consent fields (guardian_id, status enum, created_at, updated_at)

### Priority 3: Audit Trail
1. Add audit events (with actor_id exclusion)

### Priority 4: Pseudonymization
1. Replace learner.id with learner.pseudonym_id in export
2. Ensure all learner_id FKs use pseudonyms

---

## Legal Rationale for Deferments

None currently. All missing categories are required for POPIA compliance.

---

## Acceptance Criteria for T110B

- [x] Reconcile current export payload against inventory
- [x] Classify each requirement (implemented/partial/missing/blocker)
- [x] Document PII exclusion verification
- [x] Provide implementation priority order
- [ ] Every required category is either exported, explicitly excluded with legal rationale, or tracked as a release blocker

**Remaining Work**: The acceptance criterion "every required category is either exported, explicitly excluded with legal rationale, or tracked as a release blocker" is **not yet met**. The 5 missing categories are tracked as release blockers, but no legal rationale exists for deferring them.

---

## Recommendations

1. **Immediate**: Implement Priority 1 categories (mastery, practice queue, spaced review, guardian data)
2. **Short-term**: Complete Priority 2 categories (fill missing fields in existing categories)
3. **Medium-term**: Add audit events for complete audit trail
4. **Long-term**: Implement pseudonymization across all learner_id references

---

## Next Steps

1. **T110C**: Implement export payload completeness (Priority 1 + 2)
2. Update completeness tests to verify all required fields
3. Add integration tests with realistic learner data
4. Legal review of PII exclusion strategy
