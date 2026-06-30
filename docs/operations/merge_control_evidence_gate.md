# Merge-Control Evidence Gate

## Purpose

The merge-control evidence gate records the evidence conditions that must remain true before the controlled staging/beta release evidence PR is merged.

## Required Gate Inputs

- final reviewer pack checklist is present
- final release evidence table of contents is present
- PR-ready final closure certificate is present
- final merge signoff lock is present
- release owner post-closeout decision record is present
- final evidence no-op execution assertion is present
- archival lock assertion is present
- release handoff freeze assertion is present
- final acceptance packet index is present
- final release evidence ledger is present

## Merge Blocking Conditions

- Cluster H release readiness check is failing
- release candidate or commit SHA is inconsistent
- final evidence no-op execution assertion is missing
- unresolved blocker variance is present
- manual approval workflow reference is missing
- branch sync and rebase checklist is incomplete
- generated artifact conflict is unresolved
- PR-ready final closure certificate is missing
- archival lock assertion is missing
- post-closeout evidence access policy is missing

## Gate Rules

- merge-control gate must reference release candidate and commit SHA
- merge-control gate must preserve non-force-push branch discipline
- merge-control gate must preserve no-op execution boundary
- merge-control gate must preserve controlled staging/beta scope
- merge-control gate must not authorize unrestricted production launch

## Boundary

This merge-control evidence gate records merge-gating evidence only. It does not approve production launch, execute deployment, create release tags, or merge the pull request automatically.

## Command

```bash
make merge-control-evidence-gate-check
```

## Readiness Rollup Freeze Merge Summary Evidence

- `docs/operations/final_release_readiness_rollup.md`
- `docs/operations/evidence_freeze_confirmation_record.md`
- `docs/operations/pr_merge_evidence_summary.md`
