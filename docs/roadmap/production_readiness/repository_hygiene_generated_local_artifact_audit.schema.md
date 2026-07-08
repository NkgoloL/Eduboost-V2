# Repository hygiene generated/local artifact audit schema

Canonical inventory path:

`docs/roadmap/production_readiness/repository_hygiene_generated_local_artifact_audit.json`

## Required top-level fields

| Field | Type | Meaning |
|---|---:|---|
| `schema_version` | string | Must be `prd-repository-hygiene-generated-local-artifact-audit/v1`. |
| `prd_id` | string | Must be `PRD-0.9`. |
| `captured_at` | string/null | UTC capture timestamp when evidence is captured. |
| `repository_hygiene_policy_document` | string | Path to the policy document. |
| `repository_hygiene_policy_document_refreshed` | boolean | Whether the policy document records PRD-0.9 authority. |
| `generated_local_artifact_candidates` | array | Configured generated/local artifact candidates and current presence. |
| `suspicious_top_level_entries` | array | Top-level repository hygiene debt candidates. |
| `summary` | object | Count summary for verification and later remediation. |
| `authority_boundaries` | object | Production-release/beta/billing/PRD-1 boundaries. |
| `cleanup_policy` | object | Deletion/rewrite/cleanup authority boundaries. |

## Closure rule

The PRD-0.9 verifier must report `valid: true` only after the inventory is captured and the production-readiness register records `last_recorded_item: PRD-0.9` and `next_authorised_item: PRD-0.10`.
