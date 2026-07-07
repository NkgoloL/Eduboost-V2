# PRD-0.5 Test Failure Collection Stabilisation Register Schema

The generated `test_failure_collection_stabilisation_register.json` uses schema version:

```text
prd-test-failure-collection-stabilisation/v1
```

Required top-level sections:

- `upstream_baseline`
- `test_inventory`
- `pytest_configuration`
- `workflow_test_command_inventory`
- `collection_command_matrix`
- `failure_classification_schema`
- `triage_register`
- `stabilisation_boundaries`
- `authority_boundaries`

Required boundaries:

- `no_test_deletions_authorised: true`
- `no_silent_xfail_authorised: true`
- `no_product_behavior_repairs_authorised: true`
- `workflow_command_hygiene_deferred_to_prd006: true`
- `openapi_generated_artifact_canonicalisation_deferred_to_prd007: true`
