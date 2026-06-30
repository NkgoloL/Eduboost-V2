# EduBoost V2 Remaining External Evidence Checklist

## P0: Evidence refresh after final push

- [ ] Pull latest codex/production_readiness branch.
- [ ] Confirm clean working tree.
- [ ] Run full local test suite.
- [ ] Capture full test output to docs/release/full_pytest_latest_green.txt.
- [ ] Generate final backend runtime enablement report.
- [ ] Generate final backend runtime integration readiness report.
- [ ] Commit refreshed evidence artifacts.

## P1: Remote CI evidence

- [ ] Push final branch.
- [ ] Confirm GitHub Actions run URL.
- [ ] Archive workflow run URL in docs/release/ci_evidence.md.
- [ ] Confirm backend consolidation and runtime integration targets pass remotely.
- [ ] Record skipped tests and warnings.

## P2: Disposable DB schema proof

- [ ] Provision disposable PostgreSQL database.
- [ ] Export DATABASE_URL pointing to the disposable/test DB only.
- [ ] Run make disposable-db-schema-proof-execute.
- [ ] Run make disposable-db-schema-proof-execution-check.
- [ ] Run make schema-drift-check-db.
- [ ] Archive generated reports.

## P3: Staging smoke

- [ ] Deploy current branch to staging.
- [ ] Export STAGING_BASE_URL to real staging host.
- [ ] Run make staging-smoke.
- [ ] Run make staging-smoke-check.
- [ ] Archive staging smoke JSON and text output.

## P4: Operational drills

- [ ] Backup drill completed.
- [ ] Restore drill completed.
- [ ] Rollback drill completed.
- [ ] Monitoring dashboards verified.
- [ ] Incident-response owner confirmed.

## P5: Human approvals

- [ ] Security review complete.
- [ ] POPIA/privacy review complete.
- [ ] Legal review complete.
- [ ] CAPS/content review complete.
- [ ] Release-owner go/no-go memo signed.
