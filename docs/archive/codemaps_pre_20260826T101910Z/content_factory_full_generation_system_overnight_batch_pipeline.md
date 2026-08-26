# Content Factory Full Generation System: Overnight Batch Pipeline

End-to-end overnight batch generation pipeline that orchestrates content creation from planning through review submission. The system starts with gap analysis [1b], creates generation tasks [2d], executes them via providers [3c], validates artifacts [5b], verifies staging readiness [6c], seeds to staging [7c], and produces comprehensive reports [8b]. Human review gates prevent automatic approval [5e].

## Trace ID: 1
**Title:** Overnight Run Orchestration: Entry Point to Task Planning

**Description:** Main orchestration flow in run_full_generation.py that acquires locks, creates runs, and invokes the planner to identify missing content

**Motivation:**
EduBoost V2 implements an overnight batch generation pipeline to automate content creation at scale without disrupting daytime operations. The system uses distributed locks to prevent concurrent runs, ensuring only one generation process runs at a time. This approach allows for efficient resource utilization during off-peak hours while maintaining data integrity. The orchestration flow coordinates multiple phases: lock acquisition, run tracking, gap analysis, task execution, optional staging operations, and report generation. This centralized orchestration ensures reproducibility, auditability, and error handling across the entire generation pipeline.

**Details:**
- **Execution Flow:** CLI entry point main() called → asyncio.run(run_full_generation()) → Environment check (CONTENT_FACTORY_GENERATION_ENABLED) → Lock acquisition (ContentGenerationRunLock.acquire()) → Run record creation (ContentGenerationRun) → Planning phase (planner.plan_missing_for_run()) → Execution loop (for each task_id in plan_result) → Task execution and status update → Optional: seed_approved_to_staging → Optional: verify_staging → Optional: write_report → finally: lock.release()
- **Concurrency Safety:** Distributed lock with TTL prevents concurrent overnight runs. Lock acquisition uses holder identifier (hostname:pid) for tracking. Lock release in finally block ensures cleanup even on failure. Task execution is sequential within a run. No distributed locks needed within single run as operations are ordered
- **Covered Objects:** ContentGenerationRunLock, ContentGenerationRun record, ContentGenerationPlanner, ContentGenerationTask records, ContentSeedPromotionService, ContentStagingReadinessService, ContentGenerationReporter, Database session, CLI arguments
- **Timeouts:** Lock acquisition: ~1-5s. Run creation: ~10-50ms. Planning phase: ~1-5min. Task execution: varies by task count (5-30min per task). Staging operations: ~1-5min. Report generation: ~10-30s. Total overnight run: ~30min to several hours depending on task count
- **Migration Path:** From manual content generation to automated overnight pipeline. Migration requires: 1) Implement distributed lock mechanism, 2) Create run tracking system, 3) Integrate planner and executor services, 4) Add optional staging and reporting phases, 5) Configure cron/scheduler for overnight execution
- **Error Handling:** Environment check fails if CONTENT_FACTORY_GENERATION_ENABLED is false. Lock acquisition fails if lock already held (returns error). Planning failures logged and may fail run. Task execution failures logged but don't stop entire run. Lock release in finally ensures cleanup. All errors logged to stdout and error log
- **Security Considerations:** Lock holder identifier includes hostname and pid for tracking. Run records track who initiated generation. Environment variable controls enablement. Database credentials from environment. No secrets in CLI arguments. Report generation may include sensitive metadata

**Trace text diagram:**
```
Overnight Batch Run Entry Point
├── CLI Entry: main() <-- 1a
│   └── asyncio.run(run_full_generation()) <-- run_full_generation.py:201
│       ├── Environment check <-- run_full_generation.py:48
│       │   └── CONTENT_FACTORY_GENERATION_ENABLED
│       ├── Lock acquisition <-- 1b
│       │   └── ContentGenerationRunLock.acquire()
│       ├── Run record creation <-- 1c
│       │   └── ContentGenerationRun(run_id, status)
│       ├── Planning phase <-- 1d
│       │   └── planner.plan_missing_for_run()
│       ├── Execution loop <-- run_full_generation.py:110
│       │   ├── for task_id in plan_result
│       │   └── task.status = "completed" <-- run_full_generation.py:127
│       ├── Optional: seed_approved_to_staging <-- run_full_generation.py:142
│       ├── Optional: verify_staging <-- run_full_generation.py:148
│       ├── Optional: write_report <-- run_full_generation.py:154
│       └── finally: lock.release() <-- 1e
```

**Location ID: 1a**
- **Title:** Entry Point: Main Function
- **Description:** Async entry point that kicks off the full generation pipeline with parsed CLI arguments
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:201

**Location ID: 1b**
- **Title:** Lock Acquisition
- **Description:** Prevents concurrent overnight runs by acquiring a distributed lock with TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:57

**Location ID: 1c**
- **Title:** Run Record Creation
- **Description:** Creates database record tracking this generation run with metadata about layers and limits
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:67

**Location ID: 1d**
- **Title:** Invoke Planner
- **Description:** Delegates to ContentGenerationPlanner to analyze gaps and create generation tasks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:89

**Location ID: 1e**
- **Title:** Lock Release
- **Description:** Ensures lock is released in finally block even if generation fails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:179

### AI Guide: Overnight Run Orchestration

**Motivation:**
The overnight run orchestration is the main entry point for the content generation pipeline, coordinating all phases from lock acquisition through report generation. The system ensures safe, non-concurrent execution while providing flexibility for optional staging and reporting phases.

**Details:**

**Lock Management and Run Tracking**
Lock management uses a distributed lock to prevent concurrent runs, ensuring data integrity with a holder identifier (hostname:pid) for tracking and a finally block to ensure lock release even on failure [1b][1e]. Run tracking uses a ContentGenerationRun record to track metadata, status, and timing for auditability, enabling monitoring and debugging of generation runs [1c].

