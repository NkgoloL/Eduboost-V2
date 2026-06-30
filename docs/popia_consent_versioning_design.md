# POPIA Consent Versioning Design

## Purpose

This document defines the consent versioning strategy for POPIA compliance, including version tracking, migration paths, and backward compatibility requirements.

## Consent Version Schema

### Version Format

Consent versions follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to privacy policy or data processing scope
- **MINOR**: Non-breaking additions (new data categories, expanded rights)
- **PATCH**: Typo fixes, clarifications, formatting changes

Examples:
- `1.0.0` - Initial privacy policy
- `1.1.0` - Added new data category (e.g., RLHF feedback)
- `2.0.0` - Major policy revision (e.g., added third-party data sharing)

### Version Storage

| Field | Type | Description |
|-------|------|-------------|
| `policy_version` | String(20) | Version identifier (e.g., "1.0.0") |
| `granted_at` | DateTime | When consent was granted |
| `expires_at` | DateTime | When consent expires (default: 365 days) |
| `revoked_at` | DateTime | When consent was revoked (if applicable) |
| `status` | Enum | Current state (granted, denied, withdrawn, expired) |

## Version Migration Rules

### Automatic Renewal (Same MAJOR.MINOR)

When consent expires:
- If current policy version is still active (same MAJOR.MINOR)
- Auto-renew with same version
- Extend `expires_at` by 365 days
- No user action required

### Manual Renewal Required (Version Change)

When policy version changes:
- MAJOR change: Require explicit re-consent
- MINOR change: Require explicit re-consent
- PATCH change: Auto-renew with new version

### Grace Period

- **Renewal window**: 30 days before expiry
- **Grace period**: 30 days after expiry
- **Hard deadline**: 60 days after expiry (processing stops)

## Migration Paths

### Path 1: Version 1.0.0 → 1.1.0 (MINOR)

**Trigger**: Added RLHF feedback data category

**Action**:
1. Detect active consents with version `1.0.0`
2. Send renewal notification to guardians
3. Require explicit consent for `1.1.0`
4. Keep `1.0.0` record for audit (status: `withdrawn`)
5. Create new `1.1.0` record

**Migration SQL**:
```sql
-- Identify consents requiring renewal
SELECT learner_id, guardian_id, policy_version
FROM parental_consents
WHERE status = 'granted'
  AND policy_version = '1.0.0'
  AND expires_at < NOW() + INTERVAL '30 days';
```

### Path 2: Version 1.1.0 → 2.0.0 (MAJOR)

**Trigger**: Major policy revision (e.g., third-party data sharing)

**Action**:
1. Detect all active consents with version `1.1.0`
2. Send mandatory renewal notification
3. Block processing until re-consent
4. Set status to `renewal_required`
5. Create new `2.0.0` record upon consent

**Migration SQL**:
```sql
-- Mark consents for renewal
UPDATE parental_consents
SET status = 'renewal_required'
WHERE status = 'granted'
  AND policy_version = '1.1.0';
```

### Path 3: Version 1.0.0 → 1.0.1 (PATCH)

**Trigger**: Typo fix in privacy policy

**Action**:
1. Auto-upgrade all active consents
2. Update `policy_version` to `1.0.1`
3. Keep original `granted_at` timestamp
4. No user notification required

**Migration SQL**:
```sql
-- Auto-upgrade consents
UPDATE parental_consents
SET policy_version = '1.0.1'
WHERE status = 'granted'
  AND policy_version = '1.0.0';
```

## Backward Compatibility

### Data Processing Rules

| Consent Version | Data Categories Allowed | Processing Rules |
|-----------------|------------------------|------------------|
| `1.0.0` | Core learner data (profile, lessons, diagnostics) | Standard processing |
| `1.1.0` | Core + RLHF feedback | Standard + feedback processing |
| `2.0.0` | Core + RLHF + third-party analytics | Extended processing |

### Fallback Behavior

If consent version is not recognized:
- **Default**: Treat as latest version with maximum restrictions
- **Audit**: Log version mismatch event
- **Notification**: Alert guardian to update consent

## Audit Trail

### Consent Lifecycle Events

| Event Type | Payload |
|------------|---------|
| `consent.granted` | `learner_id`, `guardian_id`, `policy_version` |
| `consent.denied` | `learner_id`, `guardian_id`, `policy_version`, `reason` |
| `consent.withdrawn` | `learner_id`, `guardian_id`, `policy_version` |
| `consent.renewed` | `learner_id`, `guardian_id`, `old_version`, `new_version` |
| `consent.expired` | `learner_id`, `guardian_id`, `policy_version` |
| `consent.renewal_required` | `learner_id`, `guardian_id`, `old_version`, `new_version` |

### Version History Table

For complete audit trail, maintain version history:

```sql
CREATE TABLE consent_version_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consent_id UUID NOT NULL REFERENCES parental_consents(id),
    policy_version VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    transition_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Test Plan

### Unit Tests

1. **Version parsing**: Test semantic version comparison
2. **Migration detection**: Test version change detection logic
3. **Auto-renewal logic**: Test same-version renewal
4. **Manual renewal logic**: Test version-change renewal
5. **Grace period enforcement**: Test expiry deadlines

### Integration Tests

1. **End-to-end consent flow**: Grant → expire → renew
2. **Version migration**: Test actual migration paths
3. **Processing restrictions**: Test data blocking on expired consent
4. **Audit trail**: Verify all events are logged

### Contract Tests

1. **ConsentRepository**: Verify version field handling
2. **ConsentService**: Verify renewal logic
3. **POPIAService**: Verify consent checks before data operations

## Implementation Checklist

- [ ] Add `policy_version` field to `ParentalConsent` model
- [ ] Implement version comparison utility
- [ ] Add migration detection logic to `ConsentService`
- [ ] Implement auto-renewal for PATCH versions
- [ ] Implement manual renewal for MAJOR/MINOR versions
- [ ] Add grace period enforcement
- [ ] Create consent version history table
- [ ] Add audit events for version transitions
- [ ] Write unit tests for versioning logic
- [ ] Write integration tests for migration paths
- [ ] Update POPIA documentation
- [ ] Create guardian notification templates
