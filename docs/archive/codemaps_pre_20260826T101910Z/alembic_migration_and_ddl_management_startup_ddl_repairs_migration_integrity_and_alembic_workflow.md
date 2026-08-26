# Alembic Migration and DDL Management: Startup DDL Repairs, Migration Integrity, and Alembic Workflow

This map covers EduBoost V2's database schema management through Alembic migrations and transitional startup DDL repairs. The system maintains a single-head linear migration graph with CI enforcement, runtime health checks, and a documented path to eliminate startup DDL in favor of pure Alembic ownership. Key entry points: startup DDL execution [1b], Alembic migration runner [2d], CI integrity gate [3b], and health check verification [4b].

## Trace ID: 1
**Title:** Startup DDL Repair Execution (Transitional Mechanism)

**Description:** Runtime system in api_v2.py that applies idempotent DDL repairs at application startup in production. This is a transitional mechanism documented in ADR-002 for eventual removal.

**Motivation:**
EduBoost V2 implements a transitional startup DDL repair mechanism to handle schema inconsistencies that occurred during the migration from legacy systems to V2. The system applies idempotent DDL repairs (ALTER TABLE, CREATE TABLE, CREATE INDEX) at application startup using PostgreSQL advisory locks to prevent concurrent execution across multiple workers. This approach ensures production systems can start even if schema is slightly out of sync, while providing a safety net during the transition period. The mechanism is production-only (skipped in dev/test) and documented in ADR-002 with a clear deprecation plan to migrate ownership to Alembic.

**Details:**
- **Execution Flow:** FastAPI lifespan() context manager called → log startup message → run_startup_migrations() → if not production: return → parse DATABASE_URL to DSN → connect via asyncpg → pg_try_advisory_lock() → if not locked: skip and return → for each repair in repairs tuple: fetchval(exists_sql) → if exists: skip this repair → conn.execute(statement) → log repair applied → pg_advisory_unlock() → conn.close() → seed_launch_content_if_needed() → create background tasks → yield (app serves requests)
- **Concurrency Safety:** PostgreSQL advisory lock prevents concurrent DDL execution across multiple workers. Lock uses session-level advisory lock (pg_try_advisory_lock). If lock not acquired, execution skipped (another worker handling it). Existence checks before DDL ensure idempotency. No distributed locks needed as advisory lock is cluster-wide
- **Covered Objects:** FastAPI lifespan context manager, run_startup_migrations() function, PostgreSQL advisory lock, DDL repair statements (ALTER TABLE, CREATE TABLE, CREATE INDEX), Existence checks, asyncpg connection, Production environment flag
- **Timeouts:** Advisory lock acquisition: ~10-50ms. Existence check: ~10-50ms per repair. DDL execution: ~100-500ms per repair. Total startup DDL: ~500ms-2s depending on repairs needed
- **Migration Path:** From startup DDL to pure Alembic ownership (per ADR-002). Migration requires: Phase A: Create consolidated Alembic migration with IF NOT EXISTS guards → Phase B: Remove run_startup_migrations() from api_v2.py → Phase C: Add CI gate blocking non-Alembic DDL
- **Error Handling:** Advisory lock failures skip execution (another worker handling it). DDL execution failures logged and deferred (statement_timeout). Connection failures logged but don't block startup. All errors logged with structured logging for monitoring
- **Security Considerations:** Production-only guard prevents accidental DDL in dev/test. Advisory lock prevents concurrent DDL conflicts. Idempotent DDL with IF NOT EXISTS guards prevents errors. DDL statements validated and documented. No credentials in code (DATABASE_URL from environment)

**Trace text diagram:**
```
FastAPI Application Startup
└── lifespan() context manager <-- api_v2.py:169
    ├── log startup message <-- api_v2.py:170
    ├── run_startup_migrations() <-- 1a
    │   ├── if not production: return <-- 1b
    │   ├── parse DATABASE_URL to DSN <-- api_v2.py:132
    │   ├── connect via asyncpg <-- api_v2.py:141
    │   ├── pg_try_advisory_lock() <-- 1c
    │   │   └── if not locked: skip and return <-- api_v2.py:146
    │   ├── for each repair in repairs tuple: <-- api_v2.py:151
    │   │   ├── fetchval(exists_sql) <-- 1d
    │   │   │   └── if exists: skip this repair <-- api_v2.py:153
    │   │   ├── conn.execute(statement) <-- 1e
    │   │   └── log repair applied <-- 1f
    │   ├── pg_advisory_unlock() <-- api_v2.py:163
    │   └── conn.close() <-- api_v2.py:164
    ├── seed_launch_content_if_needed() <-- api_v2.py:172
    ├── create background tasks <-- api_v2.py:176
    └── yield (app serves requests) <-- api_v2.py:179
```

**Location ID: 1a**
- **Title:** Startup DDL Invocation
- **Description:** FastAPI lifespan context manager calls startup migrations before serving requests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:171

**Location ID: 1b**
- **Title:** Production-Only Guard
- **Description:** Startup DDL only runs in production environments, skipped in dev/test
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:36

**Location ID: 1c**
- **Title:** Advisory Lock Acquisition
- **Description:** PostgreSQL advisory lock prevents concurrent DDL execution across multiple workers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:144

**Location ID: 1d**
- **Title:** Existence Check
- **Description:** Each repair checks if schema object already exists before attempting creation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:152

