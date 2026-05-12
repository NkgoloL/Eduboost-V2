SHELL := /bin/bash
PYTHON ?= python3

.PHONY: help dev test lint typecheck migrate docs clean migration-check schema-integrity migration-smoke openapi openapi-check route-inventory route-inventory-check runtime-check verify-repo-state pr002r-check beta-release-readiness-contract-check api-envelope-error-contract-check release-candidate-evidence-sweep-check frontend-verification-evidence-check database-resilience-evidence-check privacy-legal-evidence-check caps-ai-safety-evidence-check phase2-authz-check popia-legal-check caps-learning-proof-check frontend-journey-check accessibility-pwa-e2e-check observability-ops-check

help:
	@echo "Available commands:"
	@echo "  dev             - Start development servers (API, Frontend, Postgres, Redis)"
	@echo "  test            - Run backend tests"
	@echo "  lint            - Run linters (ruff, black)"
	@echo "  typecheck       - Run type checker (mypy)"
	@echo "  migrate         - Run database migrations"
	@echo "  docs            - Build and serve documentation"
	@echo "  openapi         - Generate docs/openapi.json"
	@echo "  openapi-check   - Verify docs/openapi.json is current"
	@echo "  route-inventory - Generate docs/route_inventory.md"
	@echo "  route-inventory-check - Verify docs/route_inventory.md is current"
	@echo "  runtime-check   - Verify FastAPI runtime entrypoints"
	@echo "  verify-repo-state - Verify repository provenance and release branch expectations"
	@echo "  pr002r-check   - Verify PR-002R evidence bundle"
	@echo "  beta-release-readiness-contract-check - Verify release-readiness docs contract wording"
	@echo "  release-candidate-evidence-sweep-check - Verify release-candidate evidence sweep"
	@echo "  frontend-verification-evidence-check - Verify frontend verification evidence"
	@echo "  database-resilience-evidence-check - Verify database resilience evidence"
	@echo "  privacy-legal-evidence-check - Verify privacy and legal evidence"
	@echo "  caps-ai-safety-evidence-check - Verify CAPS AI safety evidence"
	@echo "  clean           - Remove temporary files"

dev:
	docker-compose up

test:
	pytest tests/

lint:
	ruff check .
	black --check .

typecheck:
	mypy .

migrate:
	alembic upgrade head

docs:
	mkdocs serve

openapi:
	$(PYTHON) scripts/generate_openapi.py

openapi-check:
	$(PYTHON) scripts/generate_openapi.py --check

route-inventory:
	$(PYTHON) scripts/generate_route_inventory.py

route-inventory-check:
	$(PYTHON) scripts/generate_route_inventory.py --check

runtime-check:
	$(PYTHON) scripts/check_runtime_entrypoints.py

verify-repo-state:
	$(PYTHON) scripts/verify_repo_state.py --expected-branch "$${EXPECTED_RELEASE_BRANCH:-master}" $${VERIFY_REPO_STATE_ARGS:-}

pr002r-check:
	$(PYTHON) scripts/check_pr002r_evidence.py

beta-release-readiness-contract-check:
	$(PYTHON) scripts/check_beta_release_readiness_contract.py

release-candidate-evidence-sweep-check:
	$(PYTHON) scripts/check_release_candidate_evidence_sweep.py

frontend-verification-evidence-check:
	$(PYTHON) scripts/check_frontend_verification_evidence.py

database-resilience-evidence-check:
	$(PYTHON) scripts/check_database_resilience_evidence.py

privacy-legal-evidence-check:
	$(PYTHON) scripts/check_privacy_legal_release_evidence.py

caps-ai-safety-evidence-check:
	$(PYTHON) scripts/check_caps_ai_safety_evidence.py

api-envelope-error-contract-check:
	$(PYTHON) scripts/check_api_envelope_error_contract.py

migration-check: schema-integrity
	@echo "Running migration graph and schema integrity checks"
	$(PYTHON) scripts/verify_migration_graph.py

schema-integrity:
	@echo "Validating ORM schema integrity"
	$(PYTHON) scripts/validate_schema_integrity.py

db-repository-check:
	$(PYTHON) scripts/check_db_repository_evidence.py

migration-smoke:
	@echo "Run migration smoke tests (requires DATABASE_URL pointing to disposable DB)"
	./scripts/smoke_test_migrations.sh

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

