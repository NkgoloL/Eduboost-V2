---
title: API Reference
status: archived-record
owner: documentation-governance
reviewers: [documentation-governance, evidence-custodian, release-management]
audience: evidence-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/archive, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# API Reference

| Field | Value |
|---|---|
| Document ID | EDB-API-013 |
| Product | EduBoost SA / EduBoost V2 |
| Version | 2.0 aligned baseline |
| Generated | 2026-06-22 |
| Status | Aligned baseline draft |
| Classification | Internal - controlled |
| Replacement note | Replaces stale DBE policy-advisory content previously found in `docs/DOC` |

## Authoritative project baseline

This document is aligned to the EduBoost V2 repository supplied on 2026-06-22. It replaces the prior `docs/DOC` material that described a different DBE policy-advisory system.

| Area | Current baseline |
|---|---|
| Product | EduBoost SA, a CAPS-aligned adaptive learning platform for South African primary learners |
| Active backend | `app/api_v2.py` FastAPI modular monolith, mounted under `/api/v2` and `/v2` |
| Frontend | `app/frontend`, package `eduboost-sa-frontend`, Next.js `16.2.7`, React `18.3.1`, TypeScript `5.4.5` |
| Package manager | pnpm `9.14.4` for frontend |
| Python runtime | Python `3.12.3` |
| Persistence | PostgreSQL via SQLAlchemy/Alembic; 44 Alembic revision files in the supplied archive |
| Queue/cache | Redis and ARQ worker path (`app.modules.jobs.WorkerSettings`); V2 should not introduce Celery/RabbitMQ for new work |
| Launch curriculum scope | `grade4_mathematics_en`: CAPS refs 4.M.1.1, 4.M.1.2, 4.M.1.3 |
| Content targets | 40 approved diagnostic items, 8 approved lessons, 1 assessment blueprint, and 1 study-plan template per launch CAPS ref |
| API surface | 205 route handlers discovered by static router scan, plus health/readiness/metrics root routes |
| Tests | 767 backend test files and approximately 44 frontend test/spec files in the archive |
| Workflows | 44 GitHub Actions workflow files |

### Claim discipline

Unless fresh CI, staging, backup/restore, security, POPIA and release evidence is attached, these documents describe the current implementation and target operating model. They must not be used to claim that the system is production-ready.

## API conventions

- Canonical prefixes: `/api/v2` and `/v2`.
- Operational root routes: `/`, `/health`, `/ready`, `/metrics`, `/docs`, `/redoc`.
- Authentication: bearer/session mechanisms implemented through V2 auth dependencies.
- Admin endpoints require admin dependencies and should be absent from learner/guardian UI flows.

## Route summary

| Area | Route count | Representative paths |
|---|---:|---|
|  | 1 | `/` |
| admin | 103 | `/admin/etl/status`, `/admin/etl/documents`, `/admin/etl/documents/{document_id}` |
| assessments | 2 | `/assessments`, `/assessments/{assessment_id}/attempt` |
| audit | 2 | `/audit`, `/audit/feed` |
| auth | 19 | `/auth/me`, `/auth/register`, `/auth/login` |
| billing | 3 | `/billing/checkout`, `/billing/create-checkout-session`, `/billing/webhook` |
| consent | 3 | `/consent/grant`, `/consent/revoke`, `/consent/status/{learner_id}` |
| content-review | 10 | `/content-review/artifacts/{artifact_id}/assignments`, `/content-review/assignments/{assignment_id}/accept`, `/content-review/assignments/{assignment_id}/reassign` |
| diagnostics | 9 | `/diagnostics/items/{learner_id}`, `/diagnostics/submit`, `/diagnostics/coverage` |
| gamification | 3 | `/gamification/profile/{learner_id}`, `/gamification/award-xp`, `/gamification/leaderboard` |
| health | 1 | `/health` |
| jobs | 1 | `/jobs/{job_id}` |
| learner | 5 | `/learner/content/scopes/{scope_id}/summary`, `/learner/content/scopes/{scope_id}/diagnostic-items`, `/learner/content/scopes/{scope_id}/lessons` |
| learners | 6 | `/learners/`, `/learners/{learner_id}`, `/learners/{learner_id}/mastery` |
| lessons | 6 | `/lessons/generate`, `/lessons/`, `/lessons/generate/stream` |
| onboarding | 3 | `/onboarding/questions`, `/onboarding/submit`, `/onboarding/archetype` |
| parents | 5 | `/parents/dashboard`, `/parents/{guardian_id}/dashboard`, `/parents/{guardian_id}/export` |
| popia | 9 | `/popia/consent/grant`, `/popia/consent/deny`, `/popia/consent/withdraw` |
| practice | 3 | `/practice/sessions`, `/practice/sessions/{session_id}/next-item`, `/practice/sessions/{session_id}/respond` |
| study-plans | 2 | `/study-plans/{learner_id}`, `/study-plans/generate/{learner_id}` |
| system | 4 | `/system/health`, `/system/pillars`, `/system/schema-status` |
| tutor | 5 | `/tutor/sessions`, `/tutor/sessions/{session_id}`, `/tutor/sessions/{session_id}/messages` |

