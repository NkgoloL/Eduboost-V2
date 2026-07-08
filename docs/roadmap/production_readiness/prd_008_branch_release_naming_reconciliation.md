# PRD-0.8 — Branch/release naming reconciliation

**Status:** Authority pending evidence capture  
**Stream:** PRD-PRODUCTION-READINESS  
**Depends on:** PRD-0.7 OpenAPI and generated artifact canonicalisation

## Objective

Reconcile the repository's branch and release naming language after the PRD-0 canonicalisation slices.

The current protected trunk is `master`. Historical `main` references may remain in archived docs, compatibility workflow triggers, or older release evidence. This slice records the policy and inventory needed to prevent those references from being mistaken for production-release authority.

## In scope

- Record `master` as the current canonical protected trunk.
- Replace the canonical branching policy document with PRD-0.8 language.
- Inventory branch names, release patterns, release-event workflows, and deployment-related workflow references.
- Preserve `release/**` as a reserved naming pattern without granting release authority.
- Preserve PRD branch naming conventions for authority and evidence work.
- Defer repository/generated-local artifact hygiene to PRD-0.9.

## Out of scope

- No production release.
- No release tag creation.
- No deployment authority.
- No public beta/live learner traffic authority.
- No billing/live payment authority.
- No broad workflow rewrite beyond the canonical branching-policy document.
- No repository default-branch rename.

## Closure evidence

PRD-0.8 closes only when:

- PRD-0.7 verifier remains valid.
- The branching policy document records `master` as canonical trunk.
- The branch/release naming inventory is captured.
- The production-readiness register advances to PRD-0.9.
- All release/deployment/beta/billing boundaries remain false.