phase2-authz-check:
	$(PYTHON) scripts/check_phase2_authorization_evidence.py

learner-authz-matrix:
	$(PYTHON) scripts/generate_learner_authz_matrix.py

learner-authz-check: learner-authz-matrix
	$(PYTHON) scripts/check_learner_authz_coverage.py

phase2-authz-closure:
	$(PYTHON) scripts/check_phase2_authorization_closure.py

audit-contract-check:
	$(PYTHON) scripts/check_audit_event_contracts.py

auth-boundary-check:
	$(PYTHON) scripts/check_auth_boundary_evidence.py

popia-consent-gate-check:
	$(PYTHON) scripts/generate_consent_gate_inventory.py
	$(PYTHON) scripts/check_consent_gate_inventory.py

popia-consent-audit-check:
	$(PYTHON) scripts/check_popia_consent_audit_evidence.py

popia-consent-boundary-check:
	$(PYTHON) scripts/generate_popia_consent_boundary_matrix.py
	$(PYTHON) scripts/check_popia_consent_boundary_matrix.py

popia-consent-order-check:
	$(PYTHON) scripts/check_active_consent_route_order.py

popia-consent-rejection-audit-check:
	$(PYTHON) scripts/check_consent_rejection_audit.py

popia-consent-source-check:
	$(PYTHON) scripts/check_active_consent_route_sources.py

popia-consent-closure-check:
	$(PYTHON) scripts/check_popia_consent_closure.py

privacy-boundary-check:
	$(PYTHON) scripts/check_privacy_boundary_evidence.py

popia-legal-check:
	$(PYTHON) scripts/check_popia_legal_evidence.py

environment-security-check:
	$(PYTHON) scripts/check_environment_security_contract.py

deployment-readiness-docs-check:
	$(PYTHON) scripts/check_deployment_readiness_docs.py

cluster-d-ci-check:
	$(PYTHON) scripts/check_cluster_d_ci_evidence.py

production-secret-placeholder-check:
	$(PYTHON) scripts/check_production_secret_placeholders.py

dev-only-endpoint-check:
	$(PYTHON) scripts/check_dev_only_endpoint_exposure.py

cluster-d-closure-check:
	$(PYTHON) scripts/check_cluster_d_closure.py

staging-release-gate-check:
	$(PYTHON) scripts/check_staging_release_gate.py

cicd-staging-check:
	$(PYTHON) scripts/check_cicd_staging_evidence.py

release-evidence-artifacts-check:
	$(PYTHON) scripts/check_release_evidence_artifacts.py

post-deploy-staging-smoke-checklist-check:
	$(PYTHON) scripts/check_post_deploy_staging_smoke_checklist.py

post-deploy-staging-smoke-check: post-deploy-staging-smoke-checklist-check

staging-smoke-evidence-manifest-check:
	$(PYTHON) scripts/check_staging_smoke_evidence_manifest.py

observability-ops-check:
	$(PYTHON) scripts/check_observability_ops_evidence.py

release-state-snapshot-check:
	$(PYTHON) scripts/check_release_state_snapshot.py

release-candidate-tag-manifest-check:
	$(PYTHON) scripts/check_release_candidate_tag_manifest.py

staging-operations-release-evidence-check:
	$(PYTHON) scripts/check_staging_operations_release_evidence.py

database-backup-contract-check:
	$(PYTHON) scripts/check_database_backup_contract.py

database-restore-drill-docs-check:
	$(PYTHON) scripts/check_database_restore_drill_docs.py

cluster-e-data-resilience-check:
	$(PYTHON) scripts/check_cluster_e_data_resilience_evidence.py

database-backup-dry-run:
	$(PYTHON) scripts/run_database_backup.py --dry-run

database-restore-dry-run:
	$(PYTHON) scripts/run_database_restore.py --dry-run --target-environment staging

database-backup-manifest:
	$(PYTHON) scripts/generate_database_backup_manifest.py --encrypted

database-restore-evidence:
	$(PYTHON) scripts/generate_database_restore_evidence.py

database-backup-integrity-check:
	$(PYTHON) scripts/check_database_backup_integrity.py

database-restore-integrity-check:
	$(PYTHON) scripts/check_database_restore_integrity.py

