# EduBoost SA V2 — Comprehensive Technical Assessment Report

**Repository:** [NkgoloL/Eduboost-V2](https://github.com/NkgoloL/Eduboost-V2)
**Branch Assessed:** `master` (33 commits, last commit ~40 min before report generation)
**Report Date:** 2026-05-03
**Current Version:** 0.2.0-rc1 (released 2026-05-01)
**Phase:** Beta — Active V2 Architectural Migration (`V2_BASELINE_IN_PROGRESS`)
**Forks:** 2 (noted from AGENT_INSTRUCTIONS.md page header)
**Classification:** Internal Engineering Use

> **Verification Note:** The initial assessment erroneously reported 3 commits by reading a cached or partial GitHub page render. The correct count is 33 commits on master. All findings in this report are based on direct file-level inspection of the current master branch.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview & Mission Context](#2-project-overview--mission-context)
3. [Architecture Assessment](#3-architecture-assessment)
4. [Codebase Composition & Structure](#4-codebase-composition--structure)
5. [Agent-Driven Development Paradigm](#5-agent-driven-development-paradigm)
6. [Strengths Analysis](#6-strengths-analysis)
7. [Weaknesses & Risk Register](#7-weaknesses--risk-register)
8. [Security & Compliance Deep Dive](#8-security--compliance-deep-dive)
9. [CI/CD & DevOps Assessment](#9-cicd--devops-assessment)
10. [Observability & Monitoring Assessment](#10-observability--monitoring-assessment)
11. [Dependency Review](#11-dependency-review)
12. [System Optimization Recommendations](#12-system-optimization-recommendations)
13. [Migration Completion Roadmap](#13-migration-completion-roadmap)
14. [Scoring Summary](#14-scoring-summary)

---

## 1. Executive Summary

EduBoost SA is an AI-powered adaptive learning platform targeting South African learners from Grade R through Grade 7, aligned to the CAPS curriculum and subject to POPIA regulatory compliance. The platform is currently in **active Beta** with 33 commits on master — evidence of a genuinely live, iterative development process — and is mid-way through an ambitious architectural pivot from a legacy Five-Pillar monolith to a V2 strict modular monolith optimised for deterministic outputs, AI cost-control, and single-node operational simplicity.

The codebase demonstrates impressive architectural ambition, a sophisticated compliance posture, and an unusually mature CI/CD design for a pre-1.0 project. However, the V2 migration is still self-classified as `V2_BASELINE_IN_PROGRESS`, and the `SECURITY.md` itself transparently discloses six known gaps — including incomplete right-to-erasure verification, a missing automated dependency scanner, and absent refresh token rotation — that must be resolved before the platform can handle real learner PII at production scale.

The project is well-structured, well-documented, and clearly driven by a clear product vision. The primary risks are execution-completeness (V2 migration finish line) and closing the self-identified security gaps before any production learner data ingestion begins.

**Overall Rating: 7.4 / 10** — Strong foundations, best-in-class compliance intent, maturing CI/CD; blocked on V2 completion and 6 disclosed security gaps.

---

## 2. Project Overview & Mission Context

| Attribute | Detail |
|---|---|
| **Platform Type** | Adaptive EdTech SaaS |
| **Target Users** | SA learners (Grade R–7), parents/guardians, educators |
| **Curriculum Standard** | CAPS (South African DBE) |
| **Regulatory Requirement** | POPIA No. 4 of 2013 |
| **Backend Stack** | Python 3.11 / FastAPI / SQLAlchemy (async) / Alembic |
| **Frontend Stack** | Next.js 14 (App Router) / TypeScript |
| **Primary LLM** | Anthropic Claude (secondary/fallback) |
| **Primary Inference** | Groq — Llama 3 (rate-limited: 20 req/min, 14,400/day) |
| **Offline Fallback** | HuggingFace Zephyr-7B |
| **ML Engine** | 2-Parameter Logistic IRT (scikit-learn, scipy, numpy) |
| **Infrastructure Target** | Azure Container Apps (ACA) + Bicep IaC |
| **Languages Supported** | English, isiZulu, Afrikaans, isiXhosa |
| **Current Version** | 0.2.0-rc1 |
| **Commit Count (master)** | 33 commits |
| **Active Forks** | 2 |

---

## 3. Architecture Assessment

### 3.1 The V2 Architectural North Star

The canonical V2 architecture is defined in `gemini-code-1777601244294.md` — a 5-phase agent execution manifest. The V2 paradigm has three governing constraints that represent a deliberate simplification over the legacy design:

1. **No distributed task queues** — Celery and RabbitMQ are explicitly forbidden in V2; `BackgroundTasks` is the sanctioned async mechanism.
2. **No microservices** — strict modular monolith using Domain-Driven Design directory boundaries.
3. **No complex orchestration** — Kubernetes and Bicep are legacy-tier concerns; the V2 baseline targets a single Docker Compose stack with 4 services.

This is a sound and pragmatic decision for a pre-revenue, single-team project. The complexity reduction is real and meaningful.

### 3.2 Five-Pillar Constitutional Architecture

The system organises its domain logic around five named pillars derived from a "Constitutional AI" metaphor:

| Pillar | Name | Module | Core Responsibility |
|---|---|---|---|
| 1 | Legislature | `app/api/main.py` | Request routing and entrypoint |
| 2 | Executive | `app/api/orchestrator.py` | Lesson generation and study plan workflows |
| 3 | Judiciary | `app/api/judiciary.py` | Constitutional policy enforcement — PII gate, prompt validation |
| 4 | Fourth Estate | `app/api/fourth_estate.py` | Durable audit trail (Redis stream → V2 Postgres) |
| 5 | Ether | `app/api/profiler.py` | Psychological archetype profiling (Keter, Yesod, Tiferet, etc.) |

The Judiciary pillar is particularly well-conceived — it functions as a mandatory validation layer that prevents PII from reaching LLM providers regardless of what the calling code does. This is architectural enforcement of a privacy constraint, not a documentation promise.

### 3.3 V2 Directory Structure & Boundary Enforcement

The V2 target directory structure enforces Domain-Driven Design import boundaries:

```
/app/
├── api/           # FastAPI routers — CANNOT import from /repositories/ directly
├── services/      # Business logic — mediates between api/ and repositories/
├── repositories/  # DB access abstraction — sole Postgres interaction layer
├── domain/        # ORM models + Pydantic schemas — zero dependency on FastAPI/LLM
└── core/          # config.py, security.py, logging.py
```

The success criterion for Task 0.1 in the manifest states that `__init__.py` files must enforce strict boundary imports. This is an excellent convention that prevents the common "service layer creep" anti-pattern seen in large FastAPI projects.

### 3.4 Current Runtime Duality

The repository simultaneously carries:

| Compose File | Purpose | Services |
|---|---|---|
| `docker-compose.yml` | Legacy dev (Celery, RabbitMQ, Flower) | ~9 services |
| `docker-compose.v2.yml` | V2 dev baseline | 4 services (api, docs, postgres, redis) |
| `docker-compose.aca.yml` | Azure Container Apps validation | Production-oriented |

The `docker-compose.prod.yml` referenced in the CHANGELOG does not appear to exist at the root (404 on fetch), suggesting it may have been moved, renamed, or not yet created — this should be verified.

The V2 compose file is clean and correctly health-checks Postgres. One gap is noted in Section 7.

---

## 4. Codebase Composition & Structure

**Language Distribution:**

| Language | Share | Notes |
|---|---|---|
| Python | 81.8% | Backend API, ML engine, services |
| JavaScript | 9.5% | Next.js frontend (likely pre-TypeScript migration) |
| PLpgSQL | 5.7% | Database procedures / seed migrations |
| TypeScript | 1.3% | Newer frontend components |
| Shell | 0.9% | Setup and utility scripts |
| Bicep | 0.8% | Azure IaC |

**Notable structural observations:**

- The PLpgSQL share (5.7%) is substantial — the CHANGELOG confirms SQL init scripts were removed from compose startup in favour of Alembic migrations, but the PLpgSQL volume suggests stored procedures or seed data scripts that need auditing to confirm they are all migration-managed.
- The JavaScript/TypeScript split (9.5% JS vs 1.3% TS) indicates the frontend migration to TypeScript is in progress rather than complete. This creates type-safety gaps in the client-side service layer.
- The `scratch/` directory in the repo tree is a notable code quality signal — scratch directories committed to version control should be cleaned or gitignored.

**Repository structure highlights:**

```
├── app/                  # Backend + Frontend
├── alembic/              # DB migrations (Alembic-managed)
├── audits/               # Roadmaps, reports, security checklists
├── bicep/                # Azure IaC
├── docker/               # Dockerfiles (API, Inference, V2, Nginx)
├── docs/                 # MkDocs source
├── grafana/              # Grafana dashboard provisioning
├── k8s/                  # Kubernetes manifests (legacy/future)
├── prometheus/           # Prometheus scrape config
├── scripts/              # DB seeds, POPIA sweep, maintenance
├── scratch/              # ⚠️ Uncommitted work / scratch — should be gitignored
├── tests/                # Unit, integration, POPIA, E2E (Playwright)
└── mnt/user-data/        # ⚠️ AI session artifact — should be removed
```

---

## 5. Agent-Driven Development Paradigm

EduBoost V2 operates an explicitly **agent-driven development model** — a notable architectural choice that has direct implications for code quality, documentation hygiene, and commit discipline.

The `AGENT_INSTRUCTIONS.md` defines a TDD-loop paradigm:

1. Read the roadmap epic
2. Write failing tests first
3. Run `pytest` — confirm red
4. Implement the logic
5. Re-run until green
6. Commit

This is an excellent discipline when followed. The agent instructions also mandate browser subagents for frontend verification, chaos sweeps for POPIA compliance, and terminal-heavy integration testing before sign-off.

The `audits/` directory tree — containing `roadmaps/`, `reports/`, and likely `security/` — is the project's living audit trail of agent execution. The `AGENT_INSTRUCTIONS_V2.md` adds the requirement that a V2 slice is only complete when: code is added, docs are updated, audit files are updated, and the work is committed. This four-part completion standard is excellent and unusually rigorous.

**Risk:** Agent-driven development produces high velocity but can accumulate subtle architectural drift if agents are not consistently constrained by the boundary rules in `gemini-code-1777601244294.md`. The `scratch/` directory and the `mnt/` artifact directory in the repository tree suggest that at least some agent outputs have been committed without the standard cleanup step.

---

## 6. Strengths Analysis

### 6.1 POPIA Compliance-by-Design ★★★★★

This is the project's most distinguished technical asset. The compliance implementation is structural, not cosmetic:

- **Judiciary gate**: `judiciary.py` enforces PII cannot reach any LLM provider without pseudonymisation — this is an architectural constraint, not a runtime check an engineer can accidentally bypass.
- **`pseudonym_id` isolation**: The learner's real UUID is never transmitted to Groq, Anthropic, or any external service. Confirmed in both `SECURITY.md` and requirements code structure.
- **Email storage**: SHA-256 hash + pgcrypto Fernet-encrypted ciphertext — never plaintext.
- **Consent gating**: `ConsentService.require_active_consent()` is defined as a mandatory gate at all learner endpoints, with `expires_at` annual renewal enforced at the data model level.
- **Right to erasure**: Guardian-authenticated soft-delete with `BackgroundTasks` purge within 30 days (POPIA Section 24).
- **POPIA CI gate**: Dedicated `popia-tests` job in CI filtered on `pii`, `consent`, and `erasure` markers.
- **Responsible disclosure**: `SECURITY.md` self-discloses six known gaps honestly — a sign of mature security culture.
- **CORS explicitly whitelisted**: `ALLOWED_ORIGINS` configured; wildcard origins explicitly prohibited.
- **Information Regulator escalation**: `SECURITY.md` explicitly acknowledges the Section 22 breach notification obligation to the Information Regulator.

This is compliance-by-design executed at a depth that is rare in early-stage EdTech.

### 6.2 Mature, Comprehensive CI/CD Pipeline ★★★★★

The `ci.yml` (329 lines) is one of the most complete CI pipelines in a pre-1.0 open project:

- Lint + mypy strict type checking
- Unit tests with 80% coverage enforcement + Codecov
- Integration tests with live Postgres 15 + Redis 7 service containers
- V2 smoke test — validates `app.api_v2` entrypoint and all repository imports
- Frontend build validation (Next.js / Node 20)
- Schema drift gate (`alembic check` after `upgrade head`) — prevents silent schema divergence
- POPIA compliance test gate
- Docker image Trivy scanning (CRITICAL + HIGH CVE; SARIF uploaded to GitHub Security)
- Environment-protected production gate requiring all upstream gates to pass
- Kubernetes rollout with `rollout status` verification and production health checks

The `schema-drift` job is particularly mature — running `alembic check` as a hard CI gate is a best practice that most production teams don't adopt until much later.

### 6.3 Sophisticated LLM Architecture ★★★★☆

The LLM layer demonstrates several production-grade design decisions:

- **Provider hierarchy**: Groq (primary) → Anthropic Claude (secondary) → HuggingFace Zephyr-7B (offline fallback). Three-level fallback is resilient.
- **Rate-limit awareness**: Groq capped at 20 req/min / 14,400/day per the security docs — this is correctly modelled as a cost-control and availability constraint.
- **Async inference**: Phase 2 of the V2 manifest mandates `AsyncAnthropic` and async Groq — eliminating the event-loop starvation risk from synchronous LLM calls in a FastAPI worker pool.
- **Strict schema enforcement**: V2 mandates Groq `response_format` (JSON mode) and Claude Tool Use mapped to Pydantic `TypeAdapter` — making `JSONDecodeError` at runtime mathematically impossible.
- **Inference service isolation**: The ML inference container is network-isolated, reachable only on the internal Docker network.
- **Image footprint**: API image reduced from ~4GB to <500MB by moving torch/transformers to `requirements-ml.txt` and a dedicated inference Dockerfile.

### 6.4 IRT-Based Pedagogical Engine ★★★★☆

Using a 2-Parameter Logistic IRT model rather than rule-based level assignment is a legitimate psychometric choice with strong academic backing for diagnostic assessments. The 2PL model:

```
P(correct | θ) = 1 / (1 + exp(-a(θ - b)))
```

gives the platform the ability to estimate learner ability (θ) while accounting for both item discrimination (a) and difficulty (b). The V2 manifest correctly identifies that 500+ calibrated IRT items (currently seeded at ~10 items) are required for the Gap-Probe Cascade to function validly — this is a significant outstanding data requirement.

### 6.5 Observability Stack ★★★★☆

- Prometheus scrape config + `prometheus-fastapi-instrumentator` for automatic route metrics
- Pre-provisioned Grafana dashboards: Learner Journey SLOs, LLM Provider Health, Constitutional Health (Judiciary approval/violation rates)
- Grafana Loki + Promtail for centralised structured log aggregation
- Sentry SDK for exception tracking with FastAPI integration
- `structlog` for structured JSON logging throughout the application

### 6.6 Psychological Archetype Engine (Ether — Pillar 5) ★★★★☆

The Ether pillar maps learners to Kabbalistic archetypes (Keter, Yesod, Tiferet, etc.) to adapt AI tone and scaffolding style. The V2 manifest adds a 5-question onboarding micro-diagnostic to cold-start archetype classification on session 1 — removing the legacy 8–10 event lag. This is a genuinely novel pedagogical personalisation layer that differentiates EduBoost from generic adaptive platforms.

### 6.7 Cultural Localisation Depth ★★★★☆

- Native lesson generation in English, isiZulu, Afrikaans, and isiXhosa
- Authentic SA cultural context injection (ubuntu, braai, rands, local fauna) into LLM prompts
- `babel==2.15.0` for i18n/l10n support
- Gamification split by cognitive stage: XP/badges/streaks for Grade R–3; discovery-based engagement for Grade 4–7

### 6.8 Developer & Agent Documentation ★★★★☆

- MkDocs + mkdocstrings auto-generated technical documentation served as a live V2 docs service at `localhost:8001`
- `AGENT_INSTRUCTIONS.md` (TDD loop, elevated autonomy, chaos sweep protocol)
- `AGENT_INSTRUCTIONS_V2.md` (V2-specific completion standard)
- `gemini-code-1777601244294.md` — 5-phase execution manifest
- `SECURITY.md` — transparent gap disclosure, severity tiers, POPIA legal obligations
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`
- Pre-commit config for commit-time quality gates

### 6.9 Honest Security Disclosure ★★★★★

The `SECURITY.md` transparently self-discloses six known security gaps with their current status. This level of honesty in a public repository is uncommon and reflects a mature security culture. It also creates accountability — these gaps are now on the record and must be closed.

---

## 7. Weaknesses & Risk Register

### 7.1 Six Self-Disclosed Security Gaps [HIGH RISK — CONFIRMED]

The `SECURITY.md` formally discloses the following as known incomplete items:

| Gap | Stated Status | Risk Level |
|---|---|---|
| Right-to-erasure (POPIA §24) not end-to-end verified | In progress | HIGH — legal obligation |
| Consent audit trail incomplete across all workflows | In progress | HIGH — POPIA §19 |
| No automated dependency vulnerability scanning | Planned | MEDIUM |
| HTTPS not enforced in local dev stack | By design | LOW (prod enforced) |
| Refresh token rotation not implemented | Planned | MEDIUM — session hijack risk |
| CI/CD secrets scanning not configured | Planned | HIGH — prevents key leakage |

Items 1 and 2 are **legal obligations** under POPIA. No real learner data should be ingested until end-to-end right-to-erasure is verified and the consent audit trail is complete across all workflows. Items 3 and 6 are CI gaps that should be closed within the next sprint.

---

### 7.2 Redis Health Check Missing from V2 Compose [MEDIUM RISK]

The `redis` service in `docker-compose.v2.yml` has no `healthcheck` directive, while `postgres` correctly defines one. The API's `depends_on` only waits for the Postgres healthcheck — creating a potential race condition where the API starts before Redis is accepting connections.

**Fix:**
```yaml
redis:
  image: redis:7-alpine
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5

# In api depends_on:
  redis:
    condition: service_healthy
```

---

### 7.3 IRT Item Bank is Critically Undersized [HIGH RISK — Pedagogical]

The V2 manifest explicitly states the current IRT seed is a "legacy 10-item sample" and requires a minimum of **500 calibrated items** with correct 2PL `a` (discrimination) and `b` (difficulty) parameters across Grades R–7. Until this is in place, the Gap-Probe Cascade diagnostic cannot perform at clinical validity — it would produce estimates based on insufficient information, potentially misclassifying learner ability and generating incorrect study plans.

This is the highest-risk pedagogical gap. The Alembic seed migration for 500+ items is listed as Task 3.1 and has not yet been completed.

---

### 7.4 Ether Cold-Start Lag Not Yet Fixed [MEDIUM RISK — UX]

The legacy system requires 8–10 learning events before it can classify a learner's archetype. The V2 fix (Task 3.2: 5-question onboarding micro-diagnostic) is listed as outstanding. Until this is implemented, new learner session 1 will be served with generic (non-personalised) AI tone and scaffolding, which undermines the platform's primary differentiator.

---

### 7.5 `docker-compose.prod.yml` Referenced but Unverified [MEDIUM RISK]

The CHANGELOG (`[Unreleased]`) lists `docker-compose.prod.yml` as an added canonical production deployment stack with Nginx reverse-proxy and SSL termination. A direct fetch of this file returned 404. Either it was renamed, moved into `docker/`, or was not yet committed. The production deployment path needs to be verified and, if absent, created before any staging promotion.

---

### 7.6 `scratch/` and `mnt/user-data/` in Version Control [LOW-MEDIUM RISK]

The repository tree contains two directories that should not be committed:

- **`scratch/`** — an explicit "scratch work" directory. Any useful code here should be promoted to proper modules; the rest should be deleted.
- **`mnt/user-data/outputs/eduboost`** — a path structure that matches Claude's artifact output system. This is an AI session artifact committed to the repository accidentally.

Both should be removed, added to `.gitignore`, and the history cleaned (easy with 33 commits still manageable).

---

### 7.7 `ci.yml` Placement Requires Verification [HIGH RISK]

The `ci.yml` file is at the **repository root** rather than `.github/workflows/`. GitHub Actions only automatically triggers workflows defined in `.github/workflows/`. The `.github/` directory exists in the repo, suggesting a workflow may be defined there too — but if the root `ci.yml` (329 lines, highly detailed) is the authoritative definition and not mirrored under `.github/workflows/`, **none of the sophisticated CI gates are executing** on push or PR.

This must be verified immediately. If it is confirmed that `ci.yml` is not in `.github/workflows/`, moving it there is a 2-minute fix with potentially critical impact.

---

### 7.8 Frontend TypeScript Migration Incomplete [MEDIUM RISK]

The language split (9.5% JavaScript vs 1.3% TypeScript) indicates the frontend is majority plain JavaScript. For a Next.js 14 App Router project, this means the client-side service layer (`src/lib/api/`) and UI components may lack type safety on API contracts. Given the sensitivity of the data (parental consent flows, learner PII displays), TypeScript coverage of the frontend API layer is a meaningful safety net.

---

### 7.9 Stripe Integration Not Yet Implemented [LOW RISK — Business]

Phase 5 of the V2 manifest defines a Stripe subscription engine tiered between Free and Premium access, gating the AI Gateway quotas. The `requirements.txt` contains no Stripe library. This is expected for a pre-revenue beta, but the connection between AI cost-control (daily quotas per user) and subscription state will require careful implementation to avoid billing bypass vulnerabilities.

---

### 7.10 JWT Refresh Token Rotation Absent [MEDIUM RISK — Security]

`SECURITY.md` confirms: access tokens expire after 24 hours, and the refresh token rotation flow is "planned but not yet implemented." With 24-hour token lifespans and no rotation, a stolen JWT remains valid for up to 24 hours with no revocation mechanism. For a platform handling children's data, this window is too large. HTTP-only refresh tokens with rotation should be prioritised before production launch.

---

### 7.11 No Secrets Scanning in CI [HIGH RISK — Security]

`SECURITY.md` explicitly lists "CI/CD secrets scanning not configured" as a known gap. Without tools like `gitleaks`, `truffleHog`, or GitHub's native secret scanning enabled on the repository, there is no automated prevention of API keys, JWT secrets, or encryption keys being accidentally committed.

---

## 8. Security & Compliance Deep Dive

### 8.1 Confirmed Security Controls

| Control | Implementation | Verified |
|---|---|---|
| LLM PII boundary | `judiciary.py` — structural enforcement | ✅ |
| Email encryption at rest | SHA-256 hash + Fernet ciphertext | ✅ |
| Pseudonym ID isolation | `pseudonym_id` — never real UUID to LLM | ✅ |
| JWT authentication | HS256, 64-char secret, 24h expiry | ✅ |
| Password hashing | `passlib[bcrypt]` | ✅ |
| API rate limiting | `slowapi` | ✅ |
| Input sanitisation | `bleach`, `phonenumbers` | ✅ |
| CORS whitelist | Explicit origins, no wildcard | ✅ |
| Consent gating | `require_active_consent()` mandatory gate | ✅ |
| Annual consent renewal | `expires_at` column | ✅ |
| Right to erasure | Soft-delete + background purge | ✅ (partial) |
| Audit trail | Redis stream → V2 Postgres append-only | ✅ (stream implemented) |
| Docker image CVE scan | Trivy CRITICAL+HIGH, SARIF | ✅ |
| LLM backend-mediated only | Learners never call LLM APIs directly | ✅ |
| Inference network isolation | Internal Docker network only | ✅ |

### 8.2 Security Severity Classification (from SECURITY.md)

The project has defined its own severity tiers, which align well with industry standards:

- **P0 (Critical, 24h)**: Auth bypass, unauthenticated learner data access, SQL injection, JWT downgrade, pseudonymisation bypass, plaintext key storage
- **P1 (High, 7d)**: IDOR, missing HTTPS, CSRF, broken RBAC, audit log tampering, secrets in images, Redis cache poisoning
- **P2 (Medium, 30d)**: LLM rate limiting bypass, XSS in lessons, insecure CORS, session fixation
- **P3 (Low, backlog)**: Information disclosure, missing security headers, dependency CVEs without known exploits

The presence of "Redis cache poisoning affecting learner responses" as a P1 item demonstrates domain-specific threat modelling — an attacker poisoning lesson content for a specific learner archetype is a real attack surface.

### 8.3 RBAC Status

Phase 4 (Task 4.1) defines four roles: `Student`, `Parent`, `Teacher`, `Admin` with JWT-backed short-lived access tokens and HTTP-only refresh tokens. This is the target state. The current implementation status of multi-role RBAC is not fully verifiable from public file inspection, but the SECURITY.md indicates refresh token rotation is "planned" — suggesting the full RBAC flow is not yet complete.

---

## 9. CI/CD & DevOps Assessment

### 9.1 Pipeline Architecture (ci.yml — 329 lines)

```
trigger: push→[main,develop], PR→main, release→published
│
├── lint          (ruff + mypy --strict-optional)
├── unit-tests    (pytest, 80% coverage, Codecov upload)
├── integration-tests  (Postgres 15 + Redis 7 containers)
├── v2-smoke      (import api_v2 entrypoint + repositories)
├── frontend      (npm ci, npm test, npm run build)
├── schema-drift  (alembic upgrade head + alembic check)
├── popia-tests   (pytest tests/popia/ -k "pii or consent or erasure")
├── image-scan    (Trivy CRITICAL+HIGH, SARIF, main/release only)
└── production-promote (needs ALL above, environment:production)
    ├── smoke tests against staging
    ├── kubectl set image + rollout status
    └── health check: /health + /judiciary/health
```

### 9.2 Pipeline Strengths

- The `production-promote` job correctly uses GitHub's `environment: production` protection — enabling required reviewers and environment-scoped secrets.
- The `v2-smoke` job explicitly imports the V2 entrypoint (`app.api_v2`) and all four repositories — catching import errors before integration tests run.
- The dual-path health check (`/health` AND `/judiciary/health`) in production verification confirms the Judiciary layer is also up — not just the API.

### 9.3 Pipeline Gaps

- **`ci.yml` at root** (not `.github/workflows/`) — if not mirrored there, the entire pipeline may not be running (see Weakness 7.7).
- **No E2E (Playwright) job** — the suite exists in `tests/` but is not a CI gate.
- **No dependency vulnerability scan** (`pip-audit` or Dependabot) — confirmed gap in `SECURITY.md`.
- **No secrets scanning** (`gitleaks`, `truffleHog`) — confirmed gap in `SECURITY.md`.
- **No Docker layer cache** in the `image-scan` job — cold builds are slow.
- **No `npm audit`** step in the frontend job — JavaScript dependency CVEs are undetected.

---

## 10. Observability & Monitoring Assessment

### 10.1 What Is In Place

| Component | Tool | Status |
|---|---|---|
| Metrics collection | Prometheus + `prometheus-fastapi-instrumentator` | ✅ |
| Dashboard visualisation | Grafana (provisioned dashboards) | ✅ |
| Log aggregation | Grafana Loki + Promtail | ✅ |
| Exception tracking | Sentry SDK (FastAPI integration) | ✅ |
| Structured logging | structlog (JSON) | ✅ |
| Business SLO dashboards | Learner Journey, LLM Health, Constitutional Health | ✅ |
| Celery monitoring | Flower (legacy path only) | ⚠️ Legacy |

### 10.2 Observability Gaps

- **No alerting rules** visible in `prometheus/` — dashboards without `alerts.yml` require manual human monitoring to detect SLO breaches.
- **No uptime/synthetic monitoring** for the ACA production endpoint.
- **PostHog / product telemetry** (Phase 5, Task 5.1) is planned but not yet implemented — product-loop metrics (session lengths, diagnostic drop-offs, lesson completions) are currently unavailable.
- **AI cost telemetry** — no token consumption counter per provider/model is visible in the current metrics instrumentation, making daily spend projection impossible.

---

## 11. Dependency Review

### 11.1 Positive Practices

- All packages pinned to exact versions — strong reproducibility.
- `requirements-ml.txt` separates torch/transformers from the main install — controlled by `INCLUDE_ML` Docker build arg.
- `asyncpg` for async API path; `psycopg2-binary` for Alembic sync — a correct pattern.
- `tenacity` for LLM call retry logic with exponential backoff.
- `bleach` + `phonenumbers` for multi-layer PII scrubbing.
- `azure-keyvault-secrets` + `azure-identity` present (medium-term secrets management target).

### 11.2 Concerns

- **`anthropic==0.40.0`** — The Anthropic SDK has released multiple versions beyond 0.40.0. The current version predates Claude Sonnet 4 support. Staying current is important for accessing latest model capabilities and security patches.
- **`mkdocs`, `mkdocs-material`, `mkdocstrings`** live in `requirements.txt` rather than a separate `requirements-dev.txt`. These documentation tools are installed in production containers — unnecessary attack surface and image bloat.
- **No `pip-audit` or Dependabot** — self-acknowledged gap. Python package CVEs accumulate silently.
- **`boto3==1.34.110`** for Cloudflare R2 (S3-compatible) — pinned to a specific patch. boto3 releases frequently and patches security issues. A `>=1.34,<2` range in a compiled requirements approach would allow patch updates without breaking API.
- **`openai==1.30.5`** included for Groq's OpenAI-compatible API — this is a reasonable pattern but means any OpenAI SDK breaking change affects the Groq integration path.

---

## 12. System Optimization Recommendations

Prioritised by impact × urgency.

---

### 12.1 [CRITICAL] Verify and Fix CI Workflow Placement

Confirm whether `.github/workflows/` contains an active workflow that mirrors `ci.yml`. If not, move it immediately:

```bash
mkdir -p .github/workflows
cp ci.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "fix(ci): ensure workflow is discoverable by GitHub Actions"
```

This is a 5-minute fix that could unlock the entire quality gate system.

---

### 12.2 [CRITICAL] Close POPIA §24 Right-to-Erasure Verification

Write a comprehensive integration test that:
1. Creates a guardian + learner + consent record
2. Calls `DELETE /api/v1/learners/{id}` with a valid Guardian JWT
3. Asserts consent is revoked
4. Asserts all PII fields are soft-deleted
5. Asserts a purge `BackgroundTask` is queued
6. Asserts LLM provider cannot be called for the deleted pseudonym

Gate this test in the `popia-tests` CI job before any production data ingestion.

---

### 12.3 [CRITICAL] Add Secrets Scanning to CI

```yaml
secrets-scan:
  name: Secrets Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0   # full history for gitleaks
    - uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Enable GitHub's native secret scanning in the repository settings simultaneously.

---

### 12.4 [HIGH] Implement JWT Refresh Token Rotation

```python
# In security.py
def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(days=7)
    return jwt.encode({"sub": subject, "exp": expire, "type": "refresh"}, 
                      settings.JWT_SECRET, algorithm="HS256")

# In auth router — HTTP-only cookie, SameSite=Strict
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=7 * 24 * 3600
)
```

Reduce access token expiry from 24h to 15 minutes once rotation is in place.

---

### 12.5 [HIGH] Add Redis Healthcheck to `docker-compose.v2.yml`

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5

# api service depends_on:
  redis:
    condition: service_healthy
```

---

### 12.6 [HIGH] Priority IRT Item Bank Seeding (500+ Items)

The Gap-Probe Cascade cannot function at clinical validity with 10 items. Create an Alembic seed migration:

```python
# alembic/versions/0005_irt_item_bank.py
IRT_ITEMS = [
    # {"subject": "mathematics", "grade": 1, "topic": "counting",
    #  "a": 1.2, "b": -1.5, "question": "...", "options": [...], "correct": 0},
    # ... 500+ calibrated items across Grades R-7, all CAPS-aligned subjects
]
```

Partner with a certified CAPS educator to validate discrimination (a) and difficulty (b) parameter estimates.

---

### 12.7 [HIGH] Add Prometheus Alerting Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: eduboost_slos
    rules:
      - alert: LLMProviderHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{handler="/api/v2/lessons"}[5m])) > 10
        for: 5m
        labels:
          severity: warning
      - alert: ConsentGateFailureSpike
        expr: rate(eduboost_consent_failures_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
```

---

### 12.8 [MEDIUM] Split Requirements into Environment-Specific Files

```
requirements/
├── base.txt    # Runtime only — no mkdocs, no dev tools
├── dev.txt     # -r base.txt + pytest + pre-commit + ruff + mypy
├── docs.txt    # mkdocs + mkdocs-material + mkdocstrings
└── ml.txt      # Already separate — reference as-is
```

Production Dockerfiles install only `base.txt`. This reduces image size and attack surface.

---

### 12.9 [MEDIUM] Add AI Token Cost Telemetry

```python
LLM_TOKENS_USED = Counter(
    "eduboost_llm_tokens_total",
    "Tokens consumed",
    ["provider", "model", "operation"]
)
LLM_COST_USD = Gauge(
    "eduboost_llm_estimated_cost_usd",
    "Estimated daily LLM spend",
    ["provider"]
)
```

Add a Grafana panel for daily token consumption and projected cost per provider. At beta scale with variable demand, unmonitored LLM usage can produce unexpected spend spikes.

---

### 12.10 [MEDIUM] Add Playwright E2E as a CI Gate

```yaml
e2e:
  name: E2E Tests (Playwright)
  needs: [integration-tests]
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: npm ci
    - run: npx playwright install --with-deps chromium
    - run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: playwright-report
        path: playwright-report/
```

The diagnostic → study plan → lesson → parent portal E2E suite exists but is not yet a CI gate.

---

### 12.11 [MEDIUM] Implement Ether Cold-Start Micro-Diagnostic (Task 3.2)

Five targeted onboarding questions (visual preference, learning pace, response style, motivation driver, language preference) mapped to archetype probability vectors. This unlocks personalisation from session 1 — the platform's primary differentiator.

---

### 12.12 [LOW] Clean Up Repository Artefacts

```bash
git rm -r scratch/ mnt/
echo "scratch/" >> .gitignore
echo "mnt/" >> .gitignore
git commit -m "chore: remove scratch dir and AI session artefact from tracked files"
```

---

### 12.13 [LOW] Rename the V2 Architecture Document

```bash
mkdir -p docs/architecture
git mv gemini-code-1777601244294.md docs/architecture/V2_ARCHITECTURE.md
# Update all references in AGENT_INSTRUCTIONS_V2.md, README.md
git commit -m "docs: promote V2 architecture manifest to stable path"
```

---

## 13. Migration Completion Roadmap

| Milestone | Priority | Deliverable | Estimated Effort |
|---|---|---|---|
| **M1: CI Verification** | CRITICAL | Confirm `.github/workflows/` active; add secrets scan + pip-audit | 1 day |
| **M2: POPIA §24 E2E** | CRITICAL | End-to-end erasure integration test; consent audit trail complete | 3–5 days |
| **M3: JWT Refresh Rotation** | HIGH | HTTP-only refresh tokens; 15min access token TTL | 2–3 days |
| **M4: Redis Healthcheck** | HIGH | V2 compose fix + depends_on update | 30 min |
| **M5: IRT Item Bank (500+)** | HIGH | Alembic seed migration; CAPS educator validation | 2–3 weeks |
| **M6: Ether Cold-Start** | MEDIUM | 5-question onboarding micro-diagnostic | 1 week |
| **M7: Prometheus Alerts** | MEDIUM | `alerts.yml` for LLM latency, consent failures, SLO breaches | 1 day |
| **M8: E2E in CI** | MEDIUM | Playwright job gated in pipeline | 1–2 days |
| **M9: Requirements Split** | MEDIUM | base/dev/docs split; prod Dockerfiles updated | 1 day |
| **M10: AI Cost Telemetry** | MEDIUM | Token counter + Grafana cost panel | 1 day |
| **M11: V2 Router Parity** | HIGH | All legacy routers replaced; legacy moved to `app/legacy/` | 2–4 weeks |
| **M12: RBAC Completion** | HIGH | Student/Parent/Teacher/Admin roles fully enforced | 1–2 weeks |
| **M13: Stripe Integration** | LOW | Subscription engine + AI Gateway quota gating | 2–3 weeks |
| **M14: GA Release (v1.0.0)** | — | All above complete; GitHub Release published; staging verified | 6–10 weeks |

---

## 14. Scoring Summary

| Domain | Score | Key Driver |
|---|---|---|
| Architecture Design | 7.5 / 10 | Strong V2 vision and DDD boundaries; dual-runtime transition in progress |
| POPIA / Compliance | 9.0 / 10 | Structural enforcement is best-in-class; 2 legal gaps still open |
| CI/CD Pipeline | 8.0 / 10 | Sophisticated 8-job pipeline; placement risk and missing E2E/secrets scan |
| Security Posture | 7.0 / 10 | Strong PII controls; 6 self-disclosed gaps including no refresh rotation |
| Test Strategy | 6.5 / 10 | 80% unit threshold enforced; E2E not in CI; V2 module coverage unknown |
| Observability | 7.5 / 10 | Complete stack; alerting rules and cost telemetry missing |
| Dependency Management | 6.5 / 10 | Good pinning; dev/docs deps in prod; no automated CVE scanning |
| Developer Experience | 8.0 / 10 | Excellent agent-driven docs and TDD loop; scratch artefacts committed |
| Pedagogical Validity | 6.0 / 10 | IRT model correct; item bank (10 items vs. 500 required) is critical gap |
| Scalability Readiness | 7.0 / 10 | Async LLM, inference decoupled, ACA IaC defined; caching not yet wired |
| Domain & Cultural Depth | 9.0 / 10 | IRT + 4 languages + SA cultural context + archetype engine |
| **Overall** | **7.4 / 10** | Strong foundations; 6 security gaps and IRT item bank are the blockers |

---

*Report prepared via AI-assisted technical assessment of the public repository at `https://github.com/NkgoloL/Eduboost-V2` — May 2026.*
*All findings are derived from direct inspection of publicly accessible files on the master branch (33 commits). Internal files in `audits/roadmaps/` and `app/` subdirectories that were not directly accessible via GitHub's public file pages are noted where relevant but cannot be assessed.*
