# POPIA Export Data Inventory

## Purpose

This document defines the complete data inventory for POPIA data subject right to access (export). It lists all learner-related data that must be included in a data export request, along with field-level classification and retention requirements.

## Data Categories

### 1. Learner Profile (Primary Identity)

**Table**: `learner_profiles`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | Yes | Yes (pseudonym_id only) | Internal ID, not exported directly |
| pseudonym_id | UUID | Yes | Yes | Pseudonym for external reference |
| guardian_id | UUID | Yes | Yes | Reference to guardian |
| display_name | String | Yes | Yes | Learner's display name |
| grade | Integer | No | Yes | Grade level (0-12) |
| language | Enum | No | Yes | Language preference |
| archetype | Enum | No | Yes | Learning archetype |
| theta | Float | No | Yes | IRT ability estimate |
| xp | Integer | No | Yes | Experience points |
| streak_days | Integer | No | Yes | Current streak |
| last_active | DateTime | No | Yes | Last activity timestamp |
| is_deleted | Boolean | No | Yes | Soft-delete flag |
| deletion_requested_at | DateTime | No | Yes | Deletion request timestamp |
| created_at | DateTime | No | Yes | Account creation timestamp |
| updated_at | DateTime | No | Yes | Last update timestamp |

### 2. Diagnostic Sessions

**Table**: `diagnostic_sessions`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Session identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| responses | JSONB | No | Yes | Item responses |
| theta_before | Float | No | Yes | Ability before session |
| theta_after | Float | No | Yes | Ability after session |
| se_estimate | Float | No | Yes | Standard error estimate |
| session_state | String | No | Yes | Session state |
| gap_topics | JSONB | No | Yes | Identified gaps |
| misconception_tags | JSONB | No | Yes | Misconception tags |
| items_served | Integer | No | Yes | Number of items served |
| theta_history | JSONB | No | Yes | Theta progression |
| items_correct | Integer | No | Yes | Correct count |
| completed_at | DateTime | No | Yes | Completion timestamp |
| created_at | DateTime | No | Yes | Session creation timestamp |

### 3. Lessons

**Table**: `lessons`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Lesson identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| knowledge_gap_id | UUID | No | Yes | Related gap |
| grade | Integer | No | Yes | Grade level |
| subject | String | No | Yes | Subject |
| topic | String | No | Yes | Topic |
| language | Enum | No | Yes | Language |
| archetype | Enum | No | Yes | Learning archetype |
| content | Text | No | Yes | Lesson content |
| caps_ref | String | No | Yes | CAPS reference |
| caps_reference | String | No | Yes | Full CAPS reference |
| term | Integer | No | Yes | Term (1-4) |
| subtopic | String | No | Yes | Subtopic |
| learning_objectives | JSONB | No | Yes | Learning objectives |
| explanation | Text | No | Yes | Explanation |
| worked_examples | JSONB | No | Yes | Worked examples |
| practice_questions | JSONB | No | Yes | Practice questions |
| answer_key | JSONB | No | Yes | Answer key |
| remediation_hints | JSONB | No | Yes | Remediation hints |
| difficulty_level | String | No | Yes | Difficulty |
| language_level | String | No | Yes | Language level |
| safety_classification | String | No | Yes | Safety classification |
| pii_check_passed | Boolean | No | Yes | PII check status |
| answer_key_verified | Boolean | No | Yes | Answer key verification |
| alignment_confidence | Float | No | Yes | CAPS alignment confidence |
| quality_score | Float | No | Yes | Quality score |
| trust_label | JSONB | No | Yes | Trust metadata |
| review_status | String | No | Yes | Review status |
| reviewer_id | UUID | Yes | No | Internal reviewer (not exported) |
| reviewed_at | DateTime | No | Yes | Review timestamp |
| prompt_template_version | String | No | Yes | Prompt version |
| provider | String | No | Yes | LLM provider |
| model_version | String | No | Yes | Model version |
| generation_latency_ms | Integer | No | Yes | Generation latency |
| token_usage | JSONB | No | Yes | Token usage |
| variant_type | String | No | Yes | Variant type |
| llm_provider | String | No | Yes | LLM provider |
| served_from_cache | Boolean | No | Yes | Cache flag |
| feedback_score | Integer | No | Yes | User feedback (1-5) |
| completed_at | DateTime | No | Yes | Completion timestamp |
| created_at | DateTime | No | Yes | Creation timestamp |

### 4. Knowledge Gaps

**Table**: `knowledge_gaps`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Gap identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| grade | Integer | No | Yes | Grade level |
| subject | String | No | Yes | Subject |
| topic | String | No | Yes | Topic |
| severity | Float | No | Yes | Severity (0-1) |
| resolved | Boolean | No | Yes | Resolution status |
| created_at | DateTime | No | Yes | Creation timestamp |

### 5. Parental Consents

**Table**: `parental_consents`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Consent identifier |
| guardian_id | UUID | Yes | Yes | Guardian reference |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| policy_version | String | No | Yes | Privacy policy version |
| status | Enum | No | Yes | Consent status |
| granted_at | DateTime | No | Yes | Grant timestamp |
| expires_at | DateTime | No | Yes | Expiry timestamp |
| revoked_at | DateTime | No | Yes | Revocation timestamp |
| ip_address_hash | String | Yes | No | IP hash (not exported) |
| created_at | DateTime | No | Yes | Creation timestamp |
| updated_at | DateTime | No | Yes | Update timestamp |