**Location ID: 1e**
- **Title:** DDL Statement Execution
- **Description:** Executes idempotent DDL (ALTER TABLE, CREATE TABLE, CREATE INDEX) with IF NOT EXISTS guards
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:156

**Location ID: 1f**
- **Title:** Repair Logging
- **Description:** Logs successful DDL application for operational visibility
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:160

### AI Guide: Startup DDL Repair Execution

**Motivation:**
The startup DDL repair execution is a transitional mechanism that applies idempotent schema repairs at application startup. This ensures production systems can start even with schema inconsistencies while preventing concurrent DDL execution through advisory locks.

**Details:**

**Production Guard and Locking**
The production guard only runs in production environments, skipping in dev/test to avoid schema drift and controlled by environment variable [1b]. The advisory lock uses PostgreSQL advisory lock to prevent concurrent execution with session-level lock (pg_try_advisory_lock), skipping if the lock is not acquired because another worker is handling it [1c].

**Idempotent Repairs**
Idempotent repairs check existence before DDL using IF NOT EXISTS guards and skip if the object already exists [1d][1e]. The execution loop iterates through the repair tuple, executes DDL if needed, and logs applied repairs for visibility.

**Cleanup**
The cleanup includes advisory unlock in a finally block and connection close to ensure cleanup even on failure [1f]. This ensures that locks are always released and connections are properly closed.

## Trace ID: 2
**Title:** Alembic Migration Execution (Primary Schema Management)

**Description:** Core Alembic infrastructure that manages database schema through versioned migrations. This is the authoritative schema management system per ADR-002.

**Motivation:**
EduBoost V2 uses Alembic as the authoritative schema management system, providing versioned, reversible database migrations. The system maintains a single-head linear migration graph to ensure schema consistency across environments. Alembic's autogenerate capability detects drift between ORM models and database schema, while CI enforcement prevents divergent branches. The system reads DATABASE_URL from environment (not alembic.ini) for security, imports all ORM models to populate Base.metadata for autogenerate, and executes migrations in transactions for atomicity. This approach provides a robust, auditable schema evolution path with rollback capability.

**Details:**
- **Execution Flow:** Command: alembic upgrade head → alembic/env.py → Read DATABASE_URL from env → Import app.models for metadata → run_migrations_online() → run_async_migrations() → do_run_migrations() → context.configure() with target_metadata and drift detection filters → context.run_migrations() → Execute pending migrations → 0001_v2_consolidated_schema (op.create_table()) → 20260523_0000_add_auth_extensions (enum.create()) → 20260524_1800_repair_schema (if column not exists) → Base.metadata (from app.models)
- **Concurrency Safety:** Alembic uses advisory locks internally to prevent concurrent migration execution. Migrations run in transactions for atomicity. Autogenerate uses read-only schema inspection. No distributed locks needed as Alembic handles concurrency. Multiple migration runs on different databases are independent
- **Covered Objects:** alembic/env.py, DATABASE_URL environment variable, app.models (ORM models), Base.metadata, Migration context, Migration files (versions/), op.create_table(), enum.create(), IF NOT EXISTS guards, Transaction management
- **Timeouts:** Environment read: <1ms. Model import: ~100-500ms. Context configuration: ~10-50ms. Migration execution: ~1-5s per migration. Total upgrade: ~5-30s depending on migration count
- **Migration Path:** From ad-hoc schema changes to Alembic-managed migrations. Migration requires: 1) Initialize Alembic (alembic init), 2) Configure env.py with DATABASE_URL, 3) Import ORM models, 4) Create initial migration, 5) Add CI enforcement for single head
- **Error Handling:** Missing DATABASE_URL raises RuntimeError. Migration execution failures rollback transaction. Drift detection fails CI. Invalid migration syntax fails during load. All errors logged with clear messages
- **Security Considerations:** DATABASE_URL from environment (not alembic.ini). No credentials in code. Migration files reviewed in PR. CI enforcement prevents unauthorized schema changes. Transaction rollback on failure. Drift detection prevents schema drift

**Trace text diagram:**
```
Alembic Migration Execution Flow
├── Command: `alembic upgrade head`
│   └── alembic/env.py
│       ├── Read DATABASE_URL from env <-- 2a
│       ├── Import app.models for metadata <-- 2b
│       ├── run_migrations_online() <-- env.py:104
│       │   └── run_async_migrations() <-- env.py:93
│       │       └── do_run_migrations() <-- env.py:80
│       │           ├── context.configure() <-- 2c
│       │           └── context.run_migrations() <-- 2d
│       │               └── Execute pending migrations
│       │                   ├── 0001_v2_consolidated_schema <-- 0001_v2_consolidated_schema.py:39
│       │                   │   └── op.create_table() <-- 2e
│       │                   ├── 20260523_0000_add_auth_extensions <-- 20260523_0000_add_auth_extensions.py:28
│       │                   │   └── enum.create() <-- 2f
│       │                   └── 20260524_1800_repair_schema <-- 20260524_1800_repair_auth_extensions_schema.py:43
│       │                       └── if column not exists <-- 2g
│       └── Base.metadata (from app.models) <-- env.py:40
```

**Location ID: 2a**
- **Title:** Database URL Configuration
- **Description:** Alembic reads DATABASE_URL from environment, never from alembic.ini
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/env.py:21

**Location ID: 2b**
- **Title:** ORM Model Import
- **Description:** Imports all SQLAlchemy models to populate Base.metadata for autogenerate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/env.py:41

**Location ID: 2c**
- **Title:** Migration Context Configuration
- **Description:** Configures Alembic context with target metadata and drift detection filters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/env.py:82