backup-redis-dr-check:
	$(PYTHON) scripts/check_backup_redis_dr_evidence.py

cluster-e-closure-check:
	$(PYTHON) scripts/check_cluster_e_closure.py

database-resilience-env-matrix-check:
	$(PYTHON) scripts/check_database_resilience_env_matrix.py

production-restore-approval-check:
	$(PYTHON) scripts/check_production_restore_approval.py

persistence-resilience-check:
	$(PYTHON) scripts/check_persistence_resilience_evidence.py

caps-alignment-contract-check:
	$(PYTHON) scripts/check_caps_alignment_contract.py

ai-safety-boundary-check:
	$(PYTHON) scripts/check_ai_safety_boundary_contract.py

ai-safety-release-check:
	$(PYTHON) scripts/check_ai_safety_release_evidence.py

cluster-f-ai-safety-check:
	$(PYTHON) scripts/check_cluster_f_ai_safety_evidence.py

ai-prompt-input-contract-check:
	$(PYTHON) scripts/check_ai_prompt_input_contract.py

diagnostic-generation-safety-check:
	$(PYTHON) scripts/check_diagnostic_generation_safety_contract.py

llm-provider-fallback-contract-check:
	$(PYTHON) scripts/check_llm_provider_fallback_contract.py

ai-output-schema-contract-check:
	$(PYTHON) scripts/check_ai_output_schema_contract.py

lesson-generation-safety-check:
	$(PYTHON) scripts/check_lesson_generation_safety_contract.py

remediation-safety-contract-check:
	$(PYTHON) scripts/check_remediation_safety_contract.py

cluster-f-closure-check:
	$(PYTHON) scripts/check_cluster_f_closure.py

ai-output-fixture-validation-check:
	$(PYTHON) scripts/validate_ai_output_fixtures.py

ai-prompt-surface-inventory:
	$(PYTHON) scripts/generate_ai_prompt_surface_inventory.py

ai-prompt-surface-inventory-check:
	$(PYTHON) scripts/check_ai_prompt_surface_inventory.py

lesson-bank-check:
	$(PYTHON) scripts/ci/ci_lesson_bank_check.py

diagnostics-assessment-check:
	$(PYTHON) scripts/ci/check_diagnostics_assessment.py
	pytest tests/unit/modules/diagnostics/test_irt_engine_hardening.py tests/unit/modules/diagnostics/test_session_lifecycle.py tests/unit/modules/progress/test_mastery_model.py tests/unit/modules/practice/test_practice_and_calibration.py --no-cov

learning-evidence-check:
	$(PYTHON) scripts/check_learning_evidence.py

caps-learning-proof-check:
	$(PYTHON) scripts/check_caps_learning_proof.py

frontend-journey-check:
	$(PYTHON) scripts/check_frontend_journey_evidence.py

accessibility-pwa-e2e-check:
	$(PYTHON) scripts/check_accessibility_pwa_e2e_evidence.py

observability-ops-check:
	$(PYTHON) scripts/check_observability_ops_evidence.py

# Evidence and release-control targets restored after stacked PR integration.
ai-fixture-coverage-check:
	$(PYTHON) scripts/check_ai_fixture_coverage_matrix.py

ai-prompt-secret-leakage-check:
	$(PYTHON) scripts/check_ai_prompt_secret_leakage.py

ai-refusal-fixture-check:
	$(PYTHON) scripts/check_ai_refusal_fixtures.py

archival-lock-assertion-check:
	$(PYTHON) scripts/check_archival_lock_assertion.py

audit-review-closeout-certificate-check:
	$(PYTHON) scripts/check_audit_review_closeout_certificate.py

beta-acceptance-exit-criteria-check:
	$(PYTHON) scripts/check_beta_acceptance_exit_criteria.py

beta-evidence-consistency-check:
	$(PYTHON) scripts/check_beta_evidence_consistency.py

beta-feedback-intake-contract-check:
	$(PYTHON) scripts/check_beta_feedback_intake_contract.py

beta-governance-seal-check:
	$(PYTHON) scripts/check_beta_governance_seal.py

beta-known-issues-register-check:
	$(PYTHON) scripts/check_beta_known_issues_register.py

beta-monitoring-incident-trigger-check:
	$(PYTHON) scripts/check_beta_monitoring_incident_trigger.py

