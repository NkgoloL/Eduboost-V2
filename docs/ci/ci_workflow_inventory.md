# EduBoost V2 CI Workflow Authority & Inventory

**Generated**: 2026-08-26T15:49:40.203421+00:00  
**Total Workflows Tracked**: 90  
**Canonical Active Workflows**: 6  
**Archived / Superseded Workflows**: 84  

## 1. Canonical Six-Workflow Target Graph

| Workflow File | Purpose | PR Required | Triggers | Replacement / Consolidation Role |
|---|---|---|---|---|
| `pr-core.yml` | Compile, fast product unit tests, Ruff, mypy, architecture gates, route & OpenAPI checks | **YES** | `pull_request, push:master` | Consolidates all PR static/unit/compile checks |
| `product-runtime.yml` | Product integration tests, disposable Postgres/pgvector/Redis runtime services, migrations, and critical learner journeys | **YES** | `pull_request, push:master` | Consolidates all backend runtime and DB integration checks |
| `frontend-e2e.yml` | Frozen Next.js install, type-check, lint, production build, Playwright and accessibility checks | **YES** | `pull_request, push:master` | Consolidates frontend builds, audits, and E2E journeys |
| `security-supply-chain.yml` | Bandit, pip-audit, pnpm audit, secret scan baseline, CycloneDX SBOM generation, container vulnerability checks | **YES** | `pull_request, push:master, schedule:daily` | Consolidates security scanners, dependency audits, and SBOMs |
| `release-evidence.yml` | Exact-commit immutable release candidate evidence generation and hash verification | **NO** | `workflow_dispatch` | Consolidates release-candidate evidence collection |
| `operations-drills.yml` | Database backup/restore dry runs, rollback tests, resilience verification, and incident drills | **NO** | `workflow_dispatch, schedule:weekly` | Consolidates operational and resilience drill suites |

## 2. Superseded & Archived Workflows Index

The following workflows represent historical PRD milestone audits, legacy multi-branch triggers, and fragmented checkers. All have been consolidated and archived to `archive/github_workflows/` to prevent uncoordinated CI dispatch.

| File | Original Name | Job Count | Consolidated Target |
|---|---|---|---|
| `api-envelope-error-contract.yml` | API Envelope Error Contract | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `architecture-gates.yml` | Architecture Gates | 3 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `audit-write-runtime-evidence.yml` | audit-write-runtime-evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `auth-boundary.yml` | Auth Boundary | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `auth-refresh-db-proof.yml` | Auth Refresh DB Proof | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `backend-consolidation.yml` | Backend Consolidation Evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `backend-nightly-coverage.yml` | Backend Nightly Coverage | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `beta-release-approval.yml` | Beta Release Approval | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `caps-source-topic-map.yml` | CAPS Source And Topic Map Gates | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `ci-cd.yml` | EduBoost CI/CD | 17 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `ci-core.yml` | CI Core | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `ci_diagnostics_assessment.yml` | Diagnostics Assessment Quality | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `ci_lesson_quality.yml` | AI Lesson Quality | 6 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `cluster-d-ci.yml` | Cluster D CI Deployment Evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `cluster-e-data-resilience.yml` | Cluster E Data Resilience Evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `cluster-f-ai-safety.yml` | Cluster F AI Safety Evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `cluster-g-frontend.yml` | Cluster G Frontend Journey Evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `cluster-h-release-readiness.yml` | Cluster H Release Readiness | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `db-backup-dryrun.yml` | DB Backup Dry-Run | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `db-backup-matrix.yml` | DB Backup Matrix | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `db-backup-restore-rollback-evidence.yml` | db-backup-restore-rollback-evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `dependency-scan.yml` | Dependency Scan | 4 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `deploy-frontend.yml` | Deploy Frontend to Staging | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `diag-score-live-audit.yml` | diag-score-live-audit | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `docs.yml` | Build and Deploy Docs | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `documentation-governance.yml` | Documentation Governance | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `e2e.yml` | E2E Tests | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `final-roadmap-reconciliation-closure.yml` | Final Roadmap Reconciliation Closure | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `item_bank_ci.yml` | Item Bank CI Gates | 3 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `jwt-secret-rotation-evidence.yml` | jwt-secret-rotation-evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg-roadmap-closure-report.yml` | KG Roadmap Closure Report | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg000-formal-kg-roadmap-approval.yml` | KG-0 Formal KG Roadmap Approval | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg001-caps-graph-foundation.yml` | KG-1 CAPS Graph Foundation | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg002-target-graph-generation.yml` | KG-2 Target Graph Generation | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg003-learner-graph-shadow-mode.yml` | KG-3 Learner Graph Shadow Mode | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg004-gap-engine-intervention-planner.yml` | KG-4 Gap Engine and Intervention Planner | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg005-graph-grounded-lesson-assessment-generation.yml` | KG-5 Graph-Grounded Lesson and Assessment Generation | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg006-tutor-study-plan-gamification-parent-alignment.yml` | KG-6 Tutor Study Plan Gamification Parent Alignment | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg007-authority-switch-legacy-cleanup.yml` | KG-7 Authority Switch Legacy Cleanup | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kg008-post-switch-optimisation-scale-review.yml` | KG-8 Post-Switch Optimisation and Scale Review | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `kgact001-controlled-runtime-kg-authority-activation.yml` | KG-ACT-001 Controlled Runtime KG Authority Activation | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `learner-authz-coverage.yml` | Learner Authorization Coverage | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `learning-evidence.yml` | Learning Evidence | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `lighthouse.yml` | Lighthouse Staging Audit | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `migration_check.yml` | Migration & Schema Check | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `observability_check.yml` | Observability Config Check | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `openapi-contract.yml` | openapi-contract | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `openapi-drift.yml` | OpenAPI Drift | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `persistence-resilience.yml` | Persistence Resilience | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `popia-consent-audit.yml` | POPIA Consent Audit | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd000-production-readiness-stream-authority.yml` | PRD-0.0 Production Readiness Stream Authority | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd001-canonical-current-state-documentation-refresh.yml` | PRD-0.1 Canonical Current-State Documentation Refresh | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd002-historical-report-stale-source-quarantine.yml` | PRD-0.2 Historical Report Stale Source Quarantine | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd003-documentation-housekeeping-ratchet-refresh.yml` | PRD-0.3 Documentation Housekeeping Ratchet Refresh | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd004-test-dependency-bootstrap-baseline.yml` | PRD-0.4 test dependency bootstrap baseline | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd005-test-failure-collection-stabilisation-register.yml` | PRD-0.5 Test Failure Collection Stabilisation Register | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd006-workflow-command-hygiene-ci-inventory.yml` | PRD-0.6 Workflow Command Hygiene CI Inventory | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd007-openapi-generated-artifact-canonicalisation.yml` | PRD-0.7 OpenAPI Generated Artifact Canonicalisation | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd008-branch-release-naming-reconciliation.yml` | PRD-0.8 Branch Release Naming Reconciliation | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd009-repository-hygiene-generated-local-artifact-audit.yml` | PRD-0.9 Repository Hygiene Generated Local Artifact Audit | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd010-prd0-closure-evidence-handoff.yml` | PRD-0.10 PRD-0 Closure Evidence Handoff | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd100-ci-release-gate-stream-authority.yml` | PRD-1.0 CI Release Gate Stream Authority | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `prd101-ci-inventory-authority.yml` | PRD-1.1 CI Inventory Authority | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `privacy-boundary.yml` | Privacy Boundary & Consent Gate Check | 4 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `release.yml` | Release | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `repo-state.yml` | Repo State | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr003-release-authority.yml` | RR-003 Release Authority | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr006-security-posture.yml` | RR-006 Security Posture | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr007-product-quality-gates.yml` | RR-007 Product Quality Gates | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr008-operational-readiness.yml` | RR-008 Operational Readiness | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr009-governance-process.yml` | RR-009 Governance Process | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr010-beta-outcome-reporting.yml` | RR-010 Beta Outcome Reporting | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr011-live-billing-provider-integration.yml` | RR-011 Live Billing Provider Integration | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr012-production-telemetry-dashboard.yml` | RR-012 Production Telemetry Dashboard | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr013-advanced-mastery-model-research.yml` | RR-013 Advanced Mastery Model Research | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr014-public-beta-expansion.yml` | RR-014 Public Beta Expansion | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr015-external-approvals.yml` | RR-015 External Approvals | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr016-operational-drills.yml` | RR-016 Operational Drills | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr017-release-safety-controls.yml` | RR-017 Release Safety Controls | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `rr018-trustworthy-beta-product-quality.yml` | RR-018 Trustworthy Beta Product Quality | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `runtime-contract.yml` | Runtime Contract | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `secrets-scan.yml` | Secrets Scan | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `staging-smoke.yml` | Staging Smoke | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
| `technical-audit-hosted-ci.yml` | EduBoost Hosted CI Authority | 1 | `pr-core.yml / product-runtime.yml / security-supply-chain.yml` |
