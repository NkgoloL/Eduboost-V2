---
title: "Architectural Decision Records (ADR)"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 180
evidence_command: make rr009-governance-process-check
code_anchors: []
---
# Architectural Decision Records (ADR)

This directory contains records of significant architectural decisions made during the development of EduBoost V2.

RR-009 refreshes this index so current governance does not rely on a partial ADR listing.

**ADR index completion recorded: true**

## Root ADR index

| ADR | Title | Status |
|---|---|---|
| [0001-modular-monolith](0001-modular-monolith.md) | ADR 0001: Modular Monolith Architecture | active |
| [0002-popia-first-design](0002-popia-first-design.md) | ADR 0002: POPIA-First Design | active |
| [0003-llm-provider-abstraction](0003-llm-provider-abstraction.md) | ADR 0003: LLM Provider Abstraction | active |
| [0004-standardizing-logic](0004-standardizing-logic.md) | ADR 0004: Standardizing Business Logic Location and Naming | active |
| [0005-fastapi-v2-entrypoint](0005-fastapi-v2-entrypoint.md) | ADR 0005: FastAPI V2 Entrypoint | active |
| [0006-nextjs-frontend](0006-nextjs-frontend.md) | ADR 0006: Next.js Frontend | active |
| [0007-postgresql-audit-ledger](0007-postgresql-audit-ledger.md) | ADR 0007: PostgreSQL Audit Ledger | active |
| [0008-redis-token-revocation](0008-redis-token-revocation.md) | ADR 0008: Redis Token Revocation | active |
| [0009-caps-alignment](0009-caps-alignment.md) | ADR 0009: CAPS Alignment | active |
| [0010-business-logic-location](0010-business-logic-location.md) | ADR 0010 — Business Logic Location | active |
| [ADR-001-python-runtime-version](ADR-001-python-runtime-version.md) | ADR-001 — Supported Python Runtime Version | active |
| [ADR-002-startup-ddl-repair](ADR-002-startup-ddl-repair.md) | ADR-002 — Startup DDL Repair in `app/api_v2.py` | active |
| [ADR-003-deployment-targets](ADR-003-deployment-targets.md) | ADR-003 — Deployment Targets and Promotion Model | active |
| [ADR-004-popia-data-rights-service-authority](ADR-004-popia-data-rights-service-authority.md) | ADR-004: POPIA Data Rights Service Authority | active |
| [ADR-005-database-rollback-policy](ADR-005-database-rollback-policy.md) | ADR-005 — Database Rollback Policy | active |
| [ADR-009-billing-provider](ADR-009-billing-provider.md) | ADR-009: Billing Provider Decision | active |
| [ADR-010-notifications-communication-provider](ADR-010-notifications-communication-provider.md) | ADR-010: Notifications and Communication Provider Decision | active |
| [ADR-011-observability-stack](ADR-011-observability-stack.md) | ADR-011: Observability Stack Decision | active |
| [ADR-012-ci-cd-infrastructure-deployment](ADR-012-ci-cd-infrastructure-deployment.md) | ADR-012: CI/CD, Infrastructure, Deployment, Docker, and Environment Decision | active |
| [ADR-013-backup-restore-disaster-recovery](ADR-013-backup-restore-disaster-recovery.md) | ADR-013: Backup, Restore, and Disaster Recovery Decision | active |
| [ADR-014-testing-release-evidence-quality-gates](ADR-014-testing-release-evidence-quality-gates.md) | ADR-014: Testing, Release Evidence, and Quality Gates Decision | active |
| [ADR-015-security-posture-threat-modeling](ADR-015-security-posture-threat-modeling.md) | ADR-015: Security Posture and Threat Modeling Decision | active |
| [ADR-016-incident-response-operations-support](ADR-016-incident-response-operations-support.md) | ADR-016: Incident Response, Operations, and Support Decision | active |
| [ADR-017-documentation-adrs-claim-discipline](ADR-017-documentation-adrs-claim-discipline.md) | ADR-017: Documentation, ADRs, and Claim Discipline | active |
| [ADR-018-beta-launch-staging-acceptance-product-scope](ADR-018-beta-launch-staging-acceptance-product-scope.md) | ADR-018: Beta Launch, Staging Acceptance, and Product Scope | active |
| [ADR-019-roadmap-after-production-readiness-baseline](ADR-019-roadmap-after-production-readiness-baseline.md) | ADR-019 — Roadmap After Production Readiness Baseline | active |
| [ADR-020-final-release-blocker-checklist](ADR-020-final-release-blocker-checklist.md) | ADR-020: Final Release-Blocker Checklist | active |
| [ADR-021-backend-consolidation-evidence-first](ADR-021-backend-consolidation-evidence-first.md) | ADR-021: Backend Consolidation Must Be Evidence-First | active |
| [ADR-022-audit-consent-table-ownership-options](ADR-022-audit-consent-table-ownership-options.md) | ADR-022: Audit and Consent Table Ownership Options | active |
| [ADR-023-frontend-upgrade-react-19-next-15](ADR-023-frontend-upgrade-react-19-next-15.md) | ADR-023: Frontend Upgrade - React 19 + Next 15 | active |
| [ADR-024-frontend-rollback-plan](ADR-024-frontend-rollback-plan.md) | ADR-024: Frontend Rollback Plan | active |
| [ADR-025-frontend-upgrade-backlog-metadata](ADR-025-frontend-upgrade-backlog-metadata.md) | ADR-025: Frontend Upgrade Backlog Metadata | active |
| [ADR-026-python-version-alignment](ADR-026-python-version-alignment.md) | ADR-026 — Phase 4 Python Version Alignment | active |
| [ADR-027-observability-endpoint-access-control](ADR-027-observability-endpoint-access-control.md) | ADR-027 — Observability Endpoint Access Control | active |
| [ADR-028-authoritative-deployment-target](ADR-028-authoritative-deployment-target.md) | ADR-028 — Authoritative Production Deployment Target | active |
| [ADR-029-supabase-auth-strategy](ADR-029-supabase-auth-strategy.md) | ADR-029: Supabase Auth Strategy | active |
| [ADR-030-content-review-governance](ADR-030-content-review-governance.md) | ADR-030 — Educator Consensus and Content Governance | active |
| [ADR-031-durable-ai-operations-budget-authority](ADR-031-durable-ai-operations-budget-authority.md) | ADR-031 — Durable AI Operations and Budget Authority | active |
| [ADR-032-curriculum-expansion-training-governance](ADR-032-curriculum-expansion-training-governance.md) | ADR-032 — Governed Curriculum Expansion and Training Dataset Manifests | active |
| [ADR-033-learner-tutor-safety-boundary](ADR-033-learner-tutor-safety-boundary.md) | ADR-033 — Learner Tutor Safety and Context Boundary | active |
| [ADR-034-irt-quality-self-healing](ADR-034-irt-quality-self-healing.md) | ADR-034 — IRT Quality and Self-Healing Controls | active |
| [ADR-035-supabase-vs-raw-postgres-product-quality-gate](ADR-035-supabase-vs-raw-postgres-product-quality-gate.md) | ADR-035 — Supabase versus Raw Postgres Product Quality Gate | proposed |