beta-outcome-report-template-check:
	$(PYTHON) scripts/check_beta_outcome_report_template.py

beta-participant-support-handoff-check:
	$(PYTHON) scripts/check_beta_participant_support_handoff.py

beta-pr-body:
	$(PYTHON) scripts/generate_beta_pr_body.py

beta-pr-body-check:
	$(PYTHON) scripts/check_beta_pr_body.py

beta-release-closure-attestation-check:
	$(PYTHON) scripts/check_beta_release_closure_attestation.py

beta-release-communications-plan-check:
	$(PYTHON) scripts/check_beta_release_communications_plan.py

beta-release-decision-log-check:
	$(PYTHON) scripts/check_beta_release_decision_log.py

beta-release-evidence-bundle:
	$(PYTHON) scripts/generate_beta_release_evidence_bundle.py

beta-release-evidence-bundle-check:
	$(PYTHON) scripts/check_beta_release_evidence_bundle.py

beta-release-execution-plan-check:
	$(PYTHON) scripts/check_beta_release_execution_plan.py

beta-release-final-checklist-check:
	$(PYTHON) scripts/check_beta_release_final_checklist.py

beta-release-final-index-check:
	$(PYTHON) scripts/check_beta_release_final_index.py

beta-release-freeze-window-check:
	$(PYTHON) scripts/check_beta_release_freeze_window.py

beta-retrospective-action-register-check:
	$(PYTHON) scripts/check_beta_retrospective_action_register.py

beta-rollback-runbook-check:
	$(PYTHON) scripts/check_beta_rollback_runbook.py

beta-signoff-manifest:
	$(PYTHON) scripts/generate_beta_signoff_manifest.py

beta-signoff-manifest-check:
	$(PYTHON) scripts/check_beta_signoff_manifest.py

branch-handoff-proof-record-check:
	$(PYTHON) scripts/check_branch_handoff_proof_record.py

branch-sync-rebase-checklist-check:
	$(PYTHON) scripts/check_branch_sync_rebase_checklist.py

cluster-g-frontend-check:
	$(PYTHON) scripts/check_cluster_g_frontend_evidence.py

cluster-g-closure-check:
	$(PYTHON) scripts/check_cluster_g_closure.py

cluster-h-release-readiness-check:
	$(PYTHON) scripts/check_cluster_h_release_readiness.py

cluster-h-closure-check:
	$(PYTHON) scripts/check_cluster_h_closure.py

cluster-h-final-closeout-rollup-check:
	$(PYTHON) scripts/check_cluster_h_final_closeout_rollup.py

cluster-h-release-evidence-checksum-index-check:
	$(PYTHON) scripts/check_cluster_h_release_evidence_checksum_index.py

cluster-h-terminal-closure-assertion-check:
	$(PYTHON) scripts/check_cluster_h_terminal_closure_assertion.py

evidence-archive-completeness-guard-check:
	$(PYTHON) scripts/check_evidence_archive_completeness_guard.py

evidence-freeze-confirmation-record-check:
	$(PYTHON) scripts/check_evidence_freeze_confirmation_record.py

final-acceptance-memo-check:
	$(PYTHON) scripts/check_final_acceptance_memo.py

final-acceptance-packet-index-check:
	$(PYTHON) scripts/check_final_acceptance_packet_index.py

final-archive-accession-record-check:
	$(PYTHON) scripts/check_final_archive_accession_record.py

final-audit-handoff-register-check:
	$(PYTHON) scripts/check_final_audit_handoff_register.py

final-beta-operator-packet-check:
	$(PYTHON) scripts/check_final_beta_operator_packet.py

final-closure-manifest-check:
	$(PYTHON) scripts/check_final_closure_manifest.py

final-evidence-noop-execution-assertion-check:
	$(PYTHON) scripts/check_final_evidence_noop_execution_assertion.py

final-merge-signoff-lock-check:
	$(PYTHON) scripts/check_final_merge_signoff_lock.py

final-pr-handoff-summary-check:
	$(PYTHON) scripts/check_final_pr_handoff_summary.py

final-pr-merge-readiness-check:
	$(PYTHON) scripts/check_final_pr_merge_readiness.py

final-project-closeout-attestation-check:
	$(PYTHON) scripts/check_final_project_closeout_attestation.py