### 6. Mastery Records

**Table**: `subject_mastery`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Mastery identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| subject | String | No | Yes | Subject |
| topic | String | No | Yes | Topic |
| theta | Float | No | Yes | Ability estimate |
| standard_error | Float | No | Yes | Standard error |
| created_at | DateTime | No | Yes | Creation timestamp |
| last_updated | DateTime | No | Yes | Last update timestamp |

**Table**: `topic_mastery`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Topic mastery identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| caps_ref | String | No | Yes | CAPS reference |
| mastery_score | Float | No | Yes | Mastery score (0-1) |
| mastery_label | String | No | Yes | Mastery label |
| theta_estimate | Float | No | Yes | Theta estimate |
| theta_se | Float | No | Yes | Theta standard error |
| last_updated_at | DateTime | No | Yes | Last update timestamp |

**Table**: `mastery_snapshots`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Snapshot identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| caps_ref | String | No | Yes | CAPS reference |
| mastery_score | Float | No | Yes | Mastery score |
| mastery_label | String | No | Yes | Mastery label |
| theta_estimate | Float | No | Yes | Theta estimate |
| theta_se | Float | No | Yes | Theta standard error |
| practice_accuracy | Float | No | Yes | Practice accuracy |
| trigger | String | No | Yes | Snapshot trigger |
| snapshot_at | DateTime | No | Yes | Snapshot timestamp |

### 7. Practice Queue

**Table**: `practice_queue`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Queue entry identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| caps_ref | String | No | Yes | CAPS reference |
| item_id | UUID | No | Yes | Item identifier |
| scheduled_at | DateTime | No | Yes | Scheduled timestamp |
| completed_at | DateTime | No | Yes | Completion timestamp |
| response | Text | No | Yes | User response |
| correct | Boolean | No | Yes | Correctness |

### 8. Spaced Review Schedule

**Table**: `spaced_review_schedule`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Schedule identifier |
| learner_id | UUID | Yes | Yes (via pseudonym) | Foreign key to learner |
| caps_ref | String | No | Yes | CAPS reference |
| next_review_at | DateTime | No | Yes | Next review timestamp |
| interval_days | Integer | No | Yes | Review interval |
| easiness_factor | Float | No | Yes | Easiness factor |
| updated_at | DateTime | No | Yes | Last update timestamp |

### 9. Guardian Data (Limited)

**Table**: `guardians`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | Yes | Yes | Guardian identifier |
| email_hash | String | Yes | No | Email hash (not exported) |
| email_encrypted | Text | Yes | No | Encrypted email (not exported) |
| display_name | String | Yes | Yes | Display name |
| role | Enum | No | Yes | User role |
| subscription_tier | Enum | No | Yes | Subscription tier |
| stripe_customer_id | String | Yes | No | Stripe ID (not exported) |
| stripe_subscription_id | String | Yes | No | Stripe subscription (not exported) |
| is_active | Boolean | No | Yes | Active status |
| email_verified | Boolean | No | Yes | Email verification status |
| created_at | DateTime | No | Yes | Creation timestamp |
| updated_at | DateTime | No | Yes | Update timestamp |

### 10. Audit Events (Limited)

**Table**: `audit_events`

| Field | Type | PII | Included in Export | Notes |
|-------|------|-----|---------------------|-------|
| id | UUID | No | Yes | Event identifier |
| event_type | String | No | Yes | Event type |
| actor_id | UUID | Yes | No | Actor ID (not exported) |
| resource_id | UUID | Yes | Yes (via pseudonym) | Resource identifier |
| payload | JSONB | No | Yes | Event payload |
| previous_event_hash | String | No | Yes | Previous event hash |
| event_hash | String | No | Yes | Event hash |
| hmac_signature | String | No | Yes | HMAC signature |
| created_at | DateTime | No | Yes | Creation timestamp |

## Data Not Exported

The following data is intentionally excluded from POPIA exports:

1. **Guardian PII**: Email hashes, encrypted emails, Stripe identifiers
2. **Internal reviewer IDs**: Reviewer identifiers for content review
3. **IP address hashes**: For parental consents
4. **System internal IDs**: Some internal foreign keys replaced with pseudonyms

## Export Format

The export is provided in two formats:
- **JSON**: Structured nested object with all categories
- **CSV**: Flattened key-value format for readability

## Completeness Requirements

A POPIA export is considered complete when:
1. All learner profile fields are present
2. All related records (diagnostic sessions, lessons, gaps, consents) are included
3. No PII fields are leaked (email hashes, encrypted data, Stripe IDs)
4. Pseudonymization is applied to all learner_id references
5. Timestamps are in ISO 8601 format
6. All foreign key relationships are preserved via pseudonyms

## Retention Requirements

- Export data must be retained for 30 days after request completion
- Export request must be audited with event type `data_export.requested`
- Export files must be securely stored and access-logged
