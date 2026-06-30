# Deep Application Audit - Repository Spring Cleaning Report

Generated: `2026-06-02T09:44:17Z`
Branch: `remediation/phase0-phase1`
Phase 4 update: `2026-06-02`

## Root Layout Findings

The Phase 1 audit found that the repository root mixed canonical project entrypoints with generated documentation inventories, historical release scripts, old roadmap/TODO files, PR summaries, and temporary audit artifacts.

Phase 4 moved those files into intentional locations while preserving historical evidence. Duplicate root documentation-inventory outputs were removed because canonical generated copies already exist under `docs/generated/documentation_intelligence/`. `prometheus.yml` remains at root because it is actively mounted by `docker-compose.yml` and validated by observability scripts. `Makefile.arch` remains at root because the root `Makefile` includes it directly.

## Root Allowlist

The hygiene gate now treats root as limited to:

- project essentials such as `README.md`, `TODO.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `Makefile`
- active package/config files such as `package.json`, `requirements*.txt`, `pytest*.ini`, `.coveragerc`, compose files, `alembic.ini`, `mkdocs.yml`, `playwright.config.ts`, `render.yaml`, and `prometheus.yml`
- active hidden project configuration such as `.gitignore`, `.dockerignore`, `.pre-commit-config.yaml`, `.secrets.baseline`, and env examples

The executable check lives at `scripts/maintenance/check_repo_hygiene.py` and is exposed by `make repo-hygiene-check`.

## Files Moved, Archived, Or Removed

| Source | Destination | Reason |
|---|---|---|
| `docs_gap_report.md` | removed duplicate root copy; canonical location is `docs/generated/documentation_intelligence/docs_gap_report.md` | generated documentation intelligence artifact |
| `docs_generation_plan.md` | removed duplicate root copy; canonical location is `docs/generated/documentation_intelligence/docs_generation_plan.md` | generated documentation intelligence artifact |
| `docs_inventory.json` | removed duplicate root copy; canonical location is `docs/generated/documentation_intelligence/docs_inventory.json` | generated documentation intelligence artifact |
| `docs_inventory.md` | removed duplicate root copy; canonical location is `docs/generated/documentation_intelligence/docs_inventory.md` | generated documentation intelligence artifact |
| `Todo_Production_Grade.md` | `docs/roadmap/production_grade.md` | supporting roadmap detail, no longer a root TODO |
| `Todo_Test_Velocity_And_Coverage.md` | `docs/roadmap/test_velocity_and_coverage.md` | supporting roadmap detail, no longer a root TODO |
| `RoadMap.md` | `docs/archive/roadmaps-or-todos/RoadMap.md` | superseded historical roadmap |
| `EDUBOOST_NEXT_BATCH_ALL_OUTSTANDING_TASKS.md` | `docs/archive/roadmaps-or-todos/EDUBOOST_NEXT_BATCH_ALL_OUTSTANDING_TASKS.md` | historical batch-planning tracker |
| `OUTSTANDING_TODO_ITEMS.md.bak` | `docs/archive/roadmaps-or-todos/OUTSTANDING_TODO_ITEMS.md.bak` | backup/superseded TODO artifact |
| `PR_INTEGRATION_SUMMARY.md` | `audits/reports/PR_INTEGRATION_SUMMARY.md` | historical PR/audit report |
| `deployment_data.md` | `audits/reports/deployment_data.md` | historical deployment report |
| `db_rollback_test.sql` | `audits/archive/db_rollback_test.sql` | historical rollback-test artifact |
| `task_matrix.csv` | `audits/archive/task_matrix.csv` | historical task matrix export |
| release/helper shell scripts | `scripts/archive/` | historical release/environment helpers |

## Archive Manifests

- `docs/archive/roadmaps-or-todos/MANIFEST.md`
- `docs/generated/documentation_intelligence/README.md`
- `scripts/archive/MANIFEST.md`
- `audits/archive/MANIFEST.md`

## Hygiene Controls Added

- Root clutter check for tracked root files outside the allowlist.
- Generated documentation location check for `docs_inventory*`, `docs_generation_plan.md`, and `docs_gap_report.md`.
- Tracked generated-noise check for coverage, cache, virtualenv, node_modules, and build artifacts.
- Unit coverage for the hygiene checker in `tests/unit/test_repo_hygiene.py`.

## Remaining Notes

Historical generated documents are preserved in generated-docs space where canonical copies exist. Future generated inventories should be written under `docs/generated/`, not the repository root.
