# Content Factory Full Generation System: Overnight Batch Pipeline — Complete Trace Text

This document reproduces the complete trace text for the eight steps of the Content Factory overnight batch pipeline, including the expanded "see more" details: trace text diagrams, location references with file paths and line numbers, and the provided code snippet references.

---

## Trace 1: Overnight Run Orchestration — Entry Point to Task Planning
**Phase 1: Motivation**

**Description**
Main orchestration flow in `run_full_generation.py` that acquires locks, creates runs, and invokes the planner to identify missing content.

**Trace text diagram**
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

**Locations**
- **1a — Entry Point: Main Function**
  - Description: Async entry point that kicks off the full generation pipeline with parsed CLI arguments
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:201` ([open](../scripts/content_factory/run_full_generation.py))
- **1b — Lock Acquisition**
  - Description: Prevents concurrent overnight runs by acquiring a distributed lock with TTL
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:57` ([open](../scripts/content_factory/run_full_generation.py))
- **1c — Run Record Creation**
  - Description: Creates database record tracking this generation run with metadata about layers and limits
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:67` ([open](../scripts/content_factory/run_full_generation.py))
- **1d — Invoke Planner**
  - Description: Delegates to ContentGenerationPlanner to analyze gaps and create generation tasks
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:89` ([open](../scripts/content_factory/run_full_generation.py))
- **1e — Lock Release**
  - Description: Ensures lock is released in finally block even if generation fails
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:179` ([open](../scripts/content_factory/run_full_generation.py))

### Quick links
- [scripts/content_factory/run_full_generation.py](../scripts/content_factory/run_full_generation.py)

### Code excerpts

```python
# scripts/content_factory/run_full_generation.py — main entry
def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run full content generation")
    ...
    return asyncio.run(run_full_generation(
        all_scopes=args.all_scopes,
        layers=layers,
        max_concurrency=args.max_concurrency,
        max_artifacts=args.max_artifacts,
        budget_cap=args.budget_cap,
        resume=args.resume,
        seed_approved_to_staging=args.seed_approved_to_staging,
        verify_staging=args.verify_staging,
        write_report=args.write_report,
        plan_only=args.plan_only,
    ))
```

```python
# scripts/content_factory/run_full_generation.py — acquire lock and reporter
lock = ContentGenerationRunLock()
holder = f"{os.uname().nodename}:{os.getpid()}"
...
if write_report:
    reporter = ContentGenerationReporter()
    report_dir = reporter.write_report(report_data)
    print(f"Report written to {report_dir}")
```

---

## Trace 2: Content Gap Planning — Readiness Analysis to Task Creation
**Phase 2: Motivation**

**Description**
ContentGenerationPlanner service that identifies coverage gaps via staging readiness verification, validates source context availability, and creates idempotent generation tasks.

**Trace text diagram**
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

**Locations**
- **2a — Verify Scope Readiness**
  - Description: Analyzes current coverage vs targets to identify missing artifacts per layer
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:69` ([open](../app/services/content_generation_planner.py))
- **2b — Calculate Gap**
  - Description: Computes how many artifacts are needed to reach coverage target
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:73` ([open](../app/services/content_generation_planner.py))
- **2c — Build Source Context**
  - Description: Validates that approved ETL source chunks are available for generation
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:77` ([open](../app/services/content_generation_planner.py))
- **2d — Create Generation Task**
  - Description: Creates task record with idempotency key to prevent duplicate generation
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:88` ([open](../app/services/content_generation_planner.py))
- **2e — Persist Task**
  - Description: Adds task to database session for batch insertion
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:112` ([open](../app/services/content_generation_planner.py))

### Quick links
- [app/services/content_generation_planner.py](../app/services/content_generation_planner.py)

### Code excerpts

