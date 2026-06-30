# Eduboost ETL MCP Server README

This document explains how the Eduboost ETL MCP server works, how to start it, how to verify that it is alive, and how to use it from an MCP client or from local development tooling.

The ETL MCP server exposes the Eduboost document ingestion and training-data pipeline as Model Context Protocol tools. In practical terms, it lets an agent or operator ingest source material, run extraction and normalization, inspect quality, approve or reject documents, search indexed chunks, generate training datasets, export those datasets, and monitor pipeline health through one consistent tool interface.

## Current Process State

On the development VM, the v2 ETL MCP server is currently running from this repository:

```bash
cd ~/Dev/SandBox/ml/Eduboost-V2
.venv/bin/python -m tools.etl.etl_mcp_server_v2 --transport streamable-http --port 8765
```

Observed process:

```text
PID: 703677
Host: 127.0.0.1
Port: 8765
Endpoint: http://127.0.0.1:8765/mcp
Transport: streamable-http
Entrypoint: tools.etl.etl_mcp_server_v2
```

A plain browser or curl request to `/mcp` should return a JSON-RPC error explaining that the endpoint expects an MCP client or a POST with MCP headers. That response is intentional and confirms that the HTTP app is up:

```bash
curl -i http://127.0.0.1:8765/mcp
```

Expected shape:

```json
{
  "jsonrpc": "2.0",
  "id": "server-error",
  "error": {
    "code": -32000,
    "message": "MCP endpoint. Use an MCP client or POST /mcp with MCP headers."
  }
}
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `app/services/etl/etl_pipeline.py` | Base ETL pipeline for phases 0-7: inventory, acquisition, raw storage, extraction, normalization, metadata enrichment, chunking, and validation. |
| `app/services/etl/etl_pipeline_v2.py` | Extended pipeline for phases 8-12: canonical store, versions, FTS search, training datasets, monitoring, and feedback. |
| `tools/etl/etl_mcp_server.py` | v1 MCP server. Exposes the base document lifecycle tools. |
| `tools/etl/etl_mcp_server_v2.py` | v2 MCP server. This is the preferred runtime entrypoint for local and remote use. |
| `tools/etl/etl_mcp_server_v3_additions.py` | Additional v3-style tool implementations that are not the default server entrypoint. |
| `tests/unit/test_etl_mcp_server_startup.py` | Focused tests for MCP JSON response mode and streamable HTTP startup compatibility. |
| `docs/etl/README.md` | This operator and developer guide. |

## Server Architecture

The server is intentionally thin. It does not implement ETL behavior directly. Instead, it performs five jobs:

1. Read runtime configuration from environment variables.
2. Lazily instantiate the pipeline class the first time a tool needs it.
3. Define Pydantic input models for MCP tool schemas.
4. Register ETL operations as `FastMCP` tools.
5. Start the server over either stdio or streamable HTTP.

The v2 entrypoint uses this pipeline class:

```python
EduboostETLv2(db_url=ETL_DB_URL, storage_root=ETL_STORAGE)
```

Pipeline initialization is lazy. Starting the MCP process does not immediately open or migrate the ETL database. The first tool call creates the singleton pipeline instance, initializes the database, and attempts to initialize SQLite FTS support:

```python
_pipeline = EduboostETLv2(db_url=ETL_DB_URL, storage_root=ETL_STORAGE)
_pipeline.init_db()
_pipeline.init_fts()
```

If SQLite FTS5 is not available in the local SQLite build, startup continues. Search still has a fallback path in the pipeline layer, but FTS-specific ranking may be limited.

## Runtime Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `ETL_DB_URL` | `sqlite:///eduboost_etl.db` | ETL metadata database. SQLite is the default development path. |
| `ETL_STORAGE_ROOT` | `./data` | Root directory for raw files, extracted text, normalized output, chunks, snapshots, and other pipeline artifacts. |
| `ETL_EXPORTS_DIR` | `./exports` | Directory where training dataset exports are written. v2 only. |

Recommended local development configuration:

```bash
export ETL_DB_URL="sqlite:///temp/etl_mcp_smoke.db"
export ETL_STORAGE_ROOT="temp/etl_mcp_storage"
export ETL_EXPORTS_DIR="temp/etl_mcp_exports"
```

This keeps smoke-test data out of the default repository-level `data/` and `exports/` folders.

## Transports

The server supports two transports.

### stdio

Use stdio when a local MCP host launches the process directly. This is the usual mode for Claude Desktop-style MCP configuration and for MCP Inspector when it starts the server as a child process.

```bash
.venv/bin/python -m tools.etl.etl_mcp_server_v2
.venv/bin/python -m tools.etl.etl_mcp_server_v2 --transport stdio
```