**Planning and Execution**
The planning phase delegates to the ContentGenerationPlanner to analyze coverage gaps and create tasks, centralizing gap analysis logic [1d]. The execution loop sequentially executes tasks created during planning, updates task status as tasks complete, and handles failures gracefully without stopping the entire run.

**Optional Phases**
Optional phases include staging seeding and verification based on CLI flags, and report generation for debugging and audit purposes. This provides flexibility for different deployment scenarios while maintaining core pipeline functionality.

## Trace ID: 2
**Title:** Content Gap Planning: Readiness Analysis to Task Creation

**Description:** ContentGenerationPlanner service that identifies coverage gaps via staging readiness verification, validates source context availability, and creates idempotent generation tasks

**Motivation:**
EduBoost V2 uses a gap analysis system to identify missing content before generation, ensuring efficient resource utilization and avoiding duplicate work. The planner analyzes current coverage against targets, validates source availability, and creates generation tasks only for missing content. This approach prevents over-generation, ensures source data is available before attempting generation, and provides idempotency through task deduplication. The system balances comprehensive coverage analysis with performance by batching operations and using efficient database queries.

**Details:**
- **Execution Flow:** ContentGenerationPlanner.plan_missing_for_run() called → Get run and scopes from registry → For each scope: Verify scope readiness via ContentStagingReadinessService.verify_scope() → For each layer in report: Calculate missing count (target - approved) → Build source context via SourceContextService.validate ETL chunks → Check idempotency key (prevent duplicate tasks) → Create task record (ContentGenerationTask) → Persist task to session (session.add) → Update run metadata with plan → Return GenerationPlanResult
- **Concurrency Safety:** Planning is read-only for existing data. Task creation uses idempotency key to prevent duplicates. Database session provides transaction isolation. No distributed locks needed as planning is idempotent. Multiple planners can run concurrently on different runs
- **Covered Objects:** ContentGenerationPlanner, ContentStagingReadinessService, SourceContextService, ContentGenerationTask records, ContentScope records, GenerationPlanResult, Database session, Scope definitions, Layer targets
- **Timeouts:** Scope loading: ~100-500ms per scope. Readiness verification: ~1-5s per scope. Source context validation: ~500ms-2s per scope. Task creation: ~10-50ms per task. Total planning: ~5-30min depending on scope count
- **Migration Path:** From manual task creation to automated gap analysis. Migration requires: 1) Implement readiness verification service, 2) Add source context validation, 3) Implement idempotency key logic, 4) Create task creation with deduplication, 5) Update run tracking with plan metadata
- **Error Handling:** Scope loading failures logged and skip scope. Readiness verification failures logged and skip scope. Source context validation failures skip layer (no task created). Idempotency check prevents duplicate tasks. Database failures fail entire planning phase. All errors logged with context
- **Security Considerations:** Idempotency key prevents duplicate generation. Source context validation ensures approved sources only. Task metadata tracks provenance. No secrets in task records. Scope access controlled by registry

**Trace text diagram:**
```
Content Gap Planning Pipeline
└── ContentGenerationPlanner.plan_missing_for_run() <-- content_generation_planner.py:49
    ├── Get run and scopes from registry <-- content_generation_planner.py:59
    ├── For each scope: <-- content_generation_planner.py:68
    │   ├── Verify scope readiness <-- 2a
    │   │   └── ContentStagingReadinessService
    │   │       └── verify_scope() <-- content_staging_readiness.py:132
    │   ├── For each layer in report: <-- content_generation_planner.py:70
    │   │   ├── Calculate missing count <-- 2b
    │   │   │   └── target - approved
    │   │   ├── Build source context <-- 2c
    │   │   │   └── SourceContextService
    │   │   │       └── validate ETL chunks <-- source_context.py:42
    │   │   ├── Check idempotency key <-- content_generation_planner.py:83
    │   │   └── Create task record <-- 2d
    │   │       └── ContentGenerationTask()
    │   └── Persist task to session <-- 2e
    │       └── session.add(task)
    └── Update run metadata with plan <-- content_generation_planner.py:119
        └── return GenerationPlanResult <-- content_generation_planner.py:121
```

**Location ID: 2a**
- **Title:** Verify Scope Readiness
- **Description:** Analyzes current coverage vs targets to identify missing artifacts per layer
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:69

**Location ID: 2b**
- **Title:** Calculate Gap
- **Description:** Computes how many artifacts are needed to reach coverage target
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:73

**Location ID: 2c**
- **Title:** Build Source Context
- **Description:** Validates that approved ETL source chunks are available for generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:77

**Location ID: 2d**
- **Title:** Create Generation Task
- **Description:** Creates task record with idempotency key to prevent duplicate generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:88

**Location ID: 2e**
- **Title:** Persist Task
- **Description:** Adds task to database session for batch insertion
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:112

### AI Guide: Content Gap Planning

**Motivation:**
The content gap planning system analyzes coverage gaps, validates source availability, and creates generation tasks. The planner ensures efficient resource utilization by only generating missing content while preventing duplicate work through idempotency.

**Details:**

**Readiness Verification and Gap Calculation**
Readiness verification uses the ContentStagingReadinessService to analyze current coverage against targets, identifying which layers need generation and ensuring staging readiness before planning [2a]. Gap calculation computes the missing count as target minus approved, handling edge cases (negative gaps, zero gaps) and skipping layers with no missing content [2b].

**Source Context Validation and Idempotency**
Source context validation uses the SourceContextService to validate ETL source chunks, ensuring approved sources are available and validating quality and licensing [2c]. The idempotency check uses a composite key (scope, layer, source chunks) to prevent duplicate tasks, enabling safe re-running of the planning phase.

