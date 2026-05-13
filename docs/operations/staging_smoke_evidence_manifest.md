# Staging Smoke Evidence Manifest

## Metadata

- generated_at_utc: `2026-05-13T22:04:10.912169+00:00`
- branch: `codex/production_readiness`
- commit: `ab75ab181e3328954bf1c0544237166ab5bcc8fb`
- target_environment: `staging`

## Required Smoke Checks

| Check | Command |
| --- | --- |
| runtime import smoke | `python3 -m py_compile app/api_v2.py` |
| OpenAPI drift smoke | `make openapi-check` |
| staging release gate | `make staging-release-gate-check` |
| release evidence artifacts | `make release-evidence-artifacts-check` |
| Cluster D deployment closure | `make cluster-d-closure-check` |
| Cluster E data resilience closure | `make cluster-e-closure-check` |
| Cluster F AI safety closure | `make cluster-f-closure-check` |
| Cluster G frontend journey closure | `make cluster-g-closure-check` |

## Release Boundary

Staging smoke evidence records required checks. It does not itself prove the
checks were executed unless paired with CI logs or signed release evidence.

## Command

```bash
make staging-smoke-evidence-manifest
```
