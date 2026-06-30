# Deployment And Operations

Deployment covers local compose, production-like compose smoke checks, Azure/IaC assets, runtime health, observability, backup/restore, and release evidence.

## Runtime map

- Compose: `docker-compose.yml`, `docker-compose.prod.yml`, `docker-compose.override.example.yml`
- Dockerfiles/config: `docker/`, `nginx/`
- Infrastructure: `bicep/`, `deployment/`, `k8s/`, `.github/workflows/`
- Backup/restore commands: `scripts/run_database_backup.py`, `scripts/run_database_restore.py`

## Current implementation notes

- Backup and restore commands now have guarded real execution paths; dry-run remains the CI default.
- Production frontend runtime evidence still needs deployed runtime proof, not just static compose checks.
- CI, staging, and external approval evidence must be treated separately from repository-side implementation.

## Verification

- `make runtime-check`
- `make database-backup-dry-run`
- `make database-restore-dry-run`
- `make prod-frontend-runtime-check`
- `make staging-release-gate-check`

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
