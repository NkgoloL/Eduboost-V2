# ADR-012: CI/CD, Infrastructure, Deployment, Docker, and Environment Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use a containerized deployment model with CI-required checks, environment separation, externalized secrets, artifact provenance, staged deployment, rollback controls, and manual production approval.

## Rationale

A containerized deployment model gives the platform reproducible builds, isolated runtime roles, deterministic artifact promotion, and stronger release controls for staging and production.

## Required Controls

- infrastructure-as-code is required
- environment separation is required
- manual production approval is required
- deployment artifacts must be traceable to Git SHA
- container images must be scanned
- SBOM generation is required
- production secrets must be externalized
- database migrations must be controlled
- rollback plan is required
- post-deploy smoke testing is required

## Boundary

This ADR records CI/CD and deployment decision evidence. It does not provision infrastructure, build images, push artifacts, deploy services, or authorize production launch.
