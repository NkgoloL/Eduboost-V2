---
title: "ADR-002 — Startup DDL Repair in `app/api_v2.py`"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-002 — Startup DDL Repair in `app/api_v2.py`

**Status:** Accepted (with migration plan)
**Date:** 2026-05-27 (Phase 1 T122)
**Decision owner:** Platform / Engineering
**Supersedes:** none

---

## Context

`app/api_v2.py` contains a `run_startup_migrations()` function (lines 35–165)
that executes DDL at application startup when `settings.is_production()` is
true. The function is called from the FastAPI `lifespan` context manager (line
171).

The audit raised a concern: this creates ambiguity about whether migrations
(Alembic) or startup logic (runtime code) owns schema correctness.

This ADR documents every DDL statement, the rationale for its existence, the
risk it poses, and the plan to migrate ownership entirely to Alembic.

---

## Inventory of startup DDL repairs

All repairs are idempotent (`IF NOT EXISTS` or existence checks). They are
wrapped in a `pg_try_advisory_lock` (key = 443352, 20260524) to prevent
concurrent execution by multiple worker processes.

| # | Name | DDL | Rationale (why not in Alembic) | Risk | Migration plan |
|---|---|---|---|---|---|
| 1 | `guardians.email_verified` | `ALTER TABLE guardians ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT false` | Column added during a hotfix deploy when Alembic was temporarily disabled. | Near-zero. `IF NOT EXISTS` + `DEFAULT false` makes it safe. | **Migrate to Alembic:** add a migration that adds the column with the same default. Then remove from startup. |
| 2 | `tokenpurpose` enum | `CREATE TYPE tokenpurpose AS ENUM ('password_reset', 'email_verify')` | Enum created during auth subsystem bootstrap before Alembic was introduced. | Low. `duplicate_object` exception is swallowed. | **Migrate to Alembic:** add a migration that creates the enum. Then remove from startup. |
| 3 | `secure_tokens` table | `CREATE TABLE IF NOT EXISTS secure_tokens (...)` | Table created for secure token storage during auth hardening. Pre-dates the Alembic migration that covers auth extensions. | Low. `IF NOT EXISTS` guards against re-creation. | **Migrate to Alembic:** add a migration that creates the table with full schema. Then remove from startup. |
| 4 | `ix_secure_tokens_user_purpose` | `CREATE INDEX IF NOT EXISTS ix_secure_tokens_user_purpose ON secure_tokens (user_id, purpose)` | Index added for token lookup performance. Created at same time as `secure_tokens` table. | Near-zero. `IF NOT EXISTS` guards. | **Migrate to Alembic:** include index in the same migration as `secure_tokens`. Then remove from startup. |
| 5 | `ix_secure_tokens_expires_at` | `CREATE INDEX IF NOT EXISTS ix_secure_tokens_expires_at ON secure_tokens (expires_at)` | Index added for token expiry cleanup queries. | Near-zero. `IF NOT EXISTS` guards. | **Migrate to Alembic:** include index in the same migration as `secure_tokens`. Then remove from startup. |
| 6 | `onboarding_states` table | `CREATE TABLE IF NOT EXISTS onboarding_states (...)` | Table for learner onboarding state tracking. Added during onboarding feature development. | Low. `IF NOT EXISTS` guards. | **Migrate to Alembic:** add a migration that creates the table with full schema. Then remove from startup. |
| 7 | `privacy_settings` table | `CREATE TABLE IF NOT EXISTS privacy_settings (...)` | Table for POPIA privacy settings (analytics, AI improvement, marketing, data retention). Added during POPIA compliance work. | Low. `IF NOT EXISTS` guards. | **Migrate to Alembic:** add a migration that creates the table with full schema. Then remove from startup. |

**Total repairs:** 7 DDL statements across 6 schema objects (1 column, 1 enum, 3 tables, 2 indexes).

---

## Rationale for startup DDL at the time it was introduced

Each repair was added during a production incident or feature sprint where:

1. The schema change was needed immediately to unblock a hotfix.
2. Running Alembic was considered too slow or risky (e.g., during a
   high-traffic period).
3. The change was small and idempotent, making runtime application safe.

This was a pragmatic choice under time pressure. It is no longer needed now
that the Alembic migration pipeline is validated (Phase 0 T022 proved
`alembic upgrade head` from an empty DB produces a clean schema).

---

## Risk assessment

| Risk | Severity | Mitigation | Status |
|---|---|---|---|
| Startup DDL conflicts with Alembic migration for same object | Medium | Every repair uses `IF NOT EXISTS` or an existence query. No collision can corrupt data. | Mitigated in code. |
| Startup DDL runs on every worker process start | Low | Advisory lock (`pg_try_advisory_lock`) ensures only one process executes repairs. Others skip. | Mitigated in code. |
| Startup DDL fails silently and leaves schema inconsistent | Low | Each repair logs success/failure. Timeouts are set (`lock_timeout = 5s`, `statement_timeout = 30s`). | Mitigated in code. |
| Startup DDL creates schema drift between environments | Medium | Dev/test environments skip the function (`if not settings.is_production(): return`). Only prod runs it. | **Risk accepted** but to be eliminated by migration. |
| Schema ownership ambiguity for new developers | Medium | Documented in this ADR. | **Mitigated by this ADR.** |

---

## Decision

**Schema correctness is owned by Alembic migrations. Startup DDL in
`app/api_v2.py` is a transitional mechanism that must be eliminated.**

The following plan is accepted:

### Phase A — Alembic migration consolidation (target: next sprint)

1. Create a single Alembic migration that adds every schema object listed in
   the inventory above, with `IF NOT EXISTS` guards (Alembic `op.execute`
   supports raw SQL with `IF NOT EXISTS` for PostgreSQL).
2. Run the migration against a disposable DB to verify it produces the same
   schema as the startup DDL.
3. Deploy the migration to production before removing the startup DDL.

### Phase B — Startup DDL removal (target: after Phase A is in production)

1. Remove `run_startup_migrations()` from `app/api_v2.py`.
2. Remove the `asyncpg` import and the DSN parsing code from `app/api_v2.py`.
3. Remove `run_startup_migrations()` call from the `lifespan` function.
4. Update `docs/operations/health.md` to remove any references to startup
   schema repair.

### Phase C — Prevention (ongoing)

1. Add a CI gate that fails if any PR adds DDL to `app/api_v2.py` (or any
   non-Alembic file). This can be a simple grep in `.github/workflows/`.
2. Document in the developer onboarding guide: "All schema changes must go
   through Alembic. Runtime DDL is not permitted except in documented
   emergency procedures."

---

## Consequences

### Positive

- Schema ownership is unambiguous: Alembic owns it.
- Production startup time improves (no DB connection + DDL checks on every
  deploy).
- All environments (dev, test, staging, prod) have the same schema path
  (Alembic migration history).

### Negative

- Requires a production migration window to add the consolidated Alembic
  migration before removing the startup DDL.
- The consolidated migration will be a no-op in environments where the
  startup DDL has already run (which is safe due to `IF NOT EXISTS`).

---

## Validation

After Phase A + B:

```bash
# 1. Confirm no startup DDL remains
grep -n "run_startup_migrations" app/api_v2.py
# Expected: no output

# 2. Confirm alembic upgrade head is still clean
alembic upgrade head
# Expected: exit 0, all migrations applied

# 3. Confirm schema objects exist
psql ... -c "\dt onboarding_states"
psql ... -c "\dt privacy_settings"
psql ... -c "\dt secure_tokens"
psql ... -c "\d guardians"
# Expected: all tables/columns present
```

---

## Task tracking

| Task | Status | Link |
|---|---|---|
| Create consolidated Alembic migration for 7 startup DDL objects | Open | See Phase A above |
| Remove `run_startup_migrations()` from `app/api_v2.py` | Blocked by ↑ | See Phase B above |
| Add CI gate banning non-Alembic DDL | Open | See Phase C above |
