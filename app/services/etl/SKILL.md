---
name: eduboost-etl
description: >
  Complete guide for working with the Eduboost ETL Document & Training Data Pipeline (Phases 0–12).
  Use this skill whenever a user mentions the Eduboost ETL pipeline, etl_pipeline.py,
  tools/etl/etl_mcp_server.py, the ETL Admin Dashboard, document ingestion, training data generation,
  content gaps, quality validation, or any pipeline operation across the 13-phase roadmap.
  Also triggers for: ingesting documents, running pipeline stages, fixing metadata,
  approving/rejecting content, searching chunks, generating training datasets, exporting
  JSONL/CSV/Parquet, monitoring pipeline health, or building new features on this codebase.
  Always consult this skill before writing any code that touches etl_pipeline*.py,
  etl_mcp_server*.py, or the ETLAdminDashboard. Failing to do so will produce code
  incompatible with the existing architecture.
compatibility:
  python: ">=3.10"
  dependencies:
    required: []
    optional: [numpy, pyarrow, mcp[cli], fastmcp, pydantic]
  files:
    - etl_pipeline.py        # Phases 0–7 base (not in this repo — assumed present)
    - etl_pipeline_v2.py     # Phases 8–12 extensions
    - tools/etl/etl_mcp_server_v2.py   # 21 MCP tools (stdio + streamable-http)
    - ETLAdminDashboard_v2.jsx  # React admin dashboard (Phase 11)
---

# Eduboost ETL Pipeline — Claude Skill

## Architecture Overview

```
etl_pipeline.py (Phases 0–7)
  └─ EduboostETL          ← base class (SQLite, file storage, extraction, chunking)
       ↑ inherits
etl_pipeline_v2.py (Phases 8–12)
  └─ EduboostETLv2        ← versioning, FTS, embeddings, training datasets, monitoring

tools/etl/etl_mcp_server_v2.py
  └─ MCP server       ← 21 tools wrapping EduboostETLv2
       transport: stdio | streamable-http

ETLAdminDashboard_v2.jsx
  └─ React SPA            ← Phase 11 admin UI (seeded mock data, no live API required)
```

---

## Phase Map

| Phase | Name | Key Classes / Tables | Status |
|-------|------|---------------------|--------|
| 0 | Governance & Inventory | `document_inventory`, `source_registry` | ✅ base |
| 1 | Source Registry & Acquisition | `sources`, `EduboostETL.ingest()` | ✅ base |
| 2 | Raw Document Storage | `/documents/raw/{source_id}/{doc_id}/` | ✅ base |
| 3 | Extraction Layer | `EduboostETL.extract()` | ✅ base |
| 4 | Normalization & Cleaning | `EduboostETL.normalize()` | ✅ base |
| 5 | Metadata Enrichment | `EduboostETL.enrich_metadata()` | ✅ base |
| 6 | Segmentation & Chunking | `EduboostETL.chunk()`, `document_chunks` | ✅ base |
| 7 | Quality Validation | `EduboostETL.validate()`, quality scoring | ✅ base |
| 8 | Canonical Content Store | `document_versions`, `curriculum_mappings` | ✅ v2 |
| 9 | Search & Vector Indexing | `chunks_fts` (FTS5), `chunk_embeddings` | ✅ v2 |
| 10 | Training Dataset Builder | `training_datasets`, `training_examples` | ✅ v2 |
| 11 | Admin Review & Ops | `review_tasks`, MCP tools, React dashboard | ✅ v2 |
| 12 | Monitoring & Feedback | `pipeline_metrics`, `user_feedback` | ✅ v2 |

---

## Core Data Models

### ProcessingStatus lifecycle (strict ordering)
```
raw → acquired → extracted → normalized → metadata_enriched
    → chunked → validated → needs_review ↔ approved
    → indexed → training_ready
    → rejected / archived  (terminal states)
```

### Document (base dataclass)
```python
@dataclass
class Document:
    document_id: str       # UUID
    title: str
    document_type: str     # DocumentType enum
    subject: Optional[str]
    grade: Optional[int]   # 1–12
    language: str          # ISO 639-1
    processing_status: str # ProcessingStatus enum
    quality_score: float   # 0.0–1.0 (see quality formula below)
    training_readiness: bool
    license_status: str    # LicenseStatus enum
    curriculum: str        # "CAPS" default
    # ... + ~20 more fields (see etl_pipeline.py)
```

