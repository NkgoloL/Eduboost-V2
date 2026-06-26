---
title: "ADR-026 — Phase 4 Python Version Alignment"
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
# ADR-026 — Phase 4 Python Version Alignment

**Status:** Accepted
**Date:** 2026-06-10
**Decision owner:** Platform / Engineering
**Supersedes:** ADR-001 (Partially updates implementation tracking)

---

## Context

Phase 4 of the EduBoost V2 RoadMap requires the alignment of the Python runtime and environment across the repository. The gap analysis revealed that while `ADR-001` specified Python 3.12.3 as the standard, several files still referenced older or mismatched versions:
- `docker/Dockerfile.v2` used `python:3.11-slim`
- `docker/Dockerfile.api` used `python:3.11-slim`
- `docker/Dockerfile.inference` used `python:3.11-slim`
- `docs/DEVELOPMENT.md` referenced `Python 3.11+`
- Local testing environments sometimes defaulted to newer (e.g. 3.14) or older versions.

To ensure consistency, reduce environment-specific bugs, and cleanly gate production deployments, all these definitions must be unified to match the CI environment and `.python-version` file which target `3.12.3`.

## Decision

**We enforce Python 3.12.3 as the universal runtime version across all environments (local, Docker, and CI) for EduBoost V2.**

- **Dockerfiles** will use `python:3.12.3-slim` instead of `3.11-slim`.
- **Documentation** explicitly targets `3.12+ (currently 3.12.3)`.
- **CI** is verified to strictly use `3.12.3`.
- Any local virtual environments (like `.venv`) must be rebuilt using Python 3.12.3.
- Release-candidate testing environments will reject runtime executions if the version strictly diverges from 3.12.x unless explicitly overridden.

### Rationale

This completes the rollout initiated by ADR-001 and resolves the "Phase 4 - Runtime and Environment Alignment" requirement in the RoadMap. A single, unified version ensures that what passes CI is functionally identical to what runs in Docker and staging/production.

## Consequences

- Any developer pulling the latest `master` must rebuild their local Docker containers (`docker compose build --no-cache`).
- Developers encountering native package build errors should verify they are running Python 3.12.3.

## Validation

- CI passes on the updated Dockerfiles.
- `grep "3.11" docker/Dockerfile*` returns no results.
