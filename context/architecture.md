# Architecture

**Last updated:** 2026-06-09
**Current state tracked in:** ../docs/roadmap/roadmap.md (17 phases) and ../docs/todos/todo.md (North Star)

## Technology Stack (Verified)

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Runtime | Python | 3.12.3 (target) / 3.11-slim (Docker) | RoadMap Phase 4 resolves |
| HTTP Framework | FastAPI | 0.104+ | 355 routes on app/api_v2.py |
| Database | PostgreSQL | 15+ | 35 Alembic migrations |
| ORM | SQLAlchemy | 2.0+ | AsyncSession throughout |
| Async Driver | asyncpg | 0.28+ | |
| Validation | Pydantic | v2 | model_config from_attributes=True |
| Testing | pytest | 7.4+ | 2051 passed, 1 skipped, 1 warning (local) |
| LLM Providers | Groq (primary), Anthropic, Gemini, HuggingFace | | 4 providers configured |
| Frontend | Next.js 15.5, React 18, TypeScript 5.4 | 15.5.18 | pnpm 9.x, Vitest 4.x, Tailwind 3.4 |
| Monitoring | Prometheus + Grafana | | 3 dashboards provisioned |
| Cache/Jobs | Redis + ARQ | | Durable jobs pending (Phase 6) |

## Folder Structure (Verified, June 2026)

app/
  api_v2.py                   # FastAPI entrypoint (355 routes)
  api_v2_routers/             # 28 HTTP routers
  modules/                    # 22 bounded-context domains
  repositories/               # Async data access
  models/                     # ORM (Alembic-managed)
  domain/                     # Entities, schemas, contracts
  core/                       # Infrastructure (35 modules)
  middleware/                  # Rate-limit, CORS, timing, security headers
  services/                   # Content gen, ETL, LLM, curriculum, safety
  jobs/                       # ARQ background jobs
  legacy/                     # Deprecated V1 shims
  utils/

tests/                        # 716 test files
  unit/                       # 2051 passing (local green baseline)
  integration/                # Security, Stripe, routers, jobs
  e2e/                        # Playwright (broken - Phase 13)

## Data Flow

1. Request: Client -> Router -> Service -> Repository -> DB -> Response (EnvelopedRoute)
2. Diagnostic: Start -> IRT item (3PL+MFIS) -> Respond -> Update theta/SE (EAP) -> Terminate -> Mastery
3. Practice: Start -> Select items (difficulty+spaced rep) -> Respond -> Points -> Mastery *(in-memory; Phase 2.2)*
4. ETL: Upload -> Parse -> Extract -> Map CAPS -> Validate -> Review queue
5. Content Gen: Scope registry -> LLM provider -> CAPS prompt -> Safety check -> Staging -> Promote

## Database Schema (Core)

| Table | Purpose | Status |
|-------|---------|--------|
| learners | Profile, consent tracking | Live |
| diagnostic_sessions | Assessment state, IRT params | Live |
| learner_mastery | Topic mastery (theta, SE) | Live |
| practice_items | Item bank (120 Grade 4 Math) | Live |
| practice_sessions | Session tracking, responses | Live |
| study_plans | AI-generated plans | Live |
| lessons | 24 Grade 4 Math lessons | Live |
| audit_logs | POPIA audit (append-only, HMAC) | Live |
| content_factory_* | ETL provenance, generation runs | Live |

## System Invariants (Verified)

| # | Invariant | Status | Notes |
|---|-----------|--------|-------|
| 1 | Learner queries scoped to learner_id | Enforced | Object auth in most routes |
| 2 | IRT theta/SE always updated together | Enforced | |
| 3 | Mastery only improves | Enforced | |
| 4 | POPIA consent before data access | PARTIAL | Practice routes need auth (Phase 2) |
| 5 | All writes include audit logging | Enforced | Append-only PostgreSQL |
| 6 | Items only served if approved | Enforced | |
| 7 | No hardcoded secrets | PARTIAL | Stripe localhost URLs (Phase 7) |
| 8 | Async ops wrapped in try/catch | PARTIAL | 861 Ruff findings (Phase 11) |
| 9 | Responses wrapped in EnvelopedRoute | Enforced | Global exception handlers |
| 10 | Practice items filtered by difficulty | Enforced | In-memory state (Phase 2.2) |

## Known Architecture Gaps (see ../docs/roadmap/roadmap.md)

- P0: Practice session routes unauthenticated; in-memory state (Phase 2)
- P0: Python version inconsistency across Docker/CI/local (Phase 4)
- P1: Startup schema repair outside Alembic (Phase 5)
- P1: ARQ durable jobs not wired (Phase 6)
- P1: CSP permissive; HSTS unconditional (Phase 12)
- P1: /metrics unauthenticated (Phase 12)
- P2: core->services import violations (Phase 11)
- P2: Dual route registration (/api/v2 AND /v2) (Phase 11)
- P2: 861 Ruff findings backlog (Phase 11)