```python
# app/services/content_generation_planner.py — plan_missing_for_run (core loop)
for scope in scopes:
    report = await self.readiness_service.verify_scope(scope.scope_id, session=session, include_partial=True)
    for layer in report.layers:
        if layer.layer not in PLANNABLE_LAYERS or layer.target <= 0:
            continue
        missing_count = max(0, layer.target - layer.approved)
        if missing_count <= 0:
            skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "coverage_green"})
            continue
        context = await self.source_context_service.build_context(session, scope_id=scope.scope_id, caps_ref=layer.caps_ref)
        if not context.passed:
            skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "missing_source_context", "errors": context.errors})
            continue
        task_missing = min(missing_count, max_artifacts_per_task)
        idempotency_key = f"{scope.scope_id}:{layer.caps_ref}:{layer.layer}:{target_version}:{prompt_version}:{generator_version}"
        existing = await session.execute(select(ContentGenerationTask).where(ContentGenerationTask.idempotency_key == idempotency_key))
        if existing.scalar_one_or_none() is not None:
            skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "duplicate_task"})
            continue
        task = ContentGenerationTask(...)
        session.add(task)
        created.append(task.task_id)
        missing_rows.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "missing_count": task_missing})
```

---

## Trace 3: Task Execution — Provider Invocation to Artifact Creation
**Phase 3: Task Execution in the Content Factory Generation Pipeline**

**Description**
ContentGenerationExecutor service that executes queued tasks by calling generation providers (deterministic or LLM) and creating validated artifacts.

**Trace text diagram**
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

**Locations**
- **3a — Mark Task Running**
  - Description: Updates task status and acquires lock with expiration timestamp
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:76` ([open](../app/services/content_generation_executor.py))
- **3b — Rebuild Source Context**
  - Description: Re-validates source availability at execution time (may have changed since planning)
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:82` ([open](../app/services/content_generation_executor.py))
- **3c — Call Generation Provider**
  - Description: Invokes deterministic or LLM provider to generate content artifacts
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:87` ([open](../app/services/content_generation_executor.py))
- **3d — Create Artifact Record**
  - Description: Persists generated artifact with validation, provenance, and source citations
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:97` ([open](../app/services/content_generation_executor.py))
- **3e — Update Task Status**
  - Description: Marks task as succeeded or failed based on artifact creation results
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:133` ([open](../app/services/content_generation_executor.py))

### Quick links
- [app/services/content_generation_executor.py](../app/services/content_generation_executor.py)
- [app/services/content_factory.py](../app/services/content_factory.py)

### Code excerpts

```python
# app/services/content_generation_executor.py — execute_task setup
task.status = "running"
task.locked_by = actor_id
task.lock_expires_at = datetime.now(UTC) + timedelta(minutes=10)
task.started_at = datetime.now(UTC)
await session.flush()
```

```python
# app/services/content_generation_executor.py — build provider request and diagnostic branch
base = {
    "scope_id": task.scope_id,
    "caps_ref": task.caps_ref or "",
    "grade": int(metadata.get("grade") or scope.grade),
    "subject_code": str(metadata.get("subject_code") or scope.subject_code),
    "language": str(metadata.get("language") or scope.language),
    "topic_title": str(metadata.get("topic_title") or task.caps_ref),
    "required_count": int(metadata.get("required_count") or 1),
    "approved_count": int(metadata.get("approved_count") or 0),
    "missing_count": int(metadata.get("missing_count") or 1),
    "source_chunks": chunks,
    "source_document_ids": sorted({chunk.source_document_id for chunk in chunks}),
    "source_chunk_ids": [chunk.source_chunk_id for chunk in chunks],
    "source_quality_scores": [chunk.source_quality_score for chunk in chunks if chunk.source_quality_score is not None],
    "license_statuses": sorted({chunk.license_status for chunk in chunks if chunk.license_status}),
    "prompt_version": task.prompt_version or "cf-gen-v1",
}
if _value(task.content_layer) == ContentLayer.DIAGNOSTIC_ITEMS.value:
    items = await provider.generate_diagnostic_items(DiagnosticGenerationRequest(**base))
    return [
        {
            "artifact_json": item.to_artifact_json(),
            "artifact_type": ContentArtifactType.DIAGNOSTIC_ITEM,
            "grade": item.grade,
            "subject_code": item.subject_code,
            "language": item.language,
            "validation_errors": lambda artifact_hash, hashes, item=item: self.diagnostic_generator.validate(
                item, caps_ref=task.caps_ref or "", existing_hashes=hashes, artifact_hash=artifact_hash
            ),
        }
        for item in items
    ]
