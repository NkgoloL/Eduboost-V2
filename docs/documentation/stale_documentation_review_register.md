---
title: Stale Documentation Review Register
status: active
owner: architecture_governance
reviewers: [tech_lead, devops_lead]
audience: [maintainers, auditors]
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-22'
review_interval_days: 14
evidence_command: "make docs-housekeeping-check"
code_anchors: "[docs/documentation/stale_documentation_review_register.md]"
---

# Stale Documentation Review Register

> [!IMPORTANT]
> **Anti-Theatre Governance Rule: No Blanket Date Resets**
> Batch-updating `last_reviewed` dates in YAML front matter without active code inspection and content rewrite is strictly prohibited. Stale documents cataloged here retain their true `last_reviewed` date and `days_stale` counter until substantively audited and verified against active code.

**Baseline Audit Date**: 2026-09-22  
**Total Review-Expired Documents**: 489  

## Stale Documents Summary by Domain

| Domain / Remediation Tier | Overdue Count | Max Days Stale | Target Phase |
|---|---|---|---|
| Domain 1: Core Architecture & System Blueprints | 18 | 31 days | Phase 3 |
| Domain 2: Frontend & Client Architecture | 70 | 31 days | Phase 3 |
| Domain 3: API & Route Inventory | 8 | 61 days | Phase 3 |
| Domain 4: Research, Psychometrics & LEV | 15 | 30 days | Phase 3 |
| Domain 5: Database & Migration Architecture | 12 | 30 days | Phase 3 |
| Domain 6: Release, Operations & Production Readiness | 41 | 68 days | Phase 3 |
| General Documentation | 297 | 68 days | Phase 4 |
| Testing & Quality Verification | 28 | 69 days | Phase 4 |

---

