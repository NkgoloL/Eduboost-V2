# Database Schema Readiness Contract

## Purpose

This contract records repository-verifiable schema readiness evidence for production tables, constraints, indexes, and learner/guardian data workflows.

## Required Schema Invariants

- every production table has explicit primary key evidence
- every production table has timestamp evidence
- every learner, guardian, consent, diagnostic, lesson, mastery, audit, billing, and job relationship has foreign key evidence where applicable
- role enum constraints are represented in domain and database validation evidence
- consent status constraints are represented in consent and schema validation evidence
- audit event constraints are represented in immutable audit validation evidence
- immutable audit identifier constraints are represented in audit event validation evidence
- unique guardian learner relationship constraints are represented in consent validation evidence
- non-null sensitive workflow fields are represented in schema validation evidence

## Required Index Evidence

- user email hash index
- learner ID index
- guardian ID index
- consent status index
- token identifier index
- diagnostic attempt or diagnostic session index
- lesson generation job index
- audit timestamp index
- audit actor ID index
- subscription or customer ID index
- active consent partial index
- active subscription partial index
- non-revoked session partial index
- incomplete job partial index

## Required Evidence Files

- `scripts/validate_schema_integrity.py`
- `scripts/verify_migration_graph.py`
- `alembic/versions/20260505_1734_add_missing_production_indexes.py`
- `alembic/versions/20260507_1330_database_integrity_constraints.py`
- `alembic/versions/20260507_1200_popia_consent_audit_hardening.py`
- `docs/database/schema_integrity.md`
- `tests/unit/test_schema_integrity.py`
- `tests/unit/test_migration_graph.py`

## Verification Boundary

This contract validates repository-side schema evidence. It does not replace `alembic upgrade head`, `alembic check`, staging dry runs, database administrator review, or production migration approval.