## Frontend ADR index

| ADR | Title | Status |
|---|---|---|
| [ADR-001-auth-model](frontend/ADR-001-auth-model.md) | ADR-001 — Frontend Auth Model (FastAPI JWT + httpOnly cookie) | active |
| [ADR-001-rollback](frontend/ADR-001-rollback.md) | ADR-001 Rollback Plan — Supabase Auth Restoration | active |
| [ADR-002-state-management](frontend/ADR-002-state-management.md) | ADR-002 — State Management (Zustand + TanStack Query) | active |
| [ADR-003-popia-frontend](frontend/ADR-003-popia-frontend.md) | ADR-003 — POPIA Frontend Audit Relay | active |
| [ADR-004-ai-tutor](frontend/ADR-004-ai-tutor.md) | ADR-004 — AI Tutor Proxy & Safety Envelope | active |
| [ADR-005-analytics](frontend/ADR-005-analytics.md) | ADR-005 — Analytics & Consent Tiers (Plausible Self-Host) | active |
| [ADR-006-rsc-boundaries](frontend/ADR-006-rsc-boundaries.md) | ADR-006 — RSC Boundaries & Route Component Map | active |
| [ADR-007-offline-sync](frontend/ADR-007-offline-sync.md) | ADR-007 — Offline Sync & Conflict Resolution | active |
| [ADR-008-voice-input](frontend/ADR-008-voice-input.md) | ADR-008 — Voice Input (Web Speech API en-ZA) | active |
| [ADR-023-frontend-upgrade-react19-next15](frontend/ADR-023-frontend-upgrade-react19-next15.md) | ADR-023 — Frontend Upgrade (React 19 + Next 15) | active |
| [ADR-024-frontend-rollback-plan](frontend/ADR-024-frontend-rollback-plan.md) | ADR-024 — Frontend Rollback Plan (React 19 + Next 15) | active |
| [ADR-025-frontend-upgrade-backlog-metadata](frontend/ADR-025-frontend-upgrade-backlog-metadata.md) | ADR-025 — Frontend Upgrade Backlog Metadata | active |

## Status meanings

- **Proposed**: recommended but still open to design review.
- **Accepted**: current architectural direction.
- **Superseded**: replaced by a newer ADR.
- **Deprecated**: no longer recommended but still relevant to historical context.
- **Recorded**: captured as an ADR-like decision document but without a normalized status marker.

## Governance rule

ADR changes must keep this index current and must cite the relevant RR item or roadmap source. Run `make rr009-governance-process-check` before merging governance/process changes.
