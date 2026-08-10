# Release Candidate Tag Manifest

## Metadata

- generated_at_utc: `2026-08-03T14:20:15.807577+00:00`
- branch: `fix/tsr-b01-gate-remediation`
- commit: `a55336c4112d0b994acb6a75e1db57e20e4fe381`
- release_candidate: `beta-a55336c411`

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
git tag -a beta-a55336c411 -m "Beta release candidate beta-a55336c411"
git push origin beta-a55336c411
```

## Safety Boundary

Do not create or push the release tag until Cluster H checks pass and required
manual sign-offs are complete.

## Command

```bash
make release-candidate-tag-manifest
```
