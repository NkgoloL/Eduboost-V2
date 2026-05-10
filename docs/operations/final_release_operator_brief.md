# Final Release Operator Brief

## Purpose

The final release operator brief gives the release owner and reviewer a compact operational interpretation of the sealed controlled staging/beta evidence package.

## Required Brief Inputs

- terminal evidence seal
- final PR handoff summary
- final reviewer disposition record
- final closure manifest
- branch handoff proof record
- final acceptance memo
- release record closure ledger
- PR merge evidence summary
- merge-control evidence gate
- post-closeout evidence access policy

## Brief Fields

| Field | Value |
| --- | --- |
| Brief ID | pending |
| Release Candidate | pending |
| Commit SHA | pending |
| Branch | pending |
| PR Number | pending |
| Operator | pending |
| Brief Time UTC | pending |
| Brief Outcome | pending |
| Evidence Archive Location | pending |

## Brief Rules

- brief must reference release candidate and commit SHA
- brief must reference branch and PR number
- brief must preserve terminal evidence seal references
- brief must preserve final PR handoff summary references
- brief must preserve merge-control evidence gate references
- brief must preserve no-op execution boundary references
- brief must preserve post-closeout evidence access policy references
- brief must remain controlled staging/beta evidence

## Boundary

This final release operator brief records operator-facing evidence interpretation only. It does not approve production launch, execute deployment, create release tags, or merge the pull request automatically.

## Command

```bash
make final-release-operator-brief-check
```
