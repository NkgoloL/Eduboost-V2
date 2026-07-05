---
title: RR-007 Product Completeness / Quality Gates
status: active
owner: engineering
reviewers: [roadmap-reconciliation, release-management, documentation-governance]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make roadmap-reconciliation-check
code_anchors: [docs/roadmap/reconciliation, scripts/roadmap_reconciliation]
---

# RR-007 Product Completeness / Quality Gates

**RR item:** RR-007  
**Register source:** `docs/roadmap/reconciliation/outstanding_work_register.md`  
**Canonical area:** Frontend/product completeness.

## Scope

RR-007 records the product quality gates that must exist before broader beta or public release claims:

- Playwright in CI is visible and policy-bound;
- Grades R-3 and 5-7 content expansion is documented as roadmap work, not silently started;
- load testing is planned with learner journey scenarios;
- accessibility audit expectations are recorded;
- PWA offline verification expectations are recorded;
- multilingual lesson proof expectations are recorded;
- Supabase-versus-raw-Postgres decision is recorded as an ADR.

## Non-goals

- Do not authorise production release, public beta, deployment, release tagging, or runtime KG implementation.
- Do not start Grades R-3 or 5-7 content production under this slice.
- Do not claim load, accessibility, PWA, or multilingual results beyond the evidence captured in RR-007.

## Closure rule

RR-007 is closed only when `rr_007_product_quality_gates_record.json` records the required flags and the verifier returns `valid: true` from clean `master`.
