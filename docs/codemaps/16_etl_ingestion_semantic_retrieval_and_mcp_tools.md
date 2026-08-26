# EduBoost V2 ETL, Ingestion, Semantic Retrieval, and MCP Tools

Maps ETL pipeline versions, document processing, MCP server startup and tools, semantic indexing and retrieval, curriculum extraction, and administrator controls.

## Scope and ownership

This codemap is the primary architecture owner for:
- `tools/etl`
- `app/services/etl`
- `app/services/semantic_retrieval`
- `app/services/curriculum/extraction.py`
- `app/api_v2_routers/admin_etl.py`
- `app/models/retrieval.py`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** ETL MCP server startup, backend selection, and tool exposure

**Description:** Follows server import and configuration through real FastMCP backend selection, fallback policy, tool registration, and transport startup.

**Motivation:**
The ETL MCP server exposes privileged document operations to AI tooling; backend identity and startup behaviour must be explicit and testable.

**Details:**

**Execution path**

1. Load ETL configuration and backend compatibility layer.
2. Select the real MCP backend when installed.
3. Permit test stub only under explicit test configuration.
4. Construct the server and register approved tools.
5. Start JSON-response or streamable HTTP transport.
6. Expose health and fail clearly on unsupported backend state.

**State and ownership boundaries**

Backend selection is process-level state; tool execution uses service and repository dependencies with their own scopes.

**Failure, privacy, and control points**

Production never silently uses the test stub, tool schemas remain bounded, transports do not expose secrets, and startup errors are observable.

**Verification signals**

Run ETL MCP startup tests for real backend, forced missing backend, JSON response mode, and settings fallback.

**Trace text diagram:**
```text
1. Load ETL configuration and backend compatibility layer [1a]
   |
   v
2. Select the real MCP backend when installed [1b]
   |
   v
3. Permit test stub only under explicit test configuration [1c]
   |
   v
4. Construct the server and register approved tools [1d]
   |
   v
5. Start JSON-response or streamable HTTP transport [1d]
   |
   v
6. Expose health and fail clearly on unsupported backend state [1d]
```

**Location ID: 1a**
- **Title:** ETL MCP server
- **Description:** Primary server and tool registration.
- **Path:LineNumber:** tools/etl/etl_mcp_server.py:42

**Location ID: 1b**
- **Title:** MCP compatibility
- **Description:** Real backend and explicit test fallback.
- **Path:LineNumber:** tools/etl/mcp_compat.py:11

**Location ID: 1c**
- **Title:** V2 ETL tools
- **Description:** Extended tool surface.
- **Path:LineNumber:** tools/etl/etl_mcp_server_v2.py:55

**Location ID: 1d**
- **Title:** MCP startup tests
- **Description:** Backend and transport proof.
- **Path:LineNumber:** tests/unit/test_etl_mcp_server_startup.py:68

### AI Guide: ETL MCP server startup, backend selection, and tool exposure

**Motivation:**
The ETL MCP server exposes privileged document operations to AI tooling; backend identity and startup behaviour must be explicit and testable.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors etl mcp server. [1b] anchors mcp compatibility. [1c] anchors v2 etl tools. [1d] anchors mcp startup tests.

**Safe change boundary.** Backend selection is process-level state; tool execution uses service and repository dependencies with their own scopes. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Production never silently uses the test stub, tool schemas remain bounded, transports do not expose secrets, and startup errors are observable.

**How to verify the change.** Run ETL MCP startup tests for real backend, forced missing backend, JSON response mode, and settings fallback. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Document ingestion, extraction, normalization, and storage

**Description:** Maps an administrator or tool request from source intake through parsing, chunking, validation, and persisted provenance.

**Motivation:**
Retrieval and curriculum grounding are only as trustworthy as the source identity and page/chunk provenance established during ingestion.

**Details:**

**Execution path**

1. Authenticate administrative or controlled tool request.
2. Register source identity, rights, and content hash.
3. Extract text and page-level metadata.
4. Normalize, chunk, and validate document content.
5. Persist document, chunk, and processing status.
6. Publish artefacts eligible for review, indexing, or curriculum mapping.

**State and ownership boundaries**

Original source, extracted pages, chunks, and processing records are separate immutable or versioned artefacts.

**Failure, privacy, and control points**

Unsupported files fail safely, duplicate content is detected, rights metadata is mandatory, and parsing never grants automatic approval.

**Verification signals**

Run ETL pipeline, curriculum extraction, file import, provenance, and admin route tests.