## Route inventory from static scan

| Method | Canonical path under `/api/v2` or `/v2` | Handler | Source |
|---|---|---|---|
| GET | `/admin/etl/status` | `etl_admin_status` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/documents` | `list_etl_documents` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/documents/{document_id}` | `get_etl_document` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/documents/{document_id}/chunks` | `get_etl_document_chunks` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/documents/{document_id}/audit` | `get_etl_document_audit` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/review-queue` | `get_etl_review_queue` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/quality/{document_id}` | `get_etl_quality` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/search` | `search_etl` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/datasets` | `list_etl_datasets` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/etl/metrics` | `get_etl_metrics` | `app/api_v2_routers/admin_etl.py` |
| GET | `/admin/ai-operations/budgets/users/{user_id}` | `get_user_budget` | `app/api_v2_routers/ai_operations.py` |
| GET | `/admin/ai-operations/budgets/tenants/{tenant_id}` | `get_tenant_budget` | `app/api_v2_routers/ai_operations.py` |
| GET | `/admin/ai-operations/usage` | `list_usage` | `app/api_v2_routers/ai_operations.py` |
| GET | `/admin/ai-operations/providers/health` | `provider_health` | `app/api_v2_routers/ai_operations.py` |
| GET | `/admin/ai-operations/reservations` | `list_reservations` | `app/api_v2_routers/ai_operations.py` |
| POST | `/admin/ai-operations/reservations/{operation_id}/cancel` | `cancel_reservation` | `app/api_v2_routers/ai_operations.py` |
| GET | `/health` | `health` | `app/api_v2_routers/api_v2.py` |
| GET | `/` | `root` | `app/api_v2_routers/api_v2.py` |
| GET | `/assessments` | `list_assessments` | `app/api_v2_routers/assessments.py` |
| POST | `/assessments/{assessment_id}/attempt` | `submit_attempt` | `app/api_v2_routers/assessments.py` |
| GET | `/audit` | `get_audit_feed` | `app/api_v2_routers/audit.py` |
| GET | `/audit/feed` | `get_audit_feed_alias` | `app/api_v2_routers/audit.py` |
| GET | `/auth/me` | `me` | `app/api_v2_routers/auth.py` |
| POST | `/auth/register` | `register` | `app/api_v2_routers/auth.py` |
| POST | `/auth/login` | `login` | `app/api_v2_routers/auth.py` |
| POST | `/auth/dev-session` | `create_dev_session` | `app/api_v2_routers/auth.py` |
| POST | `/auth/refresh` | `refresh` | `app/api_v2_routers/auth.py` |
| GET | `/auth/sessions` | `list_sessions` | `app/api_v2_routers/auth.py` |
| POST | `/auth/logout` | `logout` | `app/api_v2_routers/auth.py` |
| POST | `/auth/revoke-all` | `revoke_all_tokens` | `app/api_v2_routers/auth.py` |
| POST | `/auth/forgot-password` | `forgot_password` | `app/api_v2_routers/auth_extended.py` |
| POST | `/auth/reset-password` | `reset_password` | `app/api_v2_routers/auth_extended.py` |
| POST | `/auth/send-verification` | `send_verification` | `app/api_v2_routers/auth_extended.py` |
| GET | `/auth/verify-email` | `verify_email` | `app/api_v2_routers/auth_extended.py` |
| GET | `/auth/onboarding` | `get_onboarding` | `app/api_v2_routers/auth_extended.py` |
| PATCH | `/auth/onboarding/step` | `update_onboarding_step` | `app/api_v2_routers/auth_extended.py` |
| PATCH | `/auth/onboarding/profile` | `update_learner_profile` | `app/api_v2_routers/auth_extended.py` |
| GET | `/auth/privacy` | `get_privacy_settings` | `app/api_v2_routers/auth_extended.py` |
| PATCH | `/auth/privacy` | `update_privacy_settings` | `app/api_v2_routers/auth_extended.py` |
| POST | `/auth/privacy/request-export` | `request_data_export` | `app/api_v2_routers/auth_extended.py` |
| POST | `/auth/privacy/request-deletion` | `request_account_deletion` | `app/api_v2_routers/auth_extended.py` |
| POST | `/billing/checkout` | `create_checkout` | `app/api_v2_routers/billing.py` |
| POST | `/billing/create-checkout-session` | `create_checkout` | `app/api_v2_routers/billing.py` |
| POST | `/billing/webhook` | `stripe_webhook` | `app/api_v2_routers/billing.py` |
| POST | `/consent/grant` | `grant_consent` | `app/api_v2_routers/consent.py` |
| POST | `/consent/revoke` | `revoke_consent` | `app/api_v2_routers/consent.py` |
| GET | `/consent/status/{learner_id}` | `consent_status` | `app/api_v2_routers/consent.py` |
| POST | `/admin/consent/trigger-renewal-reminders` | `trigger_renewal_reminders` | `app/api_v2_routers/consent_renewal.py` |
| GET | `/admin/content-factory/health` | `content_factory_health` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/etl/status` | `etl_status` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes` | `list_content_scopes` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}` | `get_content_scope` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/targets` | `get_content_scope_targets` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/coverage` | `get_content_scope_coverage` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/coverage/{caps_ref}` | `get_content_caps_ref_coverage` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/validate-artifact` | `validate_artifact_payload` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/runs` | `list_generation_runs` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/runs` | `create_generation_run` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/runs/{run_id}` | `get_generation_run` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/runs/{run_id}/tasks` | `get_generation_run_tasks` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/runs/{run_id}/plan-missing` | `plan_missing_generation_tasks` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/runs/{run_id}/execute` | `execute_generation_run` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/tasks/{task_id}/execute` | `execute_generation_task` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/tasks/{task_id}` | `get_generation_task` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/runs/{run_id}/execution-report` | `get_generation_execution_report` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/runs/{run_id}/cancel` | `cancel_generation_run` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/runs/{run_id}/retry-failed` | `retry_failed_generation_tasks` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/artifacts` | `list_artifacts` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/artifacts/{artifact_id}` | `get_artifact` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/artifacts/{artifact_id}/provenance` | `get_artifact_provenance` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/provenance/{artifact_id}` | `get_artifact_provenance` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/artifacts/{artifact_id}/submit-review` | `submit_artifact_for_review` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/artifacts/{artifact_id}/reject` | `reject_artifact` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/artifacts/{artifact_id}/quarantine` | `quarantine_artifact` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/review-queue` | `get_review_queue` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/review-summary` | `get_review_summary` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/artifacts/{artifact_id}/review-bundle` | `get_artifact_review_bundle` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/review-assignments` | `assign_reviewer` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/review-assignments/bulk` | `bulk_assign_reviewer` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/review-assignments` | `list_review_assignments` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/reviewers/{reviewer_id}/workload` | `get_reviewer_workload` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/review/bulk-approve` | `bulk_approve_review` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/review/bulk-reject` | `bulk_reject_review` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/review/bulk-quarantine` | `bulk_quarantine_review` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/staging-verification/all-scopes` | `run_all_scope_staging_verification` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/staging-verification/runs` | `list_staging_verification_runs` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/staging-verification/runs/{run_id}` | `get_staging_verification_run` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/scopes/{scope_id}/staging-verification` | `run_scope_staging_verification` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/staging-readiness` | `get_scope_staging_readiness` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/scopes/{scope_id}/dry-run-seed` | `dry_run_scope_seed` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/scopes/{scope_id}/seed-staging` | `seed_scope_staging` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/seed-runs` | `list_seed_runs` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/seed-runs/{seed_run_id}` | `get_seed_run` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/seed-runs/{seed_run_id}/items` | `get_seed_run_items` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/seed-runs/{seed_run_id}/verify` | `verify_seed_run` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/seed-runs/{seed_run_id}/rollback` | `rollback_seed_run` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/staging-read-verification` | `verify_scope_staging` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/production-gate` | `get_production_gate` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/scopes/{scope_id}/dry-run-promotion` | `dry_run_promotion` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/scopes/{scope_id}/promote-production` | `promote_production` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/promotion-events` | `list_promotion_events` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/promotion-events/{promotion_event_id}` | `get_promotion_event` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/promotion-events/{promotion_event_id}/items` | `get_promotion_event_items` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/promotion-events/{promotion_event_id}/verify` | `verify_promotion_event` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/promotion-events/{promotion_event_id}/rollback` | `rollback_promotion_event` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/scopes/{scope_id}/production-read-verification` | `verify_scope_production` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/reports/{scope_id}` | `get_content_factory_report` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/staging-preview/scopes/{scope_id}` | `get_staging_preview` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/staging-preview/scopes/{scope_id}/caps/{caps_ref}` | `get_staging_preview_by_caps_ref` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/production-preview/scopes/{scope_id}` | `get_production_preview` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/production-preview/scopes/{scope_id}/caps/{caps_ref}` | `get_production_preview_by_caps_ref` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/full-generation/plan` | `plan_full_generation` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/full-generation/start` | `start_full_generation` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/full-generation/runs` | `list_full_generation_runs` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/full-generation/runs/{run_id}` | `get_full_generation_run` | `app/api_v2_routers/content_factory.py` |
| GET | `/admin/content-factory/full-generation/runs/{run_id}/report` | `get_full_generation_run_report` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/full-generation/runs/{run_id}/cancel` | `cancel_full_generation_run` | `app/api_v2_routers/content_factory.py` |
| POST | `/admin/content-factory/full-generation/runs/{run_id}/resume` | `resume_full_generation_run` | `app/api_v2_routers/content_factory.py` |
| POST | `/content-review/artifacts/{artifact_id}/assignments` | `assign_reviewers` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/assignments/{assignment_id}/accept` | `accept_assignment` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/assignments/{assignment_id}/reassign` | `reassign_review` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/artifacts/{artifact_id}/decisions` | `submit_review_decision` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/artifacts/{artifact_id}/quarantine` | `quarantine_artifact` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/artifacts/{artifact_id}/revisions` | `create_artifact_revision` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/artifacts/{artifact_id}/answer-key-verifications` | `record_answer_key_verification` | `app/api_v2_routers/content_review.py` |
| POST | `/content-review/artifacts/{artifact_id}/publish` | `publish_artifact` | `app/api_v2_routers/content_review.py` |
| GET | `/content-review/artifacts/{artifact_id}/history` | `get_review_history` | `app/api_v2_routers/content_review.py` |
| GET | `/content-review/assignments/stale` | `list_stale_assignments` | `app/api_v2_routers/content_review.py` |
| GET | `/admin/curriculum-expansion/coverage/{scope_id}` | `get_scope_coverage` | `app/api_v2_routers/curriculum_expansion.py` |
| POST | `/admin/curriculum-expansion/coverage/snapshots` | `capture_snapshots` | `app/api_v2_routers/curriculum_expansion.py` |
| POST | `/admin/curriculum-expansion/plans` | `create_expansion_plan` | `app/api_v2_routers/curriculum_expansion.py` |
| POST | `/admin/curriculum-expansion/training-manifests` | `create_training_manifest` | `app/api_v2_routers/curriculum_expansion.py` |
| GET | `/admin/curriculum-expansion/training-manifests/{manifest_id}` | `get_training_manifest` | `app/api_v2_routers/curriculum_expansion.py` |
| POST | `/admin/curriculum-expansion/training-manifests/{manifest_id}/decision` | `decide_training_manifest` | `app/api_v2_routers/curriculum_expansion.py` |
| POST | `/admin/curriculum-expansion/training-manifests/{manifest_id}/export` | `export_training_manifest` | `app/api_v2_routers/curriculum_expansion.py` |
| GET | `/diagnostics/items/{learner_id}` | `get_diagnostic_items` | `app/api_v2_routers/diagnostics.py` |
| POST | `/diagnostics/submit` | `submit_diagnostic` | `app/api_v2_routers/diagnostics.py` |
| GET | `/diagnostics/coverage` | `get_item_bank_coverage` | `app/api_v2_routers/diagnostics.py` |
| GET | `/diagnostics/item-bank/items/{item_id}` | `get_item_bank_item` | `app/api_v2_routers/diagnostics.py` |
| POST | `/diagnostics/item-bank/items/{item_id}/review` | `review_item_bank_item` | `app/api_v2_routers/diagnostics.py` |
| POST | `/diagnostics/sessions` | `start_diagnostic_session` | `app/api_v2_routers/diagnostics.py` |
| GET | `/diagnostics/sessions/{session_id}/recover` | `recover_diagnostic_session` | `app/api_v2_routers/diagnostics.py` |
| GET | `/diagnostics/sessions/{session_id}/next-item` | `diagnostic_next_item` | `app/api_v2_routers/diagnostics.py` |
| POST | `/diagnostics/sessions/{session_id}/respond` | `diagnostic_respond` | `app/api_v2_routers/diagnostics.py` |
| GET | `/gamification/profile/{learner_id}` | `get_profile` | `app/api_v2_routers/gamification.py` |
| POST | `/gamification/award-xp` | `award_xp` | `app/api_v2_routers/gamification.py` |
| GET | `/gamification/leaderboard` | `get_leaderboard` | `app/api_v2_routers/gamification.py` |
| POST | `/admin/generation/runs` | `start_generation_run` | `app/api_v2_routers/generation.py` |
| GET | `/admin/generation/runs/{run_id}` | `get_generation_run` | `app/api_v2_routers/generation.py` |
| GET | `/admin/generation/runs/{run_id}/tasks` | `list_run_tasks` | `app/api_v2_routers/generation.py` |
| POST | `/admin/generation/runs/{run_id}/cancel` | `cancel_generation_run` | `app/api_v2_routers/generation.py` |
| POST | `/admin/irt-quality/runs` | `create_calibration_run` | `app/api_v2_routers/irt_quality.py` |
| GET | `/admin/irt-quality/runs/{run_id}` | `get_calibration_run` | `app/api_v2_routers/irt_quality.py` |
| GET | `/admin/irt-quality/items/{item_id}` | `get_item_quality` | `app/api_v2_routers/irt_quality.py` |
| POST | `/admin/irt-quality/items/{item_id}/override` | `set_manual_override` | `app/api_v2_routers/irt_quality.py` |
| POST | `/admin/irt-quality/items/{item_id}/override/clear` | `clear_manual_override` | `app/api_v2_routers/irt_quality.py` |
| GET | `/jobs/{job_id}` | `get_job_status` | `app/api_v2_routers/jobs.py` |
| GET | `/learner/content/scopes/{scope_id}/summary` | `get_scope_summary` | `app/api_v2_routers/learner_content.py` |
| GET | `/learner/content/scopes/{scope_id}/diagnostic-items` | `get_diagnostic_items` | `app/api_v2_routers/learner_content.py` |
| GET | `/learner/content/scopes/{scope_id}/lessons` | `get_lessons` | `app/api_v2_routers/learner_content.py` |
| GET | `/learner/content/scopes/{scope_id}/caps/{caps_ref}/diagnostic-items` | `get_diagnostic_items_by_caps_ref` | `app/api_v2_routers/learner_content.py` |
| GET | `/learner/content/scopes/{scope_id}/caps/{caps_ref}/lessons` | `get_lessons_by_caps_ref` | `app/api_v2_routers/learner_content.py` |
| POST | `/learners/` | `create_learner` | `app/api_v2_routers/learners.py` |
| GET | `/learners/{learner_id}` | `get_learner` | `app/api_v2_routers/learners.py` |
| GET | `/learners/{learner_id}/mastery` | `get_mastery` | `app/api_v2_routers/learners.py` |
| GET | `/learners/{learner_id}/mastery/summary` | `get_mastery_summary` | `app/api_v2_routers/learners.py` |
| GET | `/learners/{learner_id}/mastery/{caps_ref}` | `get_topic_mastery` | `app/api_v2_routers/learners.py` |
| DELETE | `/learners/{learner_id}` | `request_erasure` | `app/api_v2_routers/learners.py` |
| POST | `/lessons/generate` | `generate_lesson` | `app/api_v2_routers/lessons.py` |
| POST | `/lessons/` | `generate_lesson` | `app/api_v2_routers/lessons.py` |
| POST | `/lessons/generate/stream` | `generate_lesson_stream` | `app/api_v2_routers/lessons.py` |
| GET | `/lessons/{lesson_id}` | `get_lesson` | `app/api_v2_routers/lessons.py` |
| POST | `/lessons/{lesson_id}/complete` | `complete_lesson` | `app/api_v2_routers/lessons.py` |
| POST | `/lessons/sync` | `sync_lessons` | `app/api_v2_routers/lessons.py` |
| GET | `/onboarding/questions` | `get_onboarding_questions` | `app/api_v2_routers/onboarding.py` |
| POST | `/onboarding/submit` | `submit_onboarding` | `app/api_v2_routers/onboarding.py` |
| POST | `/onboarding/archetype` | `submit_onboarding` | `app/api_v2_routers/onboarding.py` |
| GET | `/parents/dashboard` | `get_parent_dashboard` | `app/api_v2_routers/parents.py` |

