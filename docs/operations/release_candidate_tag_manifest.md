# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-13T22:04:10.180778+00:00`
- branch: `codex/production_readiness`
- commit: `ab75ab181e3328954bf1c0544237166ab5bcc8fb`
- release_candidate: `beta-ab75ab1`

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
git tag -a beta-ab75ab1 -m "Beta release candidate beta-ab75ab1"
git push origin beta-ab75ab1
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
