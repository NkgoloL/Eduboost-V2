# Build Plan

**Last updated:** 2026-06-12
**Authoritative execution plan:** ../docs/roadmap/roadmap.md (17 phases)
**Live task tracker:** ../docs/todos/todo.md (North Star)

This file is now a summary index. The authoritative build execution plan is ../docs/roadmap/roadmap.md (17 phases, Phase 0-16). Day-to-day task tracking lives in ../docs/todos/todo.md.

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

- Backend: 2051 unit tests passing, 355 API routes, 35 Alembic migrations
- Grade 4 Mathematics: 120 diagnostic items + 24 lessons live
- 22 domain modules, 28 API routers, Content Factory ETL pipeline
- POPIA consent/audit/erasure/export workflows (partial -- Phase 8)
- Grafana dashboards, Prometheus metrics, structured logging
- JWT auth with keyring, token revocation, Redis-backed

## Status Legend

- Not started
- In progress
- Complete (repository-side)
- CI verified
- Staging verified
- Production verified

Update ../docs/roadmap/roadmap.md and ../docs/todos/todo.md for detailed status. This file is the high-level index.
