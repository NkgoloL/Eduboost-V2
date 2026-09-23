---
title: "ADR-028 — Authoritative Production Deployment Target"
status: active
owner: architecture
reviewers: [engineering, architecture, platform]
audience: developer
source_of_truth: true
supersedes: [ADR-003]
superseded_by: null
last_reviewed: 2026-09-22
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: [render.yaml, docker-compose.yml]
---
# ADR-028 — Authoritative Production Deployment Target

**Status:** Accepted (Amended 2026-09-22)  
**Date:** 2026-06-12 (Amended 2026-09-22)  
**Decision owner:** Platform / Engineering  
**Phase:** 7 (Deployment and Security Hardening) / Platform Convergence  
**Supersedes:** ADR-003  

---

## Context

Multiple deployment artefacts coexist in this repository:

| Artefact | Purpose |
|---|---|
| `render.yaml` | Render Blueprint (Web API, Workers, Ingress) |
| `docker-compose.yml` | Local developer environment |
| `docker-compose.prod.yml` | Local production-smoke / staging convenience |
| `bicep/container_apps.bicep` | Azure Container Apps (ACA) IaC (Legacy/Secondary) |
| `k8s/api-deployment.yml` | Kubernetes (legacy/exploratory) |

To prevent deployment divergence and clarify operational authority, an authoritative primary cloud target must be designated for all staging and production deployments.

---

## Decision

**Render via `render.yaml` is the authoritative primary production and staging deployment target.**

All other deployment targets are secondary or local development conveniences:

| Target | Role | Notes |
|---|---|---|
| **Render (`render.yaml`)** | **Authoritative Primary Target** | Unified Blueprint: Python 3.12.3, `/ready` health probe, Supabase Postgres, Upstash Redis |
| `docker-compose.yml` | Developer local dev | No TLS, open ports, local mock dependencies |
| `docker-compose.prod.yml` | Local smoke-test / staging convenience | Secrets via `.env` — local only, never commit |
| `bicep/container_apps.bicep` | Secondary / Legacy Cloud Target | Retained as secondary reference; not the primary deployment target |
| `k8s/api-deployment.yml` | Legacy exploratory draft | Not maintained, not for production use |

---

## Rationale

- **Simplicity and Reliability**: `render.yaml` provides a single declarative Blueprint for web services and background workers without excessive cloud infrastructure overhead.
- **Hermetic Runtime Alignment**: `render.yaml` strictly enforces `PYTHON_VERSION: "3.12.3"` in lockstep with ADR-001 and local development.
- **Deep Health Probing**: Aligns directly with `/ready` readiness probing for real DB/Redis connectivity.
- **Managed Integrations**: Seamlessly interfaces with Supabase Managed PostgreSQL and Upstash Redis.

---

## Secret Management per Target

| Target | Secret Source |
|---|---|
| Render (production & staging) | Render Dashboard environment variables & Blueprint `sync: false` parameters |
| Docker Compose prod | `.env` file on local workstation — **local only, never commit** |
| Docker Compose dev | `.env` file — dev placeholders acceptable |
| ACA (legacy) | Azure Key Vault parameters |

---

## Consequences

### Positive
- Single authoritative cloud deployment blueprint (`render.yaml`).
- Eliminates operational confusion between ACA and Render.
- Clean environment variable mapping verified by automated repository hygiene checks.

### Negative
- Azure Container Apps pipelines become legacy/secondary reference material.

---

## References

- Render Blueprint: `render.yaml`
- Phase 7 execution plan: `docs/roadmap/execution/phase_7_execution_plan.md` §7.9  
- ADR-001 (Python Runtime): `docs/adr/ADR-001-python-runtime-version.md`  
- Health contract: `docs/operations/health.md`