final-release-evidence-ledger-check:
	$(PYTHON) scripts/check_final_release_evidence_ledger.py

final-release-evidence-toc-check:
	$(PYTHON) scripts/check_final_release_evidence_toc.py

final-release-handoff-package-check:
	$(PYTHON) scripts/check_final_release_handoff_package.py

final-release-operator-brief-check:
	$(PYTHON) scripts/check_final_release_operator_brief.py

final-release-readiness-rollup-check:
	$(PYTHON) scripts/check_final_release_readiness_rollup.py

final-release-verification-check:
	$(PYTHON) scripts/check_final_release_verification_bundle.py

final-release-verification:
	$(PYTHON) scripts/check_final_release_verification_bundle.py --execute

final-reviewer-disposition-record-check:
	$(PYTHON) scripts/check_final_reviewer_disposition_record.py

final-reviewer-pack-checklist-check:
	$(PYTHON) scripts/check_final_reviewer_pack_checklist.py

final-sealed-package-manifest-check:
	$(PYTHON) scripts/check_final_sealed_package_manifest.py

frontend-accessibility-contract-check:
	$(PYTHON) scripts/check_frontend_accessibility_contract.py

frontend-accessibility-static-check:
	$(PYTHON) scripts/check_frontend_accessibility_static.py

frontend-api-client-inventory:
	$(PYTHON) scripts/generate_frontend_api_client_inventory.py

frontend-api-client-inventory-check:
	$(PYTHON) scripts/check_frontend_api_client_inventory.py

frontend-auth-consent-denial-check:
	$(PYTHON) scripts/check_frontend_auth_consent_denial_contract.py

frontend-build-test-lint-contract-check:
	$(PYTHON) scripts/check_frontend_build_test_lint_contract.py

frontend-e2e-env-contract-check:
	$(PYTHON) scripts/check_frontend_e2e_environment_contract.py

frontend-e2e-opt-in-workflow-check:
	$(PYTHON) scripts/check_frontend_e2e_opt_in_workflow.py

frontend-e2e-runtime-command-check:
	$(PYTHON) scripts/check_frontend_e2e_runtime_commands.py

frontend-e2e-smoke:
	cd app/frontend && npx playwright test tests/e2e/learner-vertical-journey.spec.ts tests/e2e/parent-vertical-journey.spec.ts

frontend-e2e-mocked:
	cd app/frontend && PLAYWRIGHT_MOCK_API=1 npx playwright test tests/e2e/learner-mocked-api-journey.spec.ts tests/e2e/parent-mocked-api-journey.spec.ts

frontend-e2e:
	cd app/frontend && npx playwright test

frontend-journey-fixture-check:
	$(PYTHON) scripts/check_frontend_journey_fixtures.py

frontend-mock-api-fixture-check:
	$(PYTHON) scripts/check_frontend_mock_api_fixtures.py

frontend-playwright-mock-helper-check:
	$(PYTHON) scripts/check_frontend_playwright_mock_helpers.py

frontend-playwright-mocked-specs-check:
	$(PYTHON) scripts/check_frontend_playwright_mocked_specs.py

frontend-playwright-scaffold-check:
	$(PYTHON) scripts/check_frontend_playwright_scaffold.py

frontend-playwright-specs-check:
	$(PYTHON) scripts/check_frontend_playwright_specs.py

frontend-route-inventory:
	$(PYTHON) scripts/generate_frontend_route_inventory.py

frontend-route-inventory-check:
	$(PYTHON) scripts/check_frontend_route_inventory.py

frontend-runtime-inventory:
	$(PYTHON) scripts/generate_frontend_runtime_inventory.py

frontend-runtime-inventory-check:
	$(PYTHON) scripts/check_frontend_runtime_inventory.py

frozen-scope-variance-register-check:
	$(PYTHON) scripts/check_frozen_scope_variance_register.py

generated-artifact-hygiene-check:
	$(PYTHON) scripts/check_generated_artifact_hygiene.py

learner-vertical-journey-contract-check:
	$(PYTHON) scripts/check_learner_vertical_journey_contract.py

merge-control-evidence-gate-check:
	$(PYTHON) scripts/check_merge_control_evidence_gate.py

parent-vertical-journey-contract-check:
	$(PYTHON) scripts/check_parent_vertical_journey_contract.py

