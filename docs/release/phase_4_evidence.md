# Phase 4 Evidence - Runtime and Environment Alignment

**Evidence date:** 2026-06-13  
**Refresh date:** 2026-06-14
**Status:** Runtime alignment complete

## Evidence Sources

- `.python-version`
- `docker/Dockerfile.api`
- `docker/Dockerfile.v2`
- `docker/Dockerfile.inference`
- `docs/adr/ADR-026-python-version-alignment.md`
- `.github/workflows/*`

## Current Evidence

```text
.python-version: 3.12.3
docker/Dockerfile.api: FROM python:3.12.3-slim AS base
docker/Dockerfile.v2: FROM python:3.12.3-slim AS base
docker/Dockerfile.inference: FROM python:3.12.3-slim AS builder/runtime
```

ADR-026 records Python 3.12.3 as the chosen runtime for local, Docker, and CI environments.

## Current Workflow Alignment

The 2026-06-13 audit found minor alignment issues:

- some GitHub workflows use `python-version: '3.12'` instead of `3.12.3`
- `.github/workflows/migration_check.yml` contains a stale step label saying "Set up Python 3.11" while configuring `3.12.3`

The 2026-06-14 refresh repaired those issues:

```text
.github/workflows/dependency-scan.yml: python-version: '3.12.3'
.github/workflows/e2e.yml: python-version: '3.12.3'
.github/workflows/db-backup-restore-rollback-evidence.yml: python-version: "3.12.3"
.github/workflows/secrets-scan.yml: python-version: '3.12.3'
.github/workflows/jwt-secret-rotation-evidence.yml: python-version: "3.12.3"
.github/workflows/migration_check.yml: Set up Python 3.12.3
```

## Verdict

The central Phase 4 implementation is supported and the remaining workflow selectors/labels have been reconciled.