```

---

## Trace 4: Diagnostic Item Generation — Provider to Validation
**Phase 4: Diagnostic Item Generation Guide**

**Description**
Layer-specific generation flow showing how diagnostic items are created via DeterministicContentGenerationProvider and validated before artifact creation.

**Trace text diagram**
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

**Locations**
- **4a — Generate Items via Provider**
  - Description: Calls provider with request containing source chunks, topic info, and counts
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:196` ([open](../app/services/content_generation_executor.py))
- **4b — Create Diagnostic Item**
  - Description: Deterministic provider creates item with question, options, answer, and source citations
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/providers/deterministic.py:23` ([open](../app/services/content_generation/providers/deterministic.py))
- **4c — Convert to Artifact JSON**
  - Description: Transforms typed item into JSON payload for artifact storage
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/prompt_payloads.py:60` ([open](../app/services/content_generation/prompt_payloads.py))
- **4d — Validation Lambda**
  - Description: Deferred validation that checks answer keys, options, explanations, and duplicates
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:204` ([open](../app/services/content_generation_executor.py))
- **4e — Validate Diagnostic Item**
  - Description: Enforces business rules: answer key required, correct option count, source citations
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/diagnostic_generator.py:8` ([open](../app/services/content_generation/diagnostic_generator.py))

### Quick links
- [app/services/content_generation/providers/deterministic.py](../app/services/content_generation/providers/deterministic.py)
- [app/services/content_generation/prompt_payloads.py](../app/services/content_generation/prompt_payloads.py)
- [app/services/content_generation/diagnostic_generator.py](../app/services/content_generation/diagnostic_generator.py)

### Code excerpts

```python
# app/services/content_generation/providers/deterministic.py — generate_diagnostic_items
async def generate_diagnostic_items(self, request: DiagnosticGenerationRequest) -> list[GeneratedDiagnosticItem]:
    count = max(0, request.missing_count)
    chunk_ids = request.source_chunk_ids or [chunk.source_chunk_id for chunk in request.source_chunks]
    return [
        GeneratedDiagnosticItem(
            question_text=f"{request.topic_title}: diagnostic question {index + 1} for {request.caps_ref}",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            explanation=f"Grounded in source chunk {chunk_ids[index % len(chunk_ids)]}.",
            caps_ref=request.caps_ref,
            grade=request.grade,
            subject_code=request.subject_code,
            language=request.language,
            source_chunk_ids=[chunk_ids[index % len(chunk_ids)]],
        )
        for index in range(count)
    ]
```

```python
# app/services/content_generation/prompt_payloads.py — GeneratedDiagnosticItem.to_artifact_json
def to_artifact_json(self) -> dict:
    return {
        "question_text": self.question_text,
        "options": self.options,
        "answer_key": {"correct_answer": self.correct_answer},
        "explanation": self.explanation,
        "caps_ref": self.caps_ref,
        "grade": self.grade,
        "subject_code": self.subject_code,
        "language": self.language,
        "difficulty": self.difficulty,
        "cognitive_level": self.cognitive_level,
        "source_chunk_ids": self.source_chunk_ids,
        "item_type": self.item_type,
        "safety_status": self.safety_status,
    }
```

