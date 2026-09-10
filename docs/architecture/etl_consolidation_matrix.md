---
title: ETL Consolidation Matrix
status: active
owner: architecture
reviewers: [engineering, content-factory]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-03
review_interval_days: 60
evidence_command: make docs-housekeeping-check
code_anchors: [docs/architecture/etl_consolidation_matrix.md]
---

# ETL Consolidation Matrix (TSR-6.3)

## Objective
Consolidate ETL implementations (`etl_pipeline.py`, historical helpers, and staging loaders) into unified, versioned batch extraction and transformation services.

## Interface Mapping
| Legacy / Fragmented Component | Unified V2 Service | Status | Validation Gate |
|:---|:---|:---|:---|
| `app/modules/etl/legacy_loader.py` | `ContentCoverageService` / `ItemBankService` | Replaced / Wrapped | RG-3A |
| `scripts/seed_caps_items.py` | `alembic` baseline + `ContentSeedRun` | Consolidated | RG-3A |
| `app/modules/diagnostics/item_bank_pipeline.py` | `ItemBankService.from_session()` | Active Service | RG-3A |
| Direct DB ETL scripts | Async SQL repositories with explicit transactions | Enforced | RG-3B |
