# Final Merge Signoff Lock

## Purpose

The final merge signoff lock records the minimum evidence required before the PR can be treated as merge-ready for the controlled staging/beta release package.

## Required Signoff Inputs

- Cluster H release readiness check is green
- final project closeout attestation is present
- release owner execution guardrail is present
- Cluster H release evidence checksum index is present
- final release handoff package is present
- post-terminal audit readiness assertion is present
- beta release final index is present
- beta governance seal checklist is present
- final PR merge readiness contract is present
- branch sync and rebase checklist is complete

## Merge Signoff Fields

| Field | Value |
| --- | --- |
| Signoff ID | pending |
| Release Candidate | pending |
| Commit SHA | pending |
| Branch | pending |
| Reviewer | pending |
| Signoff Time UTC | pending |
| Merge Outcome | pending |
| Evidence Archive Location | pending |

## Merge Signoff Rules

- merge signoff must reference release candidate and commit SHA
- merge signoff must verify branch accepts non-force push
- merge signoff must verify generated artifacts are not unresolved
- merge signoff must verify Cluster H release readiness check is green
- merge signoff must preserve manual approval workflow references
- merge signoff must remain controlled staging/beta evidence
- merge signoff must not authorize unrestricted production launch

## Boundary

This final merge signoff lock records merge-readiness evidence only. It does not approve production launch, execute deployment, create release tags, or replace manual approval.

## Command

```bash
make final-merge-signoff-lock-check
```