```python
# app/services/content_generation/diagnostic_generator.py — validate rules
def validate(self, item: GeneratedDiagnosticItem, *, caps_ref: str, existing_hashes: set[str] | None = None, artifact_hash: str | None = None) -> list[str]:
    errors: list[str] = []
    if not item.correct_answer:
        errors.append("diagnostic item requires an answer key.")
    if item.item_type == "single_choice":
        if len(item.options) < 2:
            errors.append("diagnostic item requires at least two options.")
        if item.options.count(item.correct_answer) != 1:
            errors.append("diagnostic item requires exactly one correct answer.")
    if not item.explanation:
        errors.append("diagnostic item requires an explanation.")
    if item.caps_ref != caps_ref:
        errors.append(f"diagnostic item caps_ref {item.caps_ref} does not match task caps_ref {caps_ref}.")
    if not item.source_chunk_ids:
        errors.append("diagnostic item requires source citations.")
    if artifact_hash and existing_hashes and artifact_hash in existing_hashes:
        errors.append("diagnostic item duplicates an existing artifact hash.")
    return errors
```

---

## Trace 5: Artifact Creation and Validation — Factory Service Flow
**Phase 5: Motivation**

**Description**
ContentFactoryService that validates artifact payloads, verifies source provenance, and creates artifact records with pending_review status (never auto-approves).

**Trace text diagram**
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

**Locations**
- **5a — Validate Artifact Payload**
  - Description: Runs validation checks on artifact JSON and source bundle
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:177` ([open](../app/services/content_factory.py))
- **5b — Validate Source Provenance**
  - Description: Verifies ETL sources are approved, licensed correctly, and meet quality thresholds
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:145` ([open](../app/services/content_factory.py))
- **5c — Create Artifact Record**
  - Description: Instantiates artifact with computed hash and source snapshot hash
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:185` ([open](../app/services/content_factory.py))
- **5d — Set Initial Status**
  - Description: Status is pending_review if validation passed, validation_failed otherwise
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:189` ([open](../app/services/content_factory.py))
- **5e — Add Source Citation**
  - Description: Creates ContentArtifactSource records linking artifact to ETL source chunks
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:206` ([open](../app/services/content_factory.py))

### Quick links
- [app/services/content_factory.py](../app/services/content_factory.py)

### Code excerpts

```python
# app/services/content_factory.py — ETLProvenanceService.validate_source_bundle
if not sources:
    if allow_synthetic_without_source:
        return SourceGateResult(True, [], None)
    return SourceGateResult(False, ["At least one ETL source citation is required."], None)
...
status = str(source.get("document_status") or "").lower()
if require_approved_documents and status not in APPROVED_SOURCE_STATUSES:
    errors.append(
        f"{label} document must be approved, indexed, or training_ready; got {status or 'missing'}."
    )
```

```python
# app/services/content_factory.py — ContentFactoryService.create_artifact
sources = payload.pop("sources", [])
validation = self.validation_service.validate_artifact_payload(
    artifact_json=payload["artifact_json"],
    caps_ref=payload.get("caps_ref"),
    sources=sources,
    artifact_type=payload["artifact_type"],
    min_sources=payload.pop("min_sources", 1),
)
artifact_hash = stable_json_hash(payload["artifact_json"])
artifact = ContentGenerationArtifact(
    artifact_id=uuid.uuid4(),
    artifact_hash=artifact_hash,
    source_snapshot_hash=validation["source_snapshot_hash"],
    status=(
        ContentArtifactStatus.PENDING_REVIEW
        if validation["passed"]
        else ContentArtifactStatus.VALIDATION_FAILED
    ),
    **payload,
)
session.add(artifact)
```

---

## Trace 6: Staging Readiness Verification — Coverage Analysis
**Phase 6: Staging Readiness Verification**

**Description**
ContentStagingReadinessService that analyzes scope coverage by loading artifacts, checking provenance/license/quality, and identifying blockers.

**Trace text diagram**
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

**Locations**
- **6a — Load Scope Artifacts**
  - Description: Fetches all artifacts for the scope from content_generation_artifacts table
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:152` ([open](../app/services/content_staging_readiness.py))
- **6b — Load Source Index**
  - Description: Builds map of artifact_id to source citations for provenance checks
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:153` ([open](../app/services/content_staging_readiness.py))
- **6c — Compute Layer Summary**
  - Description: Analyzes approved vs target counts, identifies invalid provenance/license/quality
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:168` ([open](../app/services/content_staging_readiness.py))
- **6d — Calculate Stageable Count**
  - Description: Subtracts artifacts with provenance/license/quality issues from approved count
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:303` ([open](../app/services/content_staging_readiness.py))
- **6e — Identify Blockers**
  - Description: Generates blocker records for insufficient coverage or quality issues
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:170` ([open](../app/services/content_staging_readiness.py))

