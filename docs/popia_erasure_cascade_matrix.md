# POPIA Erasure Cascade Matrix

## Purpose

This document defines the data deletion cascade for POPIA Right to Erasure requests. It specifies which data is physically deleted, which is retained for audit purposes, and the order of deletion operations to maintain referential integrity.

## Deletion Policy

### Physical Deletion (CASCADE)

When a learner is physically deleted via `delete_by_id` or `purge_personal_data`, the following records are physically removed from the database due to `ON DELETE CASCADE` foreign key constraints:

| Table | Deletion Action | Retention Period | Notes |
|-------|-----------------|------------------|-------|
| `learner_profiles` | Physical delete | Immediate | Primary record |
| `diagnostic_sessions` | CASCADE delete | Immediate | Via learner_id FK |
| `knowledge_gaps` | CASCADE delete | Immediate | Via learner_id FK |
| `lessons` | CASCADE delete | Immediate | Via learner_id FK |
| `parental_consents` | CASCADE delete | Immediate | Via learner_id FK |
| `subject_mastery` | CASCADE delete | Immediate | Via learner_id FK |
| `topic_mastery` | CASCADE delete | Immediate | Via learner_id FK |
| `mastery_snapshots` | CASCADE delete | Immediate | Via learner_id FK |
| `practice_queue` | CASCADE delete | Immediate | Via learner_id FK |
| `spaced_review_schedule` | CASCADE delete | Immediate | Via learner_id FK |

### Soft Deletion (POPIA Grace Period)

When a learner is soft-deleted via `soft_delete`, the following occurs:

| Table | Deletion Action | Retention Period | Notes |
|-------|-----------------|------------------|-------|
| `learner_profiles` | Soft delete | 30 days grace | `is_deleted=True`, `display_name="[erased]"` |
| `diagnostic_sessions` | Retained | 30 days grace | No cascade on soft delete |
| `knowledge_gaps` | Retained | 30 days grace | No cascade on soft delete |
| `lessons` | Retained | 30 days grace | No cascade on soft delete |
| `parental_consents` | Retained | 30 days grace | No cascade on soft delete |
| `subject_mastery` | Retained | 30 days grace | No cascade on soft delete |
| `topic_mastery` | Retained | 30 days grace | No cascade on soft delete |
| `mastery_snapshots` | Retained | 30 days grace | No cascade on soft delete |
| `practice_queue` | Retained | 30 days grace | No cascade on soft delete |
| `spaced_review_schedule` | Retained | 30 days grace | No cascade on soft delete |

### Audit Retention (Append-Only)

The following data is NEVER deleted, even after physical erasure:

| Table | Retention Policy | Notes |
|-------|-----------------|-------|
| `audit_events` | Permanent | Append-only, immutable |
| `audit_logs` | Permanent | Append-only, immutable |

### Guardian Data (Limited Deletion)

Guardian records are NOT deleted when a learner is erased:

| Table | Deletion Action | Notes |
|-------|-----------------|-------|
| `guardians` | No deletion | Guardian may have other learners |
| `guardian.email_hash` | Retained | For authentication |
| `guardian.email_encrypted` | Retained | For authentication |
| `guardian.stripe_customer_id` | Retained | For billing records |

## Deletion Order

For physical deletion, the following order is enforced by foreign key constraints:

1. **Dependent records** (CASCADE automatically):
   - `practice_queue`
   - `spaced_review_schedule`
   - `mastery_snapshots`
   - `topic_mastery`
   - `subject_mastery`
   - `lessons`
   - `knowledge_gaps`
   - `diagnostic_sessions`
   - `parental_consents`

2. **Primary record**:
   - `learner_profiles`

The database enforces this order via `ON DELETE CASCADE` on foreign keys.

## Safety Checks

### Pre-Deletion Validation

Before executing a physical deletion, the following checks must pass:

1. **Consent status**: Learner must have active consent revoked or expired
2. **Grace period**: `deletion_requested_at` must be at least 30 days old
3. **No legal hold**: No active legal hold on learner data
4. **Audit trail**: Erasure request must be audited with event type `erasure.requested`

### Post-Deletion Verification

After physical deletion, verify:

1. **Learner record**: `learner_profiles` record no longer exists
2. **Dependent records**: All dependent records are CASCADE deleted
3. **Audit integrity**: Audit events for the learner remain intact
4. **Guardian integrity**: Guardian record still exists (if other learners)

## Deletion Methods

### Method 1: Soft Delete (Grace Period)

```python
await learner_repository.soft_delete(learner_id)
```

- Sets `is_deleted = True`
- Sets `display_name = "[erased]"`
- Sets `deletion_requested_at = now()`
- Does NOT delete dependent records
- Allows 30-day grace period for recovery

### Method 2: Physical Delete (Right to Erasure)

```python
await learner_repository.delete_by_id(learner_id)
```

- Physically deletes learner record
- CASCADE deletes all dependent records
- Irreversible
- Requires 30-day grace period to have elapsed

### Method 3: Purge Personal Data (Emergency)

```python
await learner_repository.purge_personal_data(learner_id)
```

- Same as physical delete
- Reserved for emergency/override scenarios
- Requires admin authorization

## Audit Requirements

All deletion operations must be audited:

| Event Type | Payload Fields |
|------------|----------------|
| `erasure.requested` | `learner_id`, `learner_pseudonym`, `reason`, `grace_period_days`, `requires_admin_review` |
| `erasure.cancelled` | `learner_id`, `learner_pseudonym` |
| `erasure.executed` | `learner_id`, `learner_pseudonym`, `method` (soft/physical/purge) |
| `data_subject.correction_requested` | `learner_id`, `fields`, `reason` |
| `processing.restricted` | `learner_id`, `learner_pseudonym`, `reason` |

## Recovery

### Soft Delete Recovery

Within the 30-day grace period, a soft-deleted learner can be recovered:

```python
learner.is_deleted = False
learner.deletion_requested_at = None
learner.display_name = original_display_name
```

### Physical Delete Recovery

Physical deletion is **irreversible**. No recovery mechanism exists.

## Compliance Notes

- **POPIA Section 11**: Right to deletion of personal information
- **POPIA Section 12**: Right to correction of personal information
- **POPIA Section 13**: Right to restriction of processing
- **Grace period**: 30 days for Right to Erasure (per POPIA_ERASURE_GRACE_DAYS)
- **SLA**: 30 days for erasure request processing (per POPIA_ERASURE_REVIEW_SLA_DAYS)
