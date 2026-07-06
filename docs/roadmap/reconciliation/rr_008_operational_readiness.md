---
title: RR-008 Operational Readiness
status: authority
owner: operations
reviewers: [roadmap-reconciliation, release-management, documentation-governance]
audience: developer, operator
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# RR-008 Operational Readiness

**RR item:** RR-008  
**Register source:** `docs/roadmap/reconciliation/outstanding_work_register.md`  
**Canonical area:** Operational readiness

## Scope

RR-008 records the canonical operational-readiness baseline before broader beta, public beta, production deployment, or production-release claims are made.

It covers:

- incident response runbook linkage;
- learner-journey SLO definitions;
- capacity planning assumptions;
- LLM cost model and cost guardrails;
- Grafana dashboard and alert linkage.

## Non-goals

- RR-008 does not execute backup, restore, rollback, or incident drills. Those remain outstanding under `RR-016`.
- RR-008 does not authorise production release, deployment, release tags, public beta, or runtime KG implementation.
- RR-008 does not replace external approval, legal review, POPIA review, or content review work.

## Closure rule

RR-008 is closed only when `rr_008_operational_readiness_record.json` records all required evidence flags and the verifier returns `valid: true` from clean `master`.