**Task Creation**
Task creation creates ContentGenerationTask with metadata, batch persists to the database for efficiency, and tracks provenance and configuration [2d][2e]. This ensures that tasks are created efficiently with full traceability.

## Trace ID: 3
**Title:** Task Execution: Provider Invocation to Artifact Creation

**Description:** ContentGenerationExecutor service that executes queued tasks by calling generation providers (deterministic or LLM) and creating validated artifacts

**Motivation:**
EduBoost V2 implements a task execution system that coordinates provider invocation with artifact creation and validation. The executor manages task lifecycle (queued → running → succeeded/failed), locks tasks to prevent concurrent execution, and integrates multiple provider types (deterministic and LLM). This abstraction allows for flexible provider implementation while maintaining consistent artifact creation and validation. The system handles provider failures gracefully, supports artifact limits per task, and ensures provenance tracking through source citations.

**Details:**
- **Execution Flow:** ContentGenerationExecutor.execute_task() called → task.status = "running" → Lock task with expiration → Source context validation (source_context_service.build_context()) → Provider invocation (_call_provider(provider, task, chunks)) → Build DiagnosticGenerationRequest → provider.generate_diagnostic_items() → Return validation lambdas → Artifact creation loop (for each payload) → stable_json_hash(artifact_json) → validation_errors() call → content_factory_service.create_artifact() → validate_artifact_payload → ContentGenerationArtifact() → ContentArtifactSource records → Update task metadata (task.output_artifact_ids) → task.status = "succeeded"/"failed" → session.flush()
- **Concurrency Safety:** Task lock with expiration prevents concurrent execution. Lock includes holder identifier and expiration timestamp. Source context validation is stateless. Provider invocation is isolated per task. Artifact creation uses database transactions. No distributed locks needed as task-level locks suffice
- **Covered Objects:** ContentGenerationExecutor, ContentGenerationTask, SourceContextService, Generation providers (deterministic, LLM), ContentFactoryService, ContentGenerationArtifact, ContentArtifactSource, Database session, Validation lambdas, Artifact hashes
- **Timeouts:** Task lock acquisition: ~10-50ms. Source context validation: ~500ms-2s. Provider invocation: ~5-30s per artifact. Artifact creation: ~100-500ms per artifact. Task completion: ~10-60s depending on artifact count
- **Migration Path:** From direct provider calls to executor abstraction. Migration requires: 1) Implement task locking mechanism, 2) Add source context re-validation, 3) Integrate provider abstraction, 4) Add artifact creation loop, 5) Implement task status updates
- **Error Handling:** Task lock failures skip task (already running). Source context validation failures fail task. Provider invocation failures fail task with error details. Artifact creation failures logged but don't stop task. Task status updated based on overall success. All errors logged with context
- **Security Considerations:** Task lock prevents concurrent execution. Source context validation ensures approved sources. Provider credentials from environment. Artifact validation ensures quality. Provenance tracking via source citations. No secrets in task records

**Trace text diagram:**
```
Task Execution Flow (Trace 3)
└── ContentGenerationExecutor.execute_task() <-- content_generation_executor.py:67
    ├── task.status = "running" <-- 3a
    ├── Lock task with expiration <-- content_generation_executor.py:78
    ├── Source context validation
    │   └── source_context_service.build_context() <-- 3b
    ├── Provider invocation
    │   └── _call_provider(provider, task, chunks) <-- 3c
    │       ├── Build DiagnosticGenerationRequest <-- content_generation_executor.py:196
    │       ├── provider.generate_diagnostic_items() <-- deterministic.py:16
    │       └── Return validation lambdas <-- content_generation_executor.py:197
    ├── Artifact creation loop <-- content_generation_executor.py:91
    │   ├── stable_json_hash(artifact_json) <-- content_generation_executor.py:93
    │   ├── validation_errors() call <-- content_generation_executor.py:94
    │   └── content_factory_service.create_artifact() <-- 3d
    │       ├── validate_artifact_payload() <-- content_factory.py:177
    │       ├── ContentGenerationArtifact() <-- content_factory.py:185
    │       └── ContentArtifactSource records <-- content_factory.py:206
    ├── Update task metadata
    │   ├── task.output_artifact_ids <-- content_generation_executor.py:127
    │   └── task.status = "succeeded"/"failed" <-- 3e
    └── session.flush() <-- content_generation_executor.py:136
```

**Location ID: 3a**
- **Title:** Mark Task Running
- **Description:** Updates task status and acquires lock with expiration timestamp
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:76

**Location ID: 3b**
- **Title:** Rebuild Source Context
- **Description:** Re-validates source availability at execution time (may have changed since planning)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:82

**Location ID: 3c**
- **Title:** Call Generation Provider
- **Description:** Invokes deterministic or LLM provider to generate content artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:87

**Location ID: 3d**
- **Title:** Create Artifact Record
- **Description:** Persists generated artifact with validation, provenance, and source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:97

**Location ID: 3e**
- **Title:** Update Task Status
- **Description:** Marks task as succeeded or failed based on artifact creation results
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:133

### AI Guide: Task Execution

**Motivation:**
The task execution system manages the lifecycle of generation tasks, coordinating provider invocation with artifact creation. The executor ensures safe, isolated task execution while supporting multiple provider types and maintaining comprehensive validation.

**Details:**

**Task Locking and Source Re-validation**
Task locking locks the task with expiration to prevent concurrent execution, includes a holder identifier for tracking, and uses expiration to prevent stale locks [3a]. Source context re-validation re-validates source availability at execution time, handles changes since the planning phase, and ensures sources are still approved and available [3b].

