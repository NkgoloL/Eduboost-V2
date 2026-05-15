# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-15T19:50:12.488098+00:00`
- branch: `codex/production_readiness`
- commit: `3722ce2e590e30578a0ffad4cfb5c81bd0555b0b`
- release_candidate: `beta-3722ce2`

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
git tag -a beta-3722ce2 -m "Beta release candidate beta-3722ce2"
git push origin beta-3722ce2
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
