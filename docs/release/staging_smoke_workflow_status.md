# Staging Smoke Workflow Status

Generated at: `2026-08-26T17:00:37Z`
Commit: `107d58c62d28a0d0a7a094f69894809af40f8db0`

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