post-beta-evidence-archive-manifest-check:
	$(PYTHON) scripts/check_post_beta_evidence_archive_manifest.py

post-closeout-custody-register-check:
	$(PYTHON) scripts/check_post_closeout_custody_register.py

post-closeout-evidence-access-policy-check:
	$(PYTHON) scripts/check_post_closeout_evidence_access_policy.py

post-closeout-maintenance-boundary-check:
	$(PYTHON) scripts/check_post_closeout_maintenance_boundary.py

post-deploy-staging-smoke-checklist-check:
	$(PYTHON) scripts/check_post_deploy_staging_smoke_checklist.py

post-merge-evidence-continuity-note-check:
	$(PYTHON) scripts/check_post_merge_evidence_continuity_note.py

post-merge-release-handoff-check:
	$(PYTHON) scripts/check_post_merge_release_handoff.py

post-terminal-audit-readiness-check:
	$(PYTHON) scripts/check_post_terminal_audit_readiness.py

pr-closeout-evidence-checklist-check:
	$(PYTHON) scripts/check_pr_closeout_evidence_checklist.py

pr-merge-evidence-summary-check:
	$(PYTHON) scripts/check_pr_merge_evidence_summary.py

pr-ready-final-closure-certificate-check:
	$(PYTHON) scripts/check_pr_ready_final_closure_certificate.py

project-release-closure-index-check:
	$(PYTHON) scripts/check_project_release_closure_index.py

release-approval-workflow-contract-check:
	$(PYTHON) scripts/check_release_approval_workflow_contract.py

release-artifact-retention-contract-check:
	$(PYTHON) scripts/check_release_artifact_retention_contract.py

release-audit-trail-index-check:
	$(PYTHON) scripts/check_release_audit_trail_index.py

release-candidate-tag-manifest:
	$(PYTHON) scripts/generate_release_candidate_tag_manifest.py

release-candidate-tag-manifest-check:
	$(PYTHON) scripts/check_release_candidate_tag_manifest.py

release-change-control-exception-log-check:
	$(PYTHON) scripts/check_release_change_control_exception_log.py

release-evidence-retention-finalization-check:
	$(PYTHON) scripts/check_release_evidence_retention_finalization.py

release-handoff-freeze-assertion-check:
	$(PYTHON) scripts/check_release_handoff_freeze_assertion.py

release-owner-accountability-check:
	$(PYTHON) scripts/check_release_owner_accountability.py

release-owner-execution-guardrail-check:
	$(PYTHON) scripts/check_release_owner_execution_guardrail.py

release-owner-post-closeout-decision-record-check:
	$(PYTHON) scripts/check_release_owner_post_closeout_decision_record.py

release-record-closure-ledger-check:
	$(PYTHON) scripts/check_release_record_closure_ledger.py

release-state-snapshot:
	$(PYTHON) scripts/generate_release_state_snapshot.py

release-state-snapshot-check:
	$(PYTHON) scripts/check_release_state_snapshot.py

reviewer-decision-capture-template-check:
	$(PYTHON) scripts/check_reviewer_decision_capture_template.py

sealed-evidence-access-handoff-check:
	$(PYTHON) scripts/check_sealed_evidence_access_handoff.py

sealed-reviewer-closeout-packet-check:
	$(PYTHON) scripts/check_sealed_reviewer_closeout_packet.py

staging-smoke-evidence-manifest:
	$(PYTHON) scripts/generate_staging_smoke_evidence_manifest.py

staging-smoke-evidence-manifest-check:
	$(PYTHON) scripts/check_staging_smoke_evidence_manifest.py

terminal-evidence-retrieval-guide-check:
	$(PYTHON) scripts/check_terminal_evidence_retrieval_guide.py

terminal-evidence-seal-check:
	$(PYTHON) scripts/check_terminal_evidence_seal.py

terminal-handoff-closure-note-check:
	$(PYTHON) scripts/check_terminal_handoff_closure_note.py

terminal-pr-evidence-index-check:
	$(PYTHON) scripts/check_terminal_pr_evidence_index.py

terminal-review-index-check:
	$(PYTHON) scripts/check_terminal_review_index.py

domain-01-repository-governance-ci-evidence-check:
	$(PYTHON) scripts/check_domain_01_repository_governance_ci_evidence.py
