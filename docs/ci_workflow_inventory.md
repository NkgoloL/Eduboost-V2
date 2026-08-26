---
title: CI Workflow Inventory and Authority Map
status: active
owner: release-management
reviewers: [engineering, release-management, security]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-08-26
review_interval_days: 30
evidence_command: PYTHONPATH=. python3 scripts/true_state_remediation/execute_bundle.py --bundle B03 --phase verify --json
code_anchors: [.github/workflows, scripts/maintenance/audit_ci_workflows.py]
---

# CI Workflow Inventory and Authority Map

> Generated on `2026-08-26T08:08:40.580867+00:00`. Total workflows audited: `85`.

## Target Six-Workflow Graph

| Workflow File | Core Purpose | Gate Class |
| --- | --- | --- |
| `pr-core.yml` | Compile, fast product unit tests, Ruff, mypy, architecture, route/OpenAPI checks. | Required Gate |
| `product-runtime.yml` | Integration, disposable Postgres/pgvector/Redis, migrations, critical journeys. | Required Gate |
| `frontend-e2e.yml` | Frozen install, type-check, lint, unit, build, Playwright/accessibility. | Required Gate |
| `security-supply-chain.yml` | Bandit, dependency audits, secret scan, SBOM, container scan; scheduled & release-blocking. | Required Gate |
| `release-evidence.yml` | Manually dispatched, exact-commit, immutable release-candidate evidence. | Required Gate |
| `operations-drills.yml` | Backup/restore, rollback, incident, resilience, and performance drills. | Required Gate |

## All Repository Workflows Inventory