**Provider Invocation and Artifact Creation**
Provider invocation abstracts the provider interface (deterministic, LLM), builds provider-specific requests, and returns validation lambdas for deferred validation [3c]. The artifact creation loop iterates through generated payloads, creates artifacts with validation, handles duplicate detection via hash, and tracks source citations [3d].

**Task Status Updates**
Task status updates update the task status based on overall success, track output artifact IDs, and enable monitoring and debugging [3e]. This ensures that task execution is tracked comprehensively throughout the lifecycle.

## Trace ID: 4
**Title:** Diagnostic Item Generation: Provider to Validation

**Description:** Layer-specific generation flow showing how diagnostic items are created via DeterministicContentGenerationProvider and validated before artifact creation

**Motivation:**
EduBoost V2 implements layer-specific generation flows to handle different content types appropriately. The diagnostic item generation flow demonstrates how the DeterministicContentGenerationProvider creates structured assessment items with questions, options, answers, and source citations. This provider uses deterministic algorithms rather than LLM generation for consistency and predictability. The flow includes deferred validation via lambdas, allowing validation to occur after generation while maintaining separation of concerns. This approach enables efficient batch generation with comprehensive quality checks.

**Details:**
- **Execution Flow:** ContentGenerationExecutor.execute_task() → _call_provider(provider, task, chunks) → Build DiagnosticGenerationRequest (base dict with scope/chunks/counts) → provider.generate_diagnostic_items() → DeterministicProvider impl → GeneratedDiagnosticItem() (question_text, options, answer, source_chunk_ids) → to_artifact_json() → Return list of payloads (artifact_json, artifact_type, validation_errors lambda) → validation_errors lambda → diagnostic_generator.validate() → Check answer_key exists → Check options count → Check caps_ref match → Check duplicate hash
- **Concurrency Safety:** Provider invocation is stateless and thread-safe. Item generation is independent per item. Validation is independent per item. No shared state between generations. No locks needed as operations are isolated
- **Covered Objects:** DeterministicContentGenerationProvider, DiagnosticGenerationRequest, GeneratedDiagnosticItem, diagnostic_generator, Validation lambdas, Artifact JSON payloads, Source chunk IDs, Answer keys, Options
- **Timeouts:** Request building: ~10-50ms. Item generation: ~100-500ms per item. JSON conversion: ~10-50ms per item. Validation: ~10-50ms per item. Total per item: ~200-1s
- **Migration Path:** From LLM-only generation to hybrid deterministic/LLM. Migration requires: 1) Implement deterministic provider, 2) Add validation lambdas, 3) Integrate with executor, 4) Configure provider selection logic, 5) Test deterministic generation quality
- **Error Handling:** Invalid request parameters fail generation. Item generation failures logged and skip item. Validation failures logged but don't stop generation. Invalid items filtered out during artifact creation. All errors logged with context
- **Security Considerations:** Deterministic generation prevents prompt injection. Source chunk IDs validated before use. Answer keys validated for correctness. Duplicate detection via hash prevents duplicates. No secrets in generated items

**Trace text diagram:**
```
Diagnostic Item Generation Flow
└── ContentGenerationExecutor.execute_task() <-- content_generation_executor.py:67
    └── _call_provider(provider, task, chunks) <-- content_generation_executor.py:175
        ├── Build DiagnosticGenerationRequest <-- content_generation_executor.py:178
        │   └── **base dict with scope/chunks/counts
        ├── provider.generate_diagnostic_items() <-- 4a
        │   └── DeterministicProvider impl <-- deterministic.py:12
        │       └── GeneratedDiagnosticItem() <-- 4b
        │           ├── question_text, options, answer <-- deterministic.py:24
        │           ├── source_chunk_ids from request <-- deterministic.py:32
        │           └── to_artifact_json() <-- 4c
        └── Return list of payloads <-- content_generation_executor.py:197
            └── Each payload contains:
                ├── artifact_json (from 4c) <-- content_generation_executor.py:199
                ├── artifact_type <-- content_generation_executor.py:200
                └── validation_errors lambda <-- 4d
                    └── diagnostic_generator.validate() <-- 4e
                        ├── Check answer_key exists <-- diagnostic_generator.py:10
                        ├── Check options count <-- diagnostic_generator.py:13
                        ├── Check caps_ref match <-- diagnostic_generator.py:19
                        └── Check duplicate hash <-- diagnostic_generator.py:23
```

**Location ID: 4a**
- **Title:** Generate Items via Provider
- **Description:** Calls provider with request containing source chunks, topic info, and counts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:196

**Location ID: 4b**
- **Title:** Create Diagnostic Item
- **Description:** Deterministic provider creates item with question, options, answer, and source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/providers/deterministic.py:23

**Location ID: 4c**
- **Title:** Convert to Artifact JSON
- **Description:** Transforms typed item into JSON payload for artifact storage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/prompt_payloads.py:60

**Location ID: 4d**
- **Title:** Validation Lambda
- **Description:** Deferred validation that checks answer keys, options, explanations, and duplicates
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:204

**Location ID: 4e**
- **Title:** Validate Diagnostic Item
- **Description:** Enforces business rules: answer key required, correct option count, source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/diagnostic_generator.py:8

### AI Guide: Diagnostic Item Generation

**Motivation:**
The diagnostic item generation flow demonstrates how the DeterministicContentGenerationProvider creates structured assessment items. The layer-specific generation approach uses deferred validation via lambdas and quality checks for diagnostic items to ensure consistent, high-quality content.

**Details:**

**Request Building and Provider Invocation**
Request building uses DiagnosticGenerationRequest including scope, chunks, counts, and metadata to standardize input for the provider and enable deterministic generation. Provider invocation calls the deterministic provider with the request, where the provider implements item generation logic and returns a list of GeneratedDiagnosticItem [4a].