### Quality Score Formula (Phase 7)
```
quality_score =
  metadata_score    * 0.20 +
  extraction_score  * 0.20 +
  structure_score   * 0.20 +
  completeness_score* 0.20 +
  provenance_score  * 0.10 +
  training_suitability_score * 0.10
```

### Key Tables (v2)
- `document_versions` — semver snapshots, `snapshot_path`
- `curriculum_mappings` — CAPS code ↔ chunk linkage
- `chunk_embeddings` — float32 BLOB + model_name + indexed_at
- `training_datasets` — dataset_type / split / version / export_path
- `training_examples` — input/output pairs, synthetic flag, human_reviewed
- `pipeline_metrics` — time-series name/value/tags
- `user_feedback` — 5 feedback types → auto-creates review_tasks

---

## MCP Server (21 Tools)

### Quick Reference

| Tool | Phase | Read-only | Description |
|------|-------|-----------|-------------|
| `etl_ingest_document` | 1 | ❌ | Acquire & register a document file |
| `etl_get_document` | 8 | ✅ | Fetch document record by ID |
| `etl_list_documents` | 8 | ✅ | Filter registry (status/grade/subject/type) |
| `etl_run_pipeline` | 3–7 | ❌ | Run all ETL stages on one document |
| `etl_run_stage` | 3–7 | ❌ | Run one stage (extract/normalize/chunk/validate) |
| `etl_approve_document` | 11 | ❌ | Approve for production (requires reviewer) |
| `etl_reject_document` | 11 | ❌ | Reject with auditable reason |
| `etl_reprocess_document` | 11 | ❌ | Reset & re-run pipeline |
| `etl_get_review_queue` | 11 | ✅ | Pending review tasks |
| `etl_get_pipeline_stats` | 12 | ✅ | Aggregated health metrics |
| `etl_get_content_gaps` | 11 | ✅ | Coverage by grade/subject/type |
| `etl_get_quality_report` | 7 | ✅ | Per-document quality breakdown |
| `etl_get_document_chunks` | 6/8 | ✅ | Inspect chunks (with type filter) |
| `etl_update_metadata` | 5/8 | ❌ | Partial metadata correction |
| `etl_create_document_version`| 8 | ❌ | Snapshot a version |
| `etl_search_fulltext` | 9 | ✅ | Keyword search with citations |
| `etl_generate_training_data`| 10 | ❌ | Auto-generate training examples |
| `etl_list_training_datasets`| 10 | ✅ | List all datasets |
| `etl_export_dataset` | 10 | ❌ | Export JSONL/CSV/Parquet |
| `etl_submit_feedback` | 12 | ❌ | Ingest user feedback |
| `etl_get_monitoring_report` | 12 | ✅ | Full pipeline health snapshot |
| `etl_get_completeness_report`| 12 | ✅ | Curriculum coverage map |

### Calling Pattern
All tools accept Pydantic models. Responses are JSON strings. Check `success` field.

```python
# Start server
python tools/etl/etl_mcp_server_v2.py --transport streamable-http --port 8765

# Or stdio (Claude Desktop / MCP Inspector)
python tools/etl/etl_mcp_server_v2.py
```

### Environment Variables
```bash
ETL_DB_URL=sqlite:///eduboost_etl.db   # or postgres URL
ETL_STORAGE_ROOT=./data
ETL_EXPORTS_DIR=./exports
```

---

## Common Workflows

### Ingest → Approve a document
```python
# 1. Ingest
result = etl_ingest_document(file_path="/uploads/grade4_maths.pdf",
    document_type="textbook", grade=4, subject="mathematics")
doc_id = result["document_id"]

# 2. Run pipeline (phases 3–7 in sequence)
etl_run_pipeline(document_id=doc_id)

# 3. Check quality
report = etl_get_quality_report(document_id=doc_id)

# 4. Fix metadata if needed
etl_update_metadata(document_id=doc_id, reviewer_notes="Grade confirmed via TOC")

# 5. Approve
etl_approve_document(document_id=doc_id, reviewer="admin@eduboost.com")
```

### Generate & export training data
```python
# 1. Generate QA pairs from approved documents
dataset = etl_generate_training_data(
    document_ids=["doc-abc", "doc-def"],
    example_type="qa",
    dataset_name="Grade 4 Maths QA v1",
    split="train"
)

# 2. Export
etl_export_dataset(dataset_id=dataset["dataset_id"], format="jsonl")
```

