# Build Plan

**Status:** Historical build-plan summary; not current execution authority.
**Authoritative execution plan:** `../docs/roadmap/README.md` and the active PRD-11 register.
**Live task tracker:** `../docs/current_state.md`

This file is retained as historical context. Current execution status and next work must come from the canonical current-state and production-readiness documents.

## Current Phase Status

| Phase | Name | Priority | Status |
|-------|------|----------|--------|
| 0 | Branch, Evidence, Artifacts | -- | Complete (repository-side) |
| 1 | Release-Blocking Correctness Fixes | P0 | Complete (2026-06-09) |
| 2 | Practice Session Security & Durability | P0 | Complete (2026-06-09, merged PR #220) |
| 3 | Frontend Build and Test Health | P0 | Complete (2026-06-10, merged PR #219) |
| 4 | Runtime and Environment Alignment | P0 | Complete (2026-06-10) |
| 5 | Migrations and Schema Management | P1 | Complete (2026-06-10) |
| 6 | Durable Background Jobs | P1 | Complete (2026-06-12) — live-verified on Docker stack |
| 7 | Deployment and Security Hardening | P1 | ✅ Complete (2026-06-12) |
| 8 | Privacy and Authorization Completion | P1 | Not started |
| 9 | Coverage, CI, and Evidence Renewal | P1 | Not started |
| 10 | Workspace Hygiene and Auditability | P2 | Not started |
| 11 | Technical Debt Burn-Down | P2 | Not started |
| 12 | Security Posture Deepening | P2 | Not started |
| 13 | Frontend and Product Completeness | P2 | Not started |
| 14 | Operational Readiness | P2 | Not started |
| 15 | Governance and Process | P2 | Not started |
| 16 | Beta Period with Real Learner Feedback | -- | Not started |

## Verified Implementation Baseline

The following are already implemented and tested locally (not CI-verified):

- Backend: FastAPI V2 runtime; current route, test, and migration facts come from executable evidence
- Grade 4 Mathematics: 120 diagnostic items + 24 lessons live
- 22 domain modules, 28 API routers, Content Factory ETL pipeline
- POPIA consent/audit/erasure/export workflows; current completeness is governed by the active readiness evidence
- Grafana dashboards, Prometheus metrics, structured logging
- JWT auth with keyring, token revocation, Redis-backed

## Status Legend

- Not started
- In progress
- Complete (repository-side)
- CI verified
- Staging verified
- Production verified

Update the canonical current-state and production-readiness records for detailed status. This file is historical context only.