### Quick links
- [app/services/content_staging_readiness.py](../app/services/content_staging_readiness.py)

### Code excerpts

```python
# app/services/content_staging_readiness.py — verify_scope (core)
artifacts = await self._load_scope_artifacts(session, scope_id)
source_index = await self._load_source_index(session, [artifact.artifact_id for artifact in artifacts])
layers: list[LayerReadinessSummary] = []
blockers: list[ScopeBlocker] = []
for target in targets:
    for key, required in sorted(target.targets.items()):
        layer_name = key.rsplit('.', 1)[0]
        matching = [
            artifact for artifact in artifacts
            if _value(artifact.content_layer) == layer_name and artifact.caps_ref == target.caps_ref
        ]
        summary = self._layer_summary(layer_name, target.caps_ref, int(required), matching, source_index)
        layers.append(summary)
        blockers.extend(self._layer_blockers(summary))
```

```python
# app/services/content_staging_readiness.py — provenance/license/quality helpers
def _has_valid_provenance(self, artifact, sources) -> bool:
    if not artifact.source_snapshot_hash:
        return False
    if not sources:
        return False
    return all(bool(source.source_hash or source.source_document_id) for source in sources)
```

---

## Trace 7: Staging Seed Execution — Approved Artifacts to Staging Tables
**Phase 7: Staging Seed Execution Guide**

**Description**
ContentStagingSeedExecutor that promotes only approved artifacts to staging tables (lesson_bank, assessment_blueprints, study_plan_templates) for preview.

**Trace text diagram**
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

**Locations**
- **7a — Plan Seed Operation**
  - Description: Identifies which approved artifacts are seedable vs skipped
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py:98` ([open](../app/services/content_staging_seed_executor.py))
- **7b — Execute Staging Seed**
  - Description: Delegates to executor to perform actual seeding with allow_partial flag
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_seed_promotion.py:66` ([open](../app/services/content_seed_promotion.py))
- **7c — Create Seed Run Record**
  - Description: Tracks this seeding operation with status and summary metadata
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py:75` ([open](../app/services/content_staging_seed_executor.py))
- **7d — Update Artifact Status**
  - Description: Transitions artifact from approved to seeded_staging after successful seed
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:296` ([open](../app/services/content_factory.py))

### Quick links
- [app/services/content_staging_seed_executor.py](../app/services/content_staging_seed_executor.py)
- [app/services/content_seed_promotion.py](../app/services/content_seed_promotion.py)

### Code excerpts

```python
# app/services/content_staging_seed_executor.py — seed_staging
plan = await self._plan_seed(session, scope_id, layers=layers)
if not allow_partial and plan.skipped:
    return StagingSeedRunResult(
        seed_run_id=uuid.uuid4(),
        scope_id=scope_id,
        status="failed",
        seeded_count=0,
        skipped_count=len(plan.skipped),
        errors=["Partial seed disabled and artifacts were skipped. ..."],
    )
# create ContentSeedRun, ContentStagingSeedItem, ContentStagingArtifact for each seedable
```

