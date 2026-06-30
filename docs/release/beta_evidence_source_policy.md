# Beta Evidence Source Policy

**Status:** active

Beta readiness gates may only pass when their evidence source type is trusted.

## Trusted source types

| Source type | Intended use |
|---|---|
| `github_actions` | Remote GitHub Actions run evidence |
| `github_branch_protection` | Repository branch-protection evidence |
| `educator_review_log` | Real curriculum/item-review evidence |
| `real_staging` | Real deployed staging environment smoke evidence |
| `real_backup_system` | Real backup execution evidence |
| `real_restore_drill` | Real restore drill evidence |
| `real_rollback_drill` | Real rollback drill evidence |
| `real_alertmanager_notification` | Real alerting notification evidence |

## Rejected source types

| Source type | Reason |
|---|---|
| `local_mock` | Does not prove external runtime behavior |
| `placeholder` | Not real evidence |
| `manual_bypass` | Bypasses a release gate |
| `synthetic` | Generated proof substitute |
| `unknown` | Missing provenance |
| empty/null | Missing provenance |

## Rule

A gate cannot contribute to beta readiness unless:

1. `evidence_source_type` is present.
2. `evidence_source_type` is trusted for that gate.
3. the gate status is pass/green/verified/waived only with real provenance.
4. the evidence payload does not contain placeholder/mock/bypass markers.

Synthetic evidence must be preserved for auditability but marked `synthetic_invalid`.
