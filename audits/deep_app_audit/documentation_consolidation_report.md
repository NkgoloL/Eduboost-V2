# Deep Application Audit - Documentation Consolidation Report

Generated: `2026-06-02T09:44:17Z`
Branch: `remediation/phase0-phase1`
Commit: `50227d1820b251be4513732b75e7d1ce390f0392`

## Phase 1 Baseline State

- README/TODO/Roadmap-like tracked files found: `69`.
- `docs/release/` tracked files: `440`.
- `docs/security/` tracked files: `99`.
- Root generated documentation inventory files were tracked at the baseline: `docs_inventory.json`, `docs_inventory.md`, `docs_generation_plan.md`, `docs_gap_report.md`. Phase 4 removed the duplicate root copies and preserved canonical generated copies under `docs/generated/documentation_intelligence/`.

## Target Information Architecture

- Root `README.md`: concise product, setup, current status, and links to domain docs.
- `docs/README.md`: authoritative index and freshness/governance rules.
- Domain READMEs: backend, frontend, diagnostics, IRT, ETL, POPIA, security, testing, deployment.
- `docs/generated/`: generated inventories and reports only.
- `docs/archive/`: superseded historical docs with archive manifest.

## Duplicate/Conflict Risk Areas

- Root `TODO.md`, `Todo_Production_Grade.md`, `Todo_Test_Velocity_And_Coverage.md`, `RoadMap.md`, and `EDUBOOST_NEXT_BATCH_ALL_OUTSTANDING_TASKS.md` all describe active work from different dates.
- `audits/roadmaps/`, `docs/roadmap/`, `docs/release/`, and root roadmap files all contain roadmap language and can conflict.
- Generated docs inventory files exist both at root and under `docs/`, making freshness checks ambiguous.

## Consolidation Actions Status

- Root `TODO.md` is the live task index, with specialized trackers linked through `docs/roadmap/README.md`.
- Domain READMEs exist for backend, frontend, diagnostics, IRT, ETL, POPIA, security, testing, and deployment, and are linked from root and `docs/README.md`.
- Generated documentation intelligence artifacts live under `docs/generated/documentation_intelligence/`; duplicate root copies were removed in Phase 4.
- Superseded roadmap/TODO documents moved to `docs/archive/roadmaps-or-todos/` with an archive manifest and backlinks.

## Initial README/TODO/Roadmap Inventory

