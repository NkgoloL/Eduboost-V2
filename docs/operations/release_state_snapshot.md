# Release State Snapshot

## Metadata

- generated_at_utc: `2026-05-14T21:16:33.577580+00:00`
- branch: `codex/production_readiness`
- commit: `c9b255d6a61c7854da9ebea6d632b36b25d5995c`
- release_candidate: `unset`

## Working Tree Status

```text
M alembic/versions/20260510_0300_popia_consent_audit_dsr.py
 M app/api_v2_routers/auth.py
 M app/core/audit.py
 M app/core/config.py
 M app/core/password_policy.py
 M app/core/token_revocation.py
 M app/modules/consent/service.py
 M app/repositories/repositories.py
 M docker-compose.yml
 M docs/ai/ai_prompt_surface_inventory.md
 M docs/frontend/frontend_route_inventory.md
 M docs/operations/beta_release_evidence_bundle.md
 M docs/operations/beta_release_pr_body.md
 M docs/operations/beta_signoff_manifest.md
 M docs/operations/database_backup_manifest.md
 M docs/operations/database_restore_evidence.md
 M docs/operations/release_candidate_tag_manifest.md
 M docs/operations/release_evidence_manifest.md
 M docs/operations/release_state_snapshot.md
 M docs/operations/staging_smoke_evidence_manifest.md
 M tests/conftest.py
 M tests/integration/conftest.py
 M tests/integration/test_auth_refresh.py
 M tests/integration/test_consent_grant_authorization.py
 M tests/integration/test_consent_revoke_authorization.py
 M tests/integration/test_consent_status_authorization.py
 M tests/integration/test_diagnostic_items_authorization.py
 M tests/integration/test_diagnostic_submit_authorization.py
 M tests/integration/test_gamification_award_xp_authorization.py
 M tests/integration/test_gamification_profile_authorization.py
 M tests/integration/test_learner_mastery_authorization.py
 M tests/integration/test_learner_read_authorization.py
 M tests/integration/test_lesson_sync.py
 M tests/integration/test_parent_erasure_authorization.py
 M tests/integration/test_parent_export_authorization.py
 M tests/integration/test_parent_progress_authorization.py
 M tests/integration/test_parent_trust_dashboard.py
 M tests/integration/test_rate_limits.py
 M tests/test_popia_negative.py
 M tests/unit/test_refresh_token_rotation.py
?? docs/release/full_pytest_errors_latest.txt
?? docs/release/integration_auth_refresh_trace.txt
?? docs/release/pytest_collect_all.txt
?? fix_consent_mock.py
?? fix_future_import.py
```

## State Artifacts

| Artifact | Present |
| --- | --- |
| `docs/operations/beta_release_readiness_contract.md` | `yes` |
| `docs/operations/beta_release_evidence_bundle.md` | `yes` |
| `docs/operations/beta_release_final_checklist.md` | `yes` |
| `docs/operations/beta_release_execution_plan.md` | `yes` |
| `docs/operations/beta_release_pr_body.md` | `yes` |
| `docs/operations/final_release_verification_bundle.md` | `yes` |
| `docs/operations/project_release_closure_index.md` | `yes` |
| `docs/operations/CLUSTER_H_CLOSURE.md` | `yes` |
| `PR_INTEGRATION_SUMMARY.md` | `yes` |
| `docs/project_status.md` | `yes` |

## Snapshot Boundary

This release state snapshot records local repository state at generation time.
It does not replace CI logs, platform approvals, or release tag history.

## Command

```bash
make release-state-snapshot
```
