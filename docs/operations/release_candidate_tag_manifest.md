# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-12T11:15:44.237413+00:00`
- branch: `codex/sync-frontend-lockfile-local`
- commit: `b7ef0eb83946b356402c33b69a8b905c8fbac2bd`
- release_candidate: `beta-b7ef0eb`

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
git tag -a beta-b7ef0eb -m "Beta release candidate beta-b7ef0eb"
git push origin beta-b7ef0eb
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