| Path | Proposed disposition |
|---|---|
| `OUTSTANDING_TODO_ITEMS.md.bak` | link, consolidate, or archive |
| `README.md` | keep authoritative |
| `RoadMap.md` | link, consolidate, or archive |
| `TODO.md` | keep authoritative |
| `Todo_Production_Grade.md` | link, consolidate, or archive |
| `Todo_Test_Velocity_And_Coverage.md` | link, consolidate, or archive |
| `audits/agents_tasks/AGENT_IMPLEMENTATION_TODO.md` | link, consolidate, or archive |
| `audits/agents_tasks/TODO.md` | link, consolidate, or archive |
| `audits/agents_tasks/TODO_Harmonic-Fusion.md` | link, consolidate, or archive |
| `audits/agents_tasks/eduboost_fourth_estate/README_INTEGRATION.md` | link, consolidate, or archive |
| `audits/roadmaps/Agentic_Execution_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/Backend_RoadMap.md` | link, consolidate, or archive |
| `audits/roadmaps/EduBoost_SA_Improvement_Roadmap.docx` | link, consolidate, or archive |
| `audits/roadmaps/Functional_Frontend_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/Functional_Implementation_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/LEAD_DEVELOPER_TECHNICAL_ROADMAP_2026-05-18.md` | link, consolidate, or archive |
| `audits/roadmaps/Production_Grade_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/Production_Roadmap_Issue_Tracker.md` | link, consolidate, or archive |
| `audits/roadmaps/Production_Roadmap_Phased_Checklist.md` | link, consolidate, or archive |
| `audits/roadmaps/System_Status_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/V2_Active_RoadMap.md` | link, consolidate, or archive |
| `audits/roadmaps/V2_Execution_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/V2_Outstanding_Task_Roadmap.md` | link, consolidate, or archive |
| `audits/roadmaps/V2_Outstanding_Task_Roadmap_update.md` | link, consolidate, or archive |
| `data/synthetic/README.md` | link, consolidate, or archive |
| `docs/README.md` | keep authoritative |
| `docs/adr/ADR-019-roadmap-after-production-readiness-baseline.md` | link, consolidate, or archive |
| `docs/adr/README.md` | link, consolidate, or archive |
| `docs/api/_build/html/.doctrees/notes/todo.doctree` | link, consolidate, or archive |
| `docs/api/_build/html/_sources/notes/todo.rst.txt` | link, consolidate, or archive |
| `docs/api/_build/html/notes/todo.html` | link, consolidate, or archive |
| `docs/api/build/html/.doctrees/notes/todo.doctree` | link, consolidate, or archive |
| `docs/api/build/html/_sources/notes/todo.rst.txt` | link, consolidate, or archive |
| `docs/api/build/html/notes/todo.html` | link, consolidate, or archive |
| `docs/api/source/notes/todo.rst` | link, consolidate, or archive |
| `docs/archive/LLM_Integration_Roadmap.md` | link, consolidate, or archive |
| `docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md` | link, consolidate, or archive |
| `docs/codemaps/README.md` | link, consolidate, or archive |
| `docs/operations/todo_implementation_plan.md` | link, consolidate, or archive |
| `docs/product/roadmap.md` | link, consolidate, or archive |
| `docs/production_readiness_roadmap.md` | link, consolidate, or archive |
| `docs/release/DB_BACKUP_RESTORE_ROLLBACK_DRILL_README.md` | link, consolidate, or archive |
| `docs/release/EduBoost_V2_North_Star_TODO.md` | link, consolidate, or archive |
| `docs/release/EduBoost_V2_North_Star_TODO_2026-05-22.md` | link, consolidate, or archive |
| `docs/release/EduBoost_V2_Post_Baseline_Remediation_Roadmap.md` | link, consolidate, or archive |
| `docs/roadmap/agent_roadmap_reconciliation.json` | link, consolidate, or archive |
| `docs/roadmap/agent_roadmap_reconciliation.md` | link, consolidate, or archive |
| `docs/roadmap/post_baseline_roadmap_architecture_contract.md` | link, consolidate, or archive |
| `docs/roadmap/post_baseline_roadmap_register.md` | link, consolidate, or archive |
| `docs/roadmap/roadmap_dependency_register.md` | link, consolidate, or archive |
| `docs/roadmap/roadmap_graduation_criteria.md` | link, consolidate, or archive |
| `docs/roadmap/roadmap_review_cadence_contract.md` | link, consolidate, or archive |
| `docs/testing/README.md` | keep authoritative |
| `docs/todos/todo.md` | link, consolidate, or archive |
| `k8s/README.md` | link, consolidate, or archive |
| `phases/README.md` | link, consolidate, or archive |
| `scripts/archive/LEGACY_README.txt` | link, consolidate, or archive |
| `scripts/check_domain_19_roadmap_after_baseline_evidence.py` | link, consolidate, or archive |
| `scripts/check_roadmap_after_production_readiness_baseline.py` | link, consolidate, or archive |
| `scripts/check_todo_implementation_plan.py` | link, consolidate, or archive |
| `scripts/maintenance/audit_todo_backlog.py` | link, consolidate, or archive |
| `scripts/patch_readme_ci_badge.py` | link, consolidate, or archive |
| `scripts/reconcile_agent_roadmap.py` | link, consolidate, or archive |
| `staging/pr_008/TODO.md` | link, consolidate, or archive |
| `staging/pr_009/TODO.md` | link, consolidate, or archive |
| `tests/legacy/README.md` | link, consolidate, or archive |
| `tests/unit/test_roadmap_after_production_readiness_baseline.py` | link, consolidate, or archive |
| `tests/unit/test_roadmap_production_hardening.py` | link, consolidate, or archive |
| `tests/unit/test_todo_implementation_plan.py` | link, consolidate, or archive |

## Phase 3 Consolidation Update

- Added authoritative domain READMEs for backend, frontend, diagnostics, IRT, ETL, POPIA, security, deployment, and roadmap.
- Rewrote `docs/README.md` as the current domain index and documentation governance entry point.
- Added an authoritative documentation map to root `README.md`.
- Added roadmap authority guidance to root `TODO.md`, keeping it as the live tracker while specialized trackers remain linked until spring cleaning.


## Phase 4 Documentation Movement Update

Spring cleaning moved supporting roadmap details out of the repository root:

- `Todo_Production_Grade.md` -> `docs/roadmap/production_grade.md`
- `Todo_Test_Velocity_And_Coverage.md` -> `docs/roadmap/test_velocity_and_coverage.md`
- `RoadMap.md` and older batch/TODO backups -> `docs/archive/roadmaps-or-todos/`

`TODO.md` remains the live execution tracker. `docs/roadmap/README.md` is the roadmap index and links to specialized supporting trackers. Generated documentation intelligence artifacts now live under `docs/generated/documentation_intelligence/`.