**Location ID: 2d**
- **Title:** Migration Execution
- **Description:** Executes all pending migrations in transaction
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/env.py:90

**Location ID: 2e**
- **Title:** Base Schema Creation
- **Description:** Initial migration creates foundational tables (guardians, learner_profiles, etc.)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/versions/0001_v2_consolidated_schema.py:45

**Location ID: 2f**
- **Title:** Enum Type Creation
- **Description:** Later migrations add enums, tables, and indexes with checkfirst guards
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/versions/20260523_0000_add_auth_extensions.py:35

**Location ID: 2g**
- **Title:** Drift Repair Migration
- **Description:** Repair migration checks existing schema state before applying changes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/alembic/versions/20260524_1800_repair_auth_extensions_schema.py:54

### AI Guide: Alembic Migration Execution

**Motivation:**
The Alembic migration execution system is the authoritative schema management mechanism. It manages versioned migrations, ensures single-head linear graph, and provides autogenerate capability for drift detection to maintain consistency between code and schema.

**Details:**

**Configuration**
The configuration reads DATABASE_URL from environment for security and imports ORM models to populate Base.metadata [2a][2b]. This enables autogenerate for drift detection by comparing ORM models to the current database schema.

**Context Setup and Execution**
The context setup configures the migration context with target metadata, sets drift detection filters, and configures transaction behavior [2c]. Migration execution executes pending migrations in transaction, runs upgrades sequentially, and handles rollback on failure [2d].

**Migration Files and Metadata**
Migration files are versioned files in alembic/versions/ that use op.create_table(), enum.create(), etc., with IF NOT EXISTS guards for idempotency [2e][2f][2g]. Base metadata from ORM models defines the target schema, used for autogenerate comparison to ensure consistency between code and schema.

## Trace ID: 3
**Title:** Migration Integrity CI Validation

**Description:** GitHub Actions workflow that enforces migration graph integrity, validates empty-DB upgrade path, and checks for schema drift before merging PRs.

**Motivation:**
EduBoost V2 implements comprehensive CI validation for database migrations to prevent schema inconsistencies and migration errors. The GitHub Actions workflow enforces single-head requirement (prevents divergent branches), validates empty-DB upgrade path (ensures fresh deployments work), detects schema drift (ORM vs database), validates seed files, and tests rollback capability. This multi-layered validation catches migration issues before they reach production, ensuring reliable schema evolution. The workflow runs on every PR, providing fast feedback and preventing breaking changes.

**Details:**
- **Execution Flow:** GitHub Actions Workflow triggers → Job: migration-check → PostgreSQL service container → Checkout & Python setup → Migration validation steps → Step 0: Assert single head (grep -c '(head)' check) → Step 1: Empty DB upgrade (alembic upgrade head) → Step 2: Drift detection (alembic check) → Step 3: Seed file validation (seed_item_bank.py --dry-run) → Step 6: Rollback test (alembic downgrade -2, alembic upgrade head) → Exit: Pass/Fail status to PR checks
- **Concurrency Safety:** CI workflow runs in isolated container. PostgreSQL service is fresh for each run. No concurrent CI runs on same PR. No distributed locks needed as CI is isolated. Multiple PRs can run concurrently
- **Covered Objects:** GitHub Actions workflow (migration_check.yml), PostgreSQL service container, Alembic CLI, Migration graph (heads, revisions), Database schema, ORM models, Seed files, Rollback capability
- **Timeouts:** PostgreSQL service startup: ~10-30s. Python setup: ~30-60s. Single head check: <1s. Empty DB upgrade: ~5-30s. Drift detection: ~5-10s. Seed validation: ~10-30s. Rollback test: ~10-30s. Total CI run: ~1-3min
- **Migration Path:** From manual migration testing to automated CI validation. Migration requires: 1) Create GitHub Actions workflow, 2) Add PostgreSQL service, 3) Configure validation steps, 4) Add branch protection rules, 5) Enable required status checks
- **Error Handling:** Single head check fails if multiple heads detected. Empty DB upgrade fails if migration errors. Drift detection fails if schema drift. Seed validation fails if seed errors. Rollback test fails if migration not reversible. All failures block PR merge
- **Security Considerations:** Database credentials from environment (not in workflow). Fresh PostgreSQL container for each run. No secrets in workflow files. Branch protection requires CI pass. Migration files reviewed in PR

**Trace text diagram:**
```
Migration Integrity CI Validation Pipeline
├── GitHub Actions Workflow <-- migration_check.yml:18
│   ├── Job: migration-check <-- migration_check.yml:43
│   │   ├── PostgreSQL service container <-- migration_check.yml:49
│   │   ├── Checkout & Python setup <-- migration_check.yml:76
│   │   └── Migration validation steps
│   │       ├── Step 0: Assert single head <-- 3a
│   │       │   └── grep -c '(head)' check <-- 3b
│   │       ├── Step 1: Empty DB upgrade <-- 3c
│   │       │   └── alembic upgrade head <-- migration_check.yml:118
│   │       │       └── alembic/env.py execution <-- env.py:105
│   │       ├── Step 2: Drift detection <-- 3d
│   │       │   └── alembic check <-- migration_check.yml:127
│   │       │       └── Compare ORM vs DB schema
│   │       ├── Step 3: Seed file validation <-- migration_check.yml:134
│   │       │   └── seed_item_bank.py --dry-run <-- migration_check.yml:136
│   │       └── Step 6: Rollback test <-- 3e
│   │           ├── alembic downgrade -2 <-- migration_check.yml:181
│   │           └── alembic upgrade head <-- migration_check.yml:182
│   └── Exit: Pass/Fail status to PR checks
```

