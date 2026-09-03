# Beta Release Evidence Bundle

## Metadata

- generated_at_utc: `2026-08-29T09:34:15.159820+00:00`
- branch: `feature/coverage-target-90`
- commit: `d81bc05b230256f6c4ab39540ccb03ed4b52bcfd`
- release_candidate: `unset`

## Evidence Artifacts

| Category | Artifact | Present |
| --- | --- | --- |
| backend runtime/API | `docs/openapi.json` | `yes` |
| release evidence manifest | `docs/operations/release_evidence_manifest.md` | `yes` |
| staging release gate | `docs/operations/staging_release_gate.md` | `yes` |
| deployment readiness | `docs/operations/deployment_readiness_checklist.md` | `yes` |
| project evidence index | `docs/operations/project_evidence_index.md` | `yes` |
| beta readiness contract | `docs/operations/beta_release_readiness_contract.md` | `yes` |
| staging smoke manifest | `docs/operations/staging_smoke_evidence_manifest.md` | `yes` |
| beta sign-off manifest | `docs/operations/beta_signoff_manifest.md` | `yes` |
| rollback runbook | `docs/operations/beta_rollback_runbook.md` | `yes` |
| post-deploy smoke checklist | `docs/operations/post_deploy_staging_smoke_checklist.md` | `yes` |
| Cluster C POPIA consent closure | `docs/security/POPIA_CONSENT_GATE_CLOSURE.md` | `yes` |
| Cluster D closure | `docs/operations/CLUSTER_D_CLOSURE.md` | `yes` |
| Cluster E closure | `docs/operations/CLUSTER_E_CLOSURE.md` | `yes` |
| Cluster F closure | `docs/ai/CLUSTER_F_CLOSURE.md` | `yes` |
| Cluster G closure | `docs/frontend/CLUSTER_G_CLOSURE.md` | `yes` |

## Bundle Boundary

The beta release evidence bundle indexes release artifacts. It does not replace execution logs, approvals, or deployment platform records.

## Command

```bash
make beta-release-evidence-bundle
```