## Domain 1: Core Architecture & System Blueprints (18 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/architecture/ARCHITECTURE.md`](../../docs/architecture/ARCHITECTURE.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/CORE_TECHNICAL_AUDIT_2026-05-17.md`](../../docs/architecture/CORE_TECHNICAL_AUDIT_2026-05-17.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `current-evidence` |
| [`docs/architecture/architecture_decisions.md`](../../docs/architecture/architecture_decisions.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/architecture_diagram.md`](../../docs/architecture/architecture_diagram.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/auth_lifecycle_extraction_report.md`](../../docs/architecture/auth_lifecycle_extraction_report.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `current-evidence` |
| [`docs/architecture/auth_service_ownership_report.md`](../../docs/architecture/auth_service_ownership_report.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `current-evidence` |
| [`docs/architecture/boundary_debt_queue.md`](../../docs/architecture/boundary_debt_queue.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/boundary_enforcement_policy.md`](../../docs/architecture/boundary_enforcement_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/import_boundaries.md`](../../docs/architecture/import_boundaries.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/metaphor_glossary.md`](../../docs/architecture/metaphor_glossary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/router_repository_boundary_inventory.md`](../../docs/architecture/router_repository_boundary_inventory.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `current-evidence` |
| [`docs/architecture/service_boundary_classification_policy.md`](../../docs/architecture/service_boundary_classification_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `architecture` | `active` |
| [`docs/architecture/legacy_learner_access_guard_report.md`](../../docs/architecture/legacy_learner_access_guard_report.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `architecture` | `current-evidence` |
| [`docs/adr/ADR-036-knowledge-graph-learning-state-core.md`](../../docs/adr/ADR-036-knowledge-graph-learning-state-core.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `architecture` | `active` |
| [`docs/architecture/knowledge_graph_data_model.md`](../../docs/architecture/knowledge_graph_data_model.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `architecture` | `active` |
| [`docs/architecture/knowledge_graph_learning_state_architecture.md`](../../docs/architecture/knowledge_graph_learning_state_architecture.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `architecture` | `active` |
| [`docs/architecture/knowledge_graph_transition_plan.md`](../../docs/architecture/knowledge_graph_transition_plan.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `architecture` | `active` |
| [`docs/architecture/README.md`](../../docs/architecture/README.md) | 2026-07-07 | 60d | 2026-09-05 | **+17d** | `architecture` | `active` |

## Domain 2: Frontend & Client Architecture (70 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/security/frontend_token_storage_audit.md`](../../docs/security/frontend_token_storage_audit.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/frontend/CLUSTER_G_CLOSURE.md`](../../docs/frontend/CLUSTER_G_CLOSURE.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-002-handover.md`](../../docs/frontend/FE-PR-002-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-003-handover.md`](../../docs/frontend/FE-PR-003-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-004-handover.md`](../../docs/frontend/FE-PR-004-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-005-handover.md`](../../docs/frontend/FE-PR-005-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-006-handover.md`](../../docs/frontend/FE-PR-006-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-007-handover.md`](../../docs/frontend/FE-PR-007-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-008-audit.md`](../../docs/frontend/FE-PR-008-audit.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-008-handover.md`](../../docs/frontend/FE-PR-008-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-010-handover.md`](../../docs/frontend/FE-PR-010-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-011-handover.md`](../../docs/frontend/FE-PR-011-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-012-accessibility-evidence.md`](../../docs/frontend/FE-PR-012-accessibility-evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-012-handover.md`](../../docs/frontend/FE-PR-012-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-A-handover.md`](../../docs/frontend/FE-PR-013-A-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-B-handover.md`](../../docs/frontend/FE-PR-013-B-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-B-retention-evidence.md`](../../docs/frontend/FE-PR-013-B-retention-evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-C-handover.md`](../../docs/frontend/FE-PR-013-C-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-D-handover.md`](../../docs/frontend/FE-PR-013-D-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-D-voice-consent-evidence.md`](../../docs/frontend/FE-PR-013-D-voice-consent-evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-E-implementation-handover.md`](../../docs/frontend/FE-PR-013-E-implementation-handover.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-PR-013-E-whatsapp-sharing-boundary.md`](../../docs/frontend/FE-PR-013-E-whatsapp-sharing-boundary.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/FE-PR-013-implementation-plan.md`](../../docs/frontend/FE-PR-013-implementation-plan.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/FE-PR-013-parent-review-retention.md`](../../docs/frontend/FE-PR-013-parent-review-retention.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/FE-PR-013-safety-and-compliance-boundary.md`](../../docs/frontend/FE-PR-013-safety-and-compliance-boundary.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/FE-PWA-MANIFEST-ICON-001-validation.md`](../../docs/frontend/FE-PWA-MANIFEST-ICON-001-validation.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/FE-SPIKE-004-web-speech.md`](../../docs/frontend/FE-SPIKE-004-web-speech.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/FE-SPIKE-005-ai-tutor.md`](../../docs/frontend/FE-SPIKE-005-ai-tutor.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/FE-SPIKE-006-service-worker-spike.md`](../../docs/frontend/FE-SPIKE-006-service-worker-spike.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/RC5-release-evidence.md`](../../docs/frontend/RC5-release-evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/README.md`](../../docs/frontend/README.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/accessibility_pwa_e2e_evidence.md`](../../docs/frontend/accessibility_pwa_e2e_evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/frontend_accessibility_contract.md`](../../docs/frontend/frontend_accessibility_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_accessibility_static_scan.md`](../../docs/frontend/frontend_accessibility_static_scan.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_api_client_inventory.md`](../../docs/frontend/frontend_api_client_inventory.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/frontend_auth_consent_denial_contract.md`](../../docs/frontend/frontend_auth_consent_denial_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_build_test_lint_contract.md`](../../docs/frontend/frontend_build_test_lint_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_e2e_environment_contract.md`](../../docs/frontend/frontend_e2e_environment_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_e2e_opt_in_workflow.md`](../../docs/frontend/frontend_e2e_opt_in_workflow.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_e2e_runtime_commands.md`](../../docs/frontend/frontend_e2e_runtime_commands.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/frontend_evidence_index.md`](../../docs/frontend/frontend_evidence_index.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/frontend_journey_evidence.md`](../../docs/frontend/frontend_journey_evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/frontend_route_inventory.md`](../../docs/frontend/frontend_route_inventory.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/frontend_runtime_inventory.md`](../../docs/frontend/frontend_runtime_inventory.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/frontend_verification_evidence_2026-05-11.md`](../../docs/frontend/frontend_verification_evidence_2026-05-11.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/learner_vertical_journey_contract.md`](../../docs/frontend/learner_vertical_journey_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/parent_vertical_journey_contract.md`](../../docs/frontend/parent_vertical_journey_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/playwright_e2e_scaffold.md`](../../docs/frontend/playwright_e2e_scaffold.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/playwright_journey_fixture_contract.md`](../../docs/frontend/playwright_journey_fixture_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/playwright_mock_api_fixtures.md`](../../docs/frontend/playwright_mock_api_fixtures.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/playwright_mock_route_helpers.md`](../../docs/frontend/playwright_mock_route_helpers.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/playwright_mocked_journey_specs.md`](../../docs/frontend/playwright_mocked_journey_specs.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/playwright_vertical_journey_specs.md`](../../docs/frontend/playwright_vertical_journey_specs.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/post-rc5-dependency-maintenance.md`](../../docs/frontend/post-rc5-dependency-maintenance.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/pr_checklist_FE-PR-001-013.md`](../../docs/frontend/pr_checklist_FE-PR-001-013.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/production_auth_onboarding_ux_contract.md`](../../docs/frontend/production_auth_onboarding_ux_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_frontend_api_client_contract.md`](../../docs/frontend/production_frontend_api_client_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_frontend_env_security_contract.md`](../../docs/frontend/production_frontend_env_security_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_frontend_pwa_low_data_contract.md`](../../docs/frontend/production_frontend_pwa_low_data_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_frontend_ux_accessibility_mobile_contract.md`](../../docs/frontend/production_frontend_ux_accessibility_mobile_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_learner_parent_ux_contract.md`](../../docs/frontend/production_learner_parent_ux_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_parent_privacy_controls_contract.md`](../../docs/frontend/production_parent_privacy_controls_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_protected_route_guard_contract.md`](../../docs/frontend/production_protected_route_guard_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/production_teacher_admin_scope_contract.md`](../../docs/frontend/production_teacher_admin_scope_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/frontend/spike_report_template.md`](../../docs/frontend/spike_report_template.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `current-evidence` |
| [`docs/frontend/task_metadata_template.md`](../../docs/frontend/task_metadata_template.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `frontend` | `active` |
| [`docs/testing/coverage_frontend_advisory_gate_contract.md`](../../docs/testing/coverage_frontend_advisory_gate_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/generated_contract_frontend_quality_execution.md`](../../docs/testing/generated_contract_frontend_quality_execution.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/generated_contract_frontend_quality_green_evidence.md`](../../docs/testing/generated_contract_frontend_quality_green_evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/generated_contract_frontend_quality_green_run.md`](../../docs/testing/generated_contract_frontend_quality_green_run.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |

## Domain 3: API & Route Inventory (8 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/api/README.md`](../../docs/api/README.md) | 2026-06-23 | 30d | 2026-07-23 | **+61d** | `backend` | `active` |
| [`docs/security/active_consent_route_order.md`](../../docs/security/active_consent_route_order.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/active_consent_route_sources.md`](../../docs/security/active_consent_route_sources.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_route_authorization_inspection.md`](../../docs/security/learner_route_authorization_inspection.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_route_authorization_wiring.md`](../../docs/security/learner_route_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/parent_routes_consent_gate.md`](../../docs/security/parent_routes_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/phase2_router_import_smoke.md`](../../docs/security/phase2_router_import_smoke.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/route_policy_matrix.md`](../../docs/security/route_policy_matrix.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |

## Domain 4: Research, Psychometrics & LEV (15 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/learning_science/irt_model.md`](../../docs/learning_science/irt_model.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `learning-science` | `active` |
| [`docs/learning_science/learning_evidence.md`](../../docs/learning_science/learning_evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `learning-science` | `current-evidence` |
| [`docs/learning_science/mastery_model.md`](../../docs/learning_science/mastery_model.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `learning-science` | `active` |
| [`docs/research/mastery_model/rr013_candidate_model_comparison.md`](../../docs/research/mastery_model/rr013_candidate_model_comparison.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_candidate_model_comparison.template.md`](../../docs/research/mastery_model/rr013_candidate_model_comparison.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_data_readiness_and_ethics_review.md`](../../docs/research/mastery_model/rr013_data_readiness_and_ethics_review.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_data_readiness_and_ethics_review.template.md`](../../docs/research/mastery_model/rr013_data_readiness_and_ethics_review.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_evaluation_protocol.md`](../../docs/research/mastery_model/rr013_evaluation_protocol.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_evaluation_protocol.template.md`](../../docs/research/mastery_model/rr013_evaluation_protocol.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_literature_review.template.md`](../../docs/research/mastery_model/rr013_literature_review.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_mastery_model_literature_review.md`](../../docs/research/mastery_model/rr013_mastery_model_literature_review.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_mastery_model_research_agenda.md`](../../docs/research/mastery_model/rr013_mastery_model_research_agenda.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_mastery_model_research_policy.md`](../../docs/research/mastery_model/rr013_mastery_model_research_policy.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_research_decision_memo.md`](../../docs/research/mastery_model/rr013_research_decision_memo.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/research/mastery_model/rr013_research_decision_memo.template.md`](../../docs/research/mastery_model/rr013_research_decision_memo.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |

## Domain 5: Database & Migration Architecture (12 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/ai/ai_output_schema_contract.md`](../../docs/ai/ai_output_schema_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/database/db_repository_evidence.md`](../../docs/database/db_repository_evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `current-evidence` |
| [`docs/database/migration_audit.md`](../../docs/database/migration_audit.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `current-evidence` |
| [`docs/database/migration_discipline.md`](../../docs/database/migration_discipline.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `active` |
| [`docs/database/migration_release_discipline_contract.md`](../../docs/database/migration_release_discipline_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `active` |
| [`docs/database/repository_transaction_performance_contract.md`](../../docs/database/repository_transaction_performance_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `active` |
| [`docs/database/schema_integrity.md`](../../docs/database/schema_integrity.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `active` |
| [`docs/database/schema_readiness_contract.md`](../../docs/database/schema_readiness_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `database` | `active` |
| [`docs/release_safety/rr017_migration_window_control.template.md`](../../docs/release_safety/rr017_migration_window_control.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/knowledge_graph/caps_graph/kg001_caps_graph_schema.md`](../../docs/knowledge_graph/caps_graph/kg001_caps_graph_schema.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/knowledge_graph/target_graph/kg002_target_graph_schema.md`](../../docs/knowledge_graph/target_graph/kg002_target_graph_schema.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/release_safety/rr017_migration_window_control.md`](../../docs/release_safety/rr017_migration_window_control.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `release-engineering` | `active` |

## Domain 6: Release, Operations & Production Readiness (41 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/release/current/README.md`](../../docs/release/current/README.md) | 2026-07-02 | 14d | 2026-07-16 | **+68d** | `release-management` | `active` |
| [`docs/release/current/branch_protection_evidence.md`](../../docs/release/current/branch_protection_evidence.md) | 2026-07-02 | 14d | 2026-07-16 | **+68d** | `release-management` | `active` |
| [`docs/operations/README.md`](../../docs/operations/README.md) | 2026-06-22 | 60d | 2026-08-21 | **+32d** | `operations` | `active` |
| [`docs/deployment/README.md`](../../docs/deployment/README.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/deployment/artifact_provenance_and_release_contract.md`](../../docs/deployment/artifact_provenance_and_release_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/deployment/ci_pipeline_contract.md`](../../docs/deployment/ci_pipeline_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/deployment/deployment_gate_and_rollback_contract.md`](../../docs/deployment/deployment_gate_and_rollback_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/deployment/docker_runtime_hardening_contract.md`](../../docs/deployment/docker_runtime_hardening_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/deployment/environment_configuration_contract.md`](../../docs/deployment/environment_configuration_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/deployment/production_deployment_architecture_contract.md`](../../docs/deployment/production_deployment_architecture_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `release-management` | `active` |
| [`docs/operations_support/incident_classification_matrix.md`](../../docs/operations_support/incident_classification_matrix.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/incident_response_operations_support_architecture_contract.md`](../../docs/operations_support/incident_response_operations_support_architecture_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/incidents/INC-001.md`](../../docs/operations_support/incidents/INC-001.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/on_call_escalation_policy.md`](../../docs/operations_support/on_call_escalation_policy.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/operations_support/post_incident_review_contract.md`](../../docs/operations_support/post_incident_review_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/post_incident_reviews/PIR-001.md`](../../docs/operations_support/post_incident_reviews/PIR-001.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/production_operations_handover_checklist.md`](../../docs/operations_support/production_operations_handover_checklist.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/runbooks/api_outage.md`](../../docs/operations_support/runbooks/api_outage.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/operations_support/runbooks/privacy_incident.md`](../../docs/operations_support/runbooks/privacy_incident.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/status_communication_contract.md`](../../docs/operations_support/status_communication_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/operations_support/support_sla_policy.md`](../../docs/operations_support/support_sla_policy.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/operations/drills/rr016_backup_drill_report.md`](../../docs/operations/drills/rr016_backup_drill_report.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_backup_drill_report.template.md`](../../docs/operations/drills/rr016_backup_drill_report.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_incident_handoff_verification.md`](../../docs/operations/drills/rr016_incident_handoff_verification.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_incident_handoff_verification.template.md`](../../docs/operations/drills/rr016_incident_handoff_verification.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_monitoring_dashboard_verification.md`](../../docs/operations/drills/rr016_monitoring_dashboard_verification.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_monitoring_dashboard_verification.template.md`](../../docs/operations/drills/rr016_monitoring_dashboard_verification.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_operational_drills_policy.md`](../../docs/operations/drills/rr016_operational_drills_policy.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_restore_drill_report.md`](../../docs/operations/drills/rr016_restore_drill_report.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_restore_drill_report.template.md`](../../docs/operations/drills/rr016_restore_drill_report.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_rollback_drill_report.md`](../../docs/operations/drills/rr016_rollback_drill_report.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/operations/drills/rr016_rollback_drill_report.template.md`](../../docs/operations/drills/rr016_rollback_drill_report.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/release_safety/rr017_health_probe_immutability_validation.template.md`](../../docs/release_safety/rr017_health_probe_immutability_validation.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_prohibited_operations_register.template.md`](../../docs/release_safety/rr017_prohibited_operations_register.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_release_change_control_boundary.template.md`](../../docs/release_safety/rr017_release_change_control_boundary.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_release_safety_control_attestation.template.md`](../../docs/release_safety/rr017_release_safety_control_attestation.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_release_safety_controls_policy.md`](../../docs/release_safety/rr017_release_safety_controls_policy.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_health_probe_immutability_validation.md`](../../docs/release_safety/rr017_health_probe_immutability_validation.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_prohibited_operations_register.md`](../../docs/release_safety/rr017_prohibited_operations_register.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_release_change_control_boundary.md`](../../docs/release_safety/rr017_release_change_control_boundary.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `release-engineering` | `active` |
| [`docs/release_safety/rr017_release_safety_control_attestation.md`](../../docs/release_safety/rr017_release_safety_control_attestation.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `release-engineering` | `active` |

## General Documentation (297 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/governance/rr009_branch_protection_release_docs.md`](../../docs/governance/rr009_branch_protection_release_docs.md) | 2026-07-02 | 14d | 2026-07-16 | **+68d** | `release-management` | `active` |
| [`docs/governance/rr009_current_state_refresh_cadence.md`](../../docs/governance/rr009_current_state_refresh_cadence.md) | 2026-07-02 | 14d | 2026-07-16 | **+68d** | `release-management` | `active` |
| [`docs/governance/rr009_external_todo_ownership_register.md`](../../docs/governance/rr009_external_todo_ownership_register.md) | 2026-07-02 | 14d | 2026-07-16 | **+68d** | `governance` | `active` |
| [`docs/documentation/README.md`](../../docs/documentation/README.md) | 2026-06-22 | 30d | 2026-07-22 | **+62d** | `documentation-governance` | `active` |
| [`docs/documentation/claim_discipline_policy.md`](../../docs/documentation/claim_discipline_policy.md) | 2026-06-22 | 30d | 2026-07-22 | **+62d** | `documentation-governance` | `active` |
| [`docs/documentation/documentation_debt_baseline.md`](../../docs/documentation/documentation_debt_baseline.md) | 2026-06-22 | 30d | 2026-07-22 | **+62d** | `documentation-governance` | `active` |
| [`docs/documentation/documentation_housekeeping_policy.md`](../../docs/documentation/documentation_housekeeping_policy.md) | 2026-06-22 | 30d | 2026-07-22 | **+62d** | `documentation-governance` | `active` |
| [`docs/documentation/stage_2_documentation_housekeeping.md`](../../docs/documentation/stage_2_documentation_housekeeping.md) | 2026-06-22 | 30d | 2026-07-22 | **+62d** | `documentation-governance` | `active` |
| [`docs/documentation/stale_documentation_register.md`](../../docs/documentation/stale_documentation_register.md) | 2026-06-22 | 30d | 2026-07-22 | **+62d** | `documentation-governance` | `active` |
| [`docs/documentation/stage_3_documentation_housekeeping.md`](../../docs/documentation/stage_3_documentation_housekeeping.md) | 2026-06-23 | 30d | 2026-07-23 | **+61d** | `documentation-governance` | `active` |
| [`docs/documentation/stage_4_deep_housekeeping.md`](../../docs/documentation/stage_4_deep_housekeeping.md) | 2026-06-23 | 30d | 2026-07-23 | **+61d** | `documentation-governance` | `active` |
| [`docs/documentation/stage_5_technical_delivery_housekeeping.md`](../../docs/documentation/stage_5_technical_delivery_housekeeping.md) | 2026-06-24 | 30d | 2026-07-24 | **+60d** | `documentation-governance` | `active` |
| [`docs/beta_outcomes/rr010_beta_outcome_report.md`](../../docs/beta_outcomes/rr010_beta_outcome_report.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_beta_outcome_report.template.md`](../../docs/beta_outcomes/rr010_beta_outcome_report.template.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_beta_outcome_reporting_policy.md`](../../docs/beta_outcomes/rr010_beta_outcome_reporting_policy.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_educator_feedback_summary.md`](../../docs/beta_outcomes/rr010_educator_feedback_summary.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_educator_feedback_summary.template.md`](../../docs/beta_outcomes/rr010_educator_feedback_summary.template.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_incident_summary.md`](../../docs/beta_outcomes/rr010_incident_summary.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_incident_summary.template.md`](../../docs/beta_outcomes/rr010_incident_summary.template.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_weekly_health_reviews.md`](../../docs/beta_outcomes/rr010_weekly_health_reviews.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/beta_outcomes/rr010_weekly_health_reviews.template.md`](../../docs/beta_outcomes/rr010_weekly_health_reviews.template.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/governance/rr009_adr_index_completion.md`](../../docs/governance/rr009_adr_index_completion.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `architecture` | `active` |
| [`docs/governance/rr009_governance_process_policy.md`](../../docs/governance/rr009_governance_process_policy.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `governance` | `active` |
| [`docs/roadmap/reconciliation/rr_009_governance_process_reconciliation.md`](../../docs/roadmap/reconciliation/rr_009_governance_process_reconciliation.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `governance` | `active` |
| [`docs/roadmap/reconciliation/rr_010_beta_outcome_reporting.md`](../../docs/roadmap/reconciliation/rr_010_beta_outcome_reporting.md) | 2026-07-02 | 30d | 2026-08-01 | **+52d** | `product` | `active` |
| [`docs/billing/rr011_billing_launch_boundary.md`](../../docs/billing/rr011_billing_launch_boundary.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `governance` | `active` |
| [`docs/billing/rr011_billing_launch_boundary.template.md`](../../docs/billing/rr011_billing_launch_boundary.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `governance` | `template` |
| [`docs/billing/rr011_hosted_checkout_sandbox_validation.md`](../../docs/billing/rr011_hosted_checkout_sandbox_validation.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `active` |
| [`docs/billing/rr011_hosted_checkout_sandbox_validation.template.md`](../../docs/billing/rr011_hosted_checkout_sandbox_validation.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `template` |
| [`docs/billing/rr011_live_billing_provider_attestation.md`](../../docs/billing/rr011_live_billing_provider_attestation.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `active` |
| [`docs/billing/rr011_live_billing_provider_attestation.template.md`](../../docs/billing/rr011_live_billing_provider_attestation.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `template` |
| [`docs/billing/rr011_live_billing_provider_integration_policy.md`](../../docs/billing/rr011_live_billing_provider_integration_policy.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `active` |
| [`docs/billing/rr011_pricing_catalogue_approval.md`](../../docs/billing/rr011_pricing_catalogue_approval.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `active` |
| [`docs/billing/rr011_pricing_catalogue_approval.template.md`](../../docs/billing/rr011_pricing_catalogue_approval.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `template` |
| [`docs/billing/rr011_webhook_endpoint_validation.md`](../../docs/billing/rr011_webhook_endpoint_validation.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `engineering` | `active` |
| [`docs/billing/rr011_webhook_endpoint_validation.template.md`](../../docs/billing/rr011_webhook_endpoint_validation.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `engineering` | `template` |
| [`docs/roadmap/reconciliation/rr_011_live_billing_provider_integration.md`](../../docs/roadmap/reconciliation/rr_011_live_billing_provider_integration.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `product` | `active` |
| [`docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard.md`](../../docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `pending-evidence` |
| [`docs/telemetry/rr012_alert_routing_validation.md`](../../docs/telemetry/rr012_alert_routing_validation.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `active` |
| [`docs/telemetry/rr012_alert_routing_validation.template.md`](../../docs/telemetry/rr012_alert_routing_validation.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `pending-evidence` |
| [`docs/telemetry/rr012_dashboard_privacy_boundary.md`](../../docs/telemetry/rr012_dashboard_privacy_boundary.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `active` |
| [`docs/telemetry/rr012_dashboard_privacy_boundary.template.md`](../../docs/telemetry/rr012_dashboard_privacy_boundary.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `pending-evidence` |
| [`docs/telemetry/rr012_production_telemetry_dashboard_attestation.md`](../../docs/telemetry/rr012_production_telemetry_dashboard_attestation.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `active` |
| [`docs/telemetry/rr012_production_telemetry_dashboard_attestation.template.md`](../../docs/telemetry/rr012_production_telemetry_dashboard_attestation.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `pending-evidence` |
| [`docs/telemetry/rr012_production_telemetry_dashboard_policy.md`](../../docs/telemetry/rr012_production_telemetry_dashboard_policy.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `pending-evidence` |
| [`docs/telemetry/rr012_slo_dashboard_validation.md`](../../docs/telemetry/rr012_slo_dashboard_validation.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `active` |
| [`docs/telemetry/rr012_slo_dashboard_validation.template.md`](../../docs/telemetry/rr012_slo_dashboard_validation.template.md) | 2026-07-03 | 30d | 2026-08-02 | **+51d** | `operations` | `pending-evidence` |
| [`docs/README.md`](../../docs/README.md) | 2026-07-07 | 30d | 2026-08-06 | **+47d** | `documentation-governance` | `active` |
| [`docs/engineering/README.md`](../../docs/engineering/README.md) | 2026-06-22 | 45d | 2026-08-06 | **+47d** | `engineering` | `active` |
| [`docs/roadmap/production_readiness/prd_001_canonical_current_state_documentation_refresh.md`](../../docs/roadmap/production_readiness/prd_001_canonical_current_state_documentation_refresh.md) | 2026-07-07 | 30d | 2026-08-06 | **+47d** | `production-readiness` | `active` |
| [`docs/compliance/README.md`](../../docs/compliance/README.md) | 2026-06-23 | 45d | 2026-08-07 | **+46d** | `privacy` | `active` |
| [`docs/security/README.md`](../../docs/security/README.md) | 2026-06-23 | 45d | 2026-08-07 | **+46d** | `security` | `active` |
| [`docs/roadmap/README.md`](../../docs/roadmap/README.md) | 2026-07-16 | 30d | 2026-08-15 | **+38d** | `roadmap-governance` | `active` |
| [`docs/compliance/data_retention_policy.md`](../../docs/compliance/data_retention_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `privacy` | `active` |
| [`docs/compliance/popia_data_rights.md`](../../docs/compliance/popia_data_rights.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `privacy` | `active` |
| [`docs/compliance/pr_004_implementation_summary.md`](../../docs/compliance/pr_004_implementation_summary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `privacy` | `active` |
| [`docs/compliance/subprocessor_register.md`](../../docs/compliance/subprocessor_register.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `privacy` | `active` |
| [`docs/product/README.md`](../../docs/product/README.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/ai_transparency_faq.md`](../../docs/product/ai_transparency_faq.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/differentiation_strategy.md`](../../docs/product/differentiation_strategy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/faq.md`](../../docs/product/faq.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/launch_scope.md`](../../docs/product/launch_scope.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/learner_guide.md`](../../docs/product/learner_guide.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/parent_guide.md`](../../docs/product/parent_guide.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/pricing_faq.md`](../../docs/product/pricing_faq.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/pricing_operations.md`](../../docs/product/pricing_operations.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/product_overview.md`](../../docs/product/product_overview.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/roadmap.md`](../../docs/product/roadmap.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/product/teacher_guide.md`](../../docs/product/teacher_guide.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `product` | `active` |
| [`docs/security/POPIA_CONSENT_AUDIT_BASELINE.md`](../../docs/security/POPIA_CONSENT_AUDIT_BASELINE.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/POPIA_CONSENT_GATE_CLOSURE.md`](../../docs/security/POPIA_CONSENT_GATE_CLOSURE.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/assessment_attempt_authorization_wiring.md`](../../docs/security/assessment_attempt_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/assessment_attempt_model_contract.md`](../../docs/security/assessment_attempt_model_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/assessment_consent_gate.md`](../../docs/security/assessment_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/assessment_list_auth_boundary.md`](../../docs/security/assessment_list_auth_boundary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/audit_event_contracts.md`](../../docs/security/audit_event_contracts.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/auth_boundary_evidence.md`](../../docs/security/auth_boundary_evidence.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/auth_session_policy.md`](../../docs/security/auth_session_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/authorization_dependencies.md`](../../docs/security/authorization_dependencies.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/consent_dependency_adapter.md`](../../docs/security/consent_dependency_adapter.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/consent_dependency_denial_paths.md`](../../docs/security/consent_dependency_denial_paths.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/consent_grant_authorization_wiring.md`](../../docs/security/consent_grant_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/consent_rejection_audit.md`](../../docs/security/consent_rejection_audit.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/consent_renewal_admin_auth_boundary.md`](../../docs/security/consent_renewal_admin_auth_boundary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/consent_revoke_authorization_wiring.md`](../../docs/security/consent_revoke_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/consent_status_authorization_wiring.md`](../../docs/security/consent_status_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/dev_only_endpoint_exposure.md`](../../docs/security/dev_only_endpoint_exposure.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/dev_session_environment_gate.md`](../../docs/security/dev_session_environment_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/diagnostic_items_authorization_wiring.md`](../../docs/security/diagnostic_items_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/diagnostic_submit_authorization_wiring.md`](../../docs/security/diagnostic_submit_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/diagnostics_central_consent_source.md`](../../docs/security/diagnostics_central_consent_source.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/diagnostics_consent_gate.md`](../../docs/security/diagnostics_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/environment_security_contract.md`](../../docs/security/environment_security_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/ether_onboarding_consent_gate.md`](../../docs/security/ether_onboarding_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/ether_onboarding_questions_auth_boundary.md`](../../docs/security/ether_onboarding_questions_auth_boundary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/gamification_award_xp_authorization_wiring.md`](../../docs/security/gamification_award_xp_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/gamification_consent_gate.md`](../../docs/security/gamification_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/gamification_profile_authorization_wiring.md`](../../docs/security/gamification_profile_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/jwt_rotation_plan.md`](../../docs/security/jwt_rotation_plan.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/jwt_secret_resolution_policy.md`](../../docs/security/jwt_secret_resolution_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_authz_ci.md`](../../docs/security/learner_authz_ci.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_authz_coverage_check.md`](../../docs/security/learner_authz_coverage_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_authz_matrix.md`](../../docs/security/learner_authz_matrix.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/learner_mastery_authorization_wiring.md`](../../docs/security/learner_mastery_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_read_authorization_http_tests.md`](../../docs/security/learner_read_authorization_http_tests.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/learner_read_consent_gate.md`](../../docs/security/learner_read_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/lesson_generation_authorization_wiring.md`](../../docs/security/lesson_generation_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/lesson_generation_consent_gate.md`](../../docs/security/lesson_generation_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/lesson_stream_authorization_wiring.md`](../../docs/security/lesson_stream_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/object_authorization.md`](../../docs/security/object_authorization.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/onboarding_authorization_wiring.md`](../../docs/security/onboarding_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/onboarding_consent_gate.md`](../../docs/security/onboarding_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/onboarding_questions_auth_boundary.md`](../../docs/security/onboarding_questions_auth_boundary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/operational_auth_boundaries.md`](../../docs/security/operational_auth_boundaries.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/parent_dashboard_authorization_wiring.md`](../../docs/security/parent_dashboard_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/parent_erasure_authorization_wiring.md`](../../docs/security/parent_erasure_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/parent_export_authorization_wiring.md`](../../docs/security/parent_export_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/parent_progress_authorization_wiring.md`](../../docs/security/parent_progress_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/parent_trust_dashboard_authorization_wiring.md`](../../docs/security/parent_trust_dashboard_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/phase2_authorization_closure_check.md`](../../docs/security/phase2_authorization_closure_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/phase2_authorization_closure_report.md`](../../docs/security/phase2_authorization_closure_report.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/phase2_authorization_evidence_check.md`](../../docs/security/phase2_authorization_evidence_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/pii_secret_redaction_contract.md`](../../docs/security/pii_secret_redaction_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/pip_audit_report.md`](../../docs/security/pip_audit_report.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/popia_consent_audit_ci.md`](../../docs/security/popia_consent_audit_ci.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/popia_consent_audit_evidence_check.md`](../../docs/security/popia_consent_audit_evidence_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/popia_consent_boundary_check.md`](../../docs/security/popia_consent_boundary_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_consent_closure_check.md`](../../docs/security/popia_consent_closure_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/popia_consent_closure_ci.md`](../../docs/security/popia_consent_closure_ci.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/popia_consent_gate_check.md`](../../docs/security/popia_consent_gate_check.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_correction_request_authorization_wiring.md`](../../docs/security/popia_correction_request_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_data_export_authorization_wiring.md`](../../docs/security/popia_data_export_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_data_rights_consent_boundary.md`](../../docs/security/popia_data_rights_consent_boundary.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_deletion_cancel_authorization_wiring.md`](../../docs/security/popia_deletion_cancel_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_deletion_request_authorization_wiring.md`](../../docs/security/popia_deletion_request_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/popia_restriction_request_authorization_wiring.md`](../../docs/security/popia_restriction_request_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/privacy_boundary_evidence.md`](../../docs/security/privacy_boundary_evidence.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `current-evidence` |
| [`docs/security/production_key_vault_behavior.md`](../../docs/security/production_key_vault_behavior.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/production_secret_placeholder_guard.md`](../../docs/security/production_secret_placeholder_guard.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/risk_acceptance_register.md`](../../docs/security/risk_acceptance_register.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/runbooks/security_incident_response.md`](../../docs/security/runbooks/security_incident_response.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/secret_hygiene_contract.md`](../../docs/security/secret_hygiene_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/security_control_register.md`](../../docs/security/security_control_register.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/security_headers_policy.md`](../../docs/security/security_headers_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/security_posture_architecture_contract.md`](../../docs/security/security_posture_architecture_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/security_test_strategy_contract.md`](../../docs/security/security_test_strategy_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/study_plan_authorization_wiring.md`](../../docs/security/study_plan_authorization_wiring.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/study_plan_consent_gate.md`](../../docs/security/study_plan_consent_gate.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/supply_chain_security_contract.md`](../../docs/security/supply_chain_security_contract.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/threat_model_register.md`](../../docs/security/threat_model_register.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/threat_model_v2.md`](../../docs/security/threat_model_v2.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/security/vulnerability_management_policy.md`](../../docs/security/vulnerability_management_policy.md) | 2026-06-23 | 60d | 2026-08-22 | **+31d** | `security` | `active` |
| [`docs/ai/CLUSTER_F_CLOSURE.md`](../../docs/ai/CLUSTER_F_CLOSURE.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/ai_fixture_coverage_matrix.md`](../../docs/ai/ai_fixture_coverage_matrix.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/ai_output_fixtures.md`](../../docs/ai/ai_output_fixtures.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/ai_prompt_input_contract.md`](../../docs/ai/ai_prompt_input_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/ai_prompt_secret_leakage_guard.md`](../../docs/ai/ai_prompt_secret_leakage_guard.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/ai_prompt_surface_inventory.md`](../../docs/ai/ai_prompt_surface_inventory.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/ai_refusal_regression_fixtures.md`](../../docs/ai/ai_refusal_regression_fixtures.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/ai_safety_boundary_contract.md`](../../docs/ai/ai_safety_boundary_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/ai_safety_evidence_index.md`](../../docs/ai/ai_safety_evidence_index.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/ai_safety_release_evidence.md`](../../docs/ai/ai_safety_release_evidence.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/caps_ai_safety_evidence_2026-05-11.md`](../../docs/ai/caps_ai_safety_evidence_2026-05-11.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/caps_alignment_contract.md`](../../docs/ai/caps_alignment_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/diagnostic_generation_safety_contract.md`](../../docs/ai/diagnostic_generation_safety_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/knowledge_graph_grounding_contract.md`](../../docs/ai/knowledge_graph_grounding_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/lesson_generation_safety_contract.md`](../../docs/ai/lesson_generation_safety_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/lesson_quality_rubric.md`](../../docs/ai/lesson_quality_rubric.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/llm_provider_fallback_contract.md`](../../docs/ai/llm_provider_fallback_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/production_ai_pii_safety_contract.md`](../../docs/ai/production_ai_pii_safety_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/production_lesson_generation_validation_contract.md`](../../docs/ai/production_lesson_generation_validation_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `current-evidence` |
| [`docs/ai/production_llm_gateway_contract.md`](../../docs/ai/production_llm_gateway_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/ai/remediation_safety_contract.md`](../../docs/ai/remediation_safety_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `ai-safety` | `active` |
| [`docs/backend/README.md`](../../docs/backend/README.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `backend` | `active` |
| [`docs/caps/caps_learning_proof.md`](../../docs/caps/caps_learning_proof.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/caps/caps_source_acquisition_plan_v2.md`](../../docs/caps/caps_source_acquisition_plan_v2.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/caps/content_expansion_roadmap.md`](../../docs/caps/content_expansion_roadmap.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/caps/grade4_maths_120_item_production_plan.md`](../../docs/caps/grade4_maths_120_item_production_plan.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/caps/grade4_maths_coverage_matrix.md`](../../docs/caps/grade4_maths_coverage_matrix.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `current-evidence` |
| [`docs/caps/grade4_maths_lesson_coverage_matrix.md`](../../docs/caps/grade4_maths_lesson_coverage_matrix.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `current-evidence` |
| [`docs/caps/knowledge_graph_mapping_contract.md`](../../docs/caps/knowledge_graph_mapping_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/caps/multilingual_status.md`](../../docs/caps/multilingual_status.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `current-evidence` |
| [`docs/content_factory/CONTENT_GENERATION_CONFIG.md`](../../docs/content_factory/CONTENT_GENERATION_CONFIG.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/admin_api.md`](../../docs/content_factory/admin_api.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/control_plane.md`](../../docs/content_factory/control_plane.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/controlled_generation.md`](../../docs/content_factory/controlled_generation.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/full_generation_runner.md`](../../docs/content_factory/full_generation_runner.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/promotion_gates.md`](../../docs/content_factory/promotion_gates.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/release_gate_checklist.md`](../../docs/content_factory/release_gate_checklist.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `current-evidence` |
| [`docs/content_factory/staging_seed_execution.md`](../../docs/content_factory/staging_seed_execution.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/content_factory/staging_verification.md`](../../docs/content_factory/staging_verification.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `content-factory` | `active` |
| [`docs/curriculum/StudyMaterialExpansionPlan.md`](../../docs/curriculum/StudyMaterialExpansionPlan.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/curriculum/TOPIC_MAP_REVIEW_CHECKLIST.md`](../../docs/curriculum/TOPIC_MAP_REVIEW_CHECKLIST.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `current-evidence` |
| [`docs/curriculum/caps_topic_map.md`](../../docs/curriculum/caps_topic_map.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/curriculum/caps_topic_map_production_contract.md`](../../docs/curriculum/caps_topic_map_production_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/curriculum/pedagogical_validity_review.md`](../../docs/curriculum/pedagogical_validity_review.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/curriculum/post_launch_educational_limitations_memo.md`](../../docs/curriculum/post_launch_educational_limitations_memo.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `curriculum` | `active` |
| [`docs/curriculum/rr007_content_expansion_roadmap.md`](../../docs/curriculum/rr007_content_expansion_roadmap.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `engineering` | `active` |
| [`docs/diagnostics/README.md`](../../docs/diagnostics/README.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/diagnostics/assessment_quality_fairness_contract.md`](../../docs/diagnostics/assessment_quality_fairness_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/diagnostics/item_bank_launch_coverage_contract.md`](../../docs/diagnostics/item_bank_launch_coverage_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/diagnostics/item_contract.md`](../../docs/diagnostics/item_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/diagnostics/mastery_model_assessment_contract.md`](../../docs/diagnostics/mastery_model_assessment_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/diagnostics/production_diagnostics_assessment_readiness_contract.md`](../../docs/diagnostics/production_diagnostics_assessment_readiness_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/disaster_recovery/backup_policy_retention_contract.md`](../../docs/disaster_recovery/backup_policy_retention_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/disaster_recovery/backup_restore_architecture_contract.md`](../../docs/disaster_recovery/backup_restore_architecture_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/disaster_recovery/business_continuity_contract.md`](../../docs/disaster_recovery/business_continuity_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/disaster_recovery/dr_escalation_matrix.md`](../../docs/disaster_recovery/dr_escalation_matrix.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/disaster_recovery/evidence/restore_drill_001.md`](../../docs/disaster_recovery/evidence/restore_drill_001.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/disaster_recovery/recovery_objectives_contract.md`](../../docs/disaster_recovery/recovery_objectives_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/disaster_recovery/restore_drill_evidence_contract.md`](../../docs/disaster_recovery/restore_drill_evidence_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/disaster_recovery/restore_runbook_contract.md`](../../docs/disaster_recovery/restore_runbook_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/disaster_recovery/runbooks/database_restore.md`](../../docs/disaster_recovery/runbooks/database_restore.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/disaster_recovery/runbooks/object_storage_restore.md`](../../docs/disaster_recovery/runbooks/object_storage_restore.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/irt/README.md`](../../docs/irt/README.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `diagnostics` | `active` |
| [`docs/observability/alerting_incident_routing_contract.md`](../../docs/observability/alerting_incident_routing_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `current-evidence` |
| [`docs/observability/dashboard_runbook_contract.md`](../../docs/observability/dashboard_runbook_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/observability/logging_tracing_contract.md`](../../docs/observability/logging_tracing_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/observability/metrics_slo_contract.md`](../../docs/observability/metrics_slo_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/observability/production_observability_architecture_contract.md`](../../docs/observability/production_observability_architecture_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/observability/runbooks/api_error_rate_high.md`](../../docs/observability/runbooks/api_error_rate_high.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/observability/runbooks/llm_provider_failure_spike.md`](../../docs/observability/runbooks/llm_provider_failure_spike.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/observability/runbooks/notification_dead_letter_spike.md`](../../docs/observability/runbooks/notification_dead_letter_spike.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/observability/runbooks/privacy_export_failure.md`](../../docs/observability/runbooks/privacy_export_failure.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/observability/telemetry_privacy_retention_contract.md`](../../docs/observability/telemetry_privacy_retention_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active` |
| [`docs/runbooks/ai_operations_and_budgets.md`](../../docs/runbooks/ai_operations_and_budgets.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/runbooks/content_review_governance.md`](../../docs/runbooks/content_review_governance.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/runbooks/curriculum_expansion_and_training_governance.md`](../../docs/runbooks/curriculum_expansion_and_training_governance.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/runbooks/irt_quality_watchdog.md`](../../docs/runbooks/irt_quality_watchdog.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/runbooks/learner_tutor.md`](../../docs/runbooks/learner_tutor.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `operations` | `active-runbook` |
| [`docs/performance/rr007_load_testing_plan.md`](../../docs/performance/rr007_load_testing_plan.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/product_quality/rr007_accessibility_audit_plan.md`](../../docs/product_quality/rr007_accessibility_audit_plan.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/product_quality/rr007_multilingual_lesson_proof_plan.md`](../../docs/product_quality/rr007_multilingual_lesson_proof_plan.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/product_quality/rr007_playwright_ci_gate.md`](../../docs/product_quality/rr007_playwright_ci_gate.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/product_quality/rr007_product_quality_gate_policy.md`](../../docs/product_quality/rr007_product_quality_gate_policy.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/product_quality/rr007_pwa_offline_verification_plan.md`](../../docs/product_quality/rr007_pwa_offline_verification_plan.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/roadmap/reconciliation/rr_007_product_quality_gates.md`](../../docs/roadmap/reconciliation/rr_007_product_quality_gates.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `engineering` | `active` |
| [`docs/security/python_dependency_audit_policy.md`](../../docs/security/python_dependency_audit_policy.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `security` | `active` |
| [`docs/security/rr006_security_posture_control_map.md`](../../docs/security/rr006_security_posture_control_map.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `security` | `active` |
| [`docs/security/rr006_threat_model_review.md`](../../docs/security/rr006_threat_model_review.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `security` | `current-evidence` |
| [`docs/security/secrets_scanning_enforcement.md`](../../docs/security/secrets_scanning_enforcement.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `security` | `active` |
| [`docs/security/v2_pen_test_checklist.md`](../../docs/security/v2_pen_test_checklist.md) | 2026-07-02 | 60d | 2026-08-31 | **+22d** | `security` | `active` |
| [`docs/public_beta/rr014_public_beta_consent_and_privacy_attestation.md`](../../docs/public_beta/rr014_public_beta_consent_and_privacy_attestation.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `privacy` | `active` |
| [`docs/public_beta/rr014_public_beta_consent_and_privacy_attestation.template.md`](../../docs/public_beta/rr014_public_beta_consent_and_privacy_attestation.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `privacy` | `active` |
| [`docs/public_beta/rr014_public_beta_expansion_policy.md`](../../docs/public_beta/rr014_public_beta_expansion_policy.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `product` | `active` |
| [`docs/public_beta/rr014_public_beta_expansion_readiness_plan.md`](../../docs/public_beta/rr014_public_beta_expansion_readiness_plan.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `product` | `active` |
| [`docs/public_beta/rr014_public_beta_expansion_readiness_plan.template.md`](../../docs/public_beta/rr014_public_beta_expansion_readiness_plan.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `product` | `active` |
| [`docs/public_beta/rr014_public_beta_launch_boundary.md`](../../docs/public_beta/rr014_public_beta_launch_boundary.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `product` | `active` |
| [`docs/public_beta/rr014_public_beta_launch_boundary.template.md`](../../docs/public_beta/rr014_public_beta_launch_boundary.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `product` | `active` |
| [`docs/public_beta/rr014_public_beta_support_and_incident_plan.md`](../../docs/public_beta/rr014_public_beta_support_and_incident_plan.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `operations` | `active` |
| [`docs/public_beta/rr014_public_beta_support_and_incident_plan.template.md`](../../docs/public_beta/rr014_public_beta_support_and_incident_plan.template.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `operations` | `active` |
| [`docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research.md`](../../docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `research` | `active` |
| [`docs/roadmap/reconciliation/rr_014_public_beta_expansion.md`](../../docs/roadmap/reconciliation/rr_014_public_beta_expansion.md) | 2026-07-03 | 60d | 2026-09-01 | **+21d** | `product` | `active` |
| [`docs/approvals/rr015_caps_content_review_attestation.md`](../../docs/approvals/rr015_caps_content_review_attestation.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `curriculum` | `active` |
| [`docs/approvals/rr015_caps_content_review_attestation.template.md`](../../docs/approvals/rr015_caps_content_review_attestation.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `curriculum` | `template` |
| [`docs/approvals/rr015_external_approval_boundary.md`](../../docs/approvals/rr015_external_approval_boundary.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release` | `active` |
| [`docs/approvals/rr015_external_approval_boundary.template.md`](../../docs/approvals/rr015_external_approval_boundary.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `governance` | `template` |
| [`docs/approvals/rr015_external_approvals_policy.md`](../../docs/approvals/rr015_external_approvals_policy.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `governance` | `active` |
| [`docs/approvals/rr015_legal_review_attestation.md`](../../docs/approvals/rr015_legal_review_attestation.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `legal` | `active` |
| [`docs/approvals/rr015_legal_review_attestation.template.md`](../../docs/approvals/rr015_legal_review_attestation.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `legal` | `template` |
| [`docs/approvals/rr015_popia_privacy_review_attestation.md`](../../docs/approvals/rr015_popia_privacy_review_attestation.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `privacy` | `active` |
| [`docs/approvals/rr015_popia_privacy_review_attestation.template.md`](../../docs/approvals/rr015_popia_privacy_review_attestation.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `privacy` | `template` |
| [`docs/approvals/rr015_release_owner_go_no_go_signoff.md`](../../docs/approvals/rr015_release_owner_go_no_go_signoff.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release` | `active` |
| [`docs/approvals/rr015_release_owner_go_no_go_signoff.template.md`](../../docs/approvals/rr015_release_owner_go_no_go_signoff.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-management` | `template` |
| [`docs/approvals/rr015_security_review_attestation.md`](../../docs/approvals/rr015_security_review_attestation.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `security` | `active` |
| [`docs/approvals/rr015_security_review_attestation.template.md`](../../docs/approvals/rr015_security_review_attestation.template.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `security` | `template` |
| [`docs/roadmap/reconciliation/rr_015_external_approvals.md`](../../docs/roadmap/reconciliation/rr_015_external_approvals.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `governance` | `active` |
| [`docs/roadmap/reconciliation/rr_016_operational_drills.md`](../../docs/roadmap/reconciliation/rr_016_operational_drills.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `operations` | `active` |
| [`docs/roadmap/reconciliation/rr_017_release_safety_controls.md`](../../docs/roadmap/reconciliation/rr_017_release_safety_controls.md) | 2026-07-04 | 60d | 2026-09-02 | **+20d** | `release-engineering` | `active` |
| [`docs/knowledge_graph/caps_graph/kg001_caps_graph_foundation_policy.md`](../../docs/knowledge_graph/caps_graph/kg001_caps_graph_foundation_policy.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/knowledge_graph/caps_graph/kg001_caps_graph_loader_contract.md`](../../docs/knowledge_graph/caps_graph/kg001_caps_graph_loader_contract.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/knowledge_graph/caps_graph/kg001_caps_graph_runtime_boundary.md`](../../docs/knowledge_graph/caps_graph/kg001_caps_graph_runtime_boundary.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/knowledge_graph/target_graph/kg002_target_graph_generation_policy.md`](../../docs/knowledge_graph/target_graph/kg002_target_graph_generation_policy.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/knowledge_graph/target_graph/kg002_target_graph_policy_contract.md`](../../docs/knowledge_graph/target_graph/kg002_target_graph_policy_contract.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/knowledge_graph/target_graph/kg002_target_graph_runtime_boundary.md`](../../docs/knowledge_graph/target_graph/kg002_target_graph_runtime_boundary.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/product/knowledge_graph_learning_model_brief.md`](../../docs/product/knowledge_graph_learning_model_brief.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_content_correction_workflow.md`](../../docs/product_quality/trustworthy_beta/rr018_content_correction_workflow.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_content_correction_workflow.template.md`](../../docs/product_quality/trustworthy_beta/rr018_content_correction_workflow.template.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_educator_caps_priority_review.md`](../../docs/product_quality/trustworthy_beta/rr018_educator_caps_priority_review.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_educator_caps_priority_review.template.md`](../../docs/product_quality/trustworthy_beta/rr018_educator_caps_priority_review.template.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_feedback_report_issue_validation.md`](../../docs/product_quality/trustworthy_beta/rr018_feedback_report_issue_validation.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_feedback_report_issue_validation.template.md`](../../docs/product_quality/trustworthy_beta/rr018_feedback_report_issue_validation.template.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_human_review_queue.md`](../../docs/product_quality/trustworthy_beta/rr018_human_review_queue.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_human_review_queue.template.md`](../../docs/product_quality/trustworthy_beta/rr018_human_review_queue.template.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_boundary.md`](../../docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_boundary.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_boundary.template.md`](../../docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_boundary.template.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_policy.md`](../../docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_policy.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval.md`](../../docs/roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `roadmap-governance` | `active` |
| [`docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation.md`](../../docs/roadmap/knowledge_graph/kg_001_caps_graph_foundation.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/roadmap/knowledge_graph/kg_002_target_graph_generation.md`](../../docs/roadmap/knowledge_graph/kg_002_target_graph_generation.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `knowledge-graph` | `active` |
| [`docs/roadmap/knowledge_graph/kg_implementation_roadmap.md`](../../docs/roadmap/knowledge_graph/kg_implementation_roadmap.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `roadmap-governance` | `active` |
| [`docs/roadmap/knowledge_graph_pivot_roadmap.md`](../../docs/roadmap/knowledge_graph_pivot_roadmap.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `roadmap-governance` | `active` |
| [`docs/roadmap/reconciliation/final_roadmap_reconciliation_closure.md`](../../docs/roadmap/reconciliation/final_roadmap_reconciliation_closure.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `roadmap-reconciliation` | `active` |
| [`docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality.md`](../../docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `product-quality` | `active` |
| [`docs/roadmap/risk_register_knowledge_graph_pivot.md`](../../docs/roadmap/risk_register_knowledge_graph_pivot.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `risk` | `active` |
| [`docs/security/knowledge_graph_privacy_and_popia_contract.md`](../../docs/security/knowledge_graph_privacy_and_popia_contract.md) | 2026-07-05 | 60d | 2026-09-03 | **+19d** | `privacy` | `active` |
| [`docs/documentation/documentation_alignment_plan.md`](../../docs/documentation/documentation_alignment_plan.md) | 2026-09-03 | 14d | 2026-09-17 | **+5d** | `documentation-governance` | `active` |

## Testing & Quality Verification (28 Overdue)

| Document Path | Last Reviewed | Interval | Due Date | Days Stale | Owner | Status |
|---|---|---|---|---|---|---|
| [`docs/testing/documentation_defined_coverage.md`](../../docs/testing/documentation_defined_coverage.md) | 2026-06-24 | 21d | 2026-07-15 | **+69d** | `quality` | `active` |
| [`docs/testing/README.md`](../../docs/testing/README.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/beta_release_quality_gate_checklist.md`](../../docs/testing/beta_release_quality_gate_checklist.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `current-evidence` |
| [`docs/testing/coverage_baseline_stabilisation.md`](../../docs/testing/coverage_baseline_stabilisation.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/coverage_quality_threshold_contract.md`](../../docs/testing/coverage_quality_threshold_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/coverage_static_security_green_execution.md`](../../docs/testing/coverage_static_security_green_execution.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/defect_triage_release_blocker_contract.md`](../../docs/testing/defect_triage_release_blocker_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/final_true_state_baseline_handoff_contract.md`](../../docs/testing/final_true_state_baseline_handoff_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/flake_policy_and_quarantine_register.md`](../../docs/testing/flake_policy_and_quarantine_register.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/knowledge_graph_verification_plan.md`](../../docs/testing/knowledge_graph_verification_plan.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/known_issues_release_register.md`](../../docs/testing/known_issues_release_register.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/pr002r_evidence_check.md`](../../docs/testing/pr002r_evidence_check.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `current-evidence` |
| [`docs/testing/product_critical_flow_green_execution.md`](../../docs/testing/product_critical_flow_green_execution.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/product_gate_execution_contract.md`](../../docs/testing/product_gate_execution_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/product_runtime_test_gate_contract.md`](../../docs/testing/product_runtime_test_gate_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/production_release_quality_gate_checklist.md`](../../docs/testing/production_release_quality_gate_checklist.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `current-evidence` |
| [`docs/testing/pytest_import_path.md`](../../docs/testing/pytest_import_path.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/quality_gate_waiver_policy.md`](../../docs/testing/quality_gate_waiver_policy.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/release_evidence_bundle_contract.md`](../../docs/testing/release_evidence_bundle_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `current-evidence` |
| [`docs/testing/risk_based_coverage_thresholds.md`](../../docs/testing/risk_based_coverage_thresholds.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/runtime_stack_db_lineage_ready_green.md`](../../docs/testing/runtime_stack_db_lineage_ready_green.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/script_taxonomy.md`](../../docs/testing/script_taxonomy.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/targeted_baseline_reconciliation.md`](../../docs/testing/targeted_baseline_reconciliation.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/test_strategy_matrix_contract.md`](../../docs/testing/test_strategy_matrix_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `current-evidence` |
| [`docs/testing/test_suite_taxonomy.md`](../../docs/testing/test_suite_taxonomy.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/test_taxonomy_and_fast_suite_manifest.md`](../../docs/testing/test_taxonomy_and_fast_suite_manifest.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |
| [`docs/testing/testing_release_evidence_architecture_contract.md`](../../docs/testing/testing_release_evidence_architecture_contract.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `current-evidence` |
| [`docs/testing/unit_shard_stabilisation.md`](../../docs/testing/unit_shard_stabilisation.md) | 2026-06-24 | 60d | 2026-08-23 | **+30d** | `quality` | `active` |