| File | Name | Triggers | Classification |
| --- | --- | --- | --- |
| `api-envelope-error-contract.yml` | API Envelope Error Contract | none | legacy_governance_reconciled |
| `architecture-gates.yml` | Architecture Gates | none | legacy_governance_reconciled |
| `audit-write-runtime-evidence.yml` | audit-write-runtime-evidence | none | legacy_governance_reconciled |
| `auth-boundary.yml` | Auth Boundary | none | legacy_governance_reconciled |
| `auth-refresh-db-proof.yml` | Auth Refresh DB Proof | none | legacy_governance_reconciled |
| `backend-consolidation.yml` | Backend Consolidation Evidence | none | legacy_governance_reconciled |
| `backend-nightly-coverage.yml` | Backend Nightly Coverage | none | legacy_governance_reconciled |
| `beta-release-approval.yml` | Beta Release Approval | none | legacy_governance_reconciled |
| `caps-source-topic-map.yml` | CAPS Source And Topic Map Gates | none | legacy_governance_reconciled |
| `ci-cd.yml` | EduBoost CI/CD | none | legacy_governance_reconciled |
| `ci-core.yml` | CI Core | none | legacy_governance_reconciled |
| `ci_diagnostics_assessment.yml` | Diagnostics Assessment Quality | none | legacy_governance_reconciled |
| `ci_lesson_quality.yml` | AI Lesson Quality | none | legacy_governance_reconciled |
| `cluster-d-ci.yml` | Cluster D CI Deployment Evidence | none | legacy_governance_reconciled |
| `cluster-e-data-resilience.yml` | Cluster E Data Resilience Evidence | none | legacy_governance_reconciled |
| `cluster-f-ai-safety.yml` | Cluster F AI Safety Evidence | none | legacy_governance_reconciled |
| `cluster-g-frontend.yml` | Cluster G Frontend Journey Evidence | none | legacy_governance_reconciled |
| `cluster-h-release-readiness.yml` | Cluster H Release Readiness | none | legacy_governance_reconciled |
| `db-backup-dryrun.yml` | DB Backup Dry-Run | none | legacy_governance_reconciled |
| `db-backup-matrix.yml` | DB Backup Matrix | none | legacy_governance_reconciled |
| `db-backup-restore-rollback-evidence.yml` | db-backup-restore-rollback-evidence | none | legacy_governance_reconciled |
| `dependency-scan.yml` | Dependency Scan | none | legacy_governance_reconciled |
| `deploy-frontend.yml` | Deploy Frontend to Staging | none | legacy_governance_reconciled |
| `diag-score-live-audit.yml` | diag-score-live-audit | none | legacy_governance_reconciled |
| `docs.yml` | Build and Deploy Docs | none | legacy_governance_reconciled |
| `documentation-governance.yml` | Documentation Governance | none | legacy_governance_reconciled |
| `e2e.yml` | E2E Tests | none | legacy_governance_reconciled |
| `final-roadmap-reconciliation-closure.yml` | Final Roadmap Reconciliation Closure | none | legacy_governance_reconciled |
| `frontend-e2e.yml` | Frontend E2E Opt-In | none | canonical_target_graph |
| `item_bank_ci.yml` | Item Bank CI Gates | none | legacy_governance_reconciled |
| `jwt-secret-rotation-evidence.yml` | jwt-secret-rotation-evidence | none | legacy_governance_reconciled |
| `kg-roadmap-closure-report.yml` | KG Roadmap Closure Report | none | legacy_governance_reconciled |
| `kg000-formal-kg-roadmap-approval.yml` | KG-0 Formal KG Roadmap Approval | none | legacy_governance_reconciled |
| `kg001-caps-graph-foundation.yml` | KG-1 CAPS Graph Foundation | none | legacy_governance_reconciled |
| `kg002-target-graph-generation.yml` | KG-2 Target Graph Generation | none | legacy_governance_reconciled |
| `kg003-learner-graph-shadow-mode.yml` | KG-3 Learner Graph Shadow Mode | none | legacy_governance_reconciled |
| `kg004-gap-engine-intervention-planner.yml` | KG-4 Gap Engine and Intervention Planner | none | legacy_governance_reconciled |
| `kg005-graph-grounded-lesson-assessment-generation.yml` | KG-5 Graph-Grounded Lesson and Assessment Generation | none | legacy_governance_reconciled |
| `kg006-tutor-study-plan-gamification-parent-alignment.yml` | KG-6 Tutor Study Plan Gamification Parent Alignment | none | legacy_governance_reconciled |
| `kg007-authority-switch-legacy-cleanup.yml` | KG-7 Authority Switch Legacy Cleanup | none | legacy_governance_reconciled |
| `kg008-post-switch-optimisation-scale-review.yml` | KG-8 Post-Switch Optimisation and Scale Review | none | legacy_governance_reconciled |
| `kgact001-controlled-runtime-kg-authority-activation.yml` | KG-ACT-001 Controlled Runtime KG Authority Activation | none | legacy_governance_reconciled |
| `learner-authz-coverage.yml` | Learner Authorization Coverage | none | legacy_governance_reconciled |
| `learning-evidence.yml` | Learning Evidence | none | legacy_governance_reconciled |
| `lighthouse.yml` | Lighthouse Staging Audit | none | legacy_governance_reconciled |
| `migration_check.yml` | Migration & Schema Check | none | legacy_governance_reconciled |
| `observability_check.yml` | Observability Config Check | none | legacy_governance_reconciled |
| `openapi-contract.yml` | openapi-contract | none | legacy_governance_reconciled |
| `openapi-drift.yml` | OpenAPI Drift | none | legacy_governance_reconciled |
| `persistence-resilience.yml` | Persistence Resilience | none | legacy_governance_reconciled |
| `popia-consent-audit.yml` | POPIA Consent Audit | none | legacy_governance_reconciled |
| `prd000-production-readiness-stream-authority.yml` | PRD-0.0 Production Readiness Stream Authority | none | legacy_governance_reconciled |
| `prd001-canonical-current-state-documentation-refresh.yml` | PRD-0.1 Canonical Current-State Documentation Refresh | none | legacy_governance_reconciled |
| `prd002-historical-report-stale-source-quarantine.yml` | PRD-0.2 Historical Report Stale Source Quarantine | none | legacy_governance_reconciled |
| `prd003-documentation-housekeeping-ratchet-refresh.yml` | PRD-0.3 Documentation Housekeeping Ratchet Refresh | none | legacy_governance_reconciled |
| `prd004-test-dependency-bootstrap-baseline.yml` | PRD-0.4 test dependency bootstrap baseline | none | legacy_governance_reconciled |
| `prd005-test-failure-collection-stabilisation-register.yml` | PRD-0.5 Test Failure Collection Stabilisation Register | none | legacy_governance_reconciled |
| `prd006-workflow-command-hygiene-ci-inventory.yml` | PRD-0.6 Workflow Command Hygiene CI Inventory | none | legacy_governance_reconciled |
| `prd007-openapi-generated-artifact-canonicalisation.yml` | PRD-0.7 OpenAPI Generated Artifact Canonicalisation | none | legacy_governance_reconciled |
| `prd008-branch-release-naming-reconciliation.yml` | PRD-0.8 Branch Release Naming Reconciliation | none | legacy_governance_reconciled |
| `prd009-repository-hygiene-generated-local-artifact-audit.yml` | PRD-0.9 Repository Hygiene Generated Local Artifact Audit | none | legacy_governance_reconciled |
| `prd010-prd0-closure-evidence-handoff.yml` | PRD-0.10 PRD-0 Closure Evidence Handoff | none | legacy_governance_reconciled |
| `prd100-ci-release-gate-stream-authority.yml` | PRD-1.0 CI Release Gate Stream Authority | none | legacy_governance_reconciled |
| `prd101-ci-inventory-authority.yml` | PRD-1.1 CI Inventory Authority | none | legacy_governance_reconciled |
| `privacy-boundary.yml` | Privacy Boundary & Consent Gate Check | none | legacy_governance_reconciled |
| `release.yml` | Release | none | legacy_governance_reconciled |
| `repo-state.yml` | Repo State | none | legacy_governance_reconciled |
| `rr003-release-authority.yml` | RR-003 Release Authority | none | legacy_governance_reconciled |
| `rr006-security-posture.yml` | RR-006 Security Posture | none | legacy_governance_reconciled |
| `rr007-product-quality-gates.yml` | RR-007 Product Quality Gates | none | legacy_governance_reconciled |
| `rr008-operational-readiness.yml` | RR-008 Operational Readiness | none | legacy_governance_reconciled |
| `rr009-governance-process.yml` | RR-009 Governance Process | none | legacy_governance_reconciled |
| `rr010-beta-outcome-reporting.yml` | RR-010 Beta Outcome Reporting | none | legacy_governance_reconciled |
| `rr011-live-billing-provider-integration.yml` | RR-011 Live Billing Provider Integration | none | legacy_governance_reconciled |
| `rr012-production-telemetry-dashboard.yml` | RR-012 Production Telemetry Dashboard | none | legacy_governance_reconciled |
| `rr013-advanced-mastery-model-research.yml` | RR-013 Advanced Mastery Model Research | none | legacy_governance_reconciled |
| `rr014-public-beta-expansion.yml` | RR-014 Public Beta Expansion | none | legacy_governance_reconciled |
| `rr015-external-approvals.yml` | RR-015 External Approvals | none | legacy_governance_reconciled |
| `rr016-operational-drills.yml` | RR-016 Operational Drills | none | legacy_governance_reconciled |
| `rr017-release-safety-controls.yml` | RR-017 Release Safety Controls | none | legacy_governance_reconciled |
| `rr018-trustworthy-beta-product-quality.yml` | RR-018 Trustworthy Beta Product Quality | none | legacy_governance_reconciled |
| `runtime-contract.yml` | Runtime Contract | none | legacy_governance_reconciled |
| `secrets-scan.yml` | Secrets Scan | none | legacy_governance_reconciled |
| `staging-smoke.yml` | Staging Smoke | none | legacy_governance_reconciled |
| `technical-audit-hosted-ci.yml` | EduBoost Hosted CI Authority | none | legacy_governance_reconciled |
