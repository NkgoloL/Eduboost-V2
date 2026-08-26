# EduBoost V2 Canonical Codemaps

**Generated:** 2026-07-13
**Canonical codemaps:** 20
**Execution traces:** 60
**Source anchors:** 240
**Maintained files assigned to a primary codemap:** 6218

This directory is the canonical application-wide codemap suite for EduBoost V2. It replaces the earlier overlapping set with domain-owned maps, repository-relative source references, a complete source-coverage manifest, and a verifier.

## How to use the suite

1. Start with `00_application_bootstrap_and_request_lifecycle.md` for backend composition or `01_frontend_nextjs_pwa_and_client_flows.md` for browser flows.
2. Open the codemap that owns the subsystem being changed.
3. Follow the trace from entry point to service, persistence, evidence, and verification.
4. Use each `Location ID` to navigate to the implementation.
5. Check `codemap_coverage_manifest.json` to identify the primary owner of any maintained file.
6. Run `python scripts/maintenance/verify_codemaps.py --repo-root .` after moving files or changing architecture.

## Canonical index

| # | Codemap | Primary responsibility | Assigned files |
|---:|---|---|---:|
| 00 | [`00_application_bootstrap_and_request_lifecycle.md`](00_application_bootstrap_and_request_lifecycle.md) | Maps process startup, FastAPI composition, request middleware, response envelopes, readiness checks, and graceful shutdown for the canonical V2 backend. | 66 |
| 01 | [`01_frontend_nextjs_pwa_and_client_flows.md`](01_frontend_nextjs_pwa_and_client_flows.md) | Maps App Router composition, authentication guards, API access, offline/PWA behaviour, and the learner, parent, and administrator user journeys. | 255 |
| 02 | [`02_api_routing_contracts_and_openapi.md`](02_api_routing_contracts_and_openapi.md) | Maps router discovery, dependency injection, canonical envelopes, error semantics, OpenAPI generation, and contract drift controls. | 19 |
| 03 | [`03_authentication_authorization_and_session_security.md`](03_authentication_authorization_and_session_security.md) | Maps registration, login, refresh rotation, key management, revocation, RBAC, and object-level authorization. | 154 |
| 04 | [`04_consent_popia_audit_and_data_subject_rights.md`](04_consent_popia_audit_and_data_subject_rights.md) | Maps versioned consent, request-time enforcement, audit evidence, export, correction, objection, erasure, and privacy operations. | 312 |
| 05 | [`05_learner_parent_onboarding_and_vertical_journeys.md`](05_learner_parent_onboarding_and_vertical_journeys.md) | Maps account onboarding, learner/guardian relationships, vertical journey orchestration, progress, parent reporting, and trustworthy beta experience. | 75 |
| 06 | [`06_diagnostics_irt_item_bank_and_mastery.md`](06_diagnostics_irt_item_bank_and_mastery.md) | Maps diagnostic session lifecycle, adaptive item selection, transactional responses, IRT scoring, item calibration, quality controls, and mastery projection. | 106 |
| 07 | [`07_lessons_tutor_study_plans_practice_and_gamification.md`](07_lessons_tutor_study_plans_practice_and_gamification.md) | Maps lesson generation and validation, tutor orchestration, runtime-KG study plans, practice scheduling, completion, progress, and rewards. | 104 |
| 08 | [`08_curriculum_caps_knowledge_graph_and_runtime_kg.md`](08_curriculum_caps_knowledge_graph_and_runtime_kg.md) | Maps authoritative CAPS acquisition, extraction, graph construction, target and learner graphs, gap planning, grounded generation, persistence, and route projections. | 301 |
| 09 | [`09_content_factory_review_quality_and_promotion.md`](09_content_factory_review_quality_and_promotion.md) | Maps generation planning, deterministic and LLM providers, provenance, review queues, quality scoring, staging, seeding, and production promotion. | 82 |
| 10 | [`10_persistence_repositories_models_migrations_and_transactions.md`](10_persistence_repositories_models_migrations_and_transactions.md) | Maps async database lifecycle, repository abstractions, ORM domains, transactional service patterns, Alembic migrations, Supabase artefacts, and resilience controls. | 49 |
| 11 | [`11_async_jobs_arq_redis_and_scheduled_work.md`](11_async_jobs_arq_redis_and_scheduled_work.md) | Maps job enqueueing, typed payloads, worker startup, dependency construction, retries, schedules, cleanup, and job integrity. | 10 |
| 12 | [`12_llm_gateway_ai_operations_and_safety.md`](12_llm_gateway_ai_operations_and_safety.md) | Maps provider routing, JSON contracts, prompt governance, quotas, safety filters, tutor controls, evaluation, and operational AI evidence. | 41 |
| 13 | [`13_billing_commercial_launch_and_external_integrations.md`](13_billing_commercial_launch_and_external_integrations.md) | Maps product plans, subscriptions, Stripe checkout and webhooks, idempotency, entitlements, email notifications, and commercial launch readiness. | 50 |
| 14 | [`14_observability_health_sre_performance_and_cost.md`](14_observability_health_sre_performance_and_cost.md) | Maps structured logs, metrics, tracing context, health and readiness, alerts, incident evidence, performance budgets, scale controls, and cost assurance. | 135 |
| 15 | [`15_infrastructure_deployment_backup_and_disaster_recovery.md`](15_infrastructure_deployment_backup_and_disaster_recovery.md) | Maps container images, Compose topology, reverse proxying, Kubernetes deployment, secrets, readiness, backups, restore drills, and operational recovery. | 100 |
| 16 | [`16_etl_ingestion_semantic_retrieval_and_mcp_tools.md`](16_etl_ingestion_semantic_retrieval_and_mcp_tools.md) | Maps ETL pipeline versions, document processing, MCP server startup and tools, semantic indexing and retrieval, curriculum extraction, and administrator controls. | 29 |
| 17 | [`17_testing_ci_coverage_security_and_quality_gates.md`](17_testing_ci_coverage_security_and_quality_gates.md) | Maps backend and frontend test taxonomies, fixtures, E2E flows, coverage execution, static analysis, dependency and secret scans, required checks, and failure triage. | 1485 |
| 18 | [`18_production_readiness_release_evidence_and_live_traffic.md`](18_production_readiness_release_evidence_and_live_traffic.md) | Maps PRD authority, implementation and evidence slices, CI convergence, controlled beta, production release, runtime restoration, go/no-go, and live-traffic controls. | 2109 |
| 19 | [`19_documentation_adrs_repository_governance_and_maintenance.md`](19_documentation_adrs_repository_governance_and_maintenance.md) | Maps architecture authority, ADR lifecycle, documentation indexes, codemap governance, generated artefacts, housekeeping, repository hygiene, and contributor workflows. | 736 |

