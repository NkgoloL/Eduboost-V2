---
title: "Schema Integrity Baseline & Migration Graph"
status: "active"
owner: "database"
reviewers: ["backend", "database", "release-management"]
audience: "developer"
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-22'
review_interval_days: 60
evidence_command: "make runtime-check"
code_anchors:
  - alembic/
  - app/models/
  - scripts/verify_migration_graph.py
  - scripts/validate_schema_integrity.py
---

# Schema Integrity Baseline & Migration Graph

This document summarizes the database schema integrity, Alembic migration graph, and append-only immutability baseline enforced in EduBoost V2.

## Migration Graph Integrity

The migration tree under `alembic/versions/` follows a strict single-head linear lineage verified by [`scripts/verify_migration_graph.py`](../../scripts/verify_migration_graph.py):
- **Empty Bootstrap Guarantee**: `alembic upgrade head` cleanly applies against an empty PostgreSQL 16 database.
- **Zero Drift Policy**: `alembic check` produces zero drift against active SQLAlchemy ORM models.
- **Single-Head Enforced**: Branching migrations are strictly prohibited in CI.

## Core Schema Invariants

| Area | Invariant |
|---|---|
| Tables | Production ORM tables have explicit primary keys and schema contracts |
| Timestamps | Core learner, guardian, consent, audit, diagnostic, lesson, and subscription tables have UTC timestamps |
| Foreign Keys | Learner-scoped data references learner profiles or guardians with explicit cascade policies |
| Consent Lifecycle | Guardian/learner consent transitions follow a strict state machine with unique status indexes |
| Audit Trail Immutability | Tranche 7 (DEF-12) append-only database triggers prevent UPDATE and DELETE operations on `audit_logs` |
| Learner Metrics | Grade, XP, and streak counters have database-level range guards |
| Diagnostics | Incomplete diagnostic sessions are indexed for operational cleanup |
| Billing & Entitlements | Stripe customer/subscription identifiers are indexed; fail-closed state prevents live billing without explicit human authorization |

## Append-Only Immutability: DEF-12 Trigger Controls

In accordance with POPIA and ISO 27001 audit standards, audit trail tables enforce database-level immutability:
- **No In-Place Modifications**: A PostgreSQL trigger function rejects any `UPDATE` or `DELETE` statement against `audit_logs`.
- **HMAC Hash Chaining**: Every audit entry includes an actor hash and HMAC digest verified at ingestion.
- **Erasure Cascade Isolation**: When POPIA erasure cascades execute, primary personal data is purged while an anonymized audit marker is appended to verify lawful erasure.

## Database-Backed Verified Indexes

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

Refresh-token sessions and background jobs are Redis-backed, so non-revoked session records and worker queues reside in Redis 7 with AOF/RDB persistence rather than PostgreSQL objects.

## Validation Commands

```bash
# Validate database schema integrity and constraints
PYTHONPATH=. .venv/bin/python scripts/validate_schema_integrity.py

# Verify single-head linear migration graph
PYTHONPATH=. .venv/bin/python scripts/verify_migration_graph.py
```

