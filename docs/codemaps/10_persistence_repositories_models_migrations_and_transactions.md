# EduBoost V2 Persistence, Repositories, Models, Migrations, and Transactions

Maps async database lifecycle, repository abstractions, ORM domains, transactional service patterns, Alembic migrations, Supabase artefacts, and resilience controls.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/core/database.py`
- `app/repositories`
- `app/models`
- `alembic`
- `supabase`
- `scripts/*migration*`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Async engine, session lifecycle, repositories, and transactions

**Description:** Follows a request from database dependency resolution through repository operations, commit, rollback, and cleanup.

**Motivation:**
Reliable persistence requires a single, understandable transaction boundary instead of hidden commits across services.

**Details:**

**Execution path**

1. Create the async engine and session factory from validated configuration.
2. Yield a request-scoped session.
3. Construct repositories or services against that session.
4. Execute reads and writes with explicit flush semantics.
5. Commit on accepted use-case completion or roll back on failure.
6. Close the session and return the connection to the pool.

**State and ownership boundaries**

ORM identity map and pending changes are session-scoped; domain services decide transaction boundaries.

**Failure, privacy, and control points**

Repositories do not silently commit, failed writes roll back together, and connection exhaustion and stale transactions are observable.

**Verification signals**

Run repository CRUD, transactional registration/completion/response, rollback, and database lifecycle tests.

**Trace text diagram:**
```text
1. Create the async engine and session factory from validated configuration [1a]
   |
   v
2. Yield a request-scoped session [1b]
   |
   v
3. Construct repositories or services against that session [1c]
   |
   v
4. Execute reads and writes with explicit flush semantics [1d]
   |
   v
5. Commit on accepted use-case completion or roll back on failure [1d]
   |
   v
6. Close the session and return the connection to the pool [1d]
```

**Location ID: 1a**
- **Title:** Database runtime
- **Description:** Engine, session factory, and dependency.
- **Path:LineNumber:** app/core/database.py:9

**Location ID: 1b**
- **Title:** Base repository
- **Description:** Generic async data access.
- **Path:LineNumber:** app/repositories/base.py:10

**Location ID: 1c**
- **Title:** Repository composition
- **Description:** Domain repository access patterns.
- **Path:LineNumber:** app/repositories/repositories.py:26

**Location ID: 1d**
- **Title:** Transactional use case
- **Description:** Atomic service-level persistence.
- **Path:LineNumber:** app/services/auth_transactional_registration.py:10

### AI Guide: Async engine, session lifecycle, repositories, and transactions

**Motivation:**
Reliable persistence requires a single, understandable transaction boundary instead of hidden commits across services.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors database runtime. [1b] anchors base repository. [1c] anchors repository composition. [1d] anchors transactional use case.

**Safe change boundary.** ORM identity map and pending changes are session-scoped; domain services decide transaction boundaries. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Repositories do not silently commit, failed writes roll back together, and connection exhaustion and stale transactions are observable.

**How to verify the change.** Run repository CRUD, transactional registration/completion/response, rollback, and database lifecycle tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** ORM domains and specialized repositories

**Description:** Maps model groups and repositories for identity, learning, content, billing, audit, retrieval, and runtime KG.

**Motivation:**
The model layer is the persistent vocabulary of the platform; domain boundaries should remain visible in table and repository ownership.

**Details:**

**Execution path**

1. Define ORM tables, constraints, indexes, and relationships.
2. Use specialized repositories for domain queries.
3. Translate persisted records into service/domain schemas.
4. Apply optimistic or explicit concurrency controls where required.
5. Emit audit and integrity evidence around sensitive writes.

**State and ownership boundaries**

Identity, diagnostic, content, billing, audit, retrieval, and graph domains have distinct tables but share database infrastructure.

**Failure, privacy, and control points**

Foreign keys and uniqueness enforce core invariants, repositories keep tenant/learner predicates explicit, and large payloads move to object storage.

**Verification signals**

Run model metadata, repository, schema-integrity, and domain persistence tests.

**Trace text diagram:**
```text
1. Define ORM tables, constraints, indexes, and relationships [2a]
   |
   v
2. Use specialized repositories for domain queries [2b]
   |
   v
3. Translate persisted records into service/domain schemas [2c]
   |
   v
4. Apply optimistic or explicit concurrency controls where required [2d]
   |
   v
5. Emit audit and integrity evidence around sensitive writes [2d]
```

**Location ID: 2a**
- **Title:** Content factory models
- **Description:** Generated content persistence domain.
- **Path:LineNumber:** app/models/content_factory.py:34

**Location ID: 2b**
- **Title:** Runtime KG models
- **Description:** Graph persistence domain.
- **Path:LineNumber:** app/models/runtime_kg.py:26

**Location ID: 2c**
- **Title:** Item bank repository
- **Description:** Specialized adaptive query access.
- **Path:LineNumber:** app/repositories/item_bank_repository.py:22

**Location ID: 2d**
- **Title:** Stripe event repository
- **Description:** Webhook idempotency persistence.
- **Path:LineNumber:** app/repositories/stripe_event_repository.py:11

### AI Guide: ORM domains and specialized repositories

**Motivation:**
The model layer is the persistent vocabulary of the platform; domain boundaries should remain visible in table and repository ownership.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors content factory models. [2b] anchors runtime kg models. [2c] anchors item bank repository. [2d] anchors stripe event repository.

**Safe change boundary.** Identity, diagnostic, content, billing, audit, retrieval, and graph domains have distinct tables but share database infrastructure. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Foreign keys and uniqueness enforce core invariants, repositories keep tenant/learner predicates explicit, and large payloads move to object storage.

**How to verify the change.** Run model metadata, repository, schema-integrity, and domain persistence tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Alembic, Supabase, migration integrity, backup, and restore

**Description:** Shows schema change authoring, graph validation, deployment migration, evidence capture, and recovery protection.

**Motivation:**
Production data safety depends on linear, reproducible migrations and proven restore paths.

**Details:**

**Execution path**

1. Author a forward and, where safe, reverse migration.
2. Run static graph and single-head validation.
3. Apply migrations to an empty and representative database.
4. Validate ORM/schema compatibility and seed repeatability.
5. Capture migration and backup evidence.
6. Deploy with readiness checks and retain rollback or restore path.

**State and ownership boundaries**

Migration history is append-only authority; backups are recovery artefacts with separate retention and integrity metadata.

**Failure, privacy, and control points**

Multiple heads fail CI, startup DDL does not replace migrations, destructive changes require controlled rollout, and backups are tested by restore.

**Verification signals**

Run migration_check, schema integrity, smoke migrations, backup matrix, and restore rollback evidence workflows.

**Trace text diagram:**
```text
1. Author a forward and, where safe, reverse migration [3a]
   |
   v
2. Run static graph and single-head validation [3b]
   |
   v
3. Apply migrations to an empty and representative database [3c]
   |
   v
4. Validate ORM/schema compatibility and seed repeatability [3d]
   |
   v
5. Capture migration and backup evidence [3d]
   |
   v
6. Deploy with readiness checks and retain rollback or restore path [3d]
```

**Location ID: 3a**
- **Title:** Alembic environment
- **Description:** Migration runtime configuration.
- **Path:LineNumber:** alembic/env.py:69

**Location ID: 3b**
- **Title:** Migration workflow
- **Description:** Hosted graph and migration checks.
- **Path:LineNumber:** .github/workflows/migration_check.yml:18

**Location ID: 3c**
- **Title:** Migration evidence
- **Description:** Reproducible migration capture.
- **Path:LineNumber:** scripts/capture_migration_evidence.py:263

**Location ID: 3d**
- **Title:** Restore evidence check
- **Description:** Backup and rollback assurance.
- **Path:LineNumber:** scripts/check_db_backup_restore_rollback_evidence.py:35

### AI Guide: Alembic, Supabase, migration integrity, backup, and restore

**Motivation:**
Production data safety depends on linear, reproducible migrations and proven restore paths.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors alembic environment. [3b] anchors migration workflow. [3c] anchors migration evidence. [3d] anchors restore evidence check.

**Safe change boundary.** Migration history is append-only authority; backups are recovery artefacts with separate retention and integrity metadata. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Multiple heads fail CI, startup DDL does not replace migrations, destructive changes require controlled rollout, and backups are tested by restore.

**How to verify the change.** Run migration_check, schema integrity, smoke migrations, backup matrix, and restore rollback evidence workflows. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
