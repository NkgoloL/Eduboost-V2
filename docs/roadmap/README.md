# EduBoost Roadmap Documentation

This directory contains the authoritative roadmap documentation for the EduBoost V2 programme.

## 📋 North-Star Document

**`EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md`** — This is the controlling programme baseline. It defines the complete Phase 0–13 lifecycle, phase gates, evidence requirements, and beta success criteria.

All other roadmap documents are subordinate to this baseline.

## Directory Structure

```
docs/roadmap/
├── EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md  # 📌 NORTH-STAR
├── PHASE_STATUS_REGISTER.md                                    # Current phase status
├── PROCESS_DISCIPLINE.md                                        # Process guidance
├── execution/                                                   # Phase execution plans & reports
│   ├── phase_execution_plan_template.md
│   ├── phase_implementation_report_template.md
│   ├── phase_audit_report_template.md
│   ├── phase_evidence_pack_template.md
│   ├── atlas/                                                   # Active sprint namespace
│   │   ├── phase_01_execution_plan.md
│   │   ├── phase_01_implementation_report.md
│   │   └── ...
│   ├── phase_00_execution_plan.md                             # (to be created)
│   ├── phase_00_implementation_report.md                       # (to be created)
│   └── ... (phases 1-13)
├── domains/                                                     # Domain-specific roadmaps
└── *.md                                                         # Supporting documents
```

Active sprint namespace: `docs/roadmap/execution/atlas/`

## Phase Overview

| Phase | Name | Status |
|:---:|---|:---:|
| 0 | Environment and Reproducibility | Not Started |
| 1 | Batch AI Content Generation | Verified Complete |
| 2 | Semantic Retrieval | Verified Complete |
| 3 | Educator Consensus and Content Governance | In Progress |
| 4 | IRT Quality and Self-Healing Controls | In Progress |
| 5 | Learner AI Tutor | In Progress |
| 6 | Monitoring, Budget, and Production Hardening | In Progress |
| 7 | Beta Content Coverage and Language Readiness | In Progress |
| 8 | Architecture and Codebase Assurance | In Progress |
| 9 | CI Authority and Reproducible Evidence | In Progress |
| 10 | Product Readiness | In Progress |
| 11 | Operations Readiness | In Progress |
| 12 | External Review and Governance | Not Started |
| 13 | Controlled Beta | Not Started |

## Key Documents

| Document | Purpose |
|---|---|
| `EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md` | Master programme plan (Phase 0–13) |
| `PHASE_STATUS_REGISTER.md` | Real-time status of all phases |
| `execution/phase_*_execution_plan.md` | Detailed execution plan per phase |
| `execution/phase_*_implementation_report.md` | Post-implementation reconciliation |

## Four-Artefact Control Set

Each phase requires a **complete four-artefact control set** before it can be marked `Verified Complete`:

1. **Execution Plan** — Defines scope, acceptance criteria before work starts
2. **Implementation Report** — Reconciles planned vs actual delivery
3. **Evidence Index/Pack** — Attributable proof for every criterion
4. **Phase Audit Report** — Independent verification and closure verdict

See the North-Star document for the complete protocol.

## Evidence Repository

Phase evidence is stored in: `docs/release-evidence/atlas/phase-<NN>/`

## Getting Started

1. **Read the North-Star document first** — `EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md`
2. **Check current phase status** — `PHASE_STATUS_REGISTER.md`
3. **Use templates** — `execution/phase_*_template.md`
4. **Follow the protocol** — No phase starts without an approved execution plan

## Related Documentation

- Release evidence: `docs/release-evidence/`
- Technical documentation: `docs/`
- Tests: `tests/`
- Architecture: `docs/architecture/`

<!-- KG000_FORMAL_ROADMAP_APPROVAL:start -->
## Knowledge Graph roadmap stream

The reconciled RR register is closed through RR-018. New KG work starts only through the approved Knowledge Graph roadmap stream:

- [KG-0 Formal KG Roadmap Approval](knowledge_graph/kg_000_formal_kg_roadmap_approval.md)
- [KG Implementation Roadmap](knowledge_graph/kg_implementation_roadmap.md)
- [KG Roadmap Register](knowledge_graph/kg_roadmap_register.json)

Next after KG-0: `KG-1 — CAPS graph foundation`.
<!-- KG000_FORMAL_ROADMAP_APPROVAL:end -->
