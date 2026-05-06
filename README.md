# EduBoost SA

[![CI/CD](https://github.com/NkgoloL/Eduboost-V2/actions/workflows/ci-cd.yml/badge.svg?branch=master)](https://github.com/NkgoloL/Eduboost-V2/actions/workflows/ci-cd.yml)
[![Docs](https://github.com/NkgoloL/Eduboost-V2/actions/workflows/docs.yml/badge.svg?branch=main)](https://nkgolol.github.io/Eduboost-V2/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25%2B-brightgreen)](/app/frontend/coverage/index.html)
[![Security Scans](https://img.shields.io/badge/Security-Scanned-blue)](/SECURITY.md)
[![POPIA](https://img.shields.io/badge/POPIA-Tracked-success)](/docs/POPIA_COMPLIANCE.md)
[![CAPS](https://img.shields.io/badge/CAPS-Aligned-00897B)](https://www.education.gov.za)

EduBoost SA is a modular learning platform for South African primary education.
The active implementation path is the V2 FastAPI runtime plus the Next.js
frontend, with a small compatibility surface still kept around for legacy
imports and controlled migration behavior.

## Current State

- `app/api_v2.py` is the active backend entrypoint for new work.
- `docker compose up --build` is the default local stack and points at the V2
  runtime.
- The platform has reached the **v1.0.0-rc1** milestone, representing a fully hardened, production-ready modular monolith.
- Legacy V1 code has been fully decommissioned; the V2 runtime is now the sole authoritative path.
- Background tasks are handled by `arq` (async Redis queue), replacing Celery and RabbitMQ.
- The repository is organized into domain modules (`app/modules/`) with strict architectural boundaries.
- POPIA compliance is verified via automated sweeps and a dedicated audit repository.

For the current documentation sync status, see
[`docs/project_status.md`](/docs/project_status.md) and the root
[`TODO.md`](/TODO.md).

## Quick Start

### Prerequisites

- Docker Desktop with Compose v2
- Python 3.11+
- Node.js 20 LTS

### Start the default stack

```bash
cp .env.example .env
docker compose up --build
```

Useful URLs:

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

Run backend checks:

```bash
pytest tests/ -v --tb=short
python scripts/popia_sweep.py --fail-on-issues
```

Run frontend checks:

```bash
cd app/frontend
npm test
npm run test:coverage
npm run type-check
npm run lint
```

## Runtime Layout

The codebase is organized as a modular monolith:

- `app/api_v2.py` - FastAPI entrypoint
- `app/api_v2_routers/` - HTTP routes
- `app/services/` - application workflows
- `app/repositories/` - persistence layer
- `app/domain/` - contracts and domain models
- `app/core/` - shared runtime kernel
- `app/modules/` - learning engines and bounded modules

Legacy compatibility notes:

- [`app/api/main.py`](/app/api/main.py) remains as an import shim.
- Archived legacy runtime code lives under [`app/legacy`](/app/legacy/DEPRECATED.md).
- V1 behavior that should no longer be used is intentionally narrowed rather
  than silently preserved.

## Compose File Map

The repository contains multiple Compose files on purpose:

- `docker-compose.yml` - default local V2 stack
- `docker-compose.v2.yml` - explicit V2-focused compose variant
- `docker-compose.prod.yml` - production-like compose path (Nginx + SSL)

If you are unsure which to use, start with `docker compose up --build` at the
repository root.

## Security and Compliance Snapshot

- Access tokens default to 15 minutes; refresh tokens default to 7 days.
- JWT revocation is backed by Redis.
- POPIA consent and erasure workflows are tracked in the active V2 surface.
- Security and compliance claims are documented in [`SECURITY.md`](/SECURITY.md)
  and are written to match the current repository state as closely as possible.

Operational readiness still depends on green CI, successful migrations, and a
verified release path. This repository should not claim more than those checks
can prove.

## Dependency Layout

Python dependencies are split by environment:

- `requirements/base.txt` - runtime
- `requirements/dev.txt` - tests, linting, typing, and tooling
- `requirements/docs.txt` - MkDocs and doc generation
- `requirements/ml.txt` - optional ML extras

The editable inputs for those lockfiles are:

- `requirements/base.in`
- `requirements/dev.in`
- `requirements/docs.in`
- `requirements/ml.in`

## Documentation

- Status snapshot: [`docs/project_status.md`](/docs/project_status.md)
- Architecture: [`docs/architecture/ARCHITECTURE.md`](/docs/architecture/ARCHITECTURE.md)
- Migration guide: [`docs/v2_migration.md`](/docs/v2_migration.md)
- POPIA notes: [`docs/POPIA_COMPLIANCE.md`](/docs/POPIA_COMPLIANCE.md)
- Security policy: [`SECURITY.md`](/SECURITY.md)
- Contribution guide: [`CONTRIBUTING.md`](/CONTRIBUTING.md)

Use `mkdocs serve` or `docker compose up --build` to browse the generated docs
site locally.
