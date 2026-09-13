# Project Overview

**Status:** Historical context; not a current-state authority.
**Current state:** See `../docs/current_state.md` and `../docs/roadmap/README.md`.
**Live tracker:** `../docs/roadmap/production_readiness/prd11_production_release_register.json`

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
- Backend: FastAPI V2 runtime; route and test counts must come from current executable evidence
- Content: Grade 4 Mathematics launch slice (120 items + 24 lessons) live
- ETL: Content Factory pipeline with CAPS source ingestion
- Auth: JWT with keyring, token revocation, Redis-backed
- POPIA: Consent, audit, erasure, export workflows (partial)
- Monitoring: Grafana dashboards, Prometheus metrics

**Known gaps:** See the current production-readiness register and generated evidence. The phase list is historical and is not active next-work authority.

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
| Backend | FastAPI V2 (Python 3.12.3 target) | See generated route inventory |
| Database | PostgreSQL 16/pgvector | See current migration evidence |
| Cache/Jobs | Redis + ARQ | See current runtime evidence |
| Frontend | Next.js, React, TypeScript | See current frontend manifest and evidence |
| LLM | Groq, Anthropic, Gemini, HuggingFace | Multi-provider gateway |
| Testing | pytest, Vitest, Playwright | See current test and frontend evidence |
| Monitoring | Prometheus, Grafana | 3 dashboards |
| Infrastructure | Docker Compose, Azure ACA/Render configuration | Deployment authority remains gated |

## Project Governance

- **Execution plan:** ../docs/roadmap/roadmap.md (17 phases, Phase 0-16)
- **Task tracker:** ../docs/todos/todo.md (North Star, 5 gap categories + beta)
- **Quality gate:** docs/current_state.md (currently RED, 9/11)
- **Operating model:** docs/operations/recommended_operating_model.md
- **Architecture:** docs/architecture/V2_ARCHITECTURE.md
- **Audit baseline:** audits/deep_app_audit/implementation_reality_report.md
- **Gap analysis:** Eduboost-V2_Gap_Analysis.md (2026-06-09)

## Next Milestones

1. Follow the active PRD-11 production-readiness item.
2. Preserve fail-closed release, deployment, beta, billing, and live-learner boundaries.
3. Use canonical documentation and evidence indexes for current milestones.

**EduBoost is NOT public-beta-ready or production-ready.**