**Item Creation and JSON Conversion**
Item creation uses GeneratedDiagnosticItem including question, options, answer, and source citations, uses deterministic algorithms for consistency, and tracks provenance via source chunk IDs [4b]. JSON conversion uses to_artifact_json() to transform the typed item to JSON, standardizing the artifact format and enabling storage and validation [4c].

**Deferred Validation**
Deferred validation returns a validation lambda with the payload, validates after generation, checks answer keys, options, and duplicates, and enables batch validation [4d][4e]. This ensures efficient validation while maintaining quality control.

## Trace ID: 5
**Title:** Artifact Creation and Validation: Factory Service Flow

**Description:** ContentFactoryService that validates artifact payloads, verifies source provenance, and creates artifact records with pending_review status (never auto-approves)

**Motivation:**
EduBoost V2 implements a comprehensive artifact creation and validation system to ensure content quality before approval. The ContentFactoryService validates artifact payloads (structure, required fields), verifies source provenance (approved status, license compatibility, quality thresholds), and creates artifact records with pending_review status. The system never auto-approves artifacts, requiring human review for quality control. This approach balances automation with human oversight, ensuring generated content meets quality standards while maintaining efficiency through automated validation.

**Details:**
- **Execution Flow:** ContentFactoryService.create_artifact() called → Extract sources from payload → ContentValidationService.validate_artifact_payload() → Check artifact_json not empty → Verify answer_key for diagnostic items → ETLProvenanceService.validate_source_bundle() → Check document status approved → Verify license compatibility → Validate quality thresholds → Compute source_snapshot_hash → Compute artifact_hash from JSON → Create ContentGenerationArtifact → Set status based on validation (PENDING_REVIEW if passed, VALIDATION_FAILED if errors) → session.add(artifact) → For each source chunk: Create ContentArtifactSource → session.add(source) → Create ContentValidationReport → session.add(report) → session.flush()
- **Concurrency Safety:** Artifact creation uses database transactions. Validation is stateless and thread-safe. Hash computation is deterministic. No shared state between creations. No locks needed as database provides isolation
- **Covered Objects:** ContentFactoryService, ContentValidationService, ETLProvenanceService, ContentGenerationArtifact, ContentArtifactSource, ContentValidationReport, Artifact JSON, Source chunks, Artifact hash, Source snapshot hash
- **Timeouts:** Payload validation: ~10-50ms. Provenance validation: ~100-500ms. Hash computation: ~10-50ms. Artifact creation: ~10-50ms. Source citation creation: ~10-50ms per source. Total: ~200ms-2s per artifact
- **Migration Path:** From auto-approval to human review required. Migration requires: 1) Implement validation service, 2) Add provenance validation, 3) Set status to pending_review, 4) Create validation reports, 5) Implement human review workflow
- **Error Handling:** Invalid payload fails validation with errors. Provenance validation fails with specific errors. Database failures fail artifact creation. All errors logged in validation report. Status reflects validation result
- **Security Considerations:** Never auto-approves artifacts (human review required). Validates source provenance and licensing. Tracks source snapshot hash for integrity. No secrets in artifact records. Validation reports track all checks

**Trace text diagram:**
```
Artifact Creation and Validation Flow
└── ContentFactoryService.create_artifact() <-- 5a
    ├── Extract sources from payload <-- content_factory.py:176
    ├── ContentValidationService
    │   └── validate_artifact_payload() <-- 5a
    │       ├── Check artifact_json not empty <-- content_factory.py:137
    │       ├── Verify answer_key for diagnostic items <-- content_factory.py:141
    │       └── ETLProvenanceService
    │           └── validate_source_bundle() <-- 5b
    │               ├── Check document status approved <-- content_factory.py:84
    │               ├── Verify license compatibility <-- content_factory.py:90
    │               ├── Validate quality thresholds <-- content_factory.py:98
    │               └── Compute source_snapshot_hash <-- content_factory.py:115
    ├── Compute artifact_hash from JSON <-- content_factory.py:184
    ├── Create ContentGenerationArtifact <-- 5c
    │   └── Set status based on validation <-- 5d
    │       ├── PENDING_REVIEW if passed <-- content_factory.py:190
    │       └── VALIDATION_FAILED if errors <-- content_factory.py:192
    ├── session.add(artifact) <-- content_factory.py:196
    ├── For each source chunk <-- content_factory.py:199
    │   └── Create ContentArtifactSource <-- 5e
    │       └── session.add(source) <-- content_factory.py:206
    ├── Create ContentValidationReport <-- content_factory.py:231
    │   └── session.add(report) <-- content_factory.py:231
    └── session.flush() <-- content_factory.py:239
```

**Location ID: 5a**
- **Title:** Validate Artifact Payload
- **Description:** Runs validation checks on artifact JSON and source bundle
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:177

**Location ID: 5b**
- **Title:** Validate Source Provenance
- **Description:** Verifies ETL sources are approved, licensed correctly, and meet quality thresholds
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:145

**Location ID: 5c**
- **Title:** Create Artifact Record
- **Description:** Instantiates artifact with computed hash and source snapshot hash
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:185

**Location ID: 5d**
- **Title:** Set Initial Status
- **Description:** Status is pending_review if validation passed, validation_failed otherwise
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:189

**Location ID: 5e**
- **Title:** Add Source Citation
- **Description:** Creates ContentArtifactSource records linking artifact to ETL source chunks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:206

### AI Guide: Artifact Creation and Validation

**Motivation:**
The artifact creation and validation system ensures content quality through comprehensive validation before human review. The ContentFactoryService validates payloads, verifies provenance, and creates artifacts with pending_review status to maintain quality control.

