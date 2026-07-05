---
title: "EduBoost SA"
status: active
owner: product
reviewers: [product, engineering, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# EduBoost SA

[![CI/CD](https://github.com/nkgolomatjila-svg/Eduboost_V.2/actions/workflows/ci-cd.yml/badge.svg?branch=master)](https://github.com/nkgolomatjila-svg/Eduboost_V.2/actions/workflows/ci-cd.yml)
[![Security Scans](https://img.shields.io/badge/Security-Scanned-blue)](/SECURITY.md)
[![POPIA](https://img.shields.io/badge/POPIA-Tracked-success)](/docs/POPIA_COMPLIANCE.md)
[![CAPS](https://img.shields.io/badge/CAPS-Aligned-00897B)](https://www.education.gov.za)

EduBoost SA is a modular learning platform for South African primary education.
The active implementation path is the V2 FastAPI runtime plus the Next.js
frontend, with a small compatibility surface still kept around for legacy
imports and controlled migration behavior.

## Current State

- `app/api_v2.py` is the active backend entrypoint for new work.
- The local WSL checkout at `/home/nkgolol/Dev/Development/Eduboost-V2`
  is the main working directory and current source-of-truth workspace. The
  previously referenced remote VM is not accessible and must not be treated as
  canonical until access and environment identity are re-established. See
  [`docs/operations/workspace_source_of_truth.md`](docs/operations/workspace_source_of_truth.md).
- `docker compose up --build` is the default local stack and points at the V2
  runtime.
- The merged PR-002R and production-readiness evidence work establishes the V2
  runtime and API contract baseline; production readiness still depends on
  fresh security, POPIA, CI/CD, backup/restore, AI-safety, frontend, staging,
  and release-evidence verification.
- The Recommended Operating Model and Project Assistance Status controls are
  now documented under `docs/operations/` and wired into Makefile/CI checks so
  triage, verification, release evidence, hardening, and staging readiness work
  have an executable command surface.
- Legacy code has been archived behind compatibility shims under
  [`app/legacy`](/app/legacy/DEPRECATED.md) and [`app/legacy/api/main.py`](/app/legacy/api/main.py).
- Redis is used for caching, token revocation, and background job status.
- Sensitive audit events are persisted through the V2 append-only PostgreSQL
  audit repository.
- The Grade 4 Mathematics launch content slice is deployed and seeded for 4.M.1.1, 4.M.1.2, and 4.M.1.3: 120 approved diagnostic items and 24 approved lessons are live. Evidence is recorded in docs/release/runtime_launch_content_evidence_status.md; use python3 scripts/validate_launch_content.py --strict and the coverage APIs as the operational workflow.
- The repository still carries migration-era artifacts, so documentation should
  be read as "current master state", not as a promise that every legacy surface
  is already retired.

For the current documentation sync status, see
[`docs/current_state.md`](/docs/current_state.md), [`docs/project_status.md`](/docs/project_status.md), and
[`docs/documentation/source_of_truth.yml`](docs/documentation/source_of_truth.yml).

Item-bank coverage details live in
[`docs/caps/grade4_maths_coverage_matrix.md`](/docs/caps/grade4_maths_coverage_matrix.md).
The launch content evidence lives in docs/release/runtime_launch_content_evidence_status.md.


## Authoritative Documentation Map

Use these domain indexes for current implementation guidance:

- [Backend](docs/backend/README.md)
- [Frontend](docs/frontend/README.md)
- [Diagnostics and assessment](docs/diagnostics/README.md)
- [IRT engine](docs/irt/README.md)
- [ETL and source evidence](docs/etl/README.md)
- [POPIA and data rights](docs/popia/README.md)
- [Security](docs/security/README.md)
- [Testing](docs/testing/README.md)
- [Deployment and operations](docs/deployment/README.md)
- [Roadmap index](docs/roadmap/README.md)

The active deep-audit baseline is in [audits/deep_app_audit](audits/deep_app_audit/implementation_reality_report.md).

## Quick Start

### Prerequisites

- Docker Desktop with Compose v2
- Python 3.12.3 (managed via `.python-version`; see `docs/adr/ADR-001-python-runtime-version.md`)
- Node.js 20 LTS

### Start the default stack

```bash
cp .env.example .env
docker compose up --build
```

If the local PostgreSQL migration fails with a missing role error like `role "eduboost_app" does not exist`, create the role before re-running migrations:

```bash
docker exec -it eduboost-v2-postgres-1 psql -U eduboost_user -d eduboost -c "CREATE ROLE eduboost_app NOLOGIN;"
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

- [`app/legacy/api/main.py`](/app/legacy/api/main.py) remains as an import shim.
- Archived legacy runtime code lives under [`app/legacy`](/app/legacy/DEPRECATED.md).
- V1 behavior that should no longer be used is intentionally narrowed rather
  than silently preserved.

## Compose File Map

The repository contains multiple Compose files on purpose:

- `docker-compose.yml` - default local V2 stack
- `docker-compose.v2.yml` - explicit V2-focused compose variant
- `docker-compose.aca.yml` - Azure Container Apps-oriented stack
- `docker-compose.prod.yml` - production-like compose path

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

- Current state: [`docs/current_state.md`](/docs/current_state.md)
- Status index: [`docs/project_status.md`](/docs/project_status.md)
- Documentation source-of-truth register: [`docs/documentation/source_of_truth.yml`](docs/documentation/source_of_truth.yml)
- Documentation housekeeping policy: [`docs/documentation/documentation_housekeeping_policy.md`](docs/documentation/documentation_housekeeping_policy.md)
- Operating model: [`docs/operations/recommended_operating_model.md`](/docs/operations/recommended_operating_model.md)
- Project assistance lanes: [`docs/operations/project_assistance_status.md`](/docs/operations/project_assistance_status.md)
- TODO implementation plan: [`docs/operations/todo_implementation_plan.md`](/docs/operations/todo_implementation_plan.md)
- Architecture: [`docs/architecture/ARCHITECTURE.md`](/docs/architecture/ARCHITECTURE.md)
- Migration guide: [`docs/v2_migration.md`](/docs/v2_migration.md)
- POPIA notes: [`docs/POPIA_COMPLIANCE.md`](/docs/POPIA_COMPLIANCE.md)
- Security policy: [`SECURITY.md`](/SECURITY.md)
- Contribution guide: [`CONTRIBUTING.md`](/CONTRIBUTING.md)

Use `mkdocs serve` or `docker compose up --build` to browse the generated docs
site locally.

<!-- KG000_FORMAL_ROADMAP_APPROVAL:start -->
## Knowledge Graph Roadmap

EduBoost's post-RR roadmap introduces the Knowledge Graph learning-state stream as a newly approved roadmap, starting with `KG-0 — Formal KG roadmap approval`.

Key references:

- [ADR-030 Knowledge Graph Learning-State Core](docs/adr/ADR-030-knowledge-graph-learning-state-core.md)
- [KG Implementation Roadmap](docs/roadmap/knowledge_graph/kg_implementation_roadmap.md)
- [KG Roadmap Register](docs/roadmap/knowledge_graph/kg_roadmap_register.json)

Boundary: KG-0 does not implement runtime KG behavior or authorise production release, deployment, public beta, billing launch, or a runtime KG authority switch.
<!-- KG000_FORMAL_ROADMAP_APPROVAL:end -->
