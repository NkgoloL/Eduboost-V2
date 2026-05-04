# Project Status

This page summarizes the verified repository state as of **2026-05-04**.

## Verified Today

- The active backend entrypoint is `app/api_v2.py`.
- The root `docker-compose.yml` points at the V2 runtime and is the default
  local stack.
- GitHub Actions workflows live under `.github/workflows/`, including
  `ci-cd.yml` and `release.yml`.
- The repository does **not** currently contain the `mnt/` or `scratch/`
  directories that were called out in an earlier comparative audit.
- The architecture manifest is linked through
  [`docs/architecture/V2_ARCHITECTURE.md`](architecture/V2_ARCHITECTURE.md)
  rather than a transient auto-generated filename.
- Access tokens default to 15 minutes, refresh tokens to 7 days, and sensitive
  audit events are documented as PostgreSQL-backed in the active V2 path.

## Compatibility Boundary

EduBoost is V2-first, but not every historical surface has disappeared:

- [`app/api/main.py`](/app/api/main.py) remains as a compatibility import shim.
- Archived legacy code is kept under [`app/legacy`](/app/legacy/DEPRECATED.md).
- Some migration-era documentation and support files still exist because the
  cutover has been staged rather than rewritten from scratch.

## What This Means for Contributors

- New implementation work should target the V2 runtime.
- Documentation should describe the repo as it exists now, not as a perfect
  future state.
- Security, migration, and operational claims should be phrased in terms of
  what the code and workflows currently prove.

## Audit Tracker

The comparative-audit follow-up list lives in the root
[`TODO.md`](/TODO.md). That file is the live tracker for documentation sync and
repo-hygiene items raised by the report.
