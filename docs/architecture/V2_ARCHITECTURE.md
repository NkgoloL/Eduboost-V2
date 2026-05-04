# EduBoost SA — Recommended Architecture

**Version:** 1.0 | **Date:** 2 May 2026 | **Context:** V2 Migration, No Legacy Clients

---

## Decision: Commit Fully to the V2 Modular Monolith

Since V1 had no real clients (demo only), there is **zero migration obligation**. V1 should be deleted entirely within the next sprint, not deprecated gradually. This removes the dual-architecture burden immediately.

The recommended architecture is a **single-node Modular Monolith** deployed on **Azure Container Apps (ACA)**, structured around domain modules with clear internal boundaries — not microservices, and not the over-engineered five-pillar legacy design.

---

## Why Not Microservices?

EduBoost is at beta stage with a single team. Microservices introduce:
- Distributed transaction complexity (POPIA consent gating across service boundaries)
- Network latency in learner-critical paths (IRT scoring → lesson generation)
- Operational overhead (multiple deployments, service meshes, inter-service auth)
- Cost: ACA charges per container instance

A modular monolith gives **strong internal boundaries** (enforced by Python package structure) without the operational complexity. It can be split later if a specific module needs independent scaling.

---

## Why Not the Five-Pillar Legacy Design?

The five-pillar naming (Executive, Judiciary, Fourth Estate, Ether) is:
- Conceptually creative but practically obscure for onboarding new developers
- Tightly coupled to RabbitMQ for audit durability — unnecessary infrastructure at this scale
- Mixing metaphor layers (political philosophy) with engineering layers (services, middleware)

The V2 repository pattern and domain module approach is the correct direction.

---

## Recommended Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Apps                      │
│                                                             │
│  ┌─────────────────┐        ┌─────────────────────────┐    │
│  │  Next.js Frontend│        │    FastAPI V2 Backend    │    │
│  │  (ACA Container) │◄──────►│    (ACA Container)       │    │
│  │  Port 3000       │  HTTPS │    Port 8000             │    │
│  └─────────────────┘        │                          │    │
│                              │  ┌──────────────────┐   │    │
│                              │  │  Domain Modules   │   │    │
│                              │  │                  │   │    │
│                              │  │  auth/           │   │    │
│                              │  │  learners/       │   │    │
│                              │  │  diagnostics/    │   │    │
│                              │  │  lessons/        │   │    │
│                              │  │  study_plans/    │   │    │
│                              │  │  consent/        │   │    │
│                              │  │  gamification/   │   │    │
│                              │  │  parent_portal/  │   │    │
│                              │  │  rlhf/           │   │    │
│                              │  └──────────────────┘   │    │
│                              │                          │    │
│                              │  ┌──────────────────┐   │    │
│                              │  │  Shared Kernel    │   │    │
│                              │  │  repositories/   │   │    │
│                              │  │  core/config     │   │    │
│                              │  │  core/security   │   │    │
│                              │  │  core/audit      │   │    │
│                              │  │  core/metrics    │   │    │
│                              │  └──────────────────┘   │    │
│                              └─────────────────────────┘    │
│                                        │                     │
│  ┌─────────────────┐  ┌─────────────┐ │ ┌───────────────┐  │
│  │ Inference Service│  │  PostgreSQL  │◄┘ │     Redis     │  │
│  │  (ACA Container) │  │  (Azure DB)  │   │  (ACA Redis)  │  │
│  │  torch/transformers│  │             │   │  Cache + Jobs │  │
│  └─────────────────┘  └─────────────┘   └───────────────┘  │
└─────────────────────────────────────────────────────────────┘

