---
title: "ADR-019 — Roadmap After Production Readiness Baseline"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-019 — Roadmap After Production Readiness Baseline

**Status**: Accepted  
**Date**: 2026-06-12  
**Decision Owner**: Engineering Lead  
**Phase**: 10

---

## Context

The production-readiness baseline has been achieved. This ADR defines the strategic direction for post-baseline roadmap development, ensuring we maintain velocity while managing technical debt.

---

## Decision

### Post-Baseline Principles

1. **Stabilization First**: New features wait 2 weeks after release while monitoring for regressions
2. **Batched Releases**: Fortnightly release cycles with explicit changelog
3. **Technical Debt Quota**: 20% of engineering capacity reserved for debt reduction
4. **ADRs Required**: All architectural decisions >P1 require ADRs before implementation

### Roadmap Priorities

| Priority | Focus Area | Timeline |
|----------|-----------|----------|
| P0 | Stability & monitoring | Ongoing |
| P1 | Content expansion (more subjects) | Q3 2026 |
| P1 | Mobile experience improvements | Q3 2026 |
| P2 | Offline mode | Q4 2026 |
| P2 | Voice input for accessibility | Q4 2026 |

### Feature Gates

- All P1+ features require:
  - [ ] ADR written and approved
  - [ ] Technical design document
  - [ ] Test coverage plan
  - [ ] Security review (for data-handling features)

---

## Consequences

### Positive

- Clear boundaries on feature development
- Explicit time allocation for technical debt
- Structured decision process via ADRs
- Predictable release cadence

### Negative

- Slightly slower feature velocity
- Requires discipline to enforce ADR process

---

## References

- Production Readiness Baseline: `docs/backlog/production_readiness/20_final_release-blocker_checklist.md`
- Post-Baseline Roadmap: `docs/backlog/production_readiness/19_roadmap_after_production-readiness_baseline.md`
- Architecture Contract: `docs/roadmap/post_baseline_roadmap_architecture_contract.md`