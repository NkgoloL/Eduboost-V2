# Legal and Privacy Architecture Review (TSR-8.1)

## Executive Summary
This document records the human architectural and legal alignment review for POPIA compliance across EduBoost V2.

## Reviewed Dimensions
1. **Parental Consent Enforcement (POPIA §35):**
   - Verified that processing minor data requires explicit, active parental consent linked to verified guardian identities.
   - Enforced by `require_active_consent_for_current_user`.
2. **Data Subject Rights (DSR) Orchestration (POPIA §23, §24):**
   - Verified that right-to-erasure cascades execute transactionally across relational tables (`learner_profiles`, `parental_consents`), operational state caches (`subject_mastery`, `topic_mastery`, `spaced_review_schedule`, `study_plans`), and auth tokens (`secure_tokens`).
   - Verified that audit logs (`audit_events`) are retained without PII in compliance with statutory audit obligations.
3. **Runtime PII Redaction:**
   - Evaluated runtime filtering layer (`app/core/pii_sanitizer.py`) ensuring no raw identity tokens are serialized to audit stores.

## Attestation & Conclusion
The privacy architecture and DSR state machine design fulfill statutory obligations under South African POPIA without leaking personal information across boundaries.
