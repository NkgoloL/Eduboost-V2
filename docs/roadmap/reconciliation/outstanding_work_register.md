---
title: Outstanding Work Register
status: active-control
owner: roadmap-reconciliation
reviewers: [roadmap-reconciliation, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 30
evidence_command: make roadmap-reconciliation-check
code_anchors: [docs/roadmap/reconciliation, scripts/roadmap_reconciliation]
---

# Outstanding Work Register

**Status:** initial reconciliation baseline / pending evidence capture  
**Source rule:** entries must come from roadmap or TODO sources listed in `canonical_roadmap_sources.json`.  
**New work rule:** no new work is introduced until outstanding roadmap/TODO work is triaged from this register.

## Boundary

This register is a planning and reconciliation artifact. It does not itself approve implementation, production release, public beta, deployment, release tagging, runtime KG implementation, or expanded learner traffic.

## Priority legend

- **P0** — release/blocking or legal/safety/security control.
- **P1** — required before broader beta/public readiness.
- **P2** — important but not immediate blocker.

## Reconciled outstanding items

| ID | Priority | Source | Canonical area | Outstanding work | Current note | Recommended next slice family |
|---|---:|---|---|---|---|---|
| RR-001 | P0 | `PHASE_STATUS_REGISTER.md` | Atlas phase reconciliation | Reconcile Phase 0 and Phases 1–7 closure status against current evidence, or explicitly archive/supersede that register. | Register still says overall programme reconciliation is in progress and Phase 8 / controlled beta are blocked. | Roadmap/status reconciliation |
| RR-002 | P0 | `roadmap.md` Phase 8 | Privacy and authorization | POPIA legal-hold checks before erasure; persisted export/deletion flows; repository-backed authorization enforcement; tests for erasure/export/consent expiry/audit immutability. | Some data-rights UI paths are covered by seeded E2E, but canonical privacy/authorization closure is not reconciled. | Privacy / POPIA completion |
| RR-003 | P0 | `roadmap.md` Phase 9 | Coverage / CI / route authority | Regenerate current coverage; decide/enforce release threshold; make release-blocking checks visible in CI; consolidate `/api/v2` and `/v2`; retire/archive dormant routers; ensure release docs point at current evidence. | Hosted CI and branch protection were improved, but canonical coverage and route-consolidation policy remain unreconciled. | Coverage + CI policy + route consolidation |
| RR-004 | P1 | `roadmap.md` Phase 10 | Workspace hygiene and auditability | Safe cleanup target for ignored build/cache artifacts; tracked-file-only audit inventory commands; reproducible scanner/audit counts. | Evidence discipline improved, but canonical hygiene tasks need explicit closure or backlog state. | Workspace hygiene |
| RR-005 | P1 | `roadmap.md` Phase 11 | Technical debt burn-down | Capture remaining Ruff debt; resolve/import-linter exceptions; audit stale route comments; migration history audit/squash decision; retire dormant routers if not already handled. | Several runtime repairs added shims; debt should be inventoried before new architecture work. | Technical debt burn-down |
| RR-006 | P0 | `roadmap.md` Phase 12 | Security posture | V2 threat model; pen-test checklist; dependency vulnerability scan enforcement; secrets scanning in pre-commit/CI; Python dependency audit. | Branch protection exists, but security posture deepening remains canonical work. | Security posture deepening |
| RR-007 | P1 | `roadmap.md` Phase 13 | Frontend/product completeness | Playwright in CI; content expansion roadmap for Grades R–3 and 5–7; load testing; accessibility audit; PWA offline verification; multilingual lesson proof; Supabase-vs-raw-Postgres ADR. | Backend-backed and seeded E2E are recorded, but CI/performance/accessibility/offline/multilingual work remains. | Product completeness / quality gates |
| RR-008 | P0 | `roadmap.md` Phase 14 | Operational readiness | Incident response runbook; SLO definitions; capacity planning; LLM cost model; Grafana/alert linkage. | Beta operations docs exist, but canonical ops readiness needs reconciled closure evidence. | Operational readiness drills |
| RR-009 | P1 | `roadmap.md` Phase 15 | Governance and process | Refresh cadence for `docs/current_state.md`; ADR index completion; external TODO ownership/dates; branch protection reflected in canonical release docs. | Current-state date and status language are stale relative to recent evidence. | Governance/process reconciliation |
| RR-010 | P0 | `roadmap.md` Phase 16 | Beta period with real learner feedback | Minimum beta duration/metrics: cohort size, educator feedback, uptime, latency, security/PII/consent incidents, content approval, completion rate, backup/restore drills, weekly reviews, outcome report. | Phase 20/21 evidence is governance/monitoring evidence; it does not by itself prove a 4-week beta outcome. | Beta outcome reporting |
| RR-011 | P1 | `post_baseline_roadmap_register.md` | RM-001 | Live billing provider integration. | Still future commercial work; should not start before P0/P1 safety/security/privacy items are selected. | Commercial roadmap |
| RR-012 | P1 | `post_baseline_roadmap_register.md` | RM-002 | Production telemetry dashboard implementation. | Partially related to ops monitoring, but production telemetry dashboard requires its own implementation/evidence. | Observability / telemetry |
| RR-013 | P2 | `post_baseline_roadmap_register.md` | RM-003 | Advanced mastery-model research. | Keep separate from runtime KG north-star work; do not start before current roadmap debt is cleared. | Research backlog |
| RR-014 | P2 | `post_baseline_roadmap_register.md` | RM-004 | Public beta expansion. | Explicitly blocked until controlled beta outcome and public beta readiness are evidenced. | Public beta planning |
| RR-015 | P0 | `EduBoost_V2_North_Star_TODO.md` | External approval | Security review, POPIA/privacy review, legal review, CAPS/content review, release-owner go/no-go signoff. | Controlled-beta governance exists, but external approvals should be explicitly reconciled. | Approvals / legal/security/content |
| RR-016 | P0 | `EduBoost_V2_North_Star_TODO.md` | Operational drills | Backup drill, restore drill, rollback drill, monitoring dashboard verification, incident handoff verification. | Some rollback/support docs exist; drills need executable proof/evidence. | Operational drills |
| RR-017 | P0 | `EduBoost_V2_North_Star_TODO.md` | Production deployment blockers | Keep blocked operations blocked: destructive audit/consent DB changes, `alembic stamp head` repair, production DB mutation outside migration window, mutating health probes. | Preserve explicit safety boundary. | Release safety controls |
| RR-018 | P1 | `docs/product/roadmap.md` | Trustworthy beta | Feedback/report issue button, content correction workflow, human review queue, educator review of priority CAPS topics. | These are product-facing beta quality tasks, not evidence-gate paperwork. | Product beta quality |

## Recommended next work order

1. **RR-001 Roadmap/status reconciliation** — clear conflicting source-of-truth state.
2. **RR-002 Privacy / POPIA completion** — legal/data-rights controls before broader live use.
3. **RR-006 Security posture deepening** — threat model, dependency/secrets scan, pen-test checklist.
4. **RR-016 Operational drills** — backup/restore/rollback/incident proof.
5. **RR-003 Coverage + CI + route consolidation** — ensure release-blocking checks are visible and current.
6. **RR-010 Beta outcome reporting** — only after a real beta observation period has evidence.

## Anti-scope-creep rule

The next implementation slice must cite one or more `RR-###` IDs from this register. Work that does not cite an `RR-###` ID is considered new work and must be rejected until the register is updated through a reconciliation PR.
