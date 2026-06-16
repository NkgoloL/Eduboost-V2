# Phase 0 Execution Plan — Environment and Reproducibility

**Document version:** 1.0
**Status:** Draft — approval required before execution
**Canonical path:** `docs/roadmap/execution/atlas/phase_00_execution_plan.md`

`PHASE_00_START_APPROVED=false`

## Objective

Create a clean-checkout, deterministic and CI-authoritative environment baseline before downstream phase closure is reaccepted.

## Mandatory outcomes

- Pin and record the supported Python 3 minor/patch version and Node/pnpm versions.
- Make required Content Factory registries available from a clean checkout or deterministic bootstrap.
- Prove `.venv`, dependency lockfiles, Docker, PostgreSQL/pgvector, Redis and frontend tooling setup.
- Repair and run environment, lint, OpenAPI, migration, schema and test preflights.
- Capture clean-checkout evidence and a passing independent Phase 0 audit.
- Revalidate Phases 1–7 against the verified environment.

## Start gate

- [ ] Owner and approver assigned.
- [ ] Toolchain versions approved.
- [ ] Execution plan approved and committed.
- [ ] Evidence custodian and independent auditor assigned.

## Closure gate

- [ ] Clean checkout bootstrap succeeds.
- [ ] Required runtime registries are reproducible.
- [ ] Backend/frontend environment checks pass.
- [ ] Migration and schema checks pass.
- [ ] Implementation report, evidence index and passing audit exist under Atlas.
- [ ] Post-merge CI passes on the merge commit.
