# Alembic Rollback Policy Gap — 2026-05-28

Known issue: downgrade-to-base previously failed due to PostgreSQL enum dependency cycles.

Decision required:

1. Support Alembic downgrade as rollback path and fix downgrade order/CASCADE handling; or
2. Declare restore-from-backup / forward-fix as authoritative production rollback model.

Until decided, production rollback posture is incomplete.
