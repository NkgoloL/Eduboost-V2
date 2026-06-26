# Project Assistance Status

This report implements the five ways Codex assists this project. It is a
working control surface, not a release approval.

## Current Gate Snapshot

- **Last refreshed:** 2026-06-10 12:17 UTC
- **Assessed commit:** `958c86ff8465`
- **Quality gate:** 🔴 RED (6/11 required checks passing)

## Source Coverage

| Source | Status |
| --- | --- |
| `.github/PULL_REQUEST_TEMPLATE.md` | present |
| `.github/workflows/` | present |
| `Makefile` | present |
| `TODO.md` | missing |
| `app/` | present |
| `docs/POPIA_COMPLIANCE.md` | present |
| `docs/current_state.md` | present |
| `docs/operations/` | present |
| `docs/operations/recommended_operating_model.md` | present |
| `docs/project_status.md` | present |
| `docs/release/` | present |
| `docs/release/EVIDENCE_INDEX.md` | present |
| `docs/security/` | present |
| `pytest.ini` | present |

## Assistance Lanes

| # | Lane | Primary output | First command |
| --- | --- | --- | --- |
| 1 | Current-state triage | Updated project status and current-state evidence. | `make refresh-current-state` |
| 2 | Verification and repair | Passing local checks or a concrete failure record with owner and next action. | `pytest -c pytest.ini tests/unit -q --no-cov` |
| 3 | Release evidence and governance | Release evidence files that link to real, readable artifacts. | `make recommended-operating-model-check` |
| 4 | Architecture, security, and compliance hardening | Boundary fixes, security evidence, or explicit scoped exceptions. | `make architecture-gates` |
| 5 | Staging, beta, and operational readiness | Staging and beta readiness records with commands, outputs, owners, and dates. | `make staging-smoke-check` |

## 1. Current-state triage

Keep the project honest about what is implemented, verified, blocked, or external.

Sources:
- `docs/current_state.md` (present)
- `docs/project_status.md` (present)
- `TODO.md` (missing)

Commands:
- `make refresh-current-state`
- `make project-assistance-status`

Done when: Open blockers are reflected in TODO.md and no release-ready claim exceeds the evidence.

## 2. Verification and repair

Run focused checks, repair failures, and capture the exact command evidence.

Sources:
- `Makefile` (present)
- `pytest.ini` (present)
- `docs/current_state.md` (present)

Commands:
- `pytest -c pytest.ini tests/unit -q --no-cov`
- `make runtime-check`
- `make openapi-check`

Done when: The relevant failing gate is either green or documented as blocked with evidence.

## 3. Release evidence and governance

Maintain release evidence bundles, owner accountability, and claim discipline.

Sources:
- `docs/operations/recommended_operating_model.md` (present)
- `docs/release/EVIDENCE_INDEX.md` (present)
- `.github/PULL_REQUEST_TEMPLATE.md` (present)

Commands:
- `make recommended-operating-model-check`
- `make release-owner-accountability-check`
- `make beta-release-readiness-contract-check`

Done when: Release decisions are backed by current evidence and unsigned external approvals stay external.

## 4. Architecture, security, and compliance hardening

Protect V2 boundaries, authorization, POPIA, and AI/CAPS safety claims.

Sources:
- `app/` (present)
- `docs/security/` (present)
- `docs/POPIA_COMPLIANCE.md` (present)

Commands:
- `make architecture-gates`
- `make privacy-boundary-check`
- `make caps-ai-safety-evidence-check`

Done when: Security, privacy, and architecture claims match passing checks or documented exceptions.

## 5. Staging, beta, and operational readiness

Prepare deployment, smoke, backup, restore, rollback, and beta go/no-go evidence.

Sources:
- `docs/operations/` (present)
- `docs/release/` (present)
- `.github/workflows/` (present)

Commands:
- `make staging-smoke-check`
- `make local-release-evidence-check`
- `make beta-release-evidence-bundle-check`

Done when: A release owner can make an evidence-backed go/no-go decision without guessing.

## Maintenance

Run this after meaningful status, evidence, release, or readiness changes:

```bash
make project-assistance-status
make project-assistance-status-check
```
