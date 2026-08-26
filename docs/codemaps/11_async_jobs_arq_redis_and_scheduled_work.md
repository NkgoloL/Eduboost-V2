# EduBoost V2 Async Jobs, ARQ, Redis, and Scheduled Work

Maps job enqueueing, typed payloads, worker startup, dependency construction, retries, schedules, cleanup, and job integrity.

## Scope and ownership

This codemap is the primary architecture owner for:
- `app/core/jobs.py`
- `app/core/arq_worker.py`
- `app/jobs`
- `app/modules/jobs.py`
- `app/services/job_*`
- `app/services/arq_import_compat.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Job enqueue, payload contract, and status lifecycle

**Description:** Follows an API or service request that creates a durable asynchronous unit of work.

**Motivation:**
Long-running AI, generation, renewal, calibration, and cleanup operations must not block request workers or lose operational state.

**Details:**

**Execution path**

1. Validate job type, actor, consent, and payload.
2. Create an idempotency key and job record.
3. Serialize only supported identifiers and parameters.
4. Enqueue through ARQ/Redis.
5. Return a status handle to the caller.
6. Update status, result, and evidence as work progresses.

**State and ownership boundaries**

Redis queue state is transient execution state; database job records and artefacts provide durable product evidence.

**Failure, privacy, and control points**

Payloads exclude secrets, duplicate enqueue is controlled, queue unavailability is explicit, and users cannot poll another tenant’s jobs.

**Verification signals**

Run jobs router, queue compatibility, idempotency, status, and failure-path tests.

**Trace text diagram:**
```text
1. Validate job type, actor, consent, and payload [1a]
   |
   v
2. Create an idempotency key and job record [1b]
   |
   v
3. Serialize only supported identifiers and parameters [1c]
   |
   v
4. Enqueue through ARQ/Redis [1d]
   |
   v
5. Return a status handle to the caller [1d]
   |
   v
6. Update status, result, and evidence as work progresses [1d]
```

**Location ID: 1a**
- **Title:** Jobs routes
- **Description:** Submit and inspect background work.
- **Path:LineNumber:** app/api_v2_routers/jobs.py:15

**Location ID: 1b**
- **Title:** Job primitives
- **Description:** Queue and status contracts.
- **Path:LineNumber:** app/core/jobs.py:30

**Location ID: 1c**
- **Title:** Job module
- **Description:** Domain-facing job helpers.
- **Path:LineNumber:** app/modules/jobs.py:52

**Location ID: 1d**
- **Title:** Job integrity
- **Description:** Payload and runtime invariants.
- **Path:LineNumber:** app/services/job_runtime_integrity.py:8

### AI Guide: Job enqueue, payload contract, and status lifecycle

**Motivation:**
Long-running AI, generation, renewal, calibration, and cleanup operations must not block request workers or lose operational state.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors jobs routes. [1b] anchors job primitives. [1c] anchors job module. [1d] anchors job integrity.

**Safe change boundary.** Redis queue state is transient execution state; database job records and artefacts provide durable product evidence. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Payloads exclude secrets, duplicate enqueue is controlled, queue unavailability is explicit, and users cannot poll another tenant’s jobs.

**How to verify the change.** Run jobs router, queue compatibility, idempotency, status, and failure-path tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** ARQ worker startup and dependency factory

**Description:** Maps worker settings, registered functions, startup dependencies, execution, and shutdown.

**Motivation:**
Workers are separate runtime processes and must construct the same trusted dependencies as the API without importing test stubs accidentally.

**Details:**

**Execution path**

1. Start worker process and validate queue configuration.
2. Register approved job functions and cron entries.
3. Build database, Redis, provider, and service dependencies.
4. Deserialize and validate each job payload.
5. Execute within timeout and retry policy.
6. Close clients and publish terminal status on shutdown.

**State and ownership boundaries**

Worker context is process-scoped; each job receives isolated execution and transaction state.

**Failure, privacy, and control points**

Unknown jobs fail, test stubs require explicit opt-in, retries are bounded, and startup proves real dependency availability in canonical environments.

**Verification signals**

Run ARQ startup, dependency factory, backend selection, worker registration, and timeout tests.

**Trace text diagram:**
```text
1. Start worker process and validate queue configuration [2a]
   |
   v
2. Register approved job functions and cron entries [2b]
   |
   v