**Details:**

**Payload and Provenance Validation**
Payload validation uses the ContentValidationService to check artifact structure, verifies required fields exist, validates diagnostic-specific fields (answer_key), and returns a validation result with errors [5a]. Provenance validation uses the ETLProvenanceService to validate the source bundle, checks document approval status, verifies license compatibility, validates quality thresholds, and computes the source snapshot hash [5b].

**Artifact Creation and Status Setting**
Artifact creation creates ContentGenerationArtifact with hashes, using artifact hash for deduplication and source snapshot hash for provenance tracking, with status set based on validation [5c]. Status setting sets PENDING_REVIEW if validation passed, VALIDATION_FAILED if errors, never auto-approves (human review required), and enables quality control [5d].

**Source Citations**
Source citations use ContentArtifactSource records to link artifacts to sources, track provenance, and enable source tracking and attribution [5e]. This ensures full traceability of content sources.

## Trace ID: 6
**Title:** Staging Readiness Verification: Coverage Analysis

**Description:** ContentStagingReadinessService that analyzes scope coverage by loading artifacts, checking provenance/license/quality, and identifying blockers

**Motivation:**
EduBoost V2 implements a staging readiness verification system to determine which artifacts are ready for staging. The ContentStagingReadinessService analyzes scope coverage by loading artifacts, checking provenance (approved status), license compatibility, and quality thresholds. This analysis identifies blockers (insufficient coverage, quality issues) and calculates stageable counts (approved artifacts minus those with issues). The system enables informed decisions about staging while ensuring only high-quality content is promoted to staging environments.

**Details:**
- **Execution Flow:** ContentStagingReadinessService.verify_scope(scope_id, session) called → Load Data Phase: _load_scope_artifacts() → _load_source_index() → Analysis Phase: for each target in scope → filter matching artifacts → _layer_summary() → count by status → filter approved artifacts → _has_valid_provenance() → _has_invalid_license() → _has_low_source_quality() → calculate stageable → _layer_blockers() → Return ScopeStagingVerificationReport (status, can_seed_staging flag, blockers list, layers summaries)
- **Concurrency Safety:** Artifact loading is read-only. Analysis is stateless and thread-safe. No shared state between verifications. No locks needed as operations are read-only. Multiple verifications can run concurrently
- **Covered Objects:** ContentStagingReadinessService, ScopeStagingVerificationReport, LayerReadinessSummary, ScopeBlocker, ContentGenerationArtifact, ContentArtifactSource, Source index, Layer targets, Coverage counts
- **Timeouts:** Artifact loading: ~100-500ms. Source index building: ~50-200ms. Layer analysis: ~100-500ms per layer. Blocker identification: ~50-200ms per layer. Total verification: ~1-5s per scope
- **Migration Path:** From manual staging decisions to automated verification. Migration requires: 1) Implement artifact loading, 2) Add source index building, 3) Implement layer analysis, 4) Add blocker identification, 5) Create verification report structure
- **Error Handling:** Artifact loading failures logged and skip scope. Analysis failures logged with context. Missing targets logged as not configured. All errors included in verification report
- **Security Considerations:** Only approved artifacts considered for staging. Validates license compatibility. Checks quality thresholds. Identifies security blockers. No secrets in verification reports

**Trace text diagram:**
```
Staging Readiness Verification Flow
└── ContentStagingReadinessService <-- content_staging_readiness.py:104
    └── verify_scope(scope_id, session) <-- content_staging_readiness.py:132
        ├── Load Data Phase
        │   ├── _load_scope_artifacts() <-- 6a
        │   └── _load_source_index() <-- 6b
        ├── Analysis Phase
        │   └── for each target in scope <-- content_staging_readiness.py:157
        │       ├── filter matching artifacts <-- content_staging_readiness.py:163
        │       ├── _layer_summary() <-- 6c
        │       │   ├── count by status <-- content_staging_readiness.py:296
        │       │   ├── filter approved artifacts <-- content_staging_readiness.py:299
        │       │   ├── _has_valid_provenance() <-- content_staging_readiness.py:398
        │       │   ├── _has_invalid_license() <-- content_staging_readiness.py:405
        │       │   ├── _has_low_source_quality() <-- content_staging_readiness.py:409
        │       │   └── calculate stageable <-- 6d
        │       └── _layer_blockers() <-- 6e
        └── Return ScopeStagingVerificationReport <-- content_staging_readiness.py:180
            ├── status (ready/blocked/partial) <-- content_staging_readiness.py:182
            ├── can_seed_staging flag <-- content_staging_readiness.py:183
            ├── blockers list <-- content_staging_readiness.py:185
            └── layers summaries <-- content_staging_readiness.py:186
```

**Location ID: 6a**
- **Title:** Load Scope Artifacts
- **Description:** Fetches all artifacts for the scope from content_generation_artifacts table
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:152

**Location ID: 6b**
- **Title:** Load Source Index
- **Description:** Builds map of artifact_id to source citations for provenance checks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:153

**Location ID: 6c**
- **Title:** Compute Layer Summary
- **Description:** Analyzes approved vs target counts, identifies invalid provenance/license/quality
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:168

**Location ID: 6d**
- **Title:** Calculate Stageable Count
- **Description:** Subtracts artifacts with provenance/license/quality issues from approved count
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:303

**Location ID: 6e**
- **Title:** Identify Blockers
- **Description:** Generates blocker records for insufficient coverage or quality issues
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:170

### AI Guide: Staging Readiness Verification

**Motivation:**
The staging readiness verification system analyzes scope coverage to determine which artifacts are ready for staging. The ContentStagingReadinessService checks provenance, licensing, and quality to identify blockers and calculate stageable counts for informed staging decisions.

