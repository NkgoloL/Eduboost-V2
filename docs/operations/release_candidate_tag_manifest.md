# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-16T17:02:22.786041+00:00`
- branch: `codex/production_readiness`
- commit: `c7a02d63c7ae117a8e1b9a25f94853e37c6ed2a0`
- release_candidate: `beta-c7a02d6`

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
git tag -a beta-c7a02d6 -m "Beta release candidate beta-c7a02d6"
git push origin beta-c7a02d6
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