## Coverage artefacts

- [`codemap_coverage_manifest.json`](codemap_coverage_manifest.json) — machine-readable primary ownership for every maintained application, test, workflow, infrastructure, and selected documentation file.
- [`CODEMAP_COVERAGE_REPORT.md`](CODEMAP_COVERAGE_REPORT.md) — human-readable coverage totals, inventory policy, and ownership distribution.
- [`SUPERSESSION_MAP.md`](SUPERSESSION_MAP.md) — mapping from the prior 27 codemap files to their canonical successors.

## Required trace structure

Every codemap trace contains:

1. `Trace ID`, title, description, and motivation.
2. Adaptive details covering the actual execution path, state boundaries, controls, and verification.
3. A text flow diagram.
4. Repository-relative `Location ID` references in `Path:LineNumber` form.
5. An AI Guide explaining how to reason about, change, and verify the traced flow.

### Source-reference policy

- References are **repository-relative**. Absolute workstation paths are prohibited.
- Line numbers must exist in the referenced file at verification time.
- A codemap is a navigation and reasoning aid; source code, tests, ADRs, and current release evidence remain authoritative.
- When code moves, update the codemap in the same pull request.

## Ownership model

Each maintained file has exactly one primary codemap owner. Cross-cutting references are allowed, but ownership is not duplicated. The primary owner is responsible for:

- explaining the file's architectural role;
- maintaining at least one representative execution trace for the subsystem;
- updating references after structural changes;
- identifying related tests, security/privacy controls, and release evidence.

## Update protocol

1. Modify the implementation and its tests.
2. Update the owning codemap and any genuinely affected adjacent codemap.
3. Regenerate or edit the coverage manifest when files are added, moved, or removed.
4. Run the codemap verifier.
5. Update an ADR when responsibility or a durable architecture decision changes.
6. Keep historical codemaps in the generated archive created by the apply script; do not mix them back into the canonical directory.

## Verification

```bash
python scripts/maintenance/verify_codemaps.py --repo-root .
```

The verifier checks canonical file presence, required trace sections, repository-relative source paths, line bounds, manifest ownership, duplicate assignments, and zero unassigned maintained files.