**Details:**

**Data Loading and Layer Analysis**
Data loading loads all artifacts for the scope, builds a source index for provenance checks, and uses efficient batch loading for performance [6a][6b]. Layer analysis uses _layer_summary() to analyze each layer, counts artifacts by status, filters approved artifacts, and checks provenance, license, and quality [6c].

**Stageable Calculation and Blocker Identification**
Stageable calculation calculates the stageable count as approved minus issues, subtracts invalid provenance, invalid license, and low quality, and handles edge cases (negative counts) [6d]. Blocker identification uses _layer_blockers() to generate blocker records, identifies insufficient coverage and quality issues, and enables targeted fixes [6e].

**Verification Report**
The verification report returns a comprehensive report with status, can_seed_staging flag, blockers, and layer summaries to enable informed staging decisions. This ensures that only high-quality, properly licensed artifacts are promoted to staging.

## Trace ID: 7
**Title:** Staging Seed Execution: Approved Artifacts to Staging Tables

**Description:** ContentStagingSeedExecutor that promotes only approved artifacts to staging tables (lesson_bank, assessment_blueprints, study_plan_templates) for preview

**Motivation:**
EduBoost V2 implements a staging seed execution system to promote approved artifacts to staging tables for preview and testing. The ContentStagingSeedExecutor identifies seedable artifacts (approved with valid provenance), creates seed run records for tracking, and promotes artifacts to staging tables (lesson_bank, assessment_blueprints, study_plan_templates). This system enables content preview in staging environments before production deployment, ensuring quality and correctness. The executor supports partial seeding (skip artifacts with issues) and tracks all operations for auditability.

**Details:**
- **Execution Flow:** ContentSeedPromotionService.seed_staging() called → _seed_gate() validation (Check stageable_approved count) → seed_executor.seed_staging() → _plan_seed() identify artifacts → ContentSeedRun() creation → session.add(run) → For each seedable artifact: ContentStagingArtifact() creation → session.add(staging_artifact) → artifact.status update (APPROVED → SEEDED_STAGING) → session.flush() persist changes
- **Concurrency Safety:** Seed gate validation prevents concurrent seeding. Seed run tracking provides auditability. Artifact status update uses database transactions. No distributed locks needed as database provides isolation. Multiple seed operations can run on different scopes
- **Covered Objects:** ContentSeedPromotionService, ContentStagingSeedExecutor, ContentSeedRun, ContentStagingArtifact, ContentGenerationArtifact, Staging tables (lesson_bank, assessment_blueprints, study_plan_templates), Database session
- **Timeouts:** Seed gate validation: ~10-50ms. Seed planning: ~100-500ms. Seed run creation: ~10-50ms. Artifact promotion: ~50-200ms per artifact. Session flush: ~100-500ms. Total seeding: ~1-5min depending on artifact count
- **Migration Path:** From manual staging to automated seeding. Migration requires: 1) Implement seed gate validation, 2) Add seed run tracking, 3) Implement artifact promotion logic, 4) Create staging tables, 5) Add status transition logic
- **Error Handling:** Seed gate failures prevent seeding. Planning failures logged and skip seeding. Artifact promotion failures logged but don't stop seeding. Status update failures logged. All errors tracked in seed run record
- **Security Considerations:** Only approved artifacts seeded. Seed gate validation prevents unauthorized seeding. Seed run tracking provides auditability. Staging tables isolated from production. No secrets in staging artifacts

**Trace text diagram:**
```
Staging Seed Execution Pipeline
├── ContentSeedPromotionService.seed_staging() <-- content_seed_promotion.py:51
│   ├── _seed_gate() validation <-- 7a
│   │   └── Check stageable_approved count <-- content_seed_promotion.py:61
│   └── seed_executor.seed_staging() <-- 7b
│       ├── _plan_seed() identify artifacts <-- content_staging_seed_executor.py:98
│       ├── ContentSeedRun() creation <-- 7c
│       ├── session.add(run) <-- content_seed_promotion.py:87
│       └── For each seedable artifact: <-- content_staging_seed_executor.py:94
│           ├── ContentStagingArtifact() creation <-- content_factory.py:453
│           ├── session.add(staging_artifact) <-- content_staging_seed_executor.py:92
│           └── artifact.status update <-- 7d
│               └── APPROVED → SEEDED_STAGING <-- content_factory.py:47
└── session.flush() persist changes <-- content_seed_promotion.py:88
```

**Location ID: 7a**
- **Title:** Plan Seed Operation
- **Description:** Identifies which approved artifacts are seedable vs skipped
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py:98

**Location ID: 7b**
- **Title:** Execute Staging Seed
- **Description:** Delegates to executor to perform actual seeding with allow_partial flag
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_seed_promotion.py:66

**Location ID: 7c**
- **Title:** Create Seed Run Record
- **Description:** Tracks this seeding operation with status and summary metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py:75

**Location ID: 7d**
- **Title:** Update Artifact Status
- **Description:** Transitions artifact from approved to seeded_staging after successful seed
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:296

### AI Guide: Staging Seed Execution

**Motivation:**
The staging seed execution system promotes approved artifacts to staging tables for preview. The ContentStagingSeedExecutor identifies seedable artifacts, tracks seed operations, and updates artifact status to ensure controlled promotion to staging.

**Details:**

**Seed Gate Validation and Planning**
Seed gate validation uses _seed_gate() to validate the stageable count, prevents seeding if no artifacts are ready, and ensures meaningful seeding operations [7a]. Seed planning uses _plan_seed() to identify seedable artifacts, distinguishes seedable vs skipped artifacts, and supports partial seeding (skip issues).

