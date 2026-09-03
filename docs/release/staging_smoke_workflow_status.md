# Staging Smoke Workflow Status

Generated at: `2026-08-29T09:39:18Z`
Commit: `d81bc05b230256f6c4ab39540ccb03ed4b52bcfd`

**Status:** `staging-smoke-workflow-not-configured`

| Check | Passed |
|---|---:|
| Workflow exists | False |
| Probe exists | True |
| workflow_dispatch | False |
| STAGING_SMOKE_BASE_URL secret reference | False |
| Probe step | False |
| Artifact upload | False |

## Blockers

- workflow file missing
- workflow_dispatch missing
- STAGING_SMOKE_BASE_URL secret reference missing
- staging smoke probe step missing
- artifact upload missing

## No false-closure rules

- This proves only workflow configuration.
- STAGING-001 remains external-blocked until a real successful staging smoke run is attached.
- Placeholder staging URLs and placeholder run IDs are not accepted evidence.