```python
# app/services/content_staging_seed_executor.py — _plan_seed filtering
if status_val != ContentArtifactStatus.APPROVED.value:
    skipped.append(SkippedArtifact(artifact.artifact_id, f"Artifact status {status_val} is not seedable"))
    continue
provenance = await self.factory_service.get_artifact_provenance(session, artifact.artifact_id)
if not provenance.passed:
    skipped.append(SkippedArtifact(artifact.artifact_id, "Invalid provenance"))
    continue
seedable.append(SeedableArtifact(...))
```

---

## Trace 8: Report Generation — Summary and Evidence Export
**Phase 8: Report Generation for Content Factory Overnight Runs**

**Description**
ContentGenerationReporter that writes comprehensive reports with markdown summaries, JSON metadata, and CSV exports for all tasks and artifacts.

**Trace text diagram**
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

**Locations**
- **8a — Write Report**
  - Description: Invokes reporter to generate timestamped report directory with all artifacts
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:172` ([open](../scripts/content_factory/run_full_generation.py))
- **8b — Create Report Directory**
  - Description: Creates timestamped directory under reports/content_factory/full_generation/
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:56` ([open](../app/services/content_generation_reporter.py))
- **8c — Write Summary Markdown**
  - Description: Generates human-readable summary.md with run status and metrics
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:60` ([open](../app/services/content_generation_reporter.py))
- **8d — Export Task CSVs**
  - Description: Writes CSV files for planned, executed, pending review, and failed artifacts
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:70` ([open](../app/services/content_generation_reporter.py))
- **8e — Write Error Log**
  - Description: Logs all errors encountered during generation for debugging
  - Path:LineNumber: `/home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:86` ([open](../app/services/content_generation_reporter.py))

### Quick links
- [scripts/content_factory/run_full_generation.py](../scripts/content_factory/run_full_generation.py)
- [app/services/content_generation_reporter.py](../app/services/content_generation_reporter.py)

### Code excerpts

```python
# app/services/content_generation_reporter.py — write_report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_dir = self.base_dir / timestamp
report_dir.mkdir(parents=True, exist_ok=True)
self._write_summary_md(report_dir, data)
self._write_summary_json(report_dir, data)
self._write_json(report_dir / "scope_readiness_before.json", data.scope_readiness_before)
self._write_json(report_dir / "scope_readiness_after.json", data.scope_readiness_after)
self._write_csv(report_dir / "planned_tasks.csv", data.planned_tasks_list)
```

```python
# app/services/content_generation_reporter.py — _write_summary_md
with open(report_dir / "summary.md", "w") as f:
    f.write("# Full Generation Run Report\n\n")
    f.write(f"**Run ID:** {data.run_id}\n")
    f.write(f"**Scope:** {data.scope_id}\n")
    f.write(f"**Status:** {data.status}\n\n")
    f.write("## Summary\n\n")
    f.write(f"- **Planned Tasks:** {data.planned_tasks}\n")
    f.write(f"- **Executed Tasks:** {data.executed_tasks}\n")
    f.write(f"- **Generated Artifacts:** {data.generated_artifacts}\n")
    f.write(f"- **Pending Review:** {data.pending_review}\n")
```

---

## Code snippets from Codemap files

If these seem wrong, it likely means this codemap is out of date with the state of the file.