**Seed Run Tracking and Artifact Promotion**
Seed run tracking uses ContentSeedRun to track the operation, records status and metadata, and enables auditability and debugging [7c]. Artifact promotion creates ContentStagingArtifact records, promotes to staging tables, and links to the original artifact.

**Status Update**
Status update transitions artifact status (APPROVED → SEEDED_STAGING), tracks seeding history, and prevents re-seeding [7d]. This ensures that artifacts are promoted to staging in a controlled, auditable manner with proper status tracking.

## Trace ID: 8
**Title:** Report Generation: Summary and Evidence Export

**Description:** ContentGenerationReporter that writes comprehensive reports with markdown summaries, JSON metadata, and CSV exports for all tasks and artifacts

**Motivation:**
EduBoost V2 implements a comprehensive report generation system to document generation runs for auditability and debugging. The ContentGenerationReporter creates timestamped report directories with markdown summaries (human-readable), JSON metadata (machine-readable), and CSV exports (spreadsheet analysis). The system reports on planned tasks, executed tasks, generated artifacts, pending review items, and errors. This documentation enables tracking of generation runs, analysis of success rates, and debugging of failures. Reports are stored in timestamped directories for historical tracking.

**Details:**
- **Execution Flow:** main() CLI entry point → asyncio.run(run_full_generation()) → Lock acquisition phase → Run creation & planning phase → Task execution loop → Report generation phase → reporter.write_report(report_data) → Create timestamped directory → _write_summary_md() → _write_summary_json() → CSV exports (_write_csv(planned_tasks), _write_csv(executed_tasks), _write_csv(generated_artifacts), _write_csv(pending_review)) → _write_errors_log()
- **Concurrency Safety:** Report generation is stateless and thread-safe. Directory creation uses atomic operations. File writes are independent. No shared state between reports. No locks needed as operations are isolated
- **Covered Objects:** ContentGenerationReporter, Report data (tasks, artifacts, errors), Timestamped directory, Markdown summary, JSON metadata, CSV exports, Error log, File system
- **Timeouts:** Directory creation: ~10-50ms. Summary markdown: ~100-500ms. Summary JSON: ~50-200ms. CSV exports: ~100-500ms per CSV. Error log: ~10-50ms. Total report generation: ~500ms-2s
- **Migration Path:** From no reporting to comprehensive reports. Migration requires: 1) Implement reporter service, 2) Add markdown summary generation, 3) Add JSON metadata export, 4) Add CSV exports, 5) Add error logging
- **Error Handling:** Directory creation failures fail report. File write failures logged but don't stop report. Missing data handled gracefully. All errors logged to stdout
- **Security Considerations:** Reports may contain sensitive metadata. Error logs may contain stack traces. No secrets in reports. Report directories timestamped for organization. File permissions restrict access

**Trace text diagram:**
```
Overnight Run Orchestration (run_full_generation.py)
└── main() CLI entry point <-- run_full_generation.py:183
    └── asyncio.run(run_full_generation()) <-- 8a
        ├── Lock acquisition phase
        │   └── lock.acquire(session, holder) <-- 1b
        ├── Run creation & planning phase
        │   ├── ContentGenerationRun() instantiation <-- run_full_generation.py:67
        │   └── planner.plan_missing_for_run() <-- run_full_generation.py:89
        ├── Task execution loop
        │   └── [tasks executed, artifacts created]
        └── Report generation phase <-- 8a
            └── reporter.write_report(report_data) <-- run_full_generation.py:172
                ├── Create timestamped directory <-- 8b
                ├── _write_summary_md() <-- 8c
                ├── _write_summary_json() <-- content_generation_reporter.py:63
                ├── CSV exports
                │   ├── _write_csv(planned_tasks) <-- 8d
                │   ├── _write_csv(executed_tasks) <-- content_generation_reporter.py:71
                │   ├── _write_csv(generated_artifacts) <-- content_generation_reporter.py:72
                │   └── _write_csv(pending_review) <-- content_generation_reporter.py:73
                └── _write_errors_log() <-- 8e
```

**Location ID: 8a**
- **Title:** Write Report
- **Description:** Invokes reporter to generate timestamped report directory with all artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:172

**Location ID: 8b**
- **Title:** Create Report Directory
- **Description:** Creates timestamped directory under reports/content_factory/full_generation/
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:56

**Location ID: 8c**
- **Title:** Write Summary Markdown
- **Description:** Generates human-readable summary.md with run status and metrics
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:60

**Location ID: 8d**
- **Title:** Export Task CSVs
- **Description:** Writes CSV files for planned, executed, pending review, and failed artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:70

**Location ID: 8e**
- **Title:** Write Error Log
- **Description:** Logs all errors encountered during generation for debugging
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:86

### AI Guide: Report Generation

**Motivation:**
The report generation system creates comprehensive documentation of generation runs. The ContentGenerationReporter produces markdown summaries, JSON metadata, CSV exports, and error logs for auditability and debugging to ensure full traceability of generation operations.

**Details:**

**Directory Creation and Markdown Summary**
Directory creation creates a timestamped directory, organizes reports by time, and prevents overwriting previous reports [8b]. The markdown summary uses _write_summary_md() to generate a human-readable summary, includes run status and metrics, and enables quick human review [8c].

**JSON Metadata and CSV Exports**
JSON metadata uses _write_summary_json() to export machine-readable data, enables programmatic analysis, and includes all run metadata. CSV exports use _write_csv() to export data to spreadsheets with separate CSVs for tasks, artifacts, and pending review to enable data analysis [8d].

**Error Log**
The error log uses _write_errors_log() to log all errors, includes stack traces, and enables debugging and troubleshooting [8e]. This comprehensive reporting ensures that all aspects of the generation run are documented for audit and debugging purposes.
