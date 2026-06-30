# Schema integrity baseline

This document summarizes the database integrity baseline enforced by PR-005.

## Core invariants

| Area | Invariant |
|---|---|
| Tables | Production ORM tables have explicit primary keys |
| Timestamps | Core learner/guardian/consent/audit/diagnostic/lesson/subscription tables have timestamps |
| Foreign keys | Learner-scoped data references learner profiles or guardians explicitly |
| Consent | Guardian/learner consent is unique and status-indexed |
| Audit | Audit events require non-blank event type and hash/HMAC shape checks |
| Learners | Grade, XP, and streak counters have database-level range guards |
| Diagnostics | Incomplete diagnostic sessions are indexed for operational cleanup |
| Billing | Stripe customer/subscription identifiers are indexed when present |
| Subscriptions | Active premium subscription lookup has a partial index |

## Database-backed indexes added or verified

- `ix_guardians_email_hash`
- `ix_guardians_stripe_customer_id`
- `ix_guardians_stripe_subscription_id`
- `ix_guardians_active_subscription`
- `ix_learner_guardian_grade`
- `ix_parental_consents_status`
- `ix_parental_consents_guardian_learner_status`
- `ix_parental_consents_active_status`
- `ix_diagnostic_sessions_created_at`
- `ix_diagnostic_sessions_incomplete`
- `idx_audit_events_ts`
- `idx_audit_events_actor`
- `idx_audit_events_hash`
- `ix_subject_mastery_last_updated`
- `ix_stripe_webhook_processed_at`

Refresh-token sessions and background jobs are currently Redis-backed, so non-revoked-session and incomplete-job indexes are not PostgreSQL objects. Their recoverability is documented separately in the disaster recovery plan.

## Validation commands

```bash
PYTHONPATH=. python scripts/validate_schema_integrity.py
PYTHONPATH=. python scripts/verify_migration_graph.py
```
