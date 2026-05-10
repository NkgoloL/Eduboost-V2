# Release Artifact Retention Contract

## Purpose

Cluster H release evidence must remain available after staging or beta approval
so that rollback, audit, and post-deploy verification can be reconstructed.

## Retained Evidence Artifacts

- beta release evidence bundle
- beta sign-off manifest
- staging smoke evidence manifest
- release candidate tag manifest
- release approval workflow run
- Cluster H closure report
- post-deploy staging smoke checklist
- rollback runbook
- deployment readiness checklist
- release evidence manifest
- OpenAPI contract snapshot

## Retention Requirements

- artifacts are committed or attached to CI workflow runs
- workflow logs are retained according to repository policy
- release candidate tag references the reviewed commit
- rollback owner can locate the evidence bundle
- post-deploy owner can locate smoke checklist results
- privacy/POPIA evidence remains available for audit review
- generated coverage output is not treated as release evidence

## Non-Evidence Artifacts

- local `coverage.xml`
- transient test caches
- virtual environments
- local node module directories
- temporary patch directories

## Command

```bash
make release-artifact-retention-contract-check
```