External: Anthropic API, Groq API, SendGrid, Azure Key Vault
Observability: Grafana Cloud (Prometheus + Loki — managed, no self-hosted)
```

---

## Module Structure (Python Package Layout)

```
app/
├── api_v2.py                    # Single FastAPI entrypoint
├── api_v2_routers/              # Thin HTTP layer — routing only
│   ├── auth.py
│   ├── learners.py
│   ├── diagnostics.py
│   ├── lessons.py
│   ├── study_plans.py
│   ├── consent.py
│   ├── gamification.py
│   ├── parent_portal.py
│   └── rlhf.py
│
├── modules/                     # Domain logic — bounded contexts
│   ├── auth/
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── exceptions.py
│   ├── diagnostics/
│   │   ├── service.py
│   │   ├── irt_engine.py        # IRT scoring logic
│   │   ├── schemas.py
│   │   └── exceptions.py
│   ├── lessons/
│   │   ├── service.py
│   │   ├── llm_gateway.py       # LLM provider abstraction
│   │   ├── prompt_builder.py
│   │   ├── schemas.py
│   │   └── exceptions.py
│   ├── consent/
│   │   ├── service.py           # POPIA consent enforcement
│   │   ├── schemas.py
│   │   └── exceptions.py
│   └── [other modules...]
│
├── repositories/                # Data access — one per aggregate
│   ├── base.py
│   ├── learner_repository.py
│   ├── diagnostic_repository.py
│   ├── lesson_repository.py
│   ├── consent_repository.py
│   └── audit_repository.py
│
├── core/                        # Cross-cutting concerns
│   ├── config.py                # Pydantic settings
│   ├── database.py              # Async SQLAlchemy session
│   ├── security.py              # JWT, encryption helpers
│   ├── audit.py                 # Async audit log writer (DB, not RabbitMQ)
│   ├── metrics.py               # Prometheus counters/histograms
│   ├── middleware.py            # Rate limiting, request ID, timing
│   └── exceptions.py           # Global exception handlers
│
└── models/                      # SQLAlchemy ORM models (Alembic-managed)
    ├── guardian.py
    ├── learner.py
    ├── consent.py
    ├── diagnostic.py
    ├── lesson.py
    ├── study_plan.py
    └── audit_log.py
```

---

## Key Architectural Decisions

### 1. Audit Trail: PostgreSQL, Not RabbitMQ

RabbitMQ was used for the POPIA audit trail in V1. At EduBoost's scale, a dedicated `audit_log` table in PostgreSQL is:
- Sufficient for POPIA audit requirements
- Transactionally consistent with the operation being audited (same DB commit)
- Simpler to query and export for right-of-access requests
- One fewer infrastructure dependency

Use a background async write (non-blocking) via FastAPI's `BackgroundTasks` if write latency is a concern.

### 2. LLM Gateway: Abstraction Layer with Fallback

```python
# modules/lessons/llm_gateway.py
class LLMGateway:
    async def generate(self, prompt: str, language: str) -> str:
        try:
            return await self._call_groq(prompt)      # primary (fast, cheap)
        except GroqError:
            return await self._call_anthropic(prompt)  # fallback
```

This removes direct Groq/Anthropic coupling from service logic and makes provider swapping testable.

### 3. Consent as Middleware, Not a Service Call

Rather than calling `ConsentService.require_active_consent()` at the start of every endpoint handler, implement it as a FastAPI dependency injected at the router level:

```python
# core/dependencies.py
async def require_consent(learner_id: UUID, db: AsyncSession) -> ParentalConsent:
    consent = await consent_repo.get_active(learner_id, db)
    if not consent:
        raise HTTPException(403, "Active parental consent required")
    return consent

# router
@router.get("/lessons/{lesson_id}", dependencies=[Depends(require_consent)])
async def get_lesson(...):
    ...
