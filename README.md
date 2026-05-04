# EduBoost SA

[![CI/CD](https://github.com/NkgoloL/Eduboost-V2/actions/workflows/ci-cd.yml/badge.svg?branch=master)](https://github.com/NkgoloL/Eduboost-V2/actions/workflows/ci-cd.yml)
[![Coverage](https://img.shields.io/badge/Coverage-80%25%2B-brightgreen)](/app/frontend/coverage/index.html)
[![Security Scans](https://img.shields.io/badge/Security-Scanned-blue)](/SECURITY.md)
[![POPIA](https://img.shields.io/badge/POPIA-Compliant-success)](/docs/POPIA_COMPLIANCE.md)
[![CAPS](https://img.shields.io/badge/CAPS-Aligned-00897B)](https://www.education.gov.za)

EduBoost SA is a V2 modular monolith for adaptive learning in South African
primary education. It serves CAPS-aligned diagnostics, study plans, lesson
generation, parent reporting, consent management, and compliance workflows
through a single FastAPI runtime and a typed Next.js frontend.

## Current State

- V2 is the sole supported runtime.
- The default local stack is `docker compose up --build`.
- POPIA consent, right-to-erasure, append-only audit logging, and PII export
  gates are implemented in the active runtime.
- Background work uses FastAPI `BackgroundTasks` plus a Redis job store instead
  of the old Celery-first path.
- Legacy imports are archived under [`app/legacy`](/app/legacy/DEPRECATED.md)
  and exposed only through compatibility shims.

## Quick Start

### Prerequisites

- Docker Desktop with Compose v2
- Python 3.11+
- Node.js 20 LTS

### Start the full stack

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost:3050`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- MkDocs: `http://localhost:8001`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`

### Local development without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cd app/frontend && npm ci
```

Run the backend checks:

```bash
pytest tests/ -v --tb=short
python scripts/popia_sweep.py --fail-on-issues
```

Run the frontend checks:

```bash
cd app/frontend
npm test
npm run test:coverage
npm run type-check
npm run lint
```

## Architecture

The system is organized as a modular monolith with strict boundaries:

- `app/api_v2.py` — FastAPI entrypoint
- `app/api_v2_routers/` — HTTP routes
- `app/services/` — business workflows
- `app/repositories/` — persistence layer
- `app/domain/` — request/response and domain contracts
- `app/core/` — shared runtime kernel
- `app/modules/` — adaptive engines such as IRT and archetype onboarding

The architecture record lives in
[`docs/architecture/V2_ARCHITECTURE.md`](/docs/architecture/V2_ARCHITECTURE.md).

## Key Capabilities

- Adaptive IRT diagnostics and gap ranking
- CAPS-scoped lesson generation with schema validation and semantic caching
- Redis-backed async job polling for long-running AI work
- Parent Trust Dashboard with export links and progress summaries
- POPIA consent enforcement, annual renewal reminders, and right-to-erasure
- Stripe subscription gating for free vs premium AI quotas
- PostHog and Prometheus instrumentation for product and runtime telemetry
- Offline-capable PWA lesson sync

## Dependency Layout

Python dependencies are split by environment:

- `requirements/base.txt` — runtime
- `requirements/dev.txt` — tests, linting, typing, and tooling
- `requirements/docs.txt` — MkDocs and doc generation
- `requirements/ml.txt` — optional ML extras

The editable sources for pinned locks are:

- `requirements/base.in`
- `requirements/dev.in`
- `requirements/docs.in`
- `requirements/ml.in`

## Documentation

- Architecture: [`docs/architecture/V2_ARCHITECTURE.md`](/docs/architecture/V2_ARCHITECTURE.md)
- Migration guide: [`docs/v2_migration.md`](/docs/v2_migration.md)
- POPIA notes: [`docs/POPIA_COMPLIANCE.md`](/docs/POPIA_COMPLIANCE.md)
- API reference: `mkdocs serve` or `docker compose up --build`

## Compatibility Notes

Legacy runtime files are archived, not active:

- [`app/legacy/DEPRECATED.md`](/app/legacy/DEPRECATED.md)
- [`app/api/main.py`](/app/api/main.py) remains as a compatibility import shim
- `POST /api/v1/lessons/generate` returns `410 Gone`

New work should land only in the V2 runtime surface.
