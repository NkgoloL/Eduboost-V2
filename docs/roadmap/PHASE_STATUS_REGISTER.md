# EduBoost Phase Status Register

**Document version:** 3.0
**Date:** 2026-07-02
**Canonical control root:** `roadmap-reconciliation`
**Current reconciliation item:** `RR-001 Atlas phase status reconciliation`

## Supersession notice

This document is retained as a historical Atlas phase-status register, but it is **not the current implementation queue** and is **not the current release-authority source**.

The previous version of this register described the overall programme as reconciliation-in-progress, blocked Phase 8, and blocked controlled beta. That language is now superseded by the reconciled roadmap register and current evidence records.

Current work selection is governed by:

```text
docs/roadmap/reconciliation/outstanding_work_register.md
```

Current roadmap reconciliation authority is recorded at:

```text
docs/roadmap/reconciliation/roadmap_reconciliation_record.json
docs/roadmap/reconciliation/rr_001_atlas_phase_status_record.json
```

Next implementation work must cite an RR-### item from the outstanding-work register. Work without an `RR-###` citation is new unreconciled work and is not authorised.

Phase 18-21 beta-operations records are auxiliary governance records, not canonical roadmap phases.

## Programme status

| Segment | Reconciled status |
|---|---|
| Overall programme | **Reconciled to RR outstanding-work register** |
| Historical Atlas phases 0-7 | **Historical records retained; not current implementation queue** |
| Historical Atlas Phase 8 | **Superseded by technical-audit remediation closure and RR register** |
| Controlled beta readiness / operations | **Represented by runtime-readiness and beta-operations evidence records; remaining beta outcome work is RR-010** |
| New work | **Frozen unless it cites an RR-### item** |

## Historical Atlas phase register

The rows below are preserved for traceability. They no longer block or authorise current implementation work by themselves.

| Phase | Name | Historical status | Current classification | Current action |
|:---:|---|---|---|---|
| 0 | Environment and Reproducibility | Planning / not independently closed under old four-artifact rule | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 1 | Batch AI Content Generation | Verified complete on feature-branch evidence in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 2 | Semantic Retrieval | Complete / closure review in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 3 | Educator Consensus and Content Governance | Complete / governance revalidation in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 4 | IRT Quality and Self-Healing | Evidence repair / closure review in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 5 | Safe Learner AI Tutor | Audit review in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 6 | Durable AI Operations and Budget Authority | Verification pending in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 7 | Curriculum Coverage and Training Governance | Verification pending in old register | Historical Atlas record | Preserve for history; future work selected through RR register. |
| 8 | Architecture and Codebase Assurance | Previously blocked by old Atlas reconciliation rule | Superseded by RR register | Old blocked state replaced by technical-audit remediation closure and the reconciled outstanding-work register. |

## Current source-of-truth map

| Concern | Current source |
|---|---|
| Outstanding implementation work | `docs/roadmap/reconciliation/outstanding_work_register.md` |
| Roadmap new-work freeze | `docs/roadmap/reconciliation/roadmap_new_work_freeze.md` |
| Phase 18-21 classification | `docs/roadmap/reconciliation/phase_18_to_21_governance_classification.md` |
| RR-001 matrix | `docs/roadmap/reconciliation/rr_001_atlas_phase_status_matrix.json` |
| Technical audit closure | `docs/roadmap/execution/technical_audit_remediation/technical_audit_closure_record.json` |
| Controlled beta readiness | `docs/roadmap/execution/runtime_readiness/phase_17_controlled_beta_readiness_record.json` |
| Controlled beta operations governance | `docs/operations/beta/` and runtime-readiness records |

## Boundary

This register reconciliation does not authorise:

- production release;
- deployment;
- release tagging;
- public beta;
- new unreconciled work;
- runtime KG implementation.

The knowledge-graph direction remains an architectural north star only. It is not runtime implementation scope unless explicitly authorised by a future RR-cited roadmap item.
