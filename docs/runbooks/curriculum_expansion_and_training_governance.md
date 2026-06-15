# Curriculum Expansion and Training Dataset Governance Runbook

## Scope

Operational response for Phase 7 coverage snapshots, gap plans, training manifests, exports, and training-readiness checks.

## Coverage registry failure

1. Run `PYTHONPATH=. .venv/bin/python scripts/check_phase7_registry.py --json`.
2. Confirm `data/content_factory/scopes.json` and `coverage_targets.json` are tracked.
3. Do not generate or publish content while registry integrity is unknown.
4. Restore the approved registry commit and rerun Phase 1–7 gates.

## Unexpected coverage gap

1. Inspect the latest durable snapshot.
2. Confirm the scope, language, CAPS reference, layer, and target.
3. Verify artifact lifecycle state and publication status.
4. Create a dry-run expansion plan.
5. Route any generation through Phase 1, Phase 6 budgets, and Phase 3 review.
6. Never edit counts manually.

## Ineligible artifact in a manifest

1. Reject or revoke the manifest.
2. Block training and adapter deployment.
3. Preserve the manifest, entries, export, and hashes for investigation.
4. Identify the failed eligibility control.
5. Remove the derived export from active storage.
6. Rebuild from a corrected policy and rerun PostgreSQL verification.

## Personal data found in an export

1. Treat as a privacy incident.
2. Stop training and distribution immediately.
3. Restrict access and record the dataset hash and storage locations.
4. Notify the Information Officer and security lead.
5. Delete derived copies only after evidence preservation is approved.
6. Correct the source-selection and scanning control.
7. Re-audit before creating another manifest.

## Dataset hash mismatch

1. Do not train.
2. Compare manifest entries, artifact hashes, and source snapshot hashes.
3. Confirm no artifact changed after manifest creation.
4. Rebuild from the approved manifest only after the cause is understood.
5. Record the incident and invalidate the affected manifest.

## Language-quality failure

1. Remove the language from claimed release coverage.
2. Assign a qualified reviewer.
3. Correct and re-review affected artifacts through Phase 3.
4. Create a new manifest version; never mutate the approved manifest.
