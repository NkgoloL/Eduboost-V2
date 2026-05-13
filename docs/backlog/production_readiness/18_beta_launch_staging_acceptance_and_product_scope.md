# 18. Beta launch, staging acceptance, and product scope

## 18.1 Staging acceptance

- [x] `P0` Deploy staging environment. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [verify] `P0` Use synthetic data only in staging.
- [x] `P0` Run backend smoke tests against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Run frontend Playwright tests against staging. Evidence: `docs/frontend/frontend_verification_evidence_2026-05-11.md`.
- [x] `P0` Run POPIA workflows against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Run backup/restore drill against staging. Evidence: `docs/operations/database_resilience_evidence_2026-05-11.md`.
- [x] `P0` Run security scan against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [verify] `P0` Run load smoke test against staging.
- [x] `P0` Verify dashboards in staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Verify alerts in staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Verify incident runbook against staging. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Produce staging acceptance report. Evidence: `docs/operations/staging_ops_evidence_2026-05-11.md`.
- [x] `P0` Add staging acceptance report to release evidence bundle. Evidence: `docs/operations/release_candidate_evidence_sweep_2026-05-11.md`.

## 18.2 Public beta scope

- [verify] `P0` Define supported grades.
- [verify] `P0` Define supported subjects.
- [verify] `P0` Define supported languages.
- [verify] `P0` Define supported lesson types.
- [verify] `P0` Define supported diagnostic flows.
- [verify] `P0` Define supported payment modes.
- [verify] `P0` Define unsupported features.
- [verify] `P0` Define pilot user count.
- [verify] `P0` Define parent consent onboarding script.
- [verify] `P0` Define support escalation path.
- [verify] `P0` Define feedback collection process.
- [verify] `P0` Define AI-content issue-reporting flow.
- [verify] `P0` Define manual content review SLA.
- [verify] `P0` Define go/no-go criteria.
- [verify] `P0` Hold go/no-go review.
- [verify] `P0` Record go/no-go decision.

## 18.3 Release and rollback

- [verify] `P0` Generate release evidence bundle.
- [verify] `P0` Create signed release tag.
- [verify] `P0` Deploy release candidate to staging.
- [verify] `P0` Run smoke tests.
- [verify] `P0` Test rollback.
- [verify] `P0` Document rollback result.
- [verify] `P0` Approve production promotion only if all release blockers pass.
- [verify] `P1` Add post-release monitoring checklist.
- [verify] `P1` Add first-24-hours monitoring schedule.

---



## 18.6 Repository-side implementation evidence

- [verify] Beta launch decision is documented in `docs/adr/ADR-018-beta-launch-staging-acceptance-product-scope.md`.
- [verify] Beta launch/staging acceptance architecture is documented in `docs/beta_launch/beta_launch_staging_acceptance_architecture_contract.md`.
- [verify] Beta product scope is documented in `docs/beta_launch/beta_product_scope_contract.md`.
- [verify] Staging acceptance criteria are documented in `docs/beta_launch/staging_acceptance_criteria_contract.md`.
- [verify] Beta entry/exit criteria are documented in `docs/beta_launch/beta_entry_exit_criteria_contract.md`.
- [verify] Beta cohort rollout controls are documented in `docs/beta_launch/beta_cohort_rollout_contract.md`.
- [verify] Beta feedback intake is documented in `docs/beta_launch/beta_feedback_intake_contract.md`.
- [verify] Beta known issues register is documented in `docs/beta_launch/beta_known_issues_register.md`.
- [verify] Beta launch readiness review is documented in `docs/beta_launch/beta_launch_readiness_review.md`.
- [verify] Post-beta review expectations are documented in `docs/beta_launch/post_beta_review_contract.md`.
- [verify] Deterministic repository contracts live in `app/modules/beta_launch/production_readiness_contracts.py`.
- [verify] Repository validation is provided by `scripts/check_beta_launch_staging_acceptance_production_readiness.py`.
- [verify] Domain validation wrapper is provided by `scripts/check_domain_18_beta_launch_staging_acceptance_evidence.py`.
- [verify] Unit coverage is provided by `tests/unit/test_beta_launch_staging_acceptance_production_readiness.py`.
- [verify] Make target is `make beta-launch-staging-acceptance-production-readiness-check`.

### Verification boundary

This implementation provides repository-side beta launch, staging acceptance, controlled cohort, product scope, known issues, feedback, support, rollback, and post-beta review readiness evidence. It does not enroll beta participants, deploy staging, approve general availability, or authorize production launch.
