# Backend Consolidation Dragons

This document records the architectural risks identified by the backend consolidation proposal. These are not approval to delete or consolidate code directly; they are tracked as diagnostic targets for evidence-first batches.

## Dragon 1 — Split audit persistence

**Risk:** The backend may contain two audit persistence concepts, such as `audit_events` and `audit_logs`, plus multiple `AuditRepository` implementations.

**Release-safety invariant:**

- Security/POPIA-sensitive actions must write to one canonical append-only audit trail.
- Legacy audit call sites must be inventoried before deletion.
- Historical audit data must not be discarded without explicit legal/security approval.

## Dragon 2 — Split consent persistence/service paths

**Risk:** Consent state may be represented through multiple services or tables such as `consent_records` and `parental_consents`.

**Release-safety invariant:**

- Active-consent checks must have one canonical runtime path.
- Consent history/current-state semantics must be documented before table consolidation.
- POPIA data-rights routes must preserve explicit read/write authorization boundaries.

## Dragon 3 — ORM/schema drift

**Risk:** Alembic can report the database as current while expected ORM tables are missing from the live database.

**Release-safety invariant:**

- Fresh disposable PostgreSQL must pass `alembic upgrade head`.
- SQLAlchemy metadata tables must match expected runtime database tables, or every intentional difference must be documented.
- Do not use `alembic stamp head` or baseline repair until the mismatch is understood.

## Dragon 4 — Health/readiness false positives

**Risk:** Health endpoints may check only a narrow dependency and miss missing core tables or schema drift.

**Release-safety invariant:**

- Lightweight health stays cheap.
- Deep health/readiness should verify critical runtime dependencies and schema presence without unsafe public mutations.
- Any mutating audit write/readiness check must be admin/internal only.

## Dragon 5 — Delete-first consolidation risk

**Risk:** Removing duplicate-looking repositories/services before call-site inventory can break compatibility and lose evidence.

**Release-safety invariant:**

- Inventory first.
- Add adapters where needed.
- Migrate call sites.
- Prove tests and evidence are green.
- Delete legacy code last.

## Batch policy

The next backend consolidation batches must follow this sequence:

1. Diagnostic inventory.
2. Compatibility adapters if needed.
3. Runtime call-site migration.
4. Schema/data migration decision record.
5. Deletion only after full-suite and migration evidence pass.
