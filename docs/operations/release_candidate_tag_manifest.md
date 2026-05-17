# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-05-17T22:12:28.222872+00:00`
- branch: `codex/production_readiness`
- commit: `02f3babd855703460eefc1727f5fdc71f44d2a60`
- release_candidate: `beta-02f3bab`

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
git tag -a beta-02f3bab -m "Beta release candidate beta-02f3bab"
git push origin beta-02f3bab
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