**Location ID: 3a**
- **Title:** Single Head Assertion
- **Description:** CI step that fails if multiple migration heads are detected
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/migration_check.yml:100

**Location ID: 3b**
- **Title:** Head Count Check
- **Description:** Counts migration heads and exits non-zero if not exactly 1
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/migration_check.yml:103

**Location ID: 3c**
- **Title:** Empty DB Upgrade
- **Description:** Validates that fresh database can be upgraded from empty to head
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/migration_check.yml:118

**Location ID: 3d**
- **Title:** Drift Detection
- **Description:** Verifies no drift between ORM models and migrated database schema
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/migration_check.yml:127

**Location ID: 3e**
- **Title:** Rollback Test
- **Description:** Tests downgrade and re-upgrade to verify migration reversibility
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/migration_check.yml:181

### AI Guide: Migration Integrity CI Validation

**Motivation:**
The migration integrity CI validation system ensures migration quality through automated testing. The GitHub Actions workflow validates migration graph integrity, upgrade paths, and schema drift to prevent broken migrations from reaching production.

**Details:**

**Single Head and Empty DB**
The single head check asserts exactly one migration head to prevent divergent branches using grep to count heads, failing if count != 1 [3a][3b]. The empty DB upgrade validates the fresh deployment path by upgrading an empty database to head to ensure new deployments work and catch migration errors early [3c].

**Drift and Seed Validation**
Drift detection compares ORM models to database schema using the alembic check command to detect unauthorized schema changes, failing if drift is detected [3d]. Seed validation validates seed file syntax using --dry-run mode to ensure seed files work with the current schema.

**Rollback Testing**
The rollback test tests downgrade capability by downgrading 2 steps and re-upgrading to verify reversibility and catch non-reversible migrations [3e]. This ensures that migrations can be safely rolled back if needed.

## Trace ID: 4
**Title:** Runtime Migration Health Check

**Description:** Production health endpoint component that verifies Alembic migrations have been applied by querying alembic_version table and excluding sentinel values.

**Motivation:**
EduBoost V2 implements a runtime migration health check to verify that Alembic migrations have been applied correctly. The health check queries the alembic_version table to get the current migration state, excluding the 'base' sentinel value that indicates improper stamping. This check is part of the deep health check system and returns error status if no real migrations have been applied. The system enables monitoring and alerting for migration state issues, ensuring production systems are running the correct schema version. This provides operational visibility into migration state without requiring manual database inspection.

**Details:**
- **Execution Flow:** FastAPI /ready endpoint → ready() handler → gather_deep_health() → check_migrations() → AsyncSessionLocal context → session.execute(query) → SELECT version_num FROM alembic_version WHERE version_num != 'base' ORDER BY version_num DESC LIMIT 10 → result.fetchall() → if not rows: return error status (empty or only 'base' sentinel) → Returns 200 (ok/degraded) or 503 (error)
- **Concurrency Safety:** Health check is read-only. Database query is isolated. No locks needed as read operation. Multiple health checks can run concurrently. No state modification
- **Covered Objects:** FastAPI /ready endpoint, gather_deep_health() function, check_migrations() function, AsyncSessionLocal, alembic_version table, Query with base sentinel exclusion, Health status (ok/degraded/error)
- **Timeouts:** Health check invocation: <1ms. Database query: ~10-50ms. Result processing: <1ms. Total health check: ~10-50ms
- **Migration Path:** From manual migration verification to automated health check. Migration requires: 1) Implement check_migrations() function, 2) Add to gather_deep_health(), 3) Exclude base sentinel value, 4) Integrate with /ready endpoint, 5) Configure monitoring/alerting
- **Error Handling:** Database connection failures return error status. Query failures return error status. Empty results return error status. All errors logged for monitoring. Health check never blocks application startup
- **Security Considerations:** Read-only query (no schema modification). Excludes base sentinel to detect improper stamping. No credentials in code (DATABASE_URL from environment). Health check accessible via /ready endpoint. Monitoring can alert on error status

**Trace text diagram:**
```
Runtime Migration Health Check
├── FastAPI /ready endpoint
│   └── ready() handler <-- 4e
│       └── gather_deep_health() <-- health.py:190
│           └── check_migrations() <-- 4a
│               ├── AsyncSessionLocal context <-- health.py:126
│               │   └── session.execute(query) <-- 4b
│               │       └── SELECT version_num
│               │           FROM alembic_version
│               │           WHERE version_num != 'base' <-- 4c
│               │           ORDER BY version_num DESC
│               │           LIMIT 10
│               ├── result.fetchall() <-- health.py:135
│               └── if not rows: <-- health.py:136
│                   └── return error status <-- 4d
│                       (empty or only 'base' sentinel)
└── Returns 200 (ok/degraded) or 503 (error) <-- api_v2.py:307
```

**Location ID: 4a**
- **Title:** Health Check Invocation
- **Description:** Deep health check includes migration state as critical component
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:196

**Location ID: 4b**
- **Title:** Alembic Version Query
- **Description:** Queries alembic_version table to get current migration state
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:127

**Location ID: 4c**
- **Title:** Base Sentinel Exclusion
- **Description:** Excludes 'base' sentinel value that indicates improper stamping
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:130