### streamable-http

Use streamable HTTP when a remote MCP client needs to connect to a long-running server process.

```bash
.venv/bin/python -m tools.etl.etl_mcp_server_v2 --transport streamable-http --host 127.0.0.1 --port 8765
```

The endpoint path is:

```text
http://127.0.0.1:8765/mcp
```

The server is configured with `json_response=True`, which makes HTTP responses easier for non-SSE clients and smoke tests to consume.

The startup wrapper supports both newer and older FastMCP SDK behavior. Newer SDKs accept `host` and `port` directly in `FastMCP.run(...)`. Older SDKs raise `TypeError` for those arguments, so the wrapper assigns `mcp.settings.host` and `mcp.settings.port`, builds `mcp.streamable_http_app()`, wraps it in browser-friendly middleware, and runs it through uvicorn.

## Step-By-Step Startup

### 1. SSH To The VM

```bash
ssh azureuser@135.119.52.214
```

### 2. Change Into The Repo

```bash
cd ~/Dev/SandBox/ml/Eduboost-V2
```

### 3. Confirm The Virtual Environment

```bash
.venv/bin/python --version
.venv/bin/python -c "from mcp.server.fastmcp import FastMCP; print('mcp ok')"
```

If the import fails, install the project requirements and MCP runtime dependencies in the virtual environment:

```bash
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pip install 'mcp[cli]' fastmcp uvicorn starlette
```

### 4. Pick Storage Paths

For safe local smoke testing:

```bash
export ETL_DB_URL="sqlite:///temp/etl_mcp_smoke.db"
export ETL_STORAGE_ROOT="temp/etl_mcp_storage"
export ETL_EXPORTS_DIR="temp/etl_mcp_exports"
mkdir -p temp/etl_mcp_storage temp/etl_mcp_exports
```

For normal development using the defaults, this step can be skipped.

### 5. Check Whether The Port Is Already In Use

```bash
ss -ltnp | grep ':8765' || true
pgrep -af 'etl_mcp_server.*streamable-http' || true
```

If another ETL MCP process is already running on port `8765`, either reuse it or choose a different port such as `8766`.

### 6. Start v2 Over Streamable HTTP

Foreground mode:

```bash
.venv/bin/python -m tools.etl.etl_mcp_server_v2 --transport streamable-http --host 127.0.0.1 --port 8765
```

Background mode:

```bash
mkdir -p logs
nohup .venv/bin/python -m tools.etl.etl_mcp_server_v2 \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8765 \
  > logs/etl_mcp_server_v2.log 2>&1 &
echo $!
```

### 7. Verify The Endpoint

```bash
curl -i http://127.0.0.1:8765/mcp
```

A `200 OK` with the JSON-RPC MCP endpoint message means the HTTP server is alive. It does not mean you have completed an MCP session; it only verifies routing and process health.

### 8. Inspect Logs

If started with the background command above:

```bash
tail -f logs/etl_mcp_server_v2.log
```

You should see startup lines similar to:

```text
Starting Eduboost ETL MCP Server v2 (transport=streamable-http)
  DB:      sqlite:///temp/etl_mcp_smoke.db
  Storage: temp/etl_mcp_storage
  Exports: temp/etl_mcp_exports
```

## Stopping And Restarting

Find the process:

```bash
pgrep -af 'etl_mcp_server.*streamable-http'
```

Stop it politely:

```bash
kill <pid>
```

Then restart using the startup command above.

## Client Configuration Examples

### MCP Host Using stdio

Use this when the MCP host can execute commands on the same machine as the repository:

```json
{
  "mcpServers": {
    "eduboost-etl": {
      "command": "/home/azureuser/Dev/SandBox/ml/Eduboost-V2/.venv/bin/python",
      "args": [
        "-m",
        "tools.etl.etl_mcp_server_v2",
        "--transport",
        "stdio"
      ],
      "cwd": "/home/azureuser/Dev/SandBox/ml/Eduboost-V2",
      "env": {
        "ETL_DB_URL": "sqlite:///temp/etl_mcp_smoke.db",
        "ETL_STORAGE_ROOT": "temp/etl_mcp_storage",
        "ETL_EXPORTS_DIR": "temp/etl_mcp_exports"
      }
    }
  }
}
```

### MCP Host Using streamable HTTP

Use this when the server is already running as a daemon or remote process:

```json
{
  "mcpServers": {
    "eduboost-etl-http": {
      "url": "http://127.0.0.1:8765/mcp"
    }
  }
}
```

If the client runs on your local workstation and the server binds only to `127.0.0.1` on the VM, create an SSH tunnel:

```bash
ssh -L 8765:127.0.0.1:8765 azureuser@135.119.52.214
```

Then point the local MCP client at:

```text
http://127.0.0.1:8765/mcp
```

## Tool Catalog

The preferred v2 server exposes the following tools.

| Tool | Mutates data | Phase | Use it for |
| --- | --- | --- | --- |
| `etl_ingest_document` | Yes | 1 | Register a local document file, copy it into raw storage, calculate checksum, and create the canonical document record. |
| `etl_get_document` | No | 8 | Fetch a document record by UUID. |
| `etl_list_documents` | No | 8 | Filter the document registry by status, grade, subject, type, and limit. |
| `etl_run_pipeline` | Yes | 3-7 | Run extraction, normalization, enrichment, chunking, and validation for one document. |
| `etl_run_stage` | Yes | 3-7 | Run one stage only: `extract`, `normalize`, `chunk`, or `validate`. |
| `etl_approve_document` | Yes | 11 | Mark a document as approved for production use and record reviewer metadata. |
| `etl_reject_document` | Yes | 11 | Mark a document as rejected with a reason while preserving the raw file. |
| `etl_reprocess_document` | Yes | 11 | Reset a document to `acquired` and run the full pipeline again. |
| `etl_get_review_queue` | No | 11 | List documents and tasks awaiting human review. |
| `etl_get_pipeline_stats` | No | 12 | Get status counts, average quality, and review backlog metrics. |
| `etl_get_content_gaps` | No | 11 | Inspect coverage gaps by grade, subject, document type, and status. |
| `etl_get_quality_report` | No | 7 | Read the latest quality report for a document. |
| `etl_get_document_chunks` | No | 6/8 | Inspect chunk text, headings, page ranges, curriculum codes, and token counts. |
| `etl_update_metadata` | Yes | 5/8 | Correct metadata fields and create an audit-friendly version snapshot. |
| `etl_create_document_version` | Yes | 8 | Snapshot normalized output as a version after a meaningful change. |
| `etl_search_fulltext` | No | 9 | Search approved chunks using FTS5 or fallback search and return citations. |
| `etl_generate_training_data` | Yes | 10 | Generate QA, summary, concept, or rubric examples from approved/indexed documents. |
| `etl_list_training_datasets` | No | 10 | List generated training datasets and export status. |
| `etl_export_dataset` | Yes | 10 | Export a dataset as `jsonl`, `csv`, or `parquet`. |
| `etl_submit_feedback` | Yes | 12 | Record user feedback and create review tasks for actionable feedback types. |
| `etl_get_monitoring_report` | No | 12 | Get a pipeline health snapshot with totals, rates, stale documents, failures, feedback, and alerts. |
| `etl_get_completeness_report` | No | 12 | Check curriculum coverage across grades, subjects, and required document types. |

## Core Workflows

### Ingest, Process, And Approve A Document

1. Call `etl_ingest_document` with a path to a source file and known metadata.
2. Capture the returned `document_id`.
3. Call `etl_run_pipeline` with that `document_id`.
4. Call `etl_get_quality_report` to inspect quality dimensions and issues.
5. If metadata is wrong or incomplete, call `etl_update_metadata`.
6. If the document is acceptable, call `etl_approve_document` with a reviewer name and notes.
7. Optionally call `etl_create_document_version` to snapshot the approved state.

Example tool input for ingestion:

```json
{
  "file_path": "temp/etl_sample.md",
  "document_type": "textbook",
  "source_type": "manual_upload",
  "uploaded_by": "operator",
  "grade": 4,
  "subject": "mathematics",
  "language": "en",
  "license_status": "open",
  "title": "Grade 4 Mathematics Sample",
  "notes": "Local smoke-test document"
}
```

### Run A Single Pipeline Stage

Use `etl_run_stage` when debugging a failed or suspicious pipeline step:

```json
{
  "document_id": "<document-id>",
  "stage": "extract"
}
```

Valid stages are:

```text
extract
normalize
chunk
validate
```

### Search Approved Content

Once documents have been approved and indexed, call `etl_search_fulltext`:

```json
{
  "query": "fractions grade 4",
  "grade": 4,
  "subject": "mathematics",
  "limit": 10
}
```

Search results include citation metadata so downstream AI responses can attribute answers to document, section, and page information.

### Generate And Export Training Data

1. Approve one or more source documents.
2. Call `etl_generate_training_data` with `document_ids`, `example_type`, `dataset_name`, and `split`.
3. Capture the returned `dataset_id`.
4. Call `etl_export_dataset` with the dataset ID and output format.

Example generation input:

```json
{
  "document_ids": ["<document-id>"],
  "example_type": "qa",
  "dataset_name": "Grade 4 Mathematics QA Smoke Test",
  "split": "train",
  "created_by": "operator"
}
```

Example export input:

```json
{
  "dataset_id": "<dataset-id>",
  "format": "jsonl"
}
```

## Data Lifecycle

Documents move through a strict lifecycle:

```text
raw -> acquired -> extracted -> normalized -> metadata_enriched -> chunked -> validated -> needs_review -> approved -> indexed -> training_ready
```

Terminal or side-path states:

```text
rejected
archived
```

The usual path is:

```text
ingest document -> run full pipeline -> inspect quality -> fix metadata if needed -> approve -> search/generate/export
```

## Quality Validation

The validation stage produces an overall quality score and dimension-level scores.

| Dimension | Weight | Meaning |
| --- | ---: | --- |
| Metadata | 20% | Required fields such as grade, subject, language, title, and license are present and coherent. |
| Extraction | 20% | Text extraction succeeded and produced usable content. |
| Structure | 20% | The document has headings, sections, pages, or other navigable structure. |
| Completeness | 20% | Content appears complete enough for the document type and curriculum slot. |
| Provenance | 10% | Source and rights information are traceable. |
| Training suitability | 10% | Content is useful for downstream training data generation. |

Documents below the approval threshold should move to review rather than production use.

## Operational Checks

### Check Process

```bash
pgrep -af 'etl_mcp_server.*streamable-http'
ss -ltnp | grep ':8765'
```

### Check Endpoint

```bash
curl -s http://127.0.0.1:8765/mcp | python -m json.tool
```

### Run Focused Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest --no-cov -q tests/unit/test_etl_mcp_server_startup.py
```

### Run Broader ETL Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest --no-cov -q tests/unit/test_etl_pipeline.py tests/unit/test_phase2_data_pipeline.py tests/unit/test_etl_mcp_server_startup.py
```

## Troubleshooting

### `Address already in use`

Another process is already listening on the port.

```bash
ss -ltnp | grep ':8765'
pgrep -af 'etl_mcp_server.*streamable-http'
```

Either reuse that process, stop it with `kill <pid>`, or start the new server on another port:

```bash
.venv/bin/python -m tools.etl.etl_mcp_server_v2 --transport streamable-http --port 8766
```

### `FastMCP.run() got an unexpected keyword argument 'host'`

This is handled by `_start_mcp_server`. The wrapper falls back to setting `mcp.settings.host` and `mcp.settings.port`, then runs the streamable HTTP ASGI app through uvicorn.

If this error escapes to the terminal, run the startup test and confirm the current branch contains the compatibility wrapper:

```bash
PYTHONPATH=. .venv/bin/python -m pytest --no-cov -q tests/unit/test_etl_mcp_server_startup.py
```

### Browser Shows A JSON-RPC Error

That is expected for a plain `GET /mcp`. The endpoint is not a web UI. Use an MCP client, MCP Inspector, or a correctly formed JSON-RPC POST with MCP session headers.

### Import Error For `mcp`, `fastmcp`, `uvicorn`, Or `starlette`

Install the runtime dependencies into the same interpreter used to start the server:

```bash
.venv/bin/python -m pip install 'mcp[cli]' fastmcp uvicorn starlette
```

Then verify imports:

```bash
.venv/bin/python -c "from mcp.server.fastmcp import FastMCP; import uvicorn, starlette; print('ok')"
```

### SQLite FTS Is Unavailable

The v2 pipeline catches FTS initialization failures and continues. Search may fall back to simpler matching. If ranked full-text search is required, use a Python/SQLite build with FTS5 enabled.

### Tool Call Returns `success: false`

Read the returned `error` field first. Common causes are:

- `file_path` does not exist from the server process working directory.
- The document is not in the right lifecycle state for the requested operation.
- Required metadata is missing.
- The database path points at an unexpected or stale SQLite file.
- Export directory does not exist or is not writable.

## Development Notes

When adding or changing MCP tools:

1. Keep tool functions thin; put business logic in the pipeline service.
2. Define a Pydantic input model with `ConfigDict(extra="forbid")`.
3. Use explicit field descriptions because MCP clients surface those schemas to agents.
4. Return JSON strings with a stable `success` flag for mutating operations.
5. Mark tool annotations accurately: read-only tools should use `readOnlyHint=True`; mutating tools should not.
6. Add focused tests for startup behavior and schema/tool behavior that could regress.
7. Prefer v2 as the default server unless a client explicitly needs the smaller v1 surface.

## Related Docs

Back to the main docs index: [docs/README.md](../README.md).

Root project overview: [README.md](../../README.md).
