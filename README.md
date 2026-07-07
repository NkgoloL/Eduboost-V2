---
title: "EduBoost SA"
status: active
owner: product
reviewers: [product, engineering, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-07
review_interval_days: 180
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd001_canonical_current_state_documentation_refresh.py --json
code_anchors: [docs/current_state.md, docs/roadmap/production_readiness/production_readiness_register.json]
---
# EduBoost SA

[![Security Scans](https://img.shields.io/badge/Security-Scanned-blue)](/SECURITY.md)
[![POPIA](https://img.shields.io/badge/POPIA-Tracked-success)](/docs/POPIA_COMPLIANCE.md)
[![CAPS](https://img.shields.io/badge/CAPS-Aligned-00897B)](https://www.education.gov.za)

EduBoost SA is a modular learning platform for South African Grade 4 Mathematics. The active implementation path is the V2 FastAPI runtime, the Next.js frontend, and the controlled Knowledge Graph learning-state architecture.

## Current authority state

The repository has completed two major closure streams and opened a new production-readiness stream:

```text
RR roadmap/TODO register: closed
KG roadmap: closed through KG-8
Controlled runtime KG authority switch: executed
Production-readiness stream: open at PRD-0
Current authorised item: PRD-0.1
PRD-1 implementation: blocked until PRD-0.10 closure
```

The controlled runtime KG authority switch is recorded as:

```text
runtime_kg_implementation_claimed: true
runtime_kg_authority_switch_authorised: true
authority_switch_executed: true
```

These remain unauthorised:

```text
production_release_authorised: false
deployment_authorised: false
release_tag_authorised: false
public_beta_authorised: false
public_beta_live_traffic_authorised: false
live_learner_traffic_authorised: false
billing_launch_authorised: false
live_payment_processing_authorised: false
new_kg_slice_authorised: false
prd1_implementation_authorised: false
```

## Canonical project status

Start with:

- [`docs/current_state.md`](docs/current_state.md)
- [`docs/roadmap/production_readiness/production_readiness_register.json`](docs/roadmap/production_readiness/production_readiness_register.json)
- [`docs/roadmap/production_readiness/production_readiness_boundary_contract.md`](docs/roadmap/production_readiness/production_readiness_boundary_contract.md)
- [`docs/roadmap/production_readiness/prd_0_expanded_post_closure_current_state_authority_refresh.md`](docs/roadmap/production_readiness/prd_0_expanded_post_closure_current_state_authority_refresh.md)

Historical reports and older roadmap documents may remain useful for context, but they must not override the current-state and production-readiness records above.

## Active implementation path

- `app/api_v2.py` is the active backend entrypoint for new backend work.
- `app/frontend` contains the active Next.js frontend.
- PostgreSQL/Alembic remains the persistence path.
- Redis supports configured runtime services.
- `docs/openapi.json` is the canonical OpenAPI artifact until PRD-0.7 completes generated-artifact canonicalisation.
- KG runtime authority is controlled by the KG closure and activation evidence, but production release and live learner traffic remain separately gated.

## Authoritative documentation map

Use these indexes for current implementation guidance:

- [Documentation index](docs/README.md)
- [Architecture index](docs/architecture/README.md)
- [Roadmap index](docs/roadmap/README.md)
- [Production-readiness register](docs/roadmap/production_readiness/production_readiness_register.json)
- [Backend](docs/backend/README.md)
- [Frontend](docs/frontend/README.md)
- [Diagnostics and assessment](docs/diagnostics/README.md)
- [POPIA and data rights](docs/popia/README.md)
- [Security](docs/security/README.md)
- [Testing](docs/testing/README.md)
- [Deployment and operations](docs/deployment/README.md)

## Quick start

### Prerequisites

- Docker Desktop with Compose v2
- Python 3.12.3, managed via `.python-version`
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

## Production-readiness rule

Do not start PRD-1, production release, deployment, public beta, live learner traffic, billing, or a new KG slice until the relevant future PRD gate explicitly authorises it.
