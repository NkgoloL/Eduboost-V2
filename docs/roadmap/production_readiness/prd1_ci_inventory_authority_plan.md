# PRD-1.1 CI Inventory Authority Plan

## Goal

Capture an authoritative inventory of CI, workflow, release, branch-name, pytest-command, OpenAPI, Makefile, and branch-protection references before any PRD-1 canonicalisation or required-check enforcement.

## Steps

1. Apply PRD-1.1 authority files from clean `master` after PRD-1.0 closure.
2. Run `py_compile`, focused PRD-1.1 tests, and the authority verifier.
3. Commit and merge the authority branch.
4. From merged `master`, capture PRD-1.1 inventory evidence.
5. Run the final PRD-1.1 verifier.
6. Commit and merge the evidence branch.
7. Treat PRD-1.2 — Required Check Classification as the next authorised slice.

## Non-goals

- No workflow command canonicalisation.
- No required-check classification or enforcement.
- No branch protection modification.
- No release gate enforcement.
- No OpenAPI artifact reconciliation.
- No release tag or deployment.
- No public beta, live learner traffic, billing, or live payment processing.
- No PRD-2 runtime KG implementation.

## Expected terminal register state

```json
{
  "last_recorded_item": "PRD-1.1",
  "next_authorised_item": "PRD-1.2"
}
```
