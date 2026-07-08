# OpenAPI and Generated Artifact Canonicalisation Plan

## Purpose

This plan defines the PRD-0.7 control for generated artifact source-of-truth alignment.

## Source-of-truth decisions

1. `docs/openapi.json` remains the canonical OpenAPI contract.
2. `openapi.json` is a generated root mirror of `docs/openapi.json`.
3. `openapi.yaml` is a generated root YAML mirror of `docs/openapi.json`.
4. Historical `docs/openapi_pr*.json` files remain retained snapshots, not live contracts.
5. Documentation generated artifacts remain inventoried and are not deleted in this slice.

## Commands

Authority check:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd007_openapi_generated_artifact_canonicalisation.py --authority-only --json
```

Canonicalisation:

```bash
PYTHONPATH=. python3 scripts/production_readiness/apply_prd007_openapi_generated_artifact_canonicalisation.py --write
```

Evidence capture:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/capture_prd007_openapi_generated_artifact_canonicalisation_evidence.py \
  --claim-prd007-openapi-generated-artifact-canonicalisation \
  --prd-owner "Nkgolo Lebelo" \
  --target-branch master \
  --require-valid \
  --json
```

## Non-goals

- No production release.
- No deployment.
- No public beta/live learner traffic.
- No billing/live payment authority.
- No branch/release naming reconciliation; PRD-0.8 owns that.
- No broad API behavior repair.
