# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-06-12T17:40:51.520994+00:00`
- branch: `phase-11/technical-debt-burn-down`
- commit: `a70b57616bb29572fcb57961b91a3f68f0c66329`
- release_candidate: `beta-a70b5761`

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
git tag -a beta-a70b5761 -m "Beta release candidate beta-a70b5761"
git push origin beta-a70b5761
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
