# EduBoost V2 Codemap Coverage Report

**Generated:** 2026-07-13

## Result

- Canonical codemaps: **20**
- Execution traces: **60**
- Source anchors: **240**
- Maintained files inventoried: **6218**
- Files with a primary owner: **100%**
- Unassigned files: **0**
- Duplicate primary assignments: **0**
- Legacy codemaps superseded: **27 plus the previous README**

## Inventory policy

The coverage manifest inventories text-based and executable repository artefacts under:

`app/`, `tools/`, `scripts/`, `tests/`, `alembic/`, `.github/workflows/`, `docker/`, `deployment/`, `k8s/`, `nginx/`, `supabase/`, and `docs/`, plus the canonical root configuration and contributor files.

Excluded transient or vendor directories include `.git`, `node_modules`, `.next`, `__pycache__`, virtual environments, and local test/tool caches. The old `docs/codemaps` files are excluded because this bundle intentionally supersedes them; the new canonical files and verifier are included.

## Ownership distribution

| Codemap | Files | Share |
|---|---:|---:|
| `00_application_bootstrap_and_request_lifecycle.md` | 66 | 1.1% |
| `01_frontend_nextjs_pwa_and_client_flows.md` | 255 | 4.1% |
| `02_api_routing_contracts_and_openapi.md` | 19 | 0.3% |
| `03_authentication_authorization_and_session_security.md` | 154 | 2.5% |
| `04_consent_popia_audit_and_data_subject_rights.md` | 312 | 5.0% |
| `05_learner_parent_onboarding_and_vertical_journeys.md` | 75 | 1.2% |
| `06_diagnostics_irt_item_bank_and_mastery.md` | 106 | 1.7% |
| `07_lessons_tutor_study_plans_practice_and_gamification.md` | 104 | 1.7% |
| `08_curriculum_caps_knowledge_graph_and_runtime_kg.md` | 301 | 4.8% |
| `09_content_factory_review_quality_and_promotion.md` | 82 | 1.3% |
| `10_persistence_repositories_models_migrations_and_transactions.md` | 49 | 0.8% |
| `11_async_jobs_arq_redis_and_scheduled_work.md` | 10 | 0.2% |
| `12_llm_gateway_ai_operations_and_safety.md` | 41 | 0.7% |
| `13_billing_commercial_launch_and_external_integrations.md` | 50 | 0.8% |
| `14_observability_health_sre_performance_and_cost.md` | 135 | 2.2% |
| `15_infrastructure_deployment_backup_and_disaster_recovery.md` | 100 | 1.6% |
| `16_etl_ingestion_semantic_retrieval_and_mcp_tools.md` | 29 | 0.5% |
| `17_testing_ci_coverage_security_and_quality_gates.md` | 1485 | 23.9% |
| `18_production_readiness_release_evidence_and_live_traffic.md` | 2109 | 33.9% |
| `19_documentation_adrs_repository_governance_and_maintenance.md` | 736 | 11.8% |

## Interpretation

Primary ownership does not imply that every file appears as a Location ID. Location IDs identify representative execution anchors; the manifest provides exhaustive ownership. Cross-cutting files can be cited by multiple maps while retaining a single primary owner.

Large ownership totals for production readiness and testing reflect the repository’s extensive verifier, evidence, workflow, and test surface. Runtime domain maps remain focused on the application paths that those controls exercise.

## Verification command

```bash
python scripts/maintenance/verify_codemaps.py --repo-root .
```
