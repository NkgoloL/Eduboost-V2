# Deep Application Audit - Implementation Reality Report

Generated: `2026-06-02T09:44:17Z`
Branch: `remediation/phase0-phase1`
Commit: `50227d1820b251be4513732b75e7d1ce390f0392`

## Executive Summary

This audit confirms that EduBoost V2 contains substantial real implementation, but it also carries migration-era scaffolds that can make tests and documentation look healthier than the production runtime actually is. The most important gaps are real LLM content generation, POPIA lifecycle prerequisites, backup/restore execution, ETL semantic retrieval, learner content fallback semantics, and frontend mock gating.

## Source Inventory

| Area | Tracked files |
|---|---:|
| `app/` | 478 |
| `app/frontend/` | 150 |
| `tests/` | 741 |
| `tests/unit/` | 580 |
| `docs/` | 1410 |
| `docs/release/` | 440 |
| `docs/security/` | 99 |
| `scripts/` | 639 |
| `.github/workflows/` | 37 |
| `audits/` | 90 |
| `data/` | 76 |

## Classification Register

| ID | Severity | Area | Classification | Proof | Required fix |
|---|---|---|---|---|---|
| DA-P0-001 | P0 | Content generation LLM provider | placeholder requiring production implementation | app/services/content_generation/providers/llm.py raises RuntimeError for all generation methods and declares itself a real provider placeholder. | Implement reviewed provider adapter using the existing JSON/LLM gateway contract, fail closed in production when no provider is configured, and add runtime tests proving provider selection and error behavior. |
| DA-P0-002 | P0 | POPIA data rights lifecycle | placeholder requiring production implementation | app/services/popia_service.py still hard-codes legal_hold=False and export_offered=False TODOs in erasure/compliance paths. | Add repository-backed legal hold and export-offered checks, wire them into erase/cancel flows, and cover allowed/blocked paths with tests. |
| DA-P0-003 | P0 | Backup and restore execution | test-only scaffold | scripts/run_database_backup.py and scripts/run_database_restore.py exit with "not implemented in this scaffold" outside dry-run use. | Implement guarded real backup/restore commands with explicit production safety prompts/env gates and integration-style tests using test databases. |
| DA-P1-004 | P1 | ETL semantic retrieval | placeholder requiring production implementation | app/services/etl/etl_pipeline_v2.py stores only the first embedding element and exposes semantic_search_stub. | Persist full vectors, implement cosine search where numpy is available, retain FTS fallback, and add fixture-backed retrieval tests. |
| DA-P1-005 | P1 | Learner production content reads | placeholder requiring production implementation | app/services/content_learner_read_service.py has TODO markers for legacy content fallback while default read mode includes legacy fallback. | Either implement repository-backed fallback or change default to production-only and document legacy fallback as unsupported. |
| DA-P1-006 | P1 | Frontend admin content factory | intentional deterministic/mock provider requiring production guard | app/frontend/src/app/admin/content-factory/page.tsx switches to ETLAdminDashboard when NEXT_PUBLIC_CONTENT_FACTORY_MOCK=true. | Add production environment guard and test that mock dashboard cannot render under production build semantics. |
| DA-P1-007 | P1 | Auth compatibility surface | compatibility shim | app/services/auth_service.py includes legacy synchronous token/session compatibility APIs and duplicated _compat_access_tokens assignment. | Remove duplication, document compatibility boundary, and add tests proving routers use canonical token paths. |
| DA-P2-008 | P2 | Docs generation and evidence churn | generated artifact hygiene gap | Root tracks docs_inventory.* and docs_generation/gap reports, while docs/ contains 440 release files, 99 security files, and many generated reports. | Move generated docs into docs/generated/documentation_intelligence, create domain READMEs, and archive superseded TODO/roadmap material with manifests. |
| DA-P2-009 | P2 | Root repository layout | spring-cleaning gap | Tracked root contains release batch scripts, generated inventories, old PR summaries, TODO/RoadMap variants, coverage output, and compatibility requirements. | Add root allowlist, move/redirect noncanonical root files, and enforce with a repo hygiene check. |

## Intentional Mocks And Shims

- Deterministic LLM/mock providers are acceptable only for tests, demos, local dry-runs, and contract validation. They must be impossible to select accidentally in production.
- Legacy auth/session compatibility APIs may remain while tests and old imports need them, but canonical routers must use repository-backed services and token configuration.
- Generated evidence scripts are useful, but their outputs must be separated from authoritative documentation and release claims.

## Phase 2 Fix Queue

- [P0] DA-P0-001 `Content generation LLM provider`: Implement reviewed provider adapter using the existing JSON/LLM gateway contract, fail closed in production when no provider is configured, and add runtime tests proving provider selection and error behavior.
- [P0] DA-P0-002 `POPIA data rights lifecycle`: Add repository-backed legal hold and export-offered checks, wire them into erase/cancel flows, and cover allowed/blocked paths with tests.
- [P0] DA-P0-003 `Backup and restore execution`: Implement guarded real backup/restore commands with explicit production safety prompts/env gates and integration-style tests using test databases.
- [P1] DA-P1-004 `ETL semantic retrieval`: Persist full vectors, implement cosine search where numpy is available, retain FTS fallback, and add fixture-backed retrieval tests.
- [P1] DA-P1-005 `Learner production content reads`: Either implement repository-backed fallback or change default to production-only and document legacy fallback as unsupported.
- [P1] DA-P1-006 `Frontend admin content factory`: Add production environment guard and test that mock dashboard cannot render under production build semantics.
- [P1] DA-P1-007 `Auth compatibility surface`: Remove duplication, document compatibility boundary, and add tests proving routers use canonical token paths.

## No False Closure Rule

A finding can only be marked fixed when a real runtime path is implemented or a production-safe fail-closed boundary is proven by tests. Static string checks and generated evidence files are not sufficient closure evidence.

## Phase 2 Remediation Update

- `DA-P0-003` fixed: backup/restore commands now have guarded real `pg_dump`, `pg_restore`, and `psql` execution paths while keeping dry-run as CI default.
- `DA-P1-005` fixed by boundary correction: learner content reads now default to `production_only`; unsupported legacy fallback is no longer the default promise.
- `DA-P1-006` fixed: frontend Content Factory mock dashboard is blocked when `NODE_ENV=production`.
- `DA-P1-007` partially fixed: duplicate legacy auth compatibility token store assignment removed; compatibility boundary remains documented as a shim.
- `DA-P0-001`, `DA-P0-002`, and `DA-P1-004` remain open for larger provider, POPIA prerequisite, and ETL vector implementation tranches.