```
File: /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py

Lines: 55-59
        return 1

    # Acquire lock
    lock = ContentGenerationRunLock()
    holder = f"{os.uname().nodename}:{os.getpid()}"

Lines: 65-69
            if existing is None:
                session.add(
                    ContentScope(
                        scope_id="all_scopes",
                        grade=0,

Lines: 87-91
        print(f"Lock acquired by {holder}")

        
        try:
            # Create generation run

Lines: 166-181

            # Seed approved to staging if requested
            if seed_approved_to_staging:
                print("Seeding approved artifacts to staging...")
                # Placeholder for staging seed logic
                print("Staging seed complete")

            # Verify staging if requested
            if verify_staging:
                print("Verifying staging...")
                # Placeholder for staging verification logic
                print("Staging verification complete")

            # Write report if requested
            if write_report:
                reporter = ContentGenerationReporter()

Lines: 199-203
                print(f"Report written to {report_dir}")

            return 0

        finally:

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/prompt_payloads.py

Lines: 58-62
    safety_status: str = "passed"

    def to_artifact_json(self) -> dict:
        return {
            "question_text": self.question_text,

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py

Lines: 143-147
        checks["answer_key_verified"] = artifact_type != "diagnostic_item" or...

        gate = self.provenance_service.validate_source_bundle(
            caps_ref=caps_ref,
            sources=sources,

Lines: 175-179
    ) -> ContentGenerationArtifact:
        sources = payload.pop("sources", [])
        validation = self.validation_service.validate_artifact_payload(
            artifact_json=payload["artifact_json"],
            caps_ref=payload.get("caps_ref"),

Lines: 183-191
        )
        artifact_hash = stable_json_hash(payload["artifact_json"])
        artifact = ContentGenerationArtifact(
            artifact_id=uuid.uuid4(),
            artifact_hash=artifact_hash,
            source_snapshot_hash=validation["source_snapshot_hash"],
            status=(
                ContentArtifactStatus.PENDING_REVIEW
                if validation["passed"]

Lines: 204-208
                "chunk_hash", "curriculum_mapping_id", "source_hash", "source...
            }
            session.add(
                ContentArtifactSource(
                    artifact_id=artifact.artifact_id,

Lines: 294-298
            raise ValueError("Cannot approve artifact without ETL source cita...

        artifact.status = {
            ContentReviewAction.APPROVE: ContentArtifactStatus.APPROVED,
            ContentReviewAction.REJECT: ContentArtifactStatus.REJECTED,

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_seed_promotion.py

Lines: 64-68

        layer_values = [layer.value for layer in layers] if layers else None
        result = await self.seed_executor.seed_staging(
            session,
            scope_id,

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py

Lines: 67-79

        for scope in scopes:
            report = await self.readiness_service.verify_scope(scope.scope_id...
            for layer in report.layers:
                if layer.layer not in PLANNABLE_LAYERS or layer.target <= 0:
                    continue
                missing_count = max(0, layer.target - layer.approved)
                if missing_count <= 0:
                    skipped.append({"scope_id": scope.scope_id, "caps_ref": l...
                    continue
                context = await self.source_context_service.build_context(ses...
                if not context.passed:
                    skipped.append({"scope_id": scope.scope_id, "caps_ref": l...

Lines: 86-90
                    skipped.append({"scope_id": scope.scope_id, "caps_ref": l...
                    continue
                task = ContentGenerationTask(
                    task_id=uuid.uuid4(),
                    run_id=run.run_id,

Lines: 110-114
                    },
                )
                session.add(task)
                created.append(task.task_id)
                missing_rows.append({"scope_id": scope.scope_id, "caps_ref": ...

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py

Lines: 74-78
            return TaskExecutionResult(task.task_id, "skipped", errors=[f"Tas...

        task.status = "running"
        task.locked_by = actor_id
        task.lock_expires_at = datetime.now(UTC) + timedelta(minutes=10)

Lines: 80-89
        await session.flush()

        context = await self.source_context_service.build_context(session, sc...
        if not context.passed:
            return await self._fail_task(session, task, context.errors)

        provider = get_content_generation_provider(self.settings)
        generated_payloads = await self._call_provider(provider, task, contex...
        existing_hashes = await self._existing_hashes(session)
        artifact_ids: list[uuid.UUID] = []

Lines: 95-99
            if validation_errors:
                errors.extend(validation_errors)
            artifact = await self.content_factory_service.create_artifact(
                session,
                payload={

Lines: 131-135
        task.cost_metadata = {"estimated_cost_usd": 0}
        task.validation_failures = errors
        task.status = "succeeded" if artifact_ids and not errors else "failed"
        task.finished_at = datetime.now(UTC)
        task.admin_actor_id = actor_id

Lines: 194-198
        }
        if _value(task.content_layer) == ContentLayer.DIAGNOSTIC_ITEMS.value:
            items = await provider.generate_diagnostic_items(DiagnosticGenera...
            return [
                {

Lines: 202-206
                    "subject_code": item.subject_code,
                    "language": item.language,
                    "validation_errors": lambda artifact_hash, hashes, item=i...
                }
                for item in items

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/providers/deterministic.py

Lines: 21-25
        chunk_ids = request.source_chunk_ids or [chunk.source_chunk_id for ch...
        return [
            GeneratedDiagnosticItem(
                question_text=f"{request.topic_title}: diagnostic question {i...
                options=["A", "B", "C", "D"],

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/diagnostic_generator.py

Lines: 6-10

class DiagnosticGenerator:
    def validate(self, item: GeneratedDiagnosticItem, *, caps_ref: str, exist...
        errors: list[str] = []
        if not item.correct_answer:

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py

Lines: 150-155
            )

        artifacts = await self._load_scope_artifacts(session, scope_id)
        source_index = await self._load_source_index(session, [artifact.artif...
        layers: list[LayerReadinessSummary] = []
        blockers: list[ScopeBlocker] = []

Lines: 166-172
                    if _value(artifact.content_layer) == layer_name and artif...
                ]
                summary = self._layer_summary(layer_name, target.caps_ref, in...
                layers.append(summary)
                blockers.extend(self._layer_blockers(summary))

        if not targets:

Lines: 301-305
        invalid_license = sum(1 for artifact in approved_artifacts if self._h...
        low_source_quality = sum(1 for artifact in approved_artifacts if self...
        stageable = max(0, len(approved_artifacts) - invalid_provenance - inv...
        if target <= 0:
            status_value = StagingReadinessStatus.NOT_CONFIGURED

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py

Lines: 73-77


@dataclass(frozen=True)
class StagingSeedRunPage:
    items: list[StagingSeedRunResult]

Lines: 96-100

    async def seed_staging(self, session: AsyncSession, scope_id: str, *, lay...
        plan = await self._plan_seed(session, scope_id, layers=layers)
        
        if not allow_partial and plan.skipped:

File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py

Lines: 50-76
            data: Generation report data

        Returns:
            Path to the report directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.base_dir / timestamp
        report_dir.mkdir(parents=True, exist_ok=True)

        # Write summary.md
        self._write_summary_md(report_dir, data)

        # Write summary.json
        self._write_summary_json(report_dir, data)

        # Write scope readiness
        self._write_json(report_dir / "scope_readiness_before.json", data.sco...
        self._write_json(report_dir / "scope_readiness_after.json", data.scop...

        # Write CSV files
        self._write_csv(report_dir / "planned_tasks.csv", data.planned_tasks_...
        self._write_csv(report_dir / "executed_tasks.csv", data.executed_task...
        self._write_csv(report_dir / "generated_artifacts.csv", data.generate...
        self._write_csv(report_dir / "pending_review.csv", data.pending_revie...
        self._write_csv(report_dir / "validation_failed.csv", data.validation...
        self._write_csv(report_dir / "source_blockers.csv", data.source_block...
        self._write_csv(report_dir / "staging_seed_results.csv", data.staging...

Lines: 80-92
            report_dir / "staging_verification.json",
            {"passed": data.staging_verification_passed},
        )

        # Write errors log
        if data.errors:
            self._write_errors_log(report_dir / "errors.log", data.errors)

        return report_dir

    def _write_summary_md(self, report_dir: Path, data: GenerationReportData)...
        """Write summary markdown file."""
        summary_path = report_dir / "summary.md"
```

