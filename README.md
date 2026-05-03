# 🦁 EduBoost SA

**AI-powered adaptive learning platform for South African learners — Grade R to Grade 7**

[![CAPS Aligned](https://img.shields.io/badge/CAPS-Aligned-green)](https://www.education.gov.za)
[![POPIA Compliant](https://img.shields.io/badge/POPIA-Compliant-blue)](https://popia.co.za)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)

---

## 📋 Overview

**Status (2026-05-02):** ✅ V2 Modular Monolith Architecture Complete. V1 codebase deleted.

EduBoost SA is an **adaptive learning platform** deployed as a **modular monolith** on Azure Container Apps. The architecture is documented in [`temp/EduBoost_Architecture_Recommendation.md`](temp/EduBoost_Architecture_Recommendation.md) and fully implemented.

### Current Architecture (V2)

**Single-node modular monolith** structured around domain modules with clear internal boundaries:

```
app/
├── api_v2.py                    # Single FastAPI entrypoint
├── api_v2_routers/              # Thin HTTP layer (routing only)
├── modules/                     # Domain logic (bounded contexts)
│   ├── auth/
│   ├── diagnostics/             # IRT scoring engine
│   ├── lessons/                 # LLM provider gateway
│   ├── consent/                 # POPIA enforcement
│   ├── learners/
│   ├── study_plans/
│   ├── gamification/
│   ├── parent_portal/
│   └── rlhf/
├── repositories/                # Data access layer
├── core/                        # Shared kernel
│   ├── database.py              # Async SQLAlchemy
│   ├── config.py                # Pydantic + Azure Key Vault
│   ├── security.py              # JWT, encryption
│   ├── audit.py                 # PostgreSQL audit trail
│   ├── metrics.py               # Prometheus
│   ├── middleware.py            # Rate limiting, request ID
│   ├── exceptions.py            # Global exception handlers
│   ├── dependencies.py          # Dependency injection
│   └── base.py                  # Generic repository
└── models/                      # SQLAlchemy ORM (Alembic-managed)
```

### Why This Architecture?

**Single-node modular monolith** (not microservices):
- ✅ Strong internal boundaries (Python package structure) without operational complexity
- ✅ No distributed transaction complexity (POPIA consent gating stays atomic)
- ✅ No network latency in learner-critical paths (IRT → lesson generation)
- ✅ Simple deployment: single ACA container
- ✅ Clear scaling path: split modules into independent ACA services only when load demands it

**Key simplifications from V1:**
- ❌ **Deleted:** V1 API layer, RabbitMQ, Celery, Five-Pillar metaphor
- ✅ **New:** PostgreSQL-backed audit trail (async writes), `arq` for background jobs, LLM gateway abstraction, Consent as FastAPI dependency

### Infrastructure Stack (Production)

| Component | Service |
|---|---|
| Backend | Azure Container Apps |
| Frontend | Azure Static Web Apps / ACA |
| Database | Azure Database for PostgreSQL Flexible |
| Cache / Jobs | Azure Cache for Redis (`arq`) |
| Inference | ACA sidecar container |
| Secrets | Azure Key Vault |
| Observability | Grafana Cloud (Prometheus + Loki) |

### Development Quick Start

**Prerequisites:**
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

**Local development (single command):**

```bash
docker compose -f docker-compose.v2.yml up --build
```

This starts:
- 🔵 **Backend**: FastAPI on `http://localhost:8000`
- 🔴 **Frontend**: Next.js on `http://localhost:3000`
- 🐘 **Database**: PostgreSQL on `localhost:5432`
- 🔑 **Cache**: Redis on `localhost:6379`
- 📊 **Observability**: Grafana on `http://localhost:3001`

**Run tests locally (no Docker):**

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest tests/ -v  # POPIA compliance tests in tests/popia/
```

**Generate dummy data for testing:**

```bash
python scripts/dummy_data_generator.py --count 10000
```

The V2 migration now also mirrors the repository’s existing multi-file tracking structure with dedicated:
- roadmap files
- implementation reports
- review documents
- agent instructions
- project-state and handoff documents

The current highest-priority handoff file is:
- `audits/roadmaps/V2_Outstanding_Task_Roadmap.md`

Build locally with:

```bash
mkdocs serve
```

## Developer setup (local)

To prepare a local developer environment, run the helper scripts below. They install the core runtime dependencies (excluding heavy ML inference packages) and frontend dependencies.

1. Create a Python virtual environment and install backend dependencies:

```bash
./scripts/setup_dev_env.sh
```

2. Install frontend dependencies:

```bash
./scripts/setup_frontend.sh
```

Heavy ML and inference packages are intentionally separated (see `requirements-ml.txt` and `docker/requirements.inference.txt`).


The V2 docs cover:
- architecture
- V2 API surface
- core configuration and security helpers
- service-layer reference documentation generated from Python modules

### Key Features
- 🧠 **Adaptive Diagnostic Engine** — IRT-based (Item Response Theory) assessments that find the exact grade level of each knowledge gap.
- 🤖 **AI Lesson Generation** — Claude/Llama 3 powered lessons with authentic South African context (ubuntu, braai, rands, local fauna).
- 📅 **Dynamic Study Plans** — CAPS-aligned weekly schedules that prioritise foundation gaps while keeping pace with grade-level work.
- 🏆 **Gamification** — XP, badges, streaks for Grade R–3; discovery-based engagement for Grade 4–7.
- 🔒 **POPIA-Grade Privacy** — Backend-enforced parental consent, pseudonymous learner IDs, and a durable audit trail.
- 📊 **Parent Portal** — AI-generated progress reports, right-to-access exports, and granular consent management.
- 🇿🇦 **Multilingual Support** — CAPS-aligned lessons in English, isiZulu, Afrikaans, and isiXhosa.
- 📱 **Offline-Ready PWA** — Service worker and manifest support for installation and offline resilience.
- 🧠 **RLHF Pipeline** — Learner feedback collection for continuous AI lesson quality improvement.

---

## 🗂️ Project Structure

```
eduboost-sa/
├── app/
│   ├── api/                          # FastAPI backend
│   │   ├── constitutional_schema/    # Schema and typing helpers
│   │   ├── core/                     # Config, DB, Celery
│   │   ├── ml/                       # IRT engine
│   │   ├── models/                   # SQLAlchemy models (Alembic-managed)
│   │   ├── routers/                  # API routes (including Consent/Auth)
│   │   ├── services/                 # LLM / lesson / consent services
│   │   ├── main.py                   # FastAPI entrypoint
│   │   ├── orchestrator.py           # Workflow orchestration
│   │   ├── judiciary.py              # Policy / validation layer (Pillar 3)
│   │   ├── fourth_estate.py          # Durable RabbitMQ Audit Trail (Pillar 4)
│   │   └── profiler.py               # Profiling helpers (Pillar 5 - Ether)
│   └── frontend/                     # Next.js frontend (App Router)
│       ├── src/app/                  # Feature pages (dashboard, lesson, diagnostic, etc.)
│       ├── src/components/eduboost/   # Specialized UI components
│       ├── src/lib/api/              # Production-grade service layer
│       └── package.json
├── docker/                           # Dockerfiles (API, Inference, Nginx)
├── grafana/                          # Grafana provisioning & dashboards
├── k8s/                              # Kubernetes manifests
├── scripts/                          # DB migrations, seeds, and maintenance
├── tests/                            # E2E (Playwright), Unit, and Integration tests
├── docker-compose.yml                # Local development stack (Legacy)
├── docker-compose.v2.yml             # Local development stack (V2 Baseline)
├── docker-compose.aca.yml            # Production validation stack (Azure Container Apps)
├── bicep/                            # Infrastructure as Code (Azure Container Apps)
├── prometheus.yml                    # Prometheus scrape config
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## ⚠️ Current State

EduBoost SA is currently in its **Beta** phase, with core architectural pillars fully implemented:

- ✅ **V2 Modular Monolith**: Optimized, repository-driven architecture for single-node efficiency.
- ✅ **Production Target**: Azure Container Apps (ACA) defined with Bicep IaC.
- ✅ **Pillar 2 (Executive)**: Backend-mediated lesson generation and study plan workflows.
- ✅ **Pillar 3 (Judiciary)**: Constitutional policy enforcement via the Judiciary Stamp gate.
- ✅ **Pillar 4 (Fourth Estate)**: Durable, RabbitMQ-backed audit trail for POPIA compliance.
- ✅ **Pillar 5 (Ether)**: Psychological archetype profiling and adaptive prompt modification.
- ✅ **Observability**: Prometheus/Grafana/Loki stack with business SLO dashboards.
- ✅ **Multilingual**: Native support for English, isiZulu, Afrikaans, and isiXhosa.
- ✅ **Compliance**: Full ConsentService with right-to-erasure and versioned policy support.
- ✅ **PWA**: Installable web app with offline sync capabilities.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. Clone & Configure
```bash
git clone <your-github-repo-url>
cd eduboost-sa
cp env.example .env
```

### 2. Start the Full Stack (Docker)
```bash
docker compose up --build
```

Services will be available at:

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Grafana | http://localhost:3001 |

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async SQLAlchemy connection string (Postgres) |
| `REDIS_URL` | Redis connection string (Cache/Jobs) |
| `GROQ_API_KEY` | Primary LLM inference key |
| `ANTHROPIC_API_KEY` | Secondary LLM provider key |
| `JWT_SECRET` | JWT signing secret |
| `ENCRYPTION_KEY` | AES-256 key for PII at rest |

---

## 🧪 Testing

```bash
# Unit & Integration tests
pytest

# E2E tests (Playwright)
npx playwright test
```

---

## 🔐 POPIA & Privacy

EduBoost SA implements privacy-by-design through:

1. **Consent Gating**: All learner data access requires a valid, non-expired `ParentalConsent` record.
2. **Pseudonymisation**: Real learner identities are never passed to LLM providers; opaque `pseudonym_id`s are used instead.
3. **Durable Audit**: Every sensitive action and constitutional review is logged to a persistent RabbitMQ exchange.
4. **Right to Erasure**: Guardian-initiated deletion workflows atomically revoke consent and soft-delete personal data.
5. **PII Scrubbing**: Prompt paths are audited via the "Chaos Sweep" scripts to prevent leakage.

---

## 📈 Monitoring

The stack includes pre-configured Grafana dashboards covering:
*   **Learner Journey SLOs**: Tracking diagnostic completion and lesson efficacy.
*   **LLM Provider Health**: Latency and success rates across providers.
*   **Constitutional Health**: Approval rates and violation trends.
*   **Centralised Logs**: Integrated Grafana Loki and Promtail for unified log aggregation.

---

## 🤝 Contributing

We welcome contributions! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for our engineering standards and [CHANGELOG.md](CHANGELOG.md) for version history.

1. Fork the repo and create a feature branch.
2. Ensure all tests pass (`pytest` and `playwright`).
3. Follow the 5-pillar architectural patterns.
4. Submit a PR for review.

---

## 📜 License

MIT License — see `LICENSE` file.

---

## 🇿🇦 About

Built with Ubuntu — *"I am because we are."* Every South African child deserves access to quality, personalised education.
