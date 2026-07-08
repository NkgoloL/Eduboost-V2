# Branch/release naming reconciliation plan

## Canonical decision

- Current protected trunk: `master`.
- `main` is treated as a legacy compatibility alias only.
- `release/**` remains a reserved release branch pattern, not release authority.
- PRD authority/evidence work uses short-lived `codex/prd-*` branches.

## Evidence inventory

The PRD-0.8 capture step records:

- workflow branch trigger inventory;
- workflows mentioning `master`, `main`, and `release/**`;
- release-event workflows;
- deployment-related workflow references;
- canonical branching policy state;
- authority boundary flags.

## Deferred work

Repository hygiene, generated/local artifact cleanup, ignored-file reconciliation, and broader release-folder cleanup are deferred to PRD-0.9.