**Trace text diagram:**
```text
1. Authenticate administrative or controlled tool request [2a]
   |
   v
2. Register source identity, rights, and content hash [2b]
   |
   v
3. Extract text and page-level metadata [2c]
   |
   v
4. Normalize, chunk, and validate document content [2d]
   |
   v
5. Persist document, chunk, and processing status [2d]
   |
   v
6. Publish artefacts eligible for review, indexing, or curriculum mapping [2d]
```

**Location ID: 2a**
- **Title:** Admin ETL routes
- **Description:** Controlled ingestion API.
- **Path:LineNumber:** app/api_v2_routers/admin_etl.py:27

**Location ID: 2b**
- **Title:** ETL pipeline
- **Description:** Document processing orchestration.
- **Path:LineNumber:** app/services/etl/etl_pipeline.py:84

**Location ID: 2c**
- **Title:** Curriculum extraction
- **Description:** Page-level structured extraction.
- **Path:LineNumber:** app/services/curriculum/extraction.py:25

**Location ID: 2d**
- **Title:** Retrieval models
- **Description:** Persisted documents and chunks.
- **Path:LineNumber:** app/models/retrieval.py:27

### AI Guide: Document ingestion, extraction, normalization, and storage

**Motivation:**
Retrieval and curriculum grounding are only as trustworthy as the source identity and page/chunk provenance established during ingestion.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors admin etl routes. [2b] anchors etl pipeline. [2c] anchors curriculum extraction. [2d] anchors retrieval models.

**Safe change boundary.** Original source, extracted pages, chunks, and processing records are separate immutable or versioned artefacts. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Unsupported files fail safely, duplicate content is detected, rights metadata is mandatory, and parsing never grants automatic approval.

**How to verify the change.** Run ETL pipeline, curriculum extraction, file import, provenance, and admin route tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Semantic indexing, retrieval, evaluation, and generation context

**Description:** Shows approved chunks becoming embeddings and bounded retrieval context for lessons, tutor, content, and evaluation.

**Motivation:**
Semantic retrieval must preserve source authority and avoid turning similarity into an unreviewed truth claim.

**Details:**

**Execution path**

1. Select approved and indexable chunks.
2. Generate embeddings with versioned model metadata.
3. Persist vectors and searchable metadata.
4. Execute filtered semantic retrieval.
5. Assemble a token-bounded generation context with citations.
6. Evaluate relevance, grounding, and retrieval regressions.

**State and ownership boundaries**

Index versions and embedding model metadata are rebuildable projections of approved source chunks.

**Failure, privacy, and control points**

Only approved sources are indexed, learner or tenant filters are explicit, citations survive context assembly, and evaluation detects drift.

**Verification signals**

Run semantic indexing, repository, retrieval, generation-context, and evaluation tests.

**Trace text diagram:**
```text
1. Select approved and indexable chunks [3a]
   |
   v
2. Generate embeddings with versioned model metadata [3b]
   |
   v
3. Persist vectors and searchable metadata [3c]
   |
   v
4. Execute filtered semantic retrieval [3d]
   |
   v
5. Assemble a token-bounded generation context with citations [3d]
   |
   v
6. Evaluate relevance, grounding, and retrieval regressions [3d]
```

**Location ID: 3a**
- **Title:** Semantic indexing
- **Description:** Embedding and index creation.
- **Path:LineNumber:** app/services/semantic_retrieval/indexing.py:23

**Location ID: 3b**
- **Title:** Retrieval repository
- **Description:** Vector and metadata queries.
- **Path:LineNumber:** app/services/semantic_retrieval/repository.py:70

**Location ID: 3c**
- **Title:** Retrieval service
- **Description:** Filtered search orchestration.
- **Path:LineNumber:** app/services/semantic_retrieval/service.py:20

**Location ID: 3d**
- **Title:** Retrieval evaluation
- **Description:** Grounding and relevance evidence.
- **Path:LineNumber:** app/services/semantic_retrieval/evaluation.py:10

### AI Guide: Semantic indexing, retrieval, evaluation, and generation context

**Motivation:**
Semantic retrieval must preserve source authority and avoid turning similarity into an unreviewed truth claim.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors semantic indexing. [3b] anchors retrieval repository. [3c] anchors retrieval service. [3d] anchors retrieval evaluation.

**Safe change boundary.** Index versions and embedding model metadata are rebuildable projections of approved source chunks. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Only approved sources are indexed, learner or tenant filters are explicit, citations survive context assembly, and evaluation detects drift.

**How to verify the change.** Run semantic indexing, repository, retrieval, generation-context, and evaluation tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