```

This makes the consent gate declarative, impossible to forget, and visible in the OpenAPI schema.

### 4. Background Jobs: Redis + ARQ (Not Celery)

Celery is heavyweight for the V2 single-node model. Replace with `arq` (async Redis Queue) which integrates natively with asyncio and FastAPI, requires no separate worker process management configuration, and has a simpler API. Celery Beat scheduler can be replaced with a simple APScheduler or arq's built-in cron support.

### 5. Secrets: Azure Key Vault from Day One

Do not defer Key Vault integration. The `azure-keyvault-secrets` library is already in `requirements.txt`. Wire it up in `core/config.py` so all secrets (JWT secret, encryption key, encryption salt, and API keys) are fetched from Key Vault at startup, with local `.env` fallback for development only.

Required production Key Vault secret names:
- `eduboost-jwt-secret`
- `eduboost-encryption-key`
- `eduboost-encryption-salt`
- `eduboost-groq-api-key`
- `eduboost-anthropic-api-key`

---

## Infrastructure Stack (Production)

| Component | Service | Rationale |
|---|---|---|
| API Backend | Azure Container Apps | Serverless containers, auto-scale to zero |
| Frontend | Azure Container Apps | Or Azure Static Web Apps if Next.js export |
| Database | Azure Database for PostgreSQL Flexible | Managed, POPIA-compliant region (South Africa North) |
| Cache / Jobs | Azure Cache for Redis | Managed, no ops burden |
| Inference | ACA sidecar container | Isolated, not internet-accessible |
| Secrets | Azure Key Vault | Centralised, audited secret access |
| Observability | Grafana Cloud (free tier) | Eliminates self-hosted Prometheus/Loki containers |
| CDN / Edge | Azure Front Door | SSL termination, WAF, South Africa PoP |
| Email | SendGrid | Already in requirements |
| Storage | Azure Blob Storage | Replace boto3/R2 for Azure-native stack |

---

## Migration Plan from Current State

### Week 1 — Immediate Triage
- [ ] Delete all `app/api/` (legacy V1) code and `docker-compose.yml`
- [ ] Delete `mnt/`, `scratch/` from repo
- [ ] Move `ci.yml` → `.github/workflows/ci-cd.yml`
- [ ] Confirm CI pipeline runs green

### Week 2 — Module Restructure
- [ ] Reorganise `app/` into the module layout above
- [ ] Replace RabbitMQ audit trail with async PostgreSQL writes
- [ ] Replace Celery with arq for background jobs
- [ ] Wire Azure Key Vault into `core/config.py`

### Week 3 — Testing & Compliance
- [ ] Achieve 80% unit test coverage on all domain modules
- [ ] Validate full POPIA test suite passes
- [ ] Add Bandit + Semgrep to CI lint job
- [ ] Generate Alembic revision for any schema changes

### Week 4 — Production Readiness
- [ ] Deploy to ACA staging environment via CI
- [ ] Run Playwright E2E suite against staging
- [ ] Set up Grafana Cloud dashboards
- [ ] Complete pen test checklist from `audits/security/pen_test_checklist.md`

---

## What to Keep from the Current V2 Codebase

| Keep | Why |
|---|---|
| `app/repositories/` | Already correct pattern — populate fully |
| `app/api_v2_routers/` | Thin routing layer — correct |
| `app/api/ml/` IRT engine | Core educational IP — migrate into `modules/diagnostics/` |
| `app/api/services/` ConsentService | Strong POPIA logic — migrate into `modules/consent/` |
| Alembic migrations | Single source of schema truth |
| `docker-compose.v2.yml` | Correct lean dev stack — keep and extend |
| `bicep/` | Correct production IaC target |
| `grafana/` dashboards | Good SLO definitions — move to Grafana Cloud |
| CI pipeline structure | Well-designed — just move to right directory |
| POPIA test suite | `tests/popia/` — non-negotiable compliance asset |
| Playwright config | E2E coverage is valuable |

## What to Remove

| Remove | Why |
|---|---|
| `app/api/` (V1 routers/services) | No clients, no migration needed |
| `app/api/fourth_estate.py` | RabbitMQ audit replaced by Postgres |
| `app/api/judiciary.py` | Policy logic absorbed into consent middleware |
| `docker-compose.yml` (legacy 9-service) | Replaced by v2 compose |
| `docker-compose.prod.yml` | Replaced by ACA/Bicep |
| RabbitMQ from all composes | Eliminated |
| Celery/Flower | Replaced by arq |
| `mnt/` directory | Accidental AI session artifact |
| `scratch/` directory | WIP, belongs in feature branch |
| `gemini-code-1777601244294.md` | Replaced with this document |
| Root-level `package.json` | Consolidate into `app/frontend/` |

---

*This architecture supports EduBoost SA's path from beta to 10,000 concurrent learners on a single ACA deployment, with a clear scaling path to split the inference sidecar and diagnostics module into independent services only when load evidence demands it.*
