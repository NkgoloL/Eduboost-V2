# Project Overview

**Last updated:** 2026-06-09
**Current state:** ../docs/roadmap/roadmap.md Phase 0 (in progress), quality gate RED (9/11)
**Live trackers:** ../docs/roadmap/roadmap.md (17 phases), ../docs/todos/todo.md (North Star tasks)

EduBoost V2 is an AI-powered adaptive learning platform for primary school learners in South Africa (Grades R-7), designed to accelerate mastery of CAPS learning outcomes through personalized, evidence-based learning paths.

## Problem Solved

South African primary learners face persistent achievement gaps. EduBoost solves this through:
- **Intelligent Assessment:** IRT-based diagnostics estimate learner ability accurately
- **Personalized Paths:** AI generates study plans aligned to CAPS prerequisites
- **Adaptive Practice:** Difficulty adjusted continuously based on performance
- **Parent Visibility:** Non-technical guardians see progress and actionable insights
- **Content Scale:** Admin pipeline ingests and validates CAPS-aligned content

## Core Features

### Learner Features
- Onboarding (Ether questionnaire, ~3 minutes)
- Diagnostic Assessment (IRT adaptive test, 3PL model)
- Study Plan (AI-generated, CAPS-aligned)
- Adaptive Practice (difficulty proximity + spaced repetition)
- Progress and Mastery tracking with heatmaps

### Parent Features
- Dashboard with mastery heatmap
- Progress tracking and trends
- Actionable insights

### Admin Features
- Content Factory ETL pipeline
- Quality review and approval workflow
- Staging to Production promotion
- Learner consent and data rights (POPIA)

## Current Implementation Status

**Repository-side (not CI/staging/production verified):**
- Backend: 2051 unit tests passing, 355 API routes, 22 domain modules
- Content: Grade 4 Mathematics launch slice (120 items + 24 lessons) live
- ETL: Content Factory pipeline with CAPS source ingestion
- Auth: JWT with keyring, token revocation, Redis-backed
- POPIA: Consent, audit, erasure, export workflows (partial)
- Monitoring: Grafana dashboards, Prometheus metrics

**Known critical gaps (see ../docs/roadmap/roadmap.md):**
- P0: Practice sessions unauthenticated; in-memory state (Phase 2)
- P0: Frontend build broken: dexie, TypeScript, Vitest (Phase 3)
- P0: Python version inconsistency (Phase 4)
- P1: 40.9% test coverage (Phase 9)
- P1: ARQ durable jobs not wired (Phase 6)

## Success Criteria

1. Onboarding: <3 minutes
2. Diagnostic: Reliable estimate in <20 items
3. Study Plans: Generated in <5 seconds
4. Practice: <200ms response latency
5. Content Coverage: >80% of CAPS topics with at least 5 items each
6. POPIA: 100% of learner data access audited
7. Availability: >99.5% uptime

## Technical Stack (Verified)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | FastAPI (Python 3.12.3 target) | 355 routes |
| Database | PostgreSQL 15+ | 35 Alembic migrations |
| Cache/Jobs | Redis + ARQ | Phase 6 pending |
| Frontend | Next.js 15.5, React 18, TypeScript 5.4 | Phase 3 fixes needed |
| LLM | Groq, Anthropic, Gemini, HuggingFace | Multi-provider gateway |
| Testing | pytest, Vitest, Playwright | 2051 unit / E2E broken |
| Monitoring | Prometheus, Grafana | 3 dashboards |
| Infrastructure | Docker Compose, Azure ACA (planned) | Phase 7: deployment hardening |

## Project Governance

- **Execution plan:** ../docs/roadmap/roadmap.md (17 phases, Phase 0-16)
- **Task tracker:** ../docs/todos/todo.md (North Star, 5 gap categories + beta)
- **Quality gate:** docs/current_state.md (currently RED, 9/11)
- **Operating model:** docs/operations/recommended_operating_model.md
- **Architecture:** docs/architecture/V2_ARCHITECTURE.md
- **Audit baseline:** audits/deep_app_audit/implementation_reality_report.md
- **Gap analysis:** Eduboost-V2_Gap_Analysis.md (2026-06-09)

## Next Milestones

1. Complete Phase 0 (branch, evidence) -- in progress
2. Complete Phase 1 (compile + lint fixes) -- next
3. Complete Phase 2 (practice session auth) -- P0
4. Complete Phase 3 (frontend build health) -- P0
5. CI green on all release-blocking gates -- Phase 9
6. Staging environment execution evidence -- Phase 16
7. Controlled beta with real learners -- Phase 16
8. Go/no-go production decision -- Phase 16

**EduBoost is NOT public-beta-ready or production-ready.**
