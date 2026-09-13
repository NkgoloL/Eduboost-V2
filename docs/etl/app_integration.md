---
title: "ETL App Integration (App Integration)"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# ETL App Integration

Runtime ETL pipeline modules live under `app/services/etl`.

MCP server wrappers live under `tools/etl` and must not be imported by normal FastAPI startup. Read-only ETL admin visibility is exposed through `/api/v2/admin/etl`.

The Content Factory stores provenance links to ETL source document/chunk metadata through `content_artifact_sources`.