_Inventory truncated in this document to the first 178 route rows; regenerate `docs/route_inventory.md` for the authoritative OpenAPI-derived list._

## Route-contract requirements

- Frontend API service paths must exist in the generated backend OpenAPI.
- POPIA data-rights aliases must be explicit if compatibility is required.
- Any route added to `app/api_v2_routers/` must include tests and OpenAPI drift regeneration.

## Source-of-truth references

- Runtime entrypoint: `app/api_v2.py`
- Backend routers: `app/api_v2_routers/` and `app/modules/practice/router.py`
- Domain contracts: `app/domain/`
- Persistence models: `app/models/`, `app/repositories/`, `alembic/versions/`
- Content Factory: `app/services/content_factory*.py`, `app/api_v2_routers/content_factory.py`, `data/content_factory/`
- Diagnostics and IRT: `app/services/diagnostic*.py`, `app/api_v2_routers/diagnostics.py`, `app/api_v2_routers/irt_quality.py`
- Parent portal and POPIA: `app/api_v2_routers/parents.py`, `app/api_v2_routers/popia.py`, `app/services/popia_service.py`
- Frontend: `app/frontend/package.json`, `app/frontend/src/`
- Operations: `docker-compose.yml`, `docker-compose.prod.yml`, `.github/workflows/`, `docs/operations/`

## Standard verification gate

Run the closest applicable subset before accepting a document-controlled change:

```bash
python3 -m compileall -q app scripts
python3 -m ruff check app tests scripts --select E9,F63,F7,F82,F821
python3 scripts/verify_migration_graph.py
python3 scripts/validate_schema_integrity.py
python3 scripts/check_runtime_entrypoints.py
python3 scripts/generate_openapi.py --check
python3 scripts/generate_route_inventory.py --check
make test-fast
cd app/frontend && pnpm run env-check && pnpm run lint && pnpm run type-check && pnpm run test
```

For release claims add integration tests, Docker Compose validation, staging smoke tests, Playwright E2E, backup/restore proof, rollback proof, and security/POPIA evidence.