**Location ID: 4d**
- **Title:** Empty Version Error
- **Description:** Returns error if no real migrations have been applied
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:137

**Location ID: 4e**
- **Title:** Health Endpoint Execution
- **Description:** Ready endpoint calls gather_deep_health which includes migration check
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:306

### AI Guide: Runtime Migration Health Check

**Motivation:**
The runtime migration health check verifies that Alembic migrations have been applied correctly. By querying the alembic_version table and excluding sentinel values, it detects migration state issues and integrates with the readiness endpoint for load balancer health checks.

**Details:**

**Health Check Invocation**
The health check invocation is called by gather_deep_health() as part of the deep health check system and is a critical component for readiness [4a]. This ensures that migration state is checked during health assessments.

**Version Query and Exclusion**
The version query queries the alembic_version table to get the current migration state, returning recent revisions with LIMIT 10 for performance [4b]. The base exclusion excludes the 'base' sentinel value to detect improper stamping and ensure real migrations have been applied [4c].

**Error Detection and Endpoint**
Error detection returns an error if no rows are found, indicating an empty or only base sentinel database, which triggers monitoring alerts [4d]. The health endpoint integrates with the /ready endpoint, returning 200 (ok/degraded) or 503 (error) to enable load balancer health checks [4e].

## Trace ID: 5
**Title:** Migration Graph Static Validation

**Description:** Database-free Python script that validates migration revision graph integrity, naming conventions, and single-head requirement without requiring database connection.

**Motivation:**
EduBoost V2 implements a database-free migration graph validation script to catch migration issues without requiring database connectivity. The script validates revision uniqueness, down_revision links, naming conventions (YYYYMMDD_HHMM_description.py), and single-head requirement. This static validation can run locally during development and in CI, providing fast feedback before attempting database migrations. The approach enables early detection of migration graph issues (broken links, divergent branches, naming violations) without database overhead, improving developer experience and preventing CI failures.

