# 18. Beta launch, staging acceptance, and product scope

## 18.1 Staging acceptance

- [x] `P0` Deploy staging environment. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [ ] `P0` Use synthetic data only in staging.
- [x] `P0` Run backend smoke tests against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Run frontend Playwright tests against staging. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Run POPIA workflows against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Run backup/restore drill against staging. Evidence: `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Run security scan against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [ ] `P0` Run load smoke test against staging.
- [x] `P0` Verify dashboards in staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Verify alerts in staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Verify incident runbook against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Produce staging acceptance report. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Add staging acceptance report to release evidence bundle. Evidence: `docs/operations/release_candidate_evidence_sweep_2026-05-11.md`.

## 18.2 Public beta scope

- [ ] `P0` Define supported grades.
- [ ] `P0` Define supported subjects.
- [ ] `P0` Define supported languages.
- [ ] `P0` Define supported lesson types.
- [ ] `P0` Define supported diagnostic flows.
- [ ] `P0` Define supported payment modes.
- [ ] `P0` Define unsupported features.
- [ ] `P0` Define pilot user count.
- [ ] `P0` Define parent consent onboarding script.
- [ ] `P0` Define support escalation path.
- [ ] `P0` Define feedback collection process.
- [ ] `P0` Define AI-content issue-reporting flow.
- [ ] `P0` Define manual content review SLA.
- [ ] `P0` Define go/no-go criteria.
- [ ] `P0` Hold go/no-go review.
- [ ] `P0` Record go/no-go decision.

## 18.3 Release and rollback

- [ ] `P0` Generate release evidence bundle.
- [ ] `P0` Create signed release tag.
- [ ] `P0` Deploy release candidate to staging.
- [ ] `P0` Run smoke tests.
- [ ] `P0` Test rollback.
- [ ] `P0` Document rollback result.
- [ ] `P0` Approve production promotion only if all release blockers pass.
- [ ] `P1` Add post-release monitoring checklist.
- [ ] `P1` Add first-24-hours monitoring schedule.

---

