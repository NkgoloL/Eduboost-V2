# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-08-26T17:00:23.195419+00:00`
- branch: `codex/tsr-b04-architecture-and-data-integrity`
- commit: `107d58c62d28a0d0a7a094f69894809af40f8db0`
- release_candidate: `beta-107d58c62`

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
git tag -a beta-107d58c62 -m "Beta release candidate beta-107d58c62"
git push origin beta-107d58c62
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
