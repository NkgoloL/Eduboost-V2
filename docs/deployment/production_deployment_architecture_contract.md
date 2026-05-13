# Production Deployment Architecture Contract

## Purpose

This contract defines CI/CD, infrastructure, Docker, deployment, and environment architecture for EduBoost V2.

## Required Architecture Controls

- containerized cloud runtime
- managed or GitHub container registry
- infrastructure-as-code boundary
- separate local, test, staging, and production environments
- externalized secret management
- runtime role separation for API, worker, frontend, migration, and scheduler
- deployment artifact provenance by Git SHA and image digest
- staging deployment before production deployment
- manual production approval gate
- production rollback plan
- post-deploy smoke testing
- observability enabled for staging and production

## Boundary

This contract records repository-side deployment architecture readiness. It does not provision cloud infrastructure or deploy workloads.