3. Build database, Redis, provider, and service dependencies [2c]
   |
   v
4. Deserialize and validate each job payload [2d]
   |
   v
5. Execute within timeout and retry policy [2d]
   |
   v
6. Close clients and publish terminal status on shutdown [2d]
```

**Location ID: 2a**
- **Title:** ARQ worker settings
- **Description:** Worker registration and lifecycle.
- **Path:LineNumber:** app/core/arq_worker.py:30

**Location ID: 2b**
- **Title:** Dependency factory
- **Description:** Worker service construction.
- **Path:LineNumber:** app/services/job_dependency_factory.py:9

**Location ID: 2c**
- **Title:** ARQ compatibility
- **Description:** Controlled real/stub import boundary.
- **Path:LineNumber:** app/services/arq_import_compat.py:6

**Location ID: 2d**
- **Title:** Startup backend tests
- **Description:** Backend selection regression coverage.
- **Path:LineNumber:** tests/unit/test_etl_mcp_server_startup.py:68

### AI Guide: ARQ worker startup and dependency factory

**Motivation:**
Workers are separate runtime processes and must construct the same trusted dependencies as the API without importing test stubs accidentally.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors arq worker settings. [2b] anchors dependency factory. [2c] anchors arq compatibility. [2d] anchors startup backend tests.

**Safe change boundary.** Worker context is process-scoped; each job receives isolated execution and transaction state. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Unknown jobs fail, test stubs require explicit opt-in, retries are bounded, and startup proves real dependency availability in canonical environments.

**How to verify the change.** Run ARQ startup, dependency factory, backend selection, worker registration, and timeout tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Scheduled AI, content, consent, curriculum, IRT, and cleanup jobs

**Description:** Shows the platform’s registered scheduled and batch jobs and their evidence boundaries.

**Motivation:**
Scheduled work changes production state without a direct user request, so ownership, limits, and auditability must be explicit.

**Details:**

**Execution path**

1. Scheduler or operator selects a registered job.
2. Load bounded work candidates.
3. Re-check consent, state, and feature flags.
4. Process each candidate with per-item isolation.
5. Persist results and metrics.
6. Record completion, retryable failures, and dead-letter outcomes.

**State and ownership boundaries**

Each job owns a narrow state transition; batch summaries never replace item-level evidence.

**Failure, privacy, and control points**

Schedules avoid overlapping unsafe runs, work is chunked, cancellation is respected, and cleanup never deletes active records.

**Verification signals**

Run each app/jobs unit suite plus cron registration, retry, and cleanup integration tests.

**Trace text diagram:**
```text
1. Scheduler or operator selects a registered job [3a]
   |
   v
2. Load bounded work candidates [3b]
   |
   v
3. Re-check consent, state, and feature flags [3c]
   |
   v
4. Process each candidate with per-item isolation [3d]
   |
   v
5. Persist results and metrics [3d]
   |
   v
6. Record completion, retryable failures, and dead-letter outcomes [3d]
```

**Location ID: 3a**
- **Title:** AI operations job
- **Description:** Scheduled AI governance processing.
- **Path:LineNumber:** app/jobs/ai_operations_job.py:8

**Location ID: 3b**
- **Title:** Batch generation job
- **Description:** Content generation background work.
- **Path:LineNumber:** app/jobs/batch_generation_job.py:17

**Location ID: 3c**
- **Title:** Consent renewal job
- **Description:** Scheduled renewal processing.
- **Path:LineNumber:** app/jobs/consent_renewal_job.py:30

**Location ID: 3d**
- **Title:** Practice cleanup job
- **Description:** Expired practice state cleanup.
- **Path:LineNumber:** app/jobs/practice_session_cleanup_job.py:31

### AI Guide: Scheduled AI, content, consent, curriculum, IRT, and cleanup jobs

**Motivation:**
Scheduled work changes production state without a direct user request, so ownership, limits, and auditability must be explicit.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors ai operations job. [3b] anchors batch generation job. [3c] anchors consent renewal job. [3d] anchors practice cleanup job.

**Safe change boundary.** Each job owns a narrow state transition; batch summaries never replace item-level evidence. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Schedules avoid overlapping unsafe runs, work is chunked, cancellation is respected, and cleanup never deletes active records.

**How to verify the change.** Run each app/jobs unit suite plus cron registration, retry, and cleanup integration tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
