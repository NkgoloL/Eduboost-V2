---
title: Phase 10 Execution Plan — Post-Production Product Documentation & Operational Tooling
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 10 Execution Plan — Post-Production Product Documentation & Operational Tooling

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: ✅ Complete for docs/hygiene; dependency conflicts recorded
**Branch**: `phase-10/post-production-product-docs`
**Base**: `origin/master`
**Scope**: Complete the remaining high-priority non-human-decision items from the critical path and post-baseline roadmap, focusing on product documentation, dependency hygiene, ADR consolidation, and operational tooling.

---

## 2026-06-14 Audit Note

Phase 10 delivered the product, ADR, governance, and operational runbook
artifacts claimed in the implementation report. The missing proof was
workspace-hygiene evidence. That proof is now captured in
`docs/release/phase_10_evidence.md`.

Dependency hygiene remains partial: Make targets now exist, but `make
deps-conflicts` reports local installed-package conflicts for pydantic,
websockets, and rich transitive requirements.

---

## Pre-Conditions

- [x] Phase 9 (Release-Blocker Checklist) merged to `master`
- [x] All 20 production-readiness backlog documents have actionable items closed
- [x] Branch `phase-10/post-production-product-docs` created from `master`

---

## Inventory of Remaining Work

The production-readiness baseline is complete. The remaining work comes from two sources:

1. **Critical path** (`docs/backlog/critical_path.md`) — high-priority items that are not blocked by human decisions
2. **Post-baseline roadmap** (`docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md`) — ADR and architecture documentation
3. **Own discovery** — dependency hygiene, operational documentation

---

## Work Groups

### H.1 — Product Documentation [high]

**Source:** TODO-335 from critical_path.md

- [x] Create `docs/product/product_overview.md` — what EduBoost is, who it serves, core features
- [x] Create `docs/product/parent_guide.md` — how guardians manage consent, monitor progress, export data
- [x] Create `docs/product/learner_guide.md` — how learners take diagnostics, access lessons, practice
- [x] Create `docs/product/teacher_guide.md` — how teachers view assigned learners, review progress, access reports
- [x] Create `docs/product/faq.md` — general FAQ covering pricing, data privacy, technical requirements
- [x] Create `docs/product/pricing_faq.md` — free tier, parent plan, school plan details
- [x] Create `docs/product/ai_transparency_faq.md` — how AI is used, what data is sent to LLMs, safety measures

**Evidence:** 7 product documentation files in `docs/product/`

### H.2 — Dependency Hygiene [high]

**Source:** TODO-028 from critical_path.md

- [x] Audit all `requirements*.txt` files for duplicates, conflicts, unused entries
- [x] Verify `requirements.txt`, `requirements-dev.txt`, `requirements-docs.txt`, `requirements-ml.txt` have clean separation
- [x] Document canonical dependency paths in `docs/operations/dependency_management.md`
- [x] Check for outdated major-version dependencies (report-oriented target added)
- [x] Add Makefile targets: `make deps-check`, `make deps-outdated`

**Evidence:** `docs/operations/dependency_management.md`, updated requirements files

### H.3 — Post-Baseline ADR & Architecture [verify]

**Source:** Doc #19 repository-side implementation evidence

- [x] Create `docs/adr/ADR-019-roadmap-after-production-readiness-baseline.md` — decision record for post-baseline strategy
- [x] Create `docs/roadmap/post_baseline_roadmap_architecture_contract.md` — architecture implications of post-baseline roadmap
- [x] Create `docs/roadmap/production_readiness_baseline_boundary_contract.md` — documents what is and isn't in the production readiness baseline
- [x] Update doc #19 checkboxes to `[x]` after evidence files exist

**Evidence:** 3 ADR/roadmap documents

### H.4 — Branch Protection Documentation [high]

**Source:** TODO-024 from critical_path.md

- [x] Document required branch protection settings in `docs/repository/governance.md`:
  - Require PR review (at least 1 reviewer)
  - Required checks must pass before merging
  - No force-push to `master`
  - No branch deletion
  - Signed commits (recommended)
- [x] Document the CI/CD workflow expectations for contributors

**Evidence:** Updated `docs/repository/governance.md`

### H.5 — Operational Runbook Supplements [medium]

**Source:** Complement to Phase 9 tabletop exercise

- [x] Create `docs/operations/runbooks/database_outage.md` — step-by-step for DB failure recovery
- [x] Create `docs/operations/runbooks/llm_provider_outage.md` — fallback provider activation procedure
- [x] Create `docs/operations/runbooks/security_incident.md` — breach detection and containment steps
- [x] Create `docs/operations/runbooks/consent_sla_breach.md` — erasure/export SLA escalation procedure

**Evidence:** 4 runbook files in `docs/operations/runbooks/`

### H.6 — Post-Baseline Roadmap Evidence Update [verify]

- [x] Mark all `[verify]` items in `docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md` as `[x]` where evidence files exist
- [x] Add reference links to the newly created ADR and architecture contract docs

---

## Execution Order

```
Week 1:  H.1 (product docs) — 7 files, mostly writing
         H.4 (branch protection) — 1 file, quick
Week 2:  H.2 (dependency hygiene) — audit + fix + document
         H.5 (operational runbooks) — 4 files
Week 3:  H.3 (post-baseline ADR) — 3 decision records
         H.6 (evidence update) — checkbox maintenance
```

---

## Definition of Done

- [x] 7 product documentation files created in `docs/product/`
- [x] Dependency audit command targets added and findings documented in `docs/operations/dependency_management.md`
- [x] 3 ADR/roadmap documents created for post-baseline strategy
- [x] Branch protection requirements documented in `docs/repository/governance.md`
- [x] 4 operational runbooks created in `docs/operations/runbooks/`
- [x] Doc #19 checkboxes updated with evidence references
- [x] All files committed and pushed to `phase-10/post-production-product-docs`
- [x] Implementation report written
- [x] PR merged to `master`
