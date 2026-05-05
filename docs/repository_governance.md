# Repository Governance

This document defines the management, contribution, and release policies for the EduBoost V2 repository.

## 1. Canonical Repository
The source of truth for all EduBoost V2 development is:
**`NkgoloL/Eduboost-V2`** (on GitHub)

## 2. Branching Policy
- **`main` / `master`**: Production-ready code. Every commit must be tagged and pass all CI checks.
- **`develop`**: Integration branch for the next release.
- **`feature/*`**: Individual feature development. Merged into `develop` via Pull Request.
- **`hotfix/*`**: Urgent production fixes. Merged into `main` and `develop`.

## 3. Pull Request Requirements
All PRs must:
- Pass `pytest` suite.
- Pass linting (`ruff`, `black`).
- Include updated documentation if applicable.
- Receive at least one approval from a designated code owner.
- Link to a relevant issue or task.

## 4. Release Authority
- Releases are tagged by the Technical Lead or designated Release Manager.
- Tag format: `vX.Y.Z[-beta.N]`.
- Every release must satisfy the `docs/release_checklist.md`.

## 5. Security & Secret Rotation
- No secrets (keys, passwords) shall be committed to the repository.
- Use `app/core/secret_rotation.py` for automated rotation where supported.
- Vulnerability reports should be directed to [Security Email] and handled as P0 incidents.

## 6. Archive Policy
- Stale branches (older than 3 months) will be deleted after merging or documented abandonment.
- Repository mirrors are maintained for disaster recovery purposes.
