# docs/DOC Alignment Report

Generated: 2026-06-22

## Summary

The uploaded codebase contained 37 Markdown controlled documents under `docs/DOC` plus a state-of-system DOCX. The Markdown set was not aligned to EduBoost V2: a static scan found 243 hits for stale policy-advisory terms including `stale policy-advisory system`, `graph/document database`, `Graph-search architecture`, `external ML platform`, `API gateway`, policy-query flows and retraining-pipeline claims.

This replacement pack rewrites the controlled document set around the supplied EduBoost V2 implementation:

- FastAPI V2 modular monolith in `app/api_v2.py`.
- Next.js frontend in `app/frontend` using pnpm.
- PostgreSQL/Alembic persistence and Redis/ARQ jobs.
- Diagnostics, IRT quality, lessons, tutor, gamification, parent portal and study plans.
- POPIA consent and data-subject rights.
- Content Factory scope/coverage registry and gated content promotion.
- Evidence-based release, security, compliance and ATO discipline.

## Files rewritten

| File | Status |
|---|---|
| `docs/DOC/Tier 1 - Requirements & Concept/DOC-01_System-Requirements-Specification_(SRS).md` | Rewritten and aligned |
| `docs/DOC/Tier 1 - Requirements & Concept/DOC-02_System-Subsystem-Specification_(SSS).md` | Rewritten and aligned |
| `docs/DOC/Tier 1 - Requirements & Concept/DOC-03_Concept-of-Operations_(ConOps).md` | Rewritten and aligned |
| `docs/DOC/Tier 1 - Requirements & Concept/DOC-04_Stakeholder-Requirements-Definition_(StRS).md` | Rewritten and aligned |
| `docs/DOC/Tier 1 - Requirements & Concept/DOC-05_Business-Requirements-Document_(BRD).md` | Rewritten and aligned |
| `docs/DOC/Tier 1 - Requirements & Concept/DOC-06_Use-Case-Specification_(UCS).md` | Rewritten and aligned |
| `docs/DOC/Tier 2 - Architecture & Design/DOC-07_Software-Design-Document_(SDD).md` | Rewritten and aligned |
| `docs/DOC/Tier 2 - Architecture & Design/DOC-08_Software-Architecture-Document_(SAD).md` | Rewritten and aligned |
| `docs/DOC/Tier 2 - Architecture & Design/DOC-09_Interface-Control-Document_(ICD).md` | Rewritten and aligned |
| `docs/DOC/Tier 2 - Architecture & Design/DOC-10_Database-Design-Document_(DDD).md` | Rewritten and aligned |
| `docs/DOC/Tier 2 - Architecture & Design/DOC-11_Data-Dictionary_(DD).md` | Rewritten and aligned |
| `docs/DOC/Tier 2 - Architecture & Design/DOC-12_Security-Architecture-Document_(SecAD).md` | Rewritten and aligned |
| `docs/DOC/Tier 3 - Implementation & Code/DOC-13_API-Reference.md` | Rewritten and aligned |
| `docs/DOC/Tier 3 - Implementation & Code/DOC-14_Coding-Standards-Document_(CSD).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-15_Test-Plan_(TP).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-16_Test-Design-Specification_(TDS).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-17_Test-Case-Specification_(TCS).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-18_Test-Procedures_(TestProc).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-19_Test-Item-Transmittal-Report_(TITR).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-20_Test-Summary-Report_(TSR).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-21_Software-Quality-Assurance-Plan_(SQAP).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-22_Quality-Metrics-Report_(QMR).md` | Rewritten and aligned |
| `docs/DOC/Tier 4 - Testing & Quality Assurance/DOC-23_Code-Review-Checklist_and_Standards_(CRS).md` | Rewritten and aligned |
| `docs/DOC/Tier 5 - Deployment & Operations/DOC-24_Deployment-Guide.md` | Rewritten and aligned |
| `docs/DOC/Tier 5 - Deployment & Operations/DOC-25_Operational-Manual_(OpsMan).md` | Rewritten and aligned |
| `docs/DOC/Tier 5 - Deployment & Operations/DOC-26_Disaster-Recovery-Plan_(DRP).md` | Rewritten and aligned |
| `docs/DOC/Tier 5 - Deployment & Operations/DOC-27_Installation-and-Configuration-Guide_(ICG).md` | Rewritten and aligned |
| `docs/DOC/Tier 5 - Deployment & Operations/DOC-28_Release_Notes.md` | Rewritten and aligned |
| `docs/DOC/Tier 6 - Security & Compliance/DOC-29_Security-Plan_(SecPlan).md` | Rewritten and aligned |
| `docs/DOC/Tier 6 - Security & Compliance/DOC-30_Threat-Model-Document_(TMD).md` | Rewritten and aligned |
| `docs/DOC/Tier 6 - Security & Compliance/DOC-31_Privacy-Impact-Assessment_(PIA).md` | Rewritten and aligned |
| `docs/DOC/Tier 6 - Security & Compliance/DOC-32_Compliance_Matrix.md` | Rewritten and aligned |
| `docs/DOC/Tier 6 - Security & Compliance/DOC-33_Incident-Response-Plan_(IRP).md` | Rewritten and aligned |
| `docs/DOC/Tier 6 - Security & Compliance/DOC-34_Authority-to-Operate_(ATO).md` | Rewritten and aligned |
| `docs/DOC/Tier 7 - Project Management/DOC-35_Project-Management-Plan_(PMP).md` | Rewritten and aligned |
| `docs/DOC/Tier 7 - Project Management/DOC-36_Risk-Register_(RR).md` | Rewritten and aligned |
| `docs/DOC/Tier 7 - Project Management/DOC-37_Change-Management-Plan_(CMP).md` | Rewritten and aligned |


## Path note

The original folder/file names contained spelling errors, and this pass normalizes the documented paths to the corrected spellings while keeping the content intact.

## Validation performed

- Static route inventory generated from router decorators.
- ORM table inventory generated from `app/models` classes.
- Frontend package facts read from `app/frontend/package.json`.
- Content Factory scope/coverage facts read from `data/content_factory/*.json`.
- Stale content scan run before and after replacement.

## Post-apply checks

```bash
rg -n "DBE AI Expert System|Cosmos DB|Knowledge Graph|Azure ML|APIM" docs/DOC --glob "!DOC_ALIGNMENT_REPORT.md"
python3 scripts/generate_openapi.py --check
make test-fast
cd app/frontend && pnpm run env-check && pnpm run lint && pnpm run type-check && pnpm run test
```
