---
title: "ADR-028 — Authoritative Production Deployment Target"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-028 — Authoritative Production Deployment Target

**Status:** Accepted  
**Date:** 2026-06-12  
**Decision owner:** Platform / Engineering  
**Phase:** 7 (Deployment and Security Hardening)  
**Supersedes:** ADR-003 (partial — adds authoritative cloud target)

---

## Context

Multiple deployment artefacts coexist in this repository:

| Artefact | Purpose |
|---|---|
| `docker-compose.yml` | Local developer environment |
| `docker-compose.prod.yml` | Local production-smoke / staging convenience |
| `bicep/container_apps.bicep` | Azure Container Apps (ACA) IaC |
| `render.yaml` | Render.com staging/early-beta |
| `k8s/api-deployment.yml` | Kubernetes (legacy/exploratory) |

This ambiguity has caused confusion about which target receives production traffic and
which security controls are authoritative.

---

## Decision

**Azure Container Apps (ACA) via `bicep/container_apps.bicep` is the authoritative
production deployment target.**

All other targets are secondary:

| Target | Role | Notes |
|---|---|---|
| **ACA (`bicep/container_apps.bicep`)** | **Authoritative production** | Secrets via Key Vault param injection |
| `docker-compose.prod.yml` | Local smoke-test / staging convenience | Secrets via `.env` — local only, never commit |
| `docker-compose.yml` | Developer local dev | No TLS, open ports |
| `render.yaml` | Early-beta / PR previews | Render dashboard secrets |
| `k8s/api-deployment.yml` | Legacy exploratory draft | Not maintained, not for production use |

---

## Rationale

- ACA aligns with the existing Azure identity and Key Vault investment.
- Bicep parameters allow secrets to be injected from Key Vault at deploy time
  (no secrets in repo or Compose env vars for production).
- Docker Compose prod file is retained as a local smoke-test convenience but
  is explicitly documented as **not** the production deployment path.

---

## Secret management per target

| Target | Secret source |
|---|---|
| ACA (production) | Azure Key Vault — injected as Bicep `@secure()` params via CI pipeline |
| Docker Compose prod | `.env` file on the machine — **local only, never commit** |
| Docker Compose dev | `.env` file — dev placeholders acceptable |

---

## Consequences

### Positive
- Single source of truth for production infrastructure.
- Key Vault integration eliminates secrets in Compose env vars for production.
- Non-authoritative artefacts are clearly labelled.

### Negative
- Teams without Azure access cannot test the full ACA deployment locally.
  Mitigation: `docker-compose.prod.yml` provides a functional local approximation.

---

## References

- Phase 7 execution plan: `docs/roadmap/execution/phase_7_execution_plan.md` §7.9  
- ADR-003: `docs/adr/ADR-003-deployment-targets.md`  
- Bicep: `bicep/container_apps.bicep`
