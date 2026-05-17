# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-17T14:33:30.737721+00:00`
- branch: `fix/github-ci-cd-errors`
- commit: `b5eb28226e73bc462ade0ff52d80b97ecdaf0621`
- release_candidate: `beta-b5eb282`

## Tagging Convention

- beta release candidate tag format: `beta-<short-sha>` or explicit `RELEASE_CANDIDATE`
- release tags must point to reviewed commits
- release tags must be paired with beta release evidence bundle
- release tags must be paired with beta sign-off manifest
- release tags must be paired with rollback owner assignment

## Required Evidence Before Tagging

- `docs/operations/beta_release_evidence_bundle.md`
- `docs/operations/beta_signoff_manifest.md`
- `docs/operations/staging_smoke_evidence_manifest.md`
- `docs/operations/beta_rollback_runbook.md`
- `docs/operations/post_deploy_staging_smoke_checklist.md`

## Example Commands

```bash
git tag -a beta-b5eb282 -m "Beta release candidate beta-b5eb282"
git push origin beta-b5eb282
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
