# Repository, Transaction, and Performance Contract

## Purpose

This contract records repository-side evidence for transaction boundaries, repository conventions, pagination, deterministic sorting, and performance-readiness controls.

## Required Transaction Boundary Evidence

- signup transaction boundary review evidence
- learner creation transaction boundary review evidence
- consent submission transaction boundary review evidence
- diagnostic completion transaction boundary review evidence
- lesson generation transaction boundary review evidence
- billing changes transaction boundary review evidence
- erasure request transaction boundary review evidence
- rollback on partial failure test evidence
- idempotent retry test evidence where appropriate

## Required Repository Evidence

- guardian repository evidence
- learner repository evidence
- consent repository evidence
- diagnostic repository evidence
- lesson repository evidence
- study-plan repository evidence
- gamification repository evidence
- audit repository evidence
- billing repository evidence
- repositories do not expose raw ORM objects to API responses
- repository method prefixes use `get_`, `list_`, `create_`, `update_`, `soft_delete_`, and `append_`
- list queries include pagination controls
- list queries include deterministic sorting controls
- cursor pagination is tracked for high-volume audit and event streams

## Required Performance Evidence

- slow-query logging is required in staging
- slow-query logging is required in production
- dashboard endpoint performance tests are tracked
- diagnostic endpoint performance tests are tracked
- lesson-generation endpoint performance tests are tracked
- parent-report endpoint performance tests are tracked
- audit endpoint performance tests are tracked
- POPIA export endpoint performance tests are tracked
- query latency budgets are defined before production launch
- DB connection pool monitoring is tracked
- N+1 query checks are tracked for dashboard flows

## Required Evidence Files

- `app/repositories/`
- `app/repositories/base.py`
- `docs/reference/repositories.md`
- `scripts/check_db_repository_evidence.py`
- `tests/unit/test_v2_repository_patterns.py`
- `tests/unit/test_v2_repositories_full.py`

## Verification Boundary

This contract validates repository-side and planning evidence. It does not perform production load testing, enable production telemetry, or approve live database performance posture.
