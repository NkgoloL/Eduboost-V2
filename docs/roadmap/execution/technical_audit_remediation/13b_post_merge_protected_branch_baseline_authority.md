# TA Phase 13B — Post-Merge Protected-Branch Baseline Authority

## Purpose

Phase 13B records the first protected-branch baseline after the Phase 13A
true-state authority repair has landed on `master`.

This is a baseline authority slice only. It verifies that the technical-audit
remediation stream remains closed on the protected branch and that the repaired
hosted-CI provenance model is still valid.

## Preconditions

- Phase 13A has been merged into `master` through branch protection.
- This Phase 13B harness has also landed through a protected-branch PR.
- The local checkout is on `master` and matches `origin/master`.
- `Verify repository authority` is successful on the current `master` HEAD.
- The tracked worktree is clean before capture.

## Captured Evidence

The capture script records:

- git branch, HEAD, remote target SHA, and clean-tree state;
- hosted CI authority verification;
- merge-readiness verification;
- technical-audit release-readiness verification;
- technical-audit closure verification;
- GitHub branch state;
- GitHub branch protection state;
- GitHub check runs for the post-merge baseline commit;
- immutable SHA256SUMS for the evidence bundle.

## Boundary

This slice does not authorise:

- production release;
- deployment;
- release tagging;
- live learner traffic;
- runtime knowledge-graph implementation;
- full backend-backed E2E readiness.

Those remain separate future gates.
