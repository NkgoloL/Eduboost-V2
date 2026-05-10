# Final Release Verification Bundle

## Purpose

The final release verification bundle provides one command target that executes
the final CI-safe release-readiness checks for the staging/beta layer.

## Included Commands

```bash
make generated-artifact-hygiene-check
make branch-sync-rebase-checklist-check
make beta-release-final-checklist-check
make project-release-closure-index-check
make beta-release-execution-plan-check
make beta-pr-body-check
make cluster-h-release-readiness-check
make cluster-h-closure-check
```

## Boundary

This bundle is intentionally CI-safe and evidence-focused. Runtime deployment,
manual approval, release tagging, and post-deploy browser execution remain
operator-controlled actions.

## Command

```bash
make final-release-verification
```
