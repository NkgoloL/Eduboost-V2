# OpenAPI Generated Artifact Canonicalisation Schema

The generated inventory file is:

```text
docs/roadmap/production_readiness/generated_artifact_canonicalisation_inventory.json
```

Required fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Must be `prd-openapi-generated-artifact-canonicalisation/v1`. |
| `prd_id` | Must be `PRD-0.7`. |
| `canonical_openapi_path` | Must be `docs/openapi.json`. |
| `root_openapi_json_path` | Must be `openapi.json`. |
| `root_openapi_yaml_path` | Must be `openapi.yaml`. |
| `canonical_openapi_sha256` | SHA-256 of `docs/openapi.json`. |
| `root_openapi_json_sha256` | SHA-256 of `openapi.json`. |
| `root_json_matches_canonical` | True when root JSON mirror equals canonical JSON byte-for-byte. |
| `root_yaml_schema_matches_canonical` | True when root YAML mirror parses to the same schema as canonical JSON. |
| `openapi_path_count` | Count of OpenAPI paths. |
| `openapi_operation_count` | Count of HTTP operations under paths. |
| `generated_artifacts` | Inventory of known generated artifacts. |
| `historical_openapi_snapshots` | Non-canonical retained OpenAPI snapshots. |
| `authority_boundaries` | Production-readiness boundary flags. |
```
