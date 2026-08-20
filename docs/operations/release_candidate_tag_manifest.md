# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-08-19T19:16:34.918921+00:00`
- branch: `fix/tsr-b01-gate-remediation`
- commit: `d5ae429bdec24b4d0123ea3362323fa3e4f25e4b`
- release_candidate: `beta-d5ae429bde`

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
git tag -a beta-d5ae429bde -m "Beta release candidate beta-d5ae429bde"
git push origin beta-d5ae429bde
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