**Details:**
- **Execution Flow:** verify_migration_graph.py main() → load_migrations() → glob alembic/versions/*.py → ast.parse() each file → _literal_assignment(tree, "revision") → Validate revision uniqueness → Validate down_revision links (if down_revision not in revisions) → Validate naming convention (if not TIMESTAMPED_NAME.match()) → Validate graph topology → Count base revisions (expect 1) → Count head revisions (expect 1)
- **Concurrency Safety:** Script is stateless and read-only. File parsing is independent per migration. No shared state between validations. No locks needed as operations are isolated. Multiple script runs are independent
- **Covered Objects:** verify_migration_graph.py script, Migration files (alembic/versions/*.py), AST parser, Revision IDs, down_revision links, Naming convention regex, Graph topology (bases, heads)
- **Timeouts:** File discovery: ~10-50ms. AST parsing: ~10-50ms per file. Validation: ~10-50ms per file. Total validation: ~100-500ms depending on migration count
- **Migration Path:** From manual graph validation to automated static checks. Migration requires: 1) Create validation script, 2) Add to CI workflow, 3) Add to pre-commit hooks, 4) Document naming conventions, 5) Enforce single-head requirement
- **Error Handling:** Missing revision IDs fail validation. Broken down_revision links fail validation. Naming convention violations fail validation. Multiple bases/heads fail validation. All errors reported with file context
- **Security Considerations:** Script is read-only (no database access). No credentials required. AST parsing is safe. No code execution from migration files. Can run in untrusted environments

**Trace text diagram:**
```
Migration Graph Static Validation
└── verify_migration_graph.py main() <-- verify_migration_graph.py:73
    ├── load_migrations() <-- 5a
    │   ├── glob alembic/versions/*.py <-- verify_migration_graph.py:55
    │   ├── ast.parse() each file <-- verify_migration_graph.py:58
    │   └── _literal_assignment(tree, "revision") <-- 5b
    ├── Validate revision uniqueness <-- verify_migration_graph.py:78
    ├── Validate down_revision links
    │   └── if down_revision not in revisions <-- 5c
    ├── Validate naming convention
    │   └── if not TIMESTAMPED_NAME.match() <-- 5d
    └── Validate graph topology
        ├── Count base revisions (expect 1) <-- verify_migration_graph.py:105
        └── Count head revisions (expect 1) <-- 5e
```

**Location ID: 5a**
- **Title:** Migration File Discovery
- **Description:** Scans alembic/versions/ directory and parses migration metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/verify_migration_graph.py:53

**Location ID: 5b**
- **Title:** Revision Extraction
- **Description:** Uses AST parsing to extract revision and down_revision from migration files
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/verify_migration_graph.py:59

**Location ID: 5c**
- **Title:** Broken Link Detection
- **Description:** Validates that all down_revision references point to existing migrations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/verify_migration_graph.py:88

**Location ID: 5d**
- **Title:** Naming Convention Enforcement
- **Description:** Requires YYYYMMDD_HHMM_description.py format for new migrations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/verify_migration_graph.py:91

**Location ID: 5e**
- **Title:** Single Head Requirement
- **Description:** Fails if migration graph has multiple heads (divergent branches)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/verify_migration_graph.py:107

### AI Guide: Migration Graph Static Validation

**Motivation:**
The migration graph static validation script catches migration issues without database connectivity. Using AST parsing to validate graph integrity, naming conventions, and single-head requirement provides fast, safe validation that can run in CI and pre-commit hooks.

**Details:**

**File Discovery and Parsing**
File discovery scans the alembic/versions/ directory using glob pattern matching to load all migration files [5a]. AST parsing parses migration files with AST to extract revision and down_revision, using safe parsing without code execution [5b].

**Link and Naming Validation**
Link validation validates down_revision references by checking if the target exists to detect broken links [5c]. Naming convention enforcement enforces the YYYYMMDD_HHMM_description.py format using regex matching, with exemptions for legacy migrations [5d].

**Topology Validation**
Topology validation counts base revisions (expecting 1) and head revisions (expecting 1) to detect divergent branches [5e]. This ensures the migration graph maintains a single-head linear structure.

## Trace ID: 6
**Title:** Schema Integrity ORM Validation

**Description:** Database-free validation script that verifies SQLAlchemy ORM models contain required tables, indexes, constraints, and foreign keys for production readiness.

**Motivation:**
EduBoost V2 implements a database-free ORM validation script to ensure SQLAlchemy models define all required schema elements before deployment. The script validates that ORM metadata includes required tables, primary keys, created_at timestamps, foreign keys, indexes, and check constraints. This validation catches missing schema elements early, preventing runtime errors and ensuring production readiness. The database-free approach enables fast validation during development without requiring database connectivity, improving developer experience and catching issues before migration attempts.

**Details:**
- **Execution Flow:** Script Entry Point → main() function → Import app.models (side effect) → Populates Base.metadata → Get metadata = Base.metadata → Check missing tables (REQUIRED_TABLES - set(metadata.tables)) → For each required table: Extract primary key columns (table.primary_key.columns) → Validate created_at timestamp → Count foreign key constraints → Validate required indexes (required_indexes - actual_indexes) → Validate check constraints (required_constraints - actual_constraints) → Exit with status code (0=OK, 1=errors)
- **Concurrency Safety:** Script is stateless and read-only. Model import is side-effect but thread-safe. Metadata inspection is read-only. No locks needed as operations are isolated. Multiple script runs are independent
- **Covered Objects:** validate_schema_integrity.py script, app.models (ORM models), Base.metadata, Required tables list, Primary key columns, Foreign key constraints, Indexes, Check constraints, Validation errors
- **Timeouts:** Model import: ~100-500ms. Metadata inspection: ~10-50ms per table. Validation: ~10-50ms per table. Total validation: ~200ms-2s depending on table count
- **Migration Path:** From manual schema review to automated ORM validation. Migration requires: 1) Create validation script, 2) Define required tables, 3) Add validation rules, 4) Integrate with CI, 5) Add to pre-commit hooks
- **Error Handling:** Missing tables fail validation. Missing primary keys fail validation. Missing indexes fail validation. Missing constraints fail validation. All errors reported with table context
- **Security Considerations:** Script is read-only (no database access). No credentials required. Model import is safe. No code execution from models. Can run in untrusted environments

**Trace text diagram:**
```
Schema Integrity ORM Validation Script
├── Script Entry Point
│   └── main() function <-- validate_schema_integrity.py:84
│       ├── Import app.models (side effect) <-- 6a
│       │   └── Populates Base.metadata <-- validate_schema_integrity.py:85
│       ├── Get metadata = Base.metadata <-- validate_schema_integrity.py:85
│       ├── Check missing tables <-- 6b
│       │   └── REQUIRED_TABLES - set(metadata.tables) <-- validate_schema_integrity.py:88
│       ├── For each required table: <-- validate_schema_integrity.py:92
│       │   ├── Extract primary key columns <-- 6c
│       │   │   └── table.primary_key.columns <-- validate_schema_integrity.py:94
│       │   ├── Validate created_at timestamp <-- validate_schema_integrity.py:97
│       │   └── Count foreign key constraints <-- validate_schema_integrity.py:100
│       ├── Validate required indexes <-- 6d
│       │   └── required_indexes - actual_indexes <-- validate_schema_integrity.py:108
│       └── Validate check constraints <-- 6e
│           └── required_constraints - actual_constraints <-- validate_schema_integrity.py:116
└── Exit with status code (0=OK, 1=errors) <-- validate_schema_integrity.py:126
```

**Location ID: 6a**
- **Title:** Model Import Side Effect
- **Description:** Importing app.models populates Base.metadata with all ORM table definitions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/validate_schema_integrity.py:22

**Location ID: 6b**
- **Title:** Required Table Check
- **Description:** Validates that ORM metadata includes all production-critical tables
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/validate_schema_integrity.py:88

**Location ID: 6c**
- **Title:** Primary Key Validation
- **Description:** Ensures every table has explicit primary key defined
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/validate_schema_integrity.py:94

**Location ID: 6d**
- **Title:** Index Coverage Check
- **Description:** Validates that critical indexes exist for lookups and performance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/validate_schema_integrity.py:108

**Location ID: 6e**
- **Title:** Constraint Validation
- **Description:** Ensures check constraints exist for data integrity (grade ranges, non-negative values)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/validate_schema_integrity.py:116

### AI Guide: Schema Integrity ORM Validation

**Motivation:**
The schema integrity ORM validation script ensures SQLAlchemy models define all required schema elements. By validating tables, primary keys, indexes, and constraints without database connectivity, it provides fast validation that can run in CI and pre-commit hooks.

**Details:**

**Model Import**
The model import imports app.models as a side effect to populate Base.metadata, enabling schema inspection [6a]. This loads all ORM models so their metadata can be validated.

**Table and Primary Key Validation**
Table validation checks for missing required tables by comparing REQUIRED_TABLES to metadata.tables and reports missing tables [6b]. Primary key validation extracts primary key columns to ensure every table has a PK and reports missing PKs [6c].

**Index and Constraint Validation**
Index validation validates that required indexes exist by comparing required to actual and reports missing indexes [6d]. Constraint validation validates that check constraints exist to ensure data integrity rules and reports missing constraints [6e].

## Trace ID: 7
**Title:** Migration Smoke Test Workflow

**Description:** Shell script that performs upgrade/downgrade/re-upgrade cycle on disposable database to validate migration idempotency and rollback capability.

**Motivation:**
EduBoost V2 implements a migration smoke test workflow to validate migration idempotency and rollback capability on a disposable database. The script performs an upgrade/downgrade/re-upgrade cycle to ensure migrations work correctly in both directions and that re-running upgrades is a no-op (idempotent). This testing approach catches migration issues that might not be detected in CI, such as non-idempotent migrations or irreversible changes. The disposable database ensures safe testing without affecting production data, while the comprehensive cycle validates migration reliability.

**Details:**
- **Execution Flow:** scripts/smoke_test_migrations.sh → Database readiness check → wait_for_db.py --timeout 60 → Initial migration application → alembic upgrade head → Rollback capability test → alembic downgrade -1 → alembic upgrade head → Idempotency verification → alembic upgrade head (2nd run) → grep "Running upgrade" check → exit 1 if migrations applied
- **Concurrency Safety:** Script runs on disposable database. No concurrent smoke tests on same database. No locks needed as database is disposable. Multiple smoke tests can run on different databases
- **Covered Objects:** smoke_test_migrations.sh script, wait_for_db.py, Alembic CLI, Disposable database, Migration upgrade/downgrade, Idempotency check, Exit status
- **Timeouts:** Database readiness wait: ~10-60s. Initial upgrade: ~5-30s. Rollback test: ~10-30s. Idempotency check: ~5-30s. Total smoke test: ~30s-2min
- **Migration Path:** From manual migration testing to automated smoke tests. Migration requires: 1) Create smoke test script, 2) Add database readiness check, 3. Implement upgrade/downgrade cycle, 4) Add idempotency check, 5) Integrate with CI
- **Error Handling:** Database readiness timeout fails test. Upgrade failures fail test. Downgrade failures fail test. Idempotency failures fail test. All errors logged with context
- **Security Considerations:** Uses disposable database (no production data). Database credentials from environment. No secrets in script. Safe to run in CI. No impact on production

**Trace text diagram:**
```
Migration Smoke Test Workflow
└── scripts/smoke_test_migrations.sh <-- smoke_test_migrations.sh:1
    ├── Database readiness check
    │   └── wait_for_db.py --timeout 60 <-- 7a
    ├── Initial migration application <-- smoke_test_migrations.sh:13
    │   └── alembic upgrade head <-- 7b
    ├── Rollback capability test <-- smoke_test_migrations.sh:21
    │   ├── alembic downgrade -1 <-- 7c
    │   └── alembic upgrade head <-- 7d
    └── Idempotency verification <-- smoke_test_migrations.sh:29
        ├── alembic upgrade head (2nd run) <-- 7e
        └── grep "Running upgrade" check <-- 7f
            └── exit 1 if migrations applied <-- smoke_test_migrations.sh:34
```

**Location ID: 7a**
- **Title:** Database Readiness Wait
- **Description:** Waits for PostgreSQL to be ready before running migrations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/smoke_test_migrations.sh:10

**Location ID: 7b**
- **Title:** Initial Upgrade
- **Description:** Applies all migrations to empty database
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/smoke_test_migrations.sh:14

**Location ID: 7c**
- **Title:** Rollback Test
- **Description:** Tests that migrations can be rolled back one step
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/smoke_test_migrations.sh:22

**Location ID: 7d**
- **Title:** Re-upgrade
- **Description:** Re-applies migrations to verify forward path after rollback
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/smoke_test_migrations.sh:26

**Location ID: 7e**
- **Title:** Idempotency Check
- **Description:** Runs upgrade head again on current database to verify it's a no-op
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/smoke_test_migrations.sh:30

**Location ID: 7f**
- **Title:** Idempotency Failure Detection
- **Description:** Fails if second upgrade head applies migrations (indicates non-idempotent migrations)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/smoke_test_migrations.sh:32

### AI Guide: Migration Smoke Test Workflow

**Motivation:**
The migration smoke test workflow validates migration idempotency and rollback capability. By performing an upgrade/downgrade/re-upgrade cycle on a disposable database, it ensures migrations are safe to deploy and can be rolled back if needed.

**Details:**

**Database Readiness and Initial Upgrade**
Database readiness waits for PostgreSQL to be ready using wait_for_db.py with a timeout to ensure the database is accessible [7a]. The initial upgrade applies all migrations to an empty database to test the upgrade path and validate migration execution [7b].

**Rollback Test**
The rollback test downgrades one step and re-upgrades to head to test reversibility and validate rollback capability [7c][7d]. This ensures that migrations can be safely rolled back in production if needed.

**Idempotency Check**
The idempotency check runs upgrade head again and checks for "Running upgrade" output, failing if migrations are applied (non-idempotent) [7e][7f]. This ensures that migrations can be run multiple times without causing errors.

**Exit Status**
The exit status returns 0 for success and 1 for failure to enable CI integration and provide clear test results.

## Trace ID: 8
**Title:** ADR-002: Startup DDL Deprecation Plan

**Description:** Architecture Decision Record documenting the inventory of startup DDL repairs, their rationale, risks, and the three-phase plan to migrate ownership to Alembic.

**Motivation:**
EduBoost V2 documents the startup DDL deprecation plan in ADR-002 to provide clear guidance for eliminating the transitional startup DDL mechanism. The ADR inventories all 7 DDL repairs (columns, enums, tables, indexes), documents their rationale for not being in Alembic, assesses risks, and outlines a three-phase migration plan. This documentation ensures the team has a shared understanding of the deprecation path, prevents further proliferation of startup DDL, and provides a roadmap for achieving pure Alembic ownership. The three-phase plan (Consolidation, Removal, Prevention) ensures a safe, incremental transition without disrupting production.

**Details:**
- **Execution Flow:** ADR-002: Startup DDL to Alembic Migration Plan → Documentation Structure → Inventory Section (7 DDL repairs documented in table) → Example Repair Entry (DDL, rationale, risk assessment, migration plan) → Decision Section (Alembic owns schema correctness) → Three-Phase Migration Plan → Phase A: Consolidation (Create Alembic migration with IF NOT EXISTS guards) → Phase B: Removal (Delete run_startup_migrations() from api_v2.py) → Phase C: Prevention (Add CI gate blocking non-Alembic DDL)
- **Concurrency Safety:** ADR is documentation (no execution). No concurrency concerns. Can be read by multiple team members simultaneously. No locks needed
- **Covered Objects:** ADR-002 document, DDL repair inventory (7 repairs), Rationale documentation, Risk assessment, Three-phase migration plan, CI gate configuration, Developer documentation updates
- **Timeouts:** N/A (documentation only)
- **Migration Path:** From undocumented startup DDL to documented deprecation plan. Migration requires: 1) Inventory all startup DDL repairs, 2) Document rationale and risks, 3) Create three-phase plan, 4) Get team consensus, 5) Execute phases incrementally
- **Error Handling:** N/A (documentation only)
- **Security Considerations:** ADR documents security risks of startup DDL. Plan includes CI gate to prevent future DDL. No secrets in ADR. ADR reviewed and approved by team

**Trace text diagram:**
```
ADR-002: Startup DDL to Alembic Migration Plan <-- ADR-002-startup-ddl-repair.md:1
├── Documentation Structure
│   ├── Inventory Section <-- 8a
│   │   └── 7 DDL repairs documented in table <-- 8b
│   └── Decision Section <-- ADR-002-startup-ddl-repair.md:72
│       └── Alembic owns schema correctness <-- 8c
└── Three-Phase Migration Plan <-- ADR-002-startup-ddl-repair.md:77
    ├── Phase A: Consolidation <-- 8d
    │   └── Create Alembic migration with <-- ADR-002-startup-ddl-repair.md:81
    │       IF NOT EXISTS guards
    ├── Phase B: Removal <-- 8e
    │   └── Delete run_startup_migrations() <-- ADR-002-startup-ddl-repair.md:90
    │       from api_v2.py
    └── Phase C: Prevention <-- 8f
        └── Add CI gate blocking non-Alembic DDL <-- ADR-002-startup-ddl-repair.md:98
```

**Location ID: 8a**
- **Title:** DDL Repair Inventory
- **Description:** Documents 7 DDL statements across 6 schema objects (column, enum, tables, indexes)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:25

**Location ID: 8b**
- **Title:** Example Repair Entry
- **Description:** Each repair documented with DDL, rationale, risk assessment, and migration plan
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:33

**Location ID: 8c**
- **Title:** Decision Statement
- **Description:** Declares Alembic as single source of truth for schema management
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:74

**Location ID: 8d**
- **Title:** Phase A: Migration Creation
- **Description:** Create consolidated Alembic migration with IF NOT EXISTS guards for all startup DDL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:79

**Location ID: 8e**
- **Title:** Phase B: Startup DDL Removal
- **Description:** Remove run_startup_migrations() from api_v2.py after migration is deployed
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:88

**Location ID: 8f**
- **Title:** Phase C: Prevention
- **Description:** Add CI gate to prevent future non-Alembic DDL and update developer documentation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:96

### AI Guide: ADR-002 Startup DDL Deprecation Plan

**Motivation:**
ADR-002 documents the startup DDL deprecation plan with a three-phase migration path to achieve pure Alembic ownership. By inventorying DDL repairs, documenting rationale, and outlining a clear plan, it ensures a safe transition from the transitional startup DDL mechanism to authoritative Alembic management.

**Details:**

**Inventory and Decision**
The inventory documents all 7 DDL repairs including DDL, rationale, risk, and migration plan to provide a complete picture of startup DDL [8a][8b]. The decision declares Alembic as the single source of truth, establishing the ownership principle to prevent future startup DDL proliferation [8c].

**Phase A: Consolidation**
Phase A creates a consolidated Alembic migration that includes all startup DDL with IF NOT EXISTS guards, deploying to production before removal [8d]. This ensures that all startup DDL is captured in a single migration before the transitional mechanism is removed.

**Phase B: Removal**
Phase B removes run_startup_migrations() from api_v2.py only after Phase A is in production to eliminate the transitional mechanism [8e]. This ensures that the consolidated migration is in place before removing the startup DDL execution.

**Phase C: Prevention**
Phase C adds a CI gate blocking non-Alembic DDL and updates developer documentation to prevent future startup DDL [8f]. This ensures that the team follows the new process and prevents the reintroduction of startup DDL.
