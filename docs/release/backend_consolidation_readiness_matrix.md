# Backend Consolidation Readiness Matrix

This matrix controls when backend consolidation may move from diagnostics into implementation.

## Consolidation gates

| Gate | Required evidence | Status |
|---|---|---|
| Audit call-site inventory exists | `docs/release/audit_callsite_inventory.md` | pending review |
| Consent call-site inventory exists | `docs/release/consent_callsite_inventory.md` | pending review |
| Runtime compatibility surfaces exist | `docs/release/backend_runtime_compatibility_report.md` | pending review |
| Health/readiness contract exists | `docs/release/health_readiness_diagnostic_contract.md` | pending review |
| Schema drift contract exists | `docs/release/schema_drift_evidence_contract.md` | pending review |
| Migration evidence captured against disposable DB | `docs/release/migration_latest.md` | pending runtime execution |
| Audit/consent data-retention decision recorded | `docs/release/backend_data_retention_decision_checklist.md` | pending decision |
| Deletion candidate inventory generated | `docs/release/backend_deletion_candidate_inventory.md` | pending review |
| No-op/deletion guard passes | `make backend-consolidation-noop-guard` | pending execution |
| Full test suite green after every step | `docs/release/full_pytest_latest_green.txt` | pending refresh |

## Implementation unlock rule

Backend consolidation implementation may begin only after diagnostics are green, decision records are populated, data-retention decisions are approved, migration evidence is captured, and full local/CI evidence is green.

## Deletion unlock rule

Deletion may occur only after the target is listed in the deletion candidate inventory and has replacement owner, migration plan, data-retention decision, full-suite evidence, and release-owner approval.
