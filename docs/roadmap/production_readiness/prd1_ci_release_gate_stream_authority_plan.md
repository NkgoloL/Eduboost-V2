# PRD-1.0 CI/Release-Gate Stream Authority Plan

## Goal

Establish PRD-1 as the active controlled workstream after PRD-0.10, without performing CI or release-gate implementation.

## Steps

1. Apply PRD-1.0 authority files from clean `master` after PRD-0.10 closure.
2. Run `py_compile`, focused PRD-1.0 tests, and the authority verifier.
3. Commit and merge the authority branch.
4. From merged `master`, capture PRD-1.0 evidence.
5. Run the final PRD-1.0 verifier.
6. Commit and merge the evidence branch.
7. Treat PRD-1.1 — CI Inventory Authority as the next authorised slice.

## Non-goals

- No CI workflow canonicalisation.
- No required-check enforcement.
- No branch protection change.
- No release gate enforcement.
- No release tag or deployment.
- No public beta, live learner traffic, billing, or live payment processing.
- No PRD-2 runtime KG implementation.

## Expected terminal register state

```json
{
  "last_recorded_item": "PRD-1.0",
  "next_authorised_item": "PRD-1.1"
}
```
