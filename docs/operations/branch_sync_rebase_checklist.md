# Branch Sync and Rebase Checklist

## Purpose

Release branches must be synchronized with their remote counterparts before
final push or beta approval.

## Required Sync Procedure

```bash
git status --short
git fetch origin
git rebase origin/<current-branch>
git status --short
```

## Conflict Rules

- resolve source, docs, workflow, and test conflicts intentionally
- remove generated `coverage.xml` conflicts with `git rm -f coverage.xml`
- do not carry local caches into the release commit
- do not force-push unless the branch owner has explicitly approved it
- rerun Cluster H readiness checks after rebase

## Required Post-Rebase Checks

```bash
make generated-artifact-hygiene-check
make cluster-h-release-readiness-check
make cluster-h-closure-check
```

## Push Rule

After a clean rebase and passing checks, use:

```bash
git push
```

If rejected again, repeat fetch/rebase rather than defaulting to force-push.

## Command

```bash
make branch-sync-rebase-checklist-check
```
