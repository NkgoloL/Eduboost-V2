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
