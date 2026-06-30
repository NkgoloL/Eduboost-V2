# ETL App Integration

Runtime ETL pipeline modules live under `app/services/etl`.

MCP server wrappers live under `tools/etl` and must not be imported by normal FastAPI startup. Read-only ETL admin visibility is exposed through `/api/v2/admin/etl`.

The Content Factory stores provenance links to ETL source document/chunk metadata through `content_artifact_sources`.
