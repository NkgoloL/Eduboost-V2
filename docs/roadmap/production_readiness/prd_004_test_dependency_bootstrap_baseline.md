# PRD-0.4 — Test/dependency bootstrap baseline

**Status:** authority defined  
**Stream:** PRD production-readiness  
**Depends on:** PRD-0.3 documentation housekeeping ratchet refresh

## Purpose

PRD-0.4 records the reproducible dependency and test bootstrap baseline before PRD-0 moves into explicit test-failure and CI stabilisation work.

This slice is intentionally a **baseline and contract** slice. It does not attempt to repair every failing test or workflow. It records what a valid local/CI bootstrap must install, what command form tests should converge toward, and which failure classes are deferred to PRD-0.5 and PRD-0.6.

## In scope

- Record backend Python requirement files and dependency aliases.
- Record the canonical development dependency source.
- Confirm `pytest` is declared through the development dependency path.
- Confirm project pytest configuration files exist.
- Record frontend package manager and test dependency sources.
- Record CI/test command bootstrap contract.
- Generate a dependency/test bootstrap baseline artifact during evidence capture.

## Out of scope

- No full test-suite repair.
- No product feature implementation.
- No database migration.
- No production release.
- No deployment.
- No public beta or live learner traffic.
- No billing launch or live payment processing.

## Boundary

Runtime KG authority remains executed from the closed KG roadmap, but PRD-0.4 does not authorise any production-grade runtime exposure.

The following must remain false:

- `production_release_authorised`
- `deployment_authorised`
- `release_tag_authorised`
- `public_beta_authorised`
- `public_beta_live_traffic_authorised`
- `live_learner_traffic_authorised`
- `billing_launch_authorised`
- `live_payment_processing_authorised`
- `new_kg_slice_authorised`
- `prd1_implementation_authorised`

## Handoff

After PRD-0.4 closes, the next authorised slice is PRD-0.5 — Test failure and collection stabilisation register.