### Monitor pipeline health
```python
report = etl_get_monitoring_report()
# Returns: stale_documents, failed_jobs_24h, approval_rate, alerts, feedback_summary
```

---

## Adding New Pipeline Methods (Python)

1. Add to `EduboostETLv2` (or subclass it as `EduboostETLv3`)
2. Add table DDL to a new `SCHEMA_V3_SQL` constant
3. Call `self._db().executescript(SCHEMA_V3_SQL)` in `init_db()`
4. Always use `_uid()` for PKs and `_now()` for timestamps
5. Use `self._db()` (lazy SQLite connection via `self.__db`)
6. Commit after writes: `self._db().commit()`

### Adding New MCP Tools

```python
class MyNewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(..., description="...")
    my_param: Optional[str] = Field(default=None)

@mcp.tool(name="etl_my_tool", annotations={
    "title": "My Tool Title",
    "readOnlyHint": True,   # False if mutates data
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
})
async def etl_my_tool(params: MyNewInput) -> str:
    """
    Description Claude uses to decide when to call this tool.
    Be explicit about return format and next steps.
    """
    try:
        result = pipeline().my_new_method(params.document_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)
```

---

## Admin Dashboard (ETLAdminDashboard_v2.jsx)

### Tabs
| Tab | Phase | What it shows |
|-----|-------|--------------|
| Overview | 0/12 | StatCards, PipelineFlow, recent docs + jobs |
| Documents | 8 | Filterable registry table with drawer detail |
| Gaps | 11 | Grade × Subject coverage heat matrix |
| Review | 11 | Human review queue with approve/reject |
| Search | 9 | Full-text search with citation display |
| Training | 10 | Dataset cards, export UI, example browser |
| Monitoring | 12 | Health metrics, stale docs, feedback charts |
| Jobs | 12 | Processing jobs log |

### Key Design Rules
- **Dark theme** — background `#0a0d14`, surface `rgba(255,255,255,.03)`
- **No purple gradients** — use `#818cf8` (indigo) sparingly for brand accents
- **`STATUS_META`** — all status colors live here; never hard-code status colors
- **`seedData()`** — generates all mock data deterministically; no live API calls
- **State** — `useState` only; no external state library
- **Charts** — hand-rolled SVG (no chart library) for PipelineFlow, GapMatrix, sparklines

### Extending the Dashboard
To add a new tab:
1. Add entry to `TABS` array: `["my_tab", "My Label"]`
2. Add `{tab==="my_tab" && <MyComponent />}` in the body section
3. Create `MyComponent` as a function component above the main `App`
4. Pull data from `DATA` (seeded) or add fields to `seedData()`

---

## File Structure Reference

```
eduboost-etl/
├── etl_pipeline.py              # Phases 0–7 (base, assumed present)
├── etl_pipeline_v2.py           # Phases 8–12 (EduboostETLv2)
├── tools/etl/etl_mcp_server_v2.py         # MCP server (21 tools)
├── ETLAdminDashboard_v2.jsx     # React dashboard
├── data/
│   ├── documents/raw/           # Immutable source files
│   ├── documents/extracted/     # Per-document text.json
│   ├── documents/normalized/    # Per-document normalized.json
│   ├── documents/chunks/        # Per-document chunks.jsonl
│   └── documents/rejected/      # Per-document reason.json
├── exports/                     # Training dataset exports
└── eduboost_etl.db              # SQLite database (all tables)
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `FTS5 unavailable` warning | SQLite compiled without FTS5 | Use system SQLite or `pip install pysqlite3-binary` |
| `HAS_PARQUET = False` | pyarrow not installed | `pip install pyarrow` |
| `HAS_NUMPY = False` | numpy not installed | `pip install numpy` (needed for cosine similarity) |
| Tool returns `"success": false` | Exception in pipeline | Check `error` field; run `etl_get_quality_report` for document issues |
| Document stuck in `needs_review` | Quality gate failed | Run `etl_get_quality_report`, then `etl_update_metadata`, then re-approve |
| Embedding search returns nothing | No embeddings generated | Run embedding pipeline (stub: subclass `embed_chunks`) |

---

## Reference Files

- [`references/schema_v2.md`](./references/schema_v2.md) — Full SQL schema (all tables)
- [`references/document_types.md`](./references/document_types.md) — DocumentType enum + chunking rules per type
- [`references/feedback_types.md`](./references/feedback_types.md) — Feedback → review task mapping
- [`references/quality_scoring.md`](./references/quality_scoring.md) — Detailed quality score breakdown
