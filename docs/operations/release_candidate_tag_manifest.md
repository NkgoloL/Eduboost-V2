# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-08-29T09:39:05.410977+00:00`
- branch: `feature/coverage-target-90`
- commit: `d81bc05b230256f6c4ab39540ccb03ed4b52bcfd`
- release_candidate: `beta-d81bc05b2`

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
git tag -a beta-d81bc05b2 -m "Beta release candidate beta-d81bc05b2"
git push origin beta-d81bc05b2
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
