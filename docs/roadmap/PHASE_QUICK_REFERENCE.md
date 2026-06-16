# EduBoost 13-Phase Quick Reference

Active sprint namespace: `atlas`

## Phase Sequence

```
Audit Remediation (R)
    │
    ├───────────────┐
    ▼               │
Phase 0  Environment and Reproducibility
    ▼               │
Phase 1  Batch AI Content Generation
    ▼               │
Phase 2  Semantic Retrieval
    ▼               │
Phase 3  Educator Consensus and Content Governance
    ▼               │
Phase 4  IRT Quality and Self-Healing Controls
    ▼               │
Phase 5  Learner AI Tutor
    ▼               │
Phase 6  Monitoring, Budget, and Production Hardening
    ▼               │
Phase 7  Beta Content Coverage and Language Readiness
    └──────┬────────┘
           ▼
Phase 8  Architecture and Codebase Assurance
           ▼
Phase 9  CI Authority and Reproducible Evidence
           ▼
Phase 10 Product Readiness
           ▼
Phase 11 Operations Readiness
           │
Phase 12 External Review and Governance
           │
           ▼
Phase 13 Controlled Beta
```

## Phase Summary

| Phase | Name | Objective | Provisional Duration |
|:---:|---|---|---:|
| 0 | Environment and Reproducibility | Reproducible, fail-closed environment | 1–2 weeks |
| 1 | Batch AI Content Generation | Production-safe provider abstraction | 2–4 weeks |
| 2 | Semantic Retrieval | Accurate grounding retrieval | 1–2 weeks |
| 3 | Educator Consensus | Independent content review | 1–3 weeks |
| 4 | IRT Quality | Item calibration and self-healing | 2–3 weeks |
| 5 | Learner AI Tutor | Safe interactive learner support | 2–3 weeks |
| 6 | Production Hardening | Observable, cost-controlled ops | 1–2 weeks |
| 7 | Beta Content | Content slice for controlled beta | 3–6 weeks |
| 8 | Architecture Assurance | Durable architecture and ownership | 5–8 weeks |
| 9 | CI Authority | Authoritative quality control | 2–3 weeks |
| 10 | Product Readiness | Usable, accessible beta experience | 3–4 weeks |
| 11 | Operations Readiness | Observable, supportable system | 2–3 weeks |
| 12 | External Review | Independent security/privacy review | 4–8 weeks |
| 13 | Controlled Beta | Validate with real users | 5–6 weeks |

**Total provisional duration: 27–42 weeks**

## Required Artefacts per Phase

Each phase must produce:

```
docs/roadmap/execution/
├── phase_<NN>_execution_plan.md      # Before starting
├── phase_<NN>_implementation_report.md  # Before closure

docs/release-evidence/atlas/phase-<NN>/
├── phase_<NN>_evidence_index.md     # Before audit
└── phase_<NN>_audit_report.md        # Independent verification
```

## Current Phase Status

| Phase | Status | Next Milestone |
|:---:|---|---|
| 0 | Not Started | Create execution plan |
| 1 | Verified Complete | Prepare Phase 2 execution plan |
| 2 | Verified Complete | Prepare Phase 3 execution plan |
| 3 | In Progress | Complete evidence pack |
| 4 | In Progress | Complete evidence pack |
| 5 | In Progress | Complete evidence pack |
| 6 | In Progress | Complete evidence pack |
| 7 | In Progress | Complete evidence pack |
| 8 | In Progress | Complete evidence pack |
| 9 | In Progress | Complete evidence pack |
| 10 | In Progress | Complete evidence pack |
| 11 | In Progress | Complete evidence pack |
| 12 | Not Started | Execution plan ready |
| 13 | Not Started | Execution plan ready |

## Beta Success Criteria (Phase 13)

### Engagement
- Diagnostic completion: >65% (target: 80%)
- Lesson completion: >55% (target: 70%)
- 7-day retention: >25% (target: 40%)

### Educational
- Mastery gain: ≥5pp minimum (target: 10pp)
- Positive change: ≥50% learners (target: 65%)

### Reliability
- Availability: ≥99.0% (target: 99.5%)
- P95 latency: <1s (target: <500ms)
- Critical journey success: ≥95% (target: 98%)

### Safety
- Critical incidents: 0
- Unsafe AI responses: 0
- Unapproved content served: 0

## Decision Bands

- **Go** — All targets met, or minor misses with all minimums met
- **Extend** — All minimums met, but targets missed
- **No-Go** — Any non-waivable control fails

## Key Contacts

| Role | Accountability |
|---|---|
| Product Owner | Scope, outcomes, cohort |
| Engineering Lead | Architecture, implementation, CI |
| Security Owner | Security gates, vulnerability treatment |
| Compliance Owner | POPIA, DPAs, privacy workflows |
| Content Owner | CAPS alignment, educator review |
| Operations Owner | Monitoring, backup, restore, on-call |
| Release Manager | Phase gates, evidence, deployment |

## Links

- Full lifecycle plan: `docs/roadmap/EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md`
- Phase status: `docs/roadmap/PHASE_STATUS_REGISTER.md`
- Templates: `docs/roadmap/execution/phase_*_template.md`
- Evidence: `docs/release-evidence/`
