# Development Guide

This guide is the doc-site version of the contributor setup for the active V2
runtime.

## Prerequisites

- Python 3.11+
- Node.js 20 LTS
- Docker Desktop with Compose v2

## Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cd app/frontend && npm ci && cd ../..
```

## Running the Stack

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3050`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- MkDocs: `http://localhost:8001`
- Prometheus: `http://localhost:9090`

## Focused Local Loops

Backend:

```bash
PYTHONPATH=. .venv/bin/pytest tests/smoke -q -o addopts=""
PYTHONPATH=. .venv/bin/python scripts/popia_sweep.py --fail-on-issues
```

Frontend:

```bash
cd app/frontend
npm test
npm run test:coverage
npm run type-check
npm run lint
```

Docs:

```bash
PYTHONPATH=. .venv/bin/mkdocs build --strict
```

## Dependency Locks

Pinned lockfiles live under `requirements/` and are regenerated with
`pip-compile`:

```bash
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt
pip-compile requirements/docs.in -o requirements/docs.txt
pip-compile requirements/ml.in -o requirements/ml.txt
```

## V2 Boundaries

Place new work in:

- `app/api_v2.py`
- `app/api_v2_routers/`
- `app/services/`
- `app/repositories/`
- `app/core/`

Legacy compatibility shims live under `app/legacy/` and should not receive new
feature work.
