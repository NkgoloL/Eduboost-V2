# TA Phase 10 — Branch Protection Evidence and Merge-Readiness Closure

## Status

`ready_for_controlled_execution`

Phase 09 recorded a real hosted GitHub Actions success for the exact branch SHA.
Merge readiness remains blocked until branch-protection evidence is captured for
the target branch.

## Objective

Close the hosted-CI merge-readiness control without overstating release
readiness. This phase captures GitHub branch-protection evidence from either:

- classic branch protection for the target branch, or
- active repository branch rulesets that apply to the target branch.

## Authority commands

```bash
python3 scripts/technical_audit/capture_branch_protection_evidence.py \
  --repo NkgoloL/Eduboost-V2 \
  --target-branch master \
  --require-branch-protection

python3 scripts/technical_audit/verify_merge_readiness_authority.py --json
```

## Closure rule

This phase may close only when:

1. the existing hosted-CI authority record has `hosted_ci_run_claimed: true`;
2. the hosted CI run is `completed` with `conclusion: success`;
3. branch protection is captured from GitHub API evidence;
4. `merge_readiness_authorised` is true; and
5. release readiness remains explicitly unclaimed.

## Out of scope

- Production release approval.
- Full backend-backed E2E readiness beyond already recorded authority evidence.
- Runtime knowledge-graph implementation.
- Retrospective use of the stale `hosted-ci-merge-readiness` diagnostics folder.
