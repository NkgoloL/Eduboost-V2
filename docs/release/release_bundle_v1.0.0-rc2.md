# Release Bundle v1.0.0-rc2

Status: pending evidence completion
Commit under review: ec48d99ff48d4ad08572fa300cd0d50b25fbc0ec

## Current Evidence

| Area | Evidence | Status |
|---|---|---|
| Local unit suite | `docs/release/unit_test_evidence.md` | Present, green with one accepted warning |
| CI authority | `docs/release/ci_evidence.md` | Pending remote CI verification |
| Branch protection | `docs/release/branch_protection_evidence.md` | External evidence required |
| Migration runtime | `docs/release/migration_evidence.md` | Pending runtime execution |
| Staging smoke | `docs/release/staging_smoke_evidence.md` | Pending runtime execution |
| Restore drill | `docs/release/restore_drill_evidence.md` | Pending runtime execution |
| Rollback drill | `docs/release/rollback_drill_evidence.md` | Pending runtime execution |
| Sign-off manifest | `docs/release/sign_off_manifest.md` | Pending external approval |
| Go/no-go | `docs/release/final_go_no_go_evidence.md` | Not ready for signoff |

## Bundle Rule

Only link files that exist. Pending evidence must stay visibly pending until replaced by real command output, CI URLs, staging logs, or signed approvals.