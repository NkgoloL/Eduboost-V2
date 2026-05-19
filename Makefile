SHELL := /bin/bash
PYTHON ?= python3

include Makefile.arch

.PHONY: accessibility-pwa-e2e-check ai-fixture-coverage-check ai-output-fixture-validation-check ai-output-schema-contract-check ai-prompt-input-contract-check ai-prompt-secret-leakage-check ai-prompt-surface-inventory ai-prompt-surface-inventory-check ai-refusal-fixture-check ai-safety-boundary-check ai-safety-release-check api-envelope-error-contract-check archival-lock-assertion-check audit-contract-check audit-review-closeout-certificate-check auth-boundary-check backup-redis-dr-check beta-acceptance-exit-criteria-check beta-evidence-consistency-check beta-feedback-intake-contract-check beta-governance-seal-check beta-known-issues-register-check beta-monitoring-incident-trigger-check beta-outcome-report-template-check beta-participant-support-handoff-check beta-pr-body beta-pr-body-check beta-release-closure-attestation-check beta-release-communications-plan-check beta-release-decision-log-check beta-release-evidence-bundle beta-release-evidence-bundle-check beta-release-execution-plan-check beta-release-final-checklist-check beta-release-final-index-check beta-release-freeze-window-check beta-release-readiness-contract-check beta-retrospective-action-register-check beta-rollback-runbook-check beta-signoff-manifest beta-signoff-manifest-check branch-handoff-proof-record-check branch-sync-rebase-checklist-check caps-ai-safety-evidence-check caps-alignment-contract-check caps-learning-proof-check cicd-staging-check clean cluster-d-ci-check cluster-d-closure-check cluster-e-closure-check cluster-e-data-resilience-check cluster-f-ai-safety-check cluster-f-closure-check cluster-g-closure-check cluster-g-frontend-check cluster-h-closure-check cluster-h-final-closeout-rollup-check cluster-h-release-evidence-checksum-index-check cluster-h-release-readiness-check cluster-h-terminal-closure-assertion-check database-backup-contract-check database-backup-dry-run database-backup-integrity-check database-backup-manifest database-resilience-env-matrix-check database-resilience-evidence-check database-restore-drill-docs-check database-restore-dry-run database-restore-evidence database-restore-integrity-check db-repository-check deployment-readiness-docs-check dev dev-only-endpoint-check diagnostic-generation-safety-check diagnostics-assessment-check docs domain-01-repository-governance-ci-evidence-check environment-security-check evidence-archive-completeness-guard-check evidence-freeze-confirmation-record-check final-acceptance-memo-check final-acceptance-packet-index-check final-archive-accession-record-check final-audit-handoff-register-check final-beta-operator-packet-check final-closure-manifest-check final-evidence-noop-execution-assertion-check final-merge-signoff-lock-check final-pr-handoff-summary-check final-pr-merge-readiness-check final-project-closeout-attestation-check final-release-evidence-ledger-check final-release-evidence-toc-check final-release-handoff-package-check final-release-operator-brief-check final-release-readiness-rollup-check final-release-verification final-release-verification-check final-reviewer-disposition-record-check final-reviewer-pack-checklist-check final-sealed-package-manifest-check frontend-accessibility-contract-check frontend-accessibility-static-check frontend-api-client-inventory frontend-api-client-inventory-check frontend-auth-consent-denial-check frontend-build-test-lint-contract-check frontend-e2e frontend-e2e-env-contract-check frontend-e2e-mocked frontend-e2e-opt-in-workflow-check frontend-e2e-runtime-command-check frontend-e2e-smoke frontend-journey-check frontend-journey-fixture-check frontend-mock-api-fixture-check frontend-playwright-mock-helper-check frontend-playwright-mocked-specs-check frontend-playwright-scaffold-check frontend-playwright-specs-check frontend-route-inventory frontend-route-inventory-check frontend-runtime-inventory frontend-runtime-inventory-check frontend-verification-evidence-check frozen-scope-variance-register-check generated-artifact-hygiene-check learner-authz-check learner-authz-matrix learner-vertical-journey-contract-check learning-evidence-check lesson-bank-check lesson-generation-safety-check lint llm-provider-fallback-contract-check merge-control-evidence-gate-check migrate migration-check migration-smoke observability-ops-check openapi openapi-check parent-vertical-journey-contract-check persistence-resilience-check phase2-authz-check phase2-authz-closure popia-consent-audit-check popia-consent-boundary-check popia-consent-closure-check popia-consent-gate-check popia-consent-order-check popia-consent-rejection-audit-check popia-consent-source-check popia-legal-check post-beta-evidence-archive-manifest-check post-closeout-custody-register-check post-closeout-evidence-access-policy-check post-closeout-maintenance-boundary-check post-deploy-staging-smoke-check post-deploy-staging-smoke-checklist-check post-merge-evidence-continuity-note-check post-merge-release-handoff-check post-terminal-audit-readiness-check pr-closeout-evidence-checklist-check pr-merge-evidence-summary-check pr-ready-final-closure-certificate-check pr002r-check privacy-boundary-check privacy-legal-evidence-check production-restore-approval-check production-secret-placeholder-check project-release-closure-index-check release-approval-workflow-contract-check release-artifact-retention-contract-check release-audit-trail-index-check release-candidate-evidence-sweep-check release-candidate-tag-manifest release-candidate-tag-manifest-check release-change-control-exception-log-check release-evidence-artifacts-check release-evidence-retention-finalization-check release-handoff-freeze-assertion-check release-owner-accountability-check release-owner-execution-guardrail-check release-owner-post-closeout-decision-record-check release-record-closure-ledger-check release-state-snapshot release-state-snapshot-check remediation-safety-contract-check reviewer-decision-capture-template-check route-inventory route-inventory-check runtime-check schema-integrity sealed-evidence-access-handoff-check sealed-reviewer-closeout-packet-check staging-operations-release-evidence-check staging-release-gate-check staging-smoke-evidence-manifest staging-smoke-evidence-manifest-check terminal-evidence-retrieval-guide-check terminal-evidence-seal-check terminal-handoff-closure-note-check terminal-pr-evidence-index-check terminal-review-index-check test typecheck verify-repo-state

help:
	@echo "Available commands:"
	@echo "  dev             - Start development servers (API, Frontend, Postgres, Redis)"
	@echo "  test            - Run backend tests"
	@echo "  lint            - Run linters (ruff, black)"
	@echo "  typecheck       - Run type checker (mypy)"
	@echo "  migrate         - Run database migrations"
	@echo "  docs            - Build and serve documentation"
	@echo "  docs-inventory  - Generate documentation intelligence inventory"
	@echo "  docs-inventory-check - Verify documentation intelligence inventory is current"
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

docs-inventory:
	$(PYTHON) scripts/docs_inventory.py

docs-inventory-check:
	$(PYTHON) scripts/docs_inventory.py --check

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

post-deploy-staging-smoke-check: post-deploy-staging-smoke-checklist-check

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
# =============================================================================
# Makefile additions – paste these into the existing Makefile
# (or apply via: patch -p0 < docs/patches/makefile_additions.patch)
#
# These additions address Recommendations 4 and 6 from the 2026-05-12
# technical state report.
# =============================================================================

# Add to the existing .PHONY line (or replace the line entirely):
# .PHONY: ... deduplicate-check refresh-current-state refresh-current-state-report sync-check-origin

# ---------------------------------------------------------------------------
# Recommendation 4: Makefile hygiene – detect duplicate targets
# ---------------------------------------------------------------------------

deduplicate-check:
	$(PYTHON) scripts/deduplicate_makefile_targets.py

deduplicate-fix:
	$(PYTHON) scripts/deduplicate_makefile_targets.py --fix

deduplicate-fix-dry-run:
	$(PYTHON) scripts/deduplicate_makefile_targets.py --fix --dry-run


# ---------------------------------------------------------------------------
# Recommendation 5: Sync check – verify local branch is up to date
# ---------------------------------------------------------------------------

sync-check-origin:
	./scripts/sync_check_origin.sh

sync-and-verify:
	./scripts/sync_check_origin.sh --sync


# ---------------------------------------------------------------------------
# Recommendation 6: Refresh current state documentation
# ---------------------------------------------------------------------------

refresh-current-state:
	$(PYTHON) scripts/refresh_current_state_doc.py

refresh-current-state-report:
	$(PYTHON) scripts/refresh_current_state_doc.py --dated-report

refresh-current-state-dry-run:
	$(PYTHON) scripts/refresh_current_state_doc.py --dry-run --dated-report


# ---------------------------------------------------------------------------
# Omnibus: run all six recommendation fixes in sequence
# ---------------------------------------------------------------------------
# Intended for use after applying all code changes from the 2026-05-12
# technical report.  Run this once to verify everything is clean.

rec-all-checks: deduplicate-check \
                frontend-e2e-opt-in-workflow-check \
                pr002r-check \
                runtime-check \
                openapi-check \
                route-inventory-check
	$(PYTHON) -m pytest tests/unit -m "not llm and not e2e" --tb=short --no-cov -q
	$(PYTHON) scripts/refresh_current_state_doc.py --dated-report
	@echo ""
	@echo "All recommendation checks passed."
	@echo "Review docs/current_state.md and commit."

legacy-route-guard:
	pytest tests/unit/test_api_v2_router_contract.py tests/test_entrypoints.py \
		-v -k "legacy" --tb=short --no-cov
	$(PYTHON) scripts/check_runtime_entrypoints.py

pr-002r-check: runtime-check openapi-check legacy-route-guard
	pytest \
		tests/test_entrypoints.py \
		tests/unit/test_api_v2_router_contract.py \
		tests/unit/test_api_v2_envelope.py \
		tests/unit/test_exception_envelopes.py \
		tests/unit/test_no_raw_dict_responses.py \
		-v --tb=short --no-cov
	@echo ""
	@echo "PR-002R acceptance checks passed."

database-persistence-production-readiness-check:
	$(PYTHON) scripts/check_database_persistence_production_readiness.py

ai-llm-safety-caps-production-readiness-check:
	$(PYTHON) scripts/check_ai_llm_safety_caps_production_readiness.py

diagnostics-assessment-production-readiness-check:
	$(PYTHON) scripts/check_diagnostics_assessment_production_readiness.py

domain-07-diagnostics-assessment-evidence-check:
	$(PYTHON) scripts/check_domain_07_diagnostics_assessment_evidence.py

frontend-production-readiness-check:
	$(PYTHON) scripts/check_frontend_production_readiness.py

billing-monetization-production-readiness-check:
	$(PYTHON) scripts/check_billing_monetization_production_readiness.py

notifications-communication-production-readiness-check:
	$(PYTHON) scripts/check_notifications_communication_production_readiness.py

observability-production-readiness-check:
	$(PYTHON) scripts/check_observability_production_readiness.py

ci-cd-deployment-production-readiness-check:
	$(PYTHON) scripts/check_ci_cd_deployment_production_readiness.py

backup-restore-disaster-recovery-production-readiness-check:
	$(PYTHON) scripts/check_backup_restore_disaster_recovery_production_readiness.py

testing-release-quality-gates-production-readiness-check:
	$(PYTHON) scripts/check_testing_release_quality_gates_production_readiness.py

security-posture-threat-modeling-production-readiness-check:
	$(PYTHON) scripts/check_security_posture_threat_modeling_production_readiness.py

incident-response-operations-support-production-readiness-check:
	$(PYTHON) scripts/check_incident_response_operations_support_production_readiness.py

documentation-adrs-claim-discipline-production-readiness-check:
	$(PYTHON) scripts/check_documentation_adrs_claim_discipline_production_readiness.py

beta-launch-staging-acceptance-production-readiness-check:
	$(PYTHON) scripts/check_beta_launch_staging_acceptance_production_readiness.py

roadmap-after-production-readiness-baseline-check:
	$(PYTHON) scripts/check_roadmap_after_production_readiness_baseline.py

final-release-blocker-checklist-check:
	$(PYTHON) scripts/check_final_release_blocker_checklist.py

.PHONY: test-env-check route-alias-matrix route-alias-matrix-check release-evidence-index-check release-hygiene-check reset-test-db

test-env-check:
	PYTHONPATH=. python3 scripts/check_test_environment.py

route-alias-matrix:
	PYTHONPATH=. python3 scripts/generate_route_alias_matrix.py

route-alias-matrix-check: route-alias-matrix
	test -f docs/release/route_alias_matrix.md

release-evidence-index-check:
	PYTHONPATH=. python3 scripts/check_release_evidence_index.py

release-hygiene-check: test-env-check route-alias-matrix-check release-evidence-index-check

reset-test-db:
	PYTHONPATH=. python3 scripts/check_test_environment.py --strict
	@echo "Refusing to reset automatically from Makefile. Use the project-approved DB reset script only after verifying DATABASE_URL targets a disposable test database."
	@exit 1

.PHONY: warning-cleanup-check test-env-strict-check

warning-cleanup-check:
	python3 scripts/check_warning_cleanup.py

test-env-strict-check:
	PYTHONPATH=. python3 scripts/check_test_environment.py --strict

.PHONY: route-alias-policy-check ci-workflow-consolidation-check ci-core-local ci-contract-check

route-alias-policy-check:
	PYTHONPATH=. python3 scripts/check_route_alias_matrix.py

ci-workflow-consolidation-check:
	PYTHONPATH=. python3 scripts/check_ci_workflow_consolidation.py

ci-contract-check: ci-workflow-consolidation-check route-alias-policy-check

ci-core-local: release-hygiene-check route-alias-policy-check openapi-check
	pytest -c pytest.ini tests/unit -q --no-cov
	pytest -c pytest.ini tests/integration -q --no-cov

.PHONY: runtime-release-evidence-check release-readiness-local-check

runtime-release-evidence-check:
	PYTHONPATH=. python3 scripts/check_runtime_release_evidence.py

release-readiness-local-check: release-hygiene-check runtime-release-evidence-check ci-contract-check
	pytest -c pytest.ini tests/unit/test_runtime_release_evidence_contract.py tests/unit/test_release_hygiene_tooling.py tests/unit/test_ci_route_alias_policy.py -q --no-cov

.PHONY: capture-pytest-release-evidence pytest-release-evidence-check local-release-evidence-check

capture-pytest-release-evidence:
	PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py all

pytest-release-evidence-check:
	PYTHONPATH=. python3 scripts/check_pytest_release_evidence.py

local-release-evidence-check: pytest-release-evidence-check runtime-release-evidence-check release-evidence-index-check

.PHONY: staging-smoke staging-smoke-check

staging-smoke:
	PYTHONPATH=. python3 scripts/run_staging_smoke.py
staging-smoke-check:
	PYTHONPATH=. python3 scripts/run_staging_smoke.py --validate --require-pass
staging-smoke-schema-check:
	PYTHONPATH=. python3 scripts/run_staging_smoke.py --validate
.PHONY: staging-smoke staging-smoke-check staging-smoke-schema-check

.PHONY: migration-evidence-capture migration-evidence-check migration-evidence-schema-check

migration-evidence-capture:
	PYTHONPATH=. python3 scripts/capture_migration_evidence.py

migration-evidence-check:
	PYTHONPATH=. python3 scripts/capture_migration_evidence.py --validate --require-pass

migration-evidence-schema-check:
	PYTHONPATH=. python3 scripts/capture_migration_evidence.py --validate

.PHONY: backend-consolidation-dragons-check schema-drift-check backend-consolidation-diagnostics-check

backend-consolidation-dragons-check:
	PYTHONPATH=. python3 scripts/check_backend_consolidation_dragons.py

schema-drift-check:
	PYTHONPATH=. python3 scripts/compare_orm_tables_to_database.py

backend-consolidation-diagnostics-check: backend-consolidation-dragons-check schema-drift-check
	pytest -c pytest.ini tests/unit/test_backend_consolidation_dragon_diagnostics.py -q --no-cov

.PHONY: audit-callsite-inventory audit-compatibility-check

audit-callsite-inventory:
	PYTHONPATH=. python3 scripts/generate_audit_callsite_inventory.py --fail-empty

audit-compatibility-check: audit-callsite-inventory
	pytest -c pytest.ini tests/unit/test_audit_callsite_inventory_and_adapter.py -q --no-cov

.PHONY: consent-callsite-inventory consent-compatibility-check

consent-callsite-inventory:
	PYTHONPATH=. python3 scripts/generate_consent_callsite_inventory.py --fail-empty

consent-compatibility-check: consent-callsite-inventory
	pytest -c pytest.ini tests/unit/test_consent_callsite_inventory_and_compat.py -q --no-cov

.PHONY: health-readiness-contract-check schema-drift-contract-check schema-drift-check-db backend-runtime-diagnostics-check

health-readiness-contract-check:
	PYTHONPATH=. python3 scripts/check_health_readiness_contract.py

schema-drift-contract-check:
	PYTHONPATH=. python3 scripts/check_schema_drift_contract.py

schema-drift-check-db:
	PYTHONPATH=. python3 scripts/compare_orm_tables_to_database.py --require-db --fail-on-drift

backend-runtime-diagnostics-check: health-readiness-contract-check schema-drift-contract-check backend-consolidation-diagnostics-check
	pytest -c pytest.ini tests/unit/test_health_readiness_schema_drift_guards.py -q --no-cov

.PHONY: backend-consolidation-report backend-consolidation-release-guard backend-consolidation-full-check

backend-consolidation-report:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_report.py

backend-consolidation-release-guard:
	PYTHONPATH=. python3 scripts/check_backend_consolidation_release_guard.py

backend-consolidation-full-check: backend-consolidation-report backend-consolidation-release-guard audit-compatibility-check consent-compatibility-check backend-runtime-diagnostics-check
	pytest -c pytest.ini tests/unit/test_backend_consolidation_rollup_and_guard.py -q --no-cov

.PHONY: backend-runtime-compatibility-check backend-runtime-compatibility-report backend-runtime-compatibility-full-check

backend-runtime-compatibility-check:
	PYTHONPATH=. python3 scripts/check_backend_runtime_compatibility.py

backend-runtime-compatibility-report:
	PYTHONPATH=. python3 scripts/generate_backend_runtime_compatibility_report.py

backend-runtime-compatibility-full-check: backend-runtime-compatibility-check backend-runtime-compatibility-report audit-compatibility-check consent-compatibility-check health-readiness-contract-check
	pytest -c pytest.ini tests/unit/test_backend_runtime_compatibility_contracts.py -q --no-cov

.PHONY: backend-deletion-candidate-inventory backend-consolidation-noop-guard backend-consolidation-readiness-report backend-consolidation-readiness-full-check

backend-deletion-candidate-inventory:
	PYTHONPATH=. python3 scripts/generate_backend_deletion_candidate_inventory.py --fail-empty

backend-consolidation-noop-guard: backend-deletion-candidate-inventory
	PYTHONPATH=. python3 scripts/check_backend_consolidation_noop_guard.py

backend-consolidation-readiness-report:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_readiness_report.py

backend-consolidation-readiness-full-check: backend-consolidation-readiness-report backend-consolidation-noop-guard backend-consolidation-full-check backend-runtime-compatibility-full-check
	pytest -c pytest.ini tests/unit/test_backend_consolidation_readiness_and_noop_guard.py -q --no-cov

.PHONY: backend-consolidation-execution-packet-check backend-consolidation-execution-report backend-consolidation-execution-full-check

backend-consolidation-execution-packet-check:
	PYTHONPATH=. python3 scripts/check_backend_consolidation_execution_packet.py

backend-consolidation-execution-report:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_execution_report.py

backend-consolidation-execution-full-check: backend-consolidation-execution-packet-check backend-consolidation-execution-report backend-consolidation-readiness-full-check
	pytest -c pytest.ini tests/unit/test_backend_consolidation_execution_packet.py -q --no-cov

.PHONY: backend-runtime-probe-fixtures-check backend-runtime-probe-report backend-runtime-probe-full-check

backend-runtime-probe-fixtures-check:
	PYTHONPATH=. python3 scripts/check_backend_runtime_probe_fixtures.py

backend-runtime-probe-report:
	PYTHONPATH=. python3 scripts/generate_backend_runtime_probe_report.py

backend-runtime-probe-full-check: backend-runtime-probe-fixtures-check backend-runtime-probe-report backend-consolidation-execution-full-check
	pytest -c pytest.ini tests/unit/test_backend_runtime_probe_fixtures.py -q --no-cov

.PHONY: backend-consolidation-evidence-manifest backend-consolidation-terminal-check backend-consolidation-terminal-report backend-consolidation-terminal-full-check

backend-consolidation-evidence-manifest:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_evidence_manifest.py

backend-consolidation-terminal-check: backend-consolidation-evidence-manifest
	PYTHONPATH=. python3 scripts/check_backend_consolidation_terminal_packet.py

backend-consolidation-terminal-report:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_terminal_report.py

backend-consolidation-terminal-full-check: backend-consolidation-terminal-report backend-consolidation-terminal-check backend-consolidation-execution-full-check backend-runtime-probe-full-check
	pytest -c pytest.ini tests/unit/test_backend_consolidation_terminal_packet.py -q --no-cov

.PHONY: backend-consolidation-implementation-foundation-check backend-consolidation-implementation-foundation-report backend-consolidation-implementation-foundation-full-check

backend-consolidation-implementation-foundation-check:
	PYTHONPATH=. python3 scripts/check_backend_consolidation_implementation_foundation.py

backend-consolidation-implementation-foundation-report:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_implementation_report.py

backend-consolidation-implementation-foundation-full-check: backend-consolidation-implementation-foundation-check backend-consolidation-implementation-foundation-report backend-consolidation-terminal-full-check
	pytest -c pytest.ini tests/unit/test_backend_consolidation_implementation_foundation.py -q --no-cov

.PHONY: schema-drift-disposable-proof schema-drift-disposable-proof-check schema-drift-disposable-proof-schema-check deep-readiness-readonly-check audit-canonicalization-slice-check backend-implementation-364-366-full-check

schema-drift-disposable-proof:
	PYTHONPATH=. python3 scripts/run_disposable_schema_drift_proof.py

schema-drift-disposable-proof-check:
	PYTHONPATH=. python3 scripts/run_disposable_schema_drift_proof.py --validate --require-pass

schema-drift-disposable-proof-schema-check:
	PYTHONPATH=. python3 scripts/run_disposable_schema_drift_proof.py --validate

deep-readiness-readonly-check:
	PYTHONPATH=. python3 scripts/check_deep_readiness_readonly_guard.py

audit-canonicalization-slice-check:
	PYTHONPATH=. python3 scripts/check_audit_canonicalization_slice.py

backend-implementation-364-366-full-check: deep-readiness-readonly-check audit-canonicalization-slice-check backend-consolidation-implementation-foundation-full-check
	pytest -c pytest.ini tests/unit/test_schema_drift_deep_readiness_audit_slice.py -q --no-cov

.PHONY: consent-runtime-compatibility-slice-check audit-canonicalization-registry-check backend-consolidation-progress-report backend-implementation-367-370-full-check

consent-runtime-compatibility-slice-check:
	PYTHONPATH=. python3 scripts/check_consent_runtime_compatibility_slice.py

audit-canonicalization-registry-check:
	PYTHONPATH=. python3 scripts/check_audit_canonicalization_registry.py

backend-consolidation-progress-report:
	PYTHONPATH=. python3 scripts/generate_backend_consolidation_progress_report.py

backend-implementation-367-370-full-check: consent-runtime-compatibility-slice-check audit-canonicalization-registry-check backend-consolidation-progress-report backend-implementation-364-366-full-check backend-consolidation-implementation-foundation-full-check
	pytest -c pytest.ini tests/unit/test_consent_runtime_audit_registry_progress.py -q --no-cov

.PHONY: backend-implementation-371-375-check backend-implementation-371-375-report backend-implementation-371-375-full-check

backend-implementation-371-375-check:
	PYTHONPATH=. python3 scripts/check_backend_implementation_371_375.py

backend-implementation-371-375-report:
	PYTHONPATH=. python3 scripts/generate_backend_implementation_371_375_report.py

backend-implementation-371-375-full-check: backend-implementation-371-375-check backend-implementation-371-375-report backend-implementation-367-370-full-check backend-implementation-364-366-full-check
	pytest -c pytest.ini tests/unit/test_backend_implementation_371_375.py -q --no-cov

.PHONY: backend-runtime-wiring-preflight-check backend-runtime-wiring-preflight-report backend-implementation-376-382-full-check

backend-runtime-wiring-preflight-check:
	PYTHONPATH=. python3 scripts/check_backend_runtime_wiring_preflight.py

backend-runtime-wiring-preflight-report:
	PYTHONPATH=. python3 scripts/generate_backend_runtime_wiring_preflight_report.py

backend-implementation-376-382-full-check: backend-runtime-wiring-preflight-check backend-runtime-wiring-preflight-report backend-implementation-371-375-full-check backend-implementation-367-370-full-check
	pytest -c pytest.ini tests/unit/test_backend_runtime_wiring_preflight.py -q --no-cov

.PHONY: backend-runtime-wiring-cases-check backend-runtime-wiring-cases-report backend-implementation-383-390-full-check

backend-runtime-wiring-cases-check:
	PYTHONPATH=. python3 scripts/check_backend_runtime_wiring_cases.py

backend-runtime-wiring-cases-report:
	PYTHONPATH=. python3 scripts/generate_backend_runtime_wiring_cases_report.py

backend-implementation-383-390-full-check: backend-runtime-wiring-cases-check backend-runtime-wiring-cases-report backend-implementation-376-382-full-check backend-implementation-371-375-full-check
	pytest -c pytest.ini tests/unit/test_backend_runtime_wiring_cases.py -q --no-cov

.PHONY: backend-first-wiring-candidates-check backend-first-wiring-candidates-report backend-implementation-391-400-full-check

backend-first-wiring-candidates-check:
	PYTHONPATH=. python3 scripts/check_backend_first_wiring_candidates.py

backend-first-wiring-candidates-report:
	PYTHONPATH=. python3 scripts/generate_backend_first_wiring_candidates_report.py

backend-implementation-391-400-full-check: backend-first-wiring-candidates-check backend-first-wiring-candidates-report backend-implementation-383-390-full-check backend-implementation-376-382-full-check
	pytest -c pytest.ini tests/unit/test_backend_first_wiring_candidates.py -q --no-cov

.PHONY: backend-runtime-enablement-guard backend-destructive-action-blocklist-check backend-runtime-enablement-report backend-runtime-enablement-full-check

backend-runtime-enablement-guard:
	PYTHONPATH=. python3 scripts/check_backend_runtime_enablement_guard.py

backend-destructive-action-blocklist-check:
	PYTHONPATH=. python3 scripts/check_backend_destructive_action_blocklist.py

backend-runtime-enablement-report:
	PYTHONPATH=. python3 scripts/generate_backend_runtime_enablement_report.py

backend-runtime-enablement-full-check: backend-runtime-enablement-guard backend-destructive-action-blocklist-check backend-runtime-enablement-report backend-implementation-391-400-full-check backend-implementation-383-390-full-check
	pytest -c pytest.ini tests/unit/test_backend_runtime_enablement_pack.py -q --no-cov

.PHONY: first-audit-runtime-wiring-check first-audit-runtime-wiring-no-destructive-actions first-audit-runtime-wiring-report backend-implementation-421-430-full-check

first-audit-runtime-wiring-check:
	PYTHONPATH=. python3 scripts/check_first_audit_runtime_wiring.py

first-audit-runtime-wiring-no-destructive-actions:
	PYTHONPATH=. python3 scripts/check_first_audit_runtime_wiring_no_destructive_actions.py

first-audit-runtime-wiring-report:
	PYTHONPATH=. python3 scripts/generate_first_audit_runtime_wiring_report.py

backend-implementation-421-430-full-check: first-audit-runtime-wiring-check first-audit-runtime-wiring-no-destructive-actions first-audit-runtime-wiring-report backend-runtime-enablement-full-check backend-implementation-391-400-full-check
	pytest -c pytest.ini tests/unit/test_first_audit_runtime_wiring.py -q --no-cov

.PHONY: first-consent-deep-readiness-runtime-wiring-check runtime-wiring-no-destructive-actions runtime-wiring-431-450-report backend-implementation-431-450-full-check

first-consent-deep-readiness-runtime-wiring-check:
	PYTHONPATH=. python3 scripts/check_first_consent_and_deep_readiness_runtime_wiring.py

runtime-wiring-no-destructive-actions:
	PYTHONPATH=. python3 scripts/check_runtime_wiring_no_destructive_actions.py

runtime-wiring-431-450-report:
	PYTHONPATH=. python3 scripts/generate_runtime_wiring_431_450_report.py

backend-implementation-431-450-full-check: first-consent-deep-readiness-runtime-wiring-check runtime-wiring-no-destructive-actions runtime-wiring-431-450-report backend-implementation-421-430-full-check backend-runtime-enablement-full-check
	pytest -c pytest.ini tests/unit/test_consent_deep_readiness_runtime_wiring.py -q --no-cov

.PHONY: backend-runtime-integration-readiness-check backend-runtime-integration-blocklists-check backend-runtime-integration-readiness-report backend-runtime-integration-readiness-full-check

backend-runtime-integration-readiness-check:
	PYTHONPATH=. python3 scripts/check_backend_runtime_integration_readiness.py

backend-runtime-integration-blocklists-check:
	PYTHONPATH=. python3 scripts/check_backend_runtime_integration_blocklists.py

backend-runtime-integration-readiness-report:
	PYTHONPATH=. python3 scripts/generate_backend_runtime_integration_readiness_report.py

backend-runtime-integration-readiness-full-check: backend-runtime-integration-readiness-check backend-runtime-integration-blocklists-check backend-runtime-integration-readiness-report backend-implementation-431-450-full-check backend-implementation-421-430-full-check
	pytest -c pytest.ini tests/unit/test_backend_runtime_integration_readiness.py -q --no-cov
.PHONY: real-audit-runtime-integration-wire real-audit-runtime-integration-check backend-implementation-481-490-full-check
real-audit-runtime-integration-wire:
	PYTHONPATH=. python3 scripts/wire_real_audit_runtime_path.py
real-audit-runtime-integration-check:
	PYTHONPATH=. python3 scripts/check_real_audit_runtime_integration.py
backend-implementation-481-490-full-check: real-audit-runtime-integration-check
	pytest -c pytest.ini tests/unit/test_real_audit_runtime_facade.py -q --no-cov
.PHONY: real-consent-runtime-repair real-consent-runtime-repair-check backend-implementation-491-500-full-check
real-consent-runtime-repair:
	PYTHONPATH=. python3 scripts/repair_real_consent_runtime_seams.py
real-consent-runtime-repair-check:
	PYTHONPATH=. python3 scripts/check_real_consent_runtime_repair.py
backend-implementation-491-500-full-check: real-consent-runtime-repair-check
	pytest -c pytest.ini tests/unit/test_real_consent_runtime_facade.py -q --no-cov
.PHONY: readonly-deep-readiness-wire readonly-deep-readiness-check backend-implementation-501-510-full-check
readonly-deep-readiness-wire:
	PYTHONPATH=. python3 scripts/wire_readonly_deep_readiness_route.py
readonly-deep-readiness-check:
	PYTHONPATH=. python3 scripts/check_readonly_deep_readiness_runtime.py
backend-implementation-501-510-full-check: readonly-deep-readiness-check
	pytest -c pytest.ini tests/unit/test_readonly_deep_readiness_runtime.py -q --no-cov
.PHONY: disposable-db-schema-proof-execute disposable-db-schema-proof-execution-check backend-implementation-511-520-full-check
disposable-db-schema-proof-execute:
	PYTHONPATH=. python3 scripts/execute_disposable_db_schema_proof.py
disposable-db-schema-proof-execution-check:
	PYTHONPATH=. python3 scripts/check_disposable_db_schema_proof_execution.py
backend-implementation-511-520-full-check: disposable-db-schema-proof-execute disposable-db-schema-proof-execution-check
	pytest -c pytest.ini tests/unit/test_disposable_db_schema_proof_execution.py -q --no-cov
.PHONY: post-migration-cleanup post-migration-cleanup-check backend-implementation-521-530-full-check
post-migration-cleanup:
	PYTHONPATH=. python3 scripts/remove_proven_dead_backend_consolidation_artifacts.py
post-migration-cleanup-check:
	PYTHONPATH=. python3 scripts/check_post_migration_cleanup.py
backend-implementation-521-530-full-check: post-migration-cleanup post-migration-cleanup-check
	pytest -c pytest.ini tests/unit/test_post_migration_cleanup.py -q --no-cov

.PHONY: roadmap-reconciliation-check readme-ci-badge-patch docker-production-hardening-patch docker-production-hardening-check warning-integrity-check popia-sweep-evidence beta-content-threshold-check beta-content-threshold-schema-check auth-hardening-status backend-implementation-531-560-full-check

roadmap-reconciliation-check:
	PYTHONPATH=. python3 scripts/reconcile_agent_roadmap.py

readme-ci-badge-patch:
	PYTHONPATH=. python3 scripts/patch_readme_ci_badge.py

docker-production-hardening-patch:
	PYTHONPATH=. python3 scripts/harden_docker_compose.py

docker-production-hardening-check:
	PYTHONPATH=. python3 scripts/check_docker_production_hardening.py

warning-integrity-check:
	PYTHONPATH=. python3 scripts/run_warning_integrity_check.py

popia-sweep-evidence:
	PYTHONPATH=. python3 scripts/run_popia_sweep_evidence.py

beta-content-threshold-check:
	PYTHONPATH=. python3 scripts/check_beta_content_threshold.py

beta-content-threshold-schema-check:
	PYTHONPATH=. python3 scripts/check_beta_content_threshold_schema.py

auth-hardening-status:
	PYTHONPATH=. python3 scripts/check_auth_hardening_status.py

backend-implementation-531-560-full-check: roadmap-reconciliation-check readme-ci-badge-patch docker-production-hardening-patch docker-production-hardening-check auth-hardening-status beta-content-threshold-schema-check
	pytest -c pytest.ini tests/unit/test_roadmap_production_hardening.py -q --no-cov

.PHONY: remote-ci-evidence-capture branch-protection-evidence-capture beta-content-hard-gate staging-smoke-finalize backup-drill-evidence restore-drill-evidence rollback-drill-evidence alertmanager-drill-evidence beta-readiness-status release-owner-beta-go-no-go beta-evidence-schema-check backend-implementation-561-580-full-check

remote-ci-evidence-capture:
	PYTHONPATH=. python3 scripts/capture_remote_ci_evidence.py

branch-protection-evidence-capture:
	PYTHONPATH=. python3 scripts/capture_branch_protection_evidence.py

beta-content-hard-gate:
	PYTHONPATH=. python3 scripts/enforce_beta_content_gate.py

staging-smoke-finalize:
	PYTHONPATH=. python3 scripts/finalize_staging_smoke_evidence.py

backup-drill-evidence:
	OPERATIONAL_DRILL=backup PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py

restore-drill-evidence:
	OPERATIONAL_DRILL=restore PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py

rollback-drill-evidence:
	OPERATIONAL_DRILL=rollback PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py

alertmanager-drill-evidence:
	OPERATIONAL_DRILL=alertmanager PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py

beta-readiness-status:
	PYTHONPATH=. python3 scripts/generate_beta_readiness_status.py

release-owner-beta-go-no-go:
	PYTHONPATH=. python3 scripts/generate_release_owner_beta_go_no_go.py

beta-evidence-schema-check:
	PYTHONPATH=. python3 scripts/check_evidence_json_schema.py docs/release/ci_evidence.json docs/release/branch_protection_evidence.json docs/beta/beta_content_hard_gate.json docs/release/staging_smoke_final_evidence.json docs/release/beta_readiness_status.json

backend-implementation-561-580-full-check:
	PYTHONPATH=. python3 scripts/capture_remote_ci_evidence.py || true
	PYTHONPATH=. python3 scripts/capture_branch_protection_evidence.py || true
	PYTHONPATH=. python3 scripts/enforce_beta_content_gate.py || true
	PYTHONPATH=. python3 scripts/finalize_staging_smoke_evidence.py || true
	OPERATIONAL_DRILL=backup PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py || true
	OPERATIONAL_DRILL=restore PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py || true
	OPERATIONAL_DRILL=rollback PYTHONPATH=. python3 scripts/capture_operational_drill_evidence.py || true
	PYTHONPATH=. python3 scripts/generate_beta_readiness_status.py || true
	PYTHONPATH=. python3 scripts/generate_release_owner_beta_go_no_go.py
	PYTHONPATH=. python3 scripts/check_evidence_json_schema.py docs/release/ci_evidence.json docs/release/branch_protection_evidence.json docs/beta/beta_content_hard_gate.json docs/release/staging_smoke_final_evidence.json docs/release/backup_drill_evidence.json docs/release/restore_drill_evidence.json docs/release/rollback_drill_evidence.json docs/release/beta_readiness_status.json
	pytest -c pytest.ini tests/unit/test_beta_evidence_release_gating.py -q --no-cov

.PHONY: beta-evidence-integrity-repair truthful-beta-readiness-status truthful-release-owner-beta-go-no-go beta-evidence-integrity-check backend-implementation-581-590-full-check

beta-evidence-integrity-repair:
	PYTHONPATH=. python3 scripts/repair_beta_evidence_integrity.py

truthful-beta-readiness-status:
	PYTHONPATH=. python3 scripts/generate_truthful_beta_readiness_status.py

truthful-release-owner-beta-go-no-go:
	PYTHONPATH=. python3 scripts/generate_truthful_release_owner_beta_go_no_go.py

beta-evidence-integrity-check:
	PYTHONPATH=. python3 scripts/check_beta_evidence_integrity.py

backend-implementation-581-590-full-check: beta-evidence-integrity-repair truthful-release-owner-beta-go-no-go beta-evidence-integrity-check
	PYTHONPATH=. python3 scripts/generate_truthful_beta_readiness_status.py || true
	PYTHONPATH=. python3 scripts/generate_truthful_release_owner_beta_go_no_go.py
	pytest -c pytest.ini tests/unit/test_beta_evidence_integrity_repair.py -q --no-cov

.PHONY: popia-consent-lifecycle-inspect popia-consent-lifecycle-repair popia-consent-lifecycle-check backend-implementation-591-610-full-check

popia-consent-lifecycle-inspect:
	PYTHONPATH=. python3 scripts/inspect_popia_consent_lifecycle.py

popia-consent-lifecycle-repair:
	PYTHONPATH=. python3 scripts/repair_popia_consent_lifecycle.py

popia-consent-lifecycle-check:
	PYTHONPATH=. python3 scripts/check_popia_consent_lifecycle_repair.py

backend-implementation-591-610-full-check: popia-consent-lifecycle-inspect popia-consent-lifecycle-repair popia-consent-lifecycle-check
	python3 -m compileall -q app/api_v2_routers app/modules/consent app/services app/repositories
	pytest -c pytest.ini tests/unit/test_popia_consent_lifecycle_contracts.py -q --no-cov --tb=short

.PHONY: lesson-object-authorization-inspect lesson-object-authorization-repair lesson-object-authorization-check backend-implementation-611-630-full-check

lesson-object-authorization-inspect:
	PYTHONPATH=. python3 scripts/inspect_lesson_object_authorization.py

lesson-object-authorization-repair:
	PYTHONPATH=. python3 scripts/repair_lesson_object_authorization.py

lesson-object-authorization-check:
	PYTHONPATH=. python3 scripts/check_lesson_object_authorization_repair.py

backend-implementation-611-630-full-check: lesson-object-authorization-inspect lesson-object-authorization-repair lesson-object-authorization-check
	python3 -m compileall -q app/api_v2_routers app/modules/lessons app/services app/repositories
	pytest -c pytest.ini tests/unit/test_lesson_object_authorization_contracts.py -q --no-cov --tb=short

.PHONY: auth-token-claims-inspect auth-token-claims-repair auth-token-claims-check backend-implementation-631-650-full-check

auth-token-claims-inspect:
	PYTHONPATH=. python3 scripts/inspect_auth_token_claims.py

auth-token-claims-repair:
	PYTHONPATH=. python3 scripts/repair_auth_token_claims.py

auth-token-claims-check:
	PYTHONPATH=. python3 scripts/check_auth_token_claims_repair.py

backend-implementation-631-650-full-check: auth-token-claims-inspect auth-token-claims-repair auth-token-claims-check
	python3 -m compileall -q app/api_v2_routers app/services app/modules/auth app/repositories
	pytest -c pytest.ini tests/unit/test_auth_token_claims_contracts.py -q --no-cov --tb=short

.PHONY: popia-router-boundary-repair router-boundary-matrix router-boundary-check import-linter-availability service-boundary-inventory legacy-learner-access-guard-report backend-implementation-651-670-full-check

popia-router-boundary-repair:
	PYTHONPATH=. python3 scripts/patch_popia_router_boundary.py

router-boundary-matrix:
	PYTHONPATH=. python3 scripts/generate_router_boundary_matrix.py

router-boundary-check:
	PYTHONPATH=. python3 scripts/check_router_boundary_enforcement.py

import-linter-availability:
	PYTHONPATH=. python3 scripts/check_import_linter_availability.py

service-boundary-inventory:
	PYTHONPATH=. python3 scripts/generate_service_boundary_inventory.py

legacy-learner-access-guard-report:
	PYTHONPATH=. python3 scripts/generate_legacy_learner_access_guard_report.py

backend-implementation-651-670-full-check: popia-router-boundary-repair router-boundary-check import-linter-availability service-boundary-inventory legacy-learner-access-guard-report
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services app/repositories
	pytest -c pytest.ini tests/unit/test_boundary_enforcement_contracts.py -q --no-cov --tb=short

.PHONY: service-family-map router-service-dependency-map architecture-boundary-contracts-check import-linter-contracts-run backend-implementation-671-690-full-check

service-family-map:
	PYTHONPATH=. python3 scripts/generate_service_family_map.py

router-service-dependency-map:
	PYTHONPATH=. python3 scripts/generate_router_service_dependency_map.py

architecture-boundary-contracts-check:
	PYTHONPATH=. python3 scripts/check_architecture_boundary_contracts.py

import-linter-contracts-run:
	PYTHONPATH=. python3 scripts/run_import_linter_contracts.py

backend-implementation-671-690-full-check: service-family-map router-service-dependency-map architecture-boundary-contracts-check import-linter-contracts-run
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services scripts
	pytest -c pytest.ini tests/unit/test_architecture_boundary_contracts.py -q --no-cov --tb=short

.PHONY: diagnostics-jobs-integrity-inspect diagnostics-data-integrity-repair arq-consent-job-repair diagnostics-jobs-integrity-check backend-implementation-691-720-full-check

diagnostics-jobs-integrity-inspect:
	PYTHONPATH=. python3 scripts/inspect_diagnostics_and_jobs_integrity.py

diagnostics-data-integrity-repair:
	PYTHONPATH=. python3 scripts/repair_diagnostics_data_integrity.py

arq-consent-job-repair:
	PYTHONPATH=. python3 scripts/repair_arq_consent_reminder_job.py

diagnostics-jobs-integrity-check:
	PYTHONPATH=. python3 scripts/check_diagnostics_jobs_integrity.py

backend-implementation-691-720-full-check: diagnostics-jobs-integrity-inspect diagnostics-data-integrity-repair arq-consent-job-repair diagnostics-jobs-integrity-check
	python3 -m compileall -q app/api_v2_routers app/modules app/services scripts
	pytest -c pytest.ini tests/unit/test_diagnostics_jobs_integrity_contracts.py -q --no-cov --tb=short

.PHONY: auth-router-boundary-inspect auth-router-boundary-repair auth-router-boundary-check auth-boundary-debt-report backend-implementation-721-750-full-check

auth-router-boundary-inspect:
	PYTHONPATH=. python3 scripts/inspect_auth_router_boundary.py

auth-router-boundary-repair:
	PYTHONPATH=. python3 scripts/repair_auth_router_boundary.py

auth-router-boundary-check:
	PYTHONPATH=. python3 scripts/check_auth_router_boundary.py

auth-boundary-debt-report:
	PYTHONPATH=. python3 scripts/generate_auth_boundary_debt_report.py

backend-implementation-721-750-full-check: auth-router-boundary-inspect auth-router-boundary-repair auth-router-boundary-check auth-boundary-debt-report
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services scripts
	pytest -c pytest.ini tests/unit/test_auth_router_boundary_contracts.py -q --no-cov --tb=short

.PHONY: jwt-rotation-inspect jwt-rotation-repair jwt-rotation-check dependency-pin-report dependency-constraints-snapshot optional-pip-audit auth-extraction-followup backend-implementation-751-780-full-check

jwt-rotation-inspect:
	PYTHONPATH=. python3 scripts/inspect_jwt_rotation.py

jwt-rotation-repair:
	PYTHONPATH=. python3 scripts/repair_jwt_rotation.py

jwt-rotation-check:
	PYTHONPATH=. python3 scripts/check_jwt_rotation.py

dependency-pin-report:
	PYTHONPATH=. python3 scripts/generate_dependency_pin_report.py || true

dependency-constraints-snapshot:
	PYTHONPATH=. python3 scripts/generate_constraints_snapshot.py

optional-pip-audit:
	PYTHONPATH=. python3 scripts/run_optional_pip_audit.py || true

auth-extraction-followup:
	PYTHONPATH=. python3 scripts/generate_auth_extraction_followup.py

backend-implementation-751-780-full-check: jwt-rotation-inspect jwt-rotation-repair jwt-rotation-check dependency-pin-report dependency-constraints-snapshot optional-pip-audit auth-extraction-followup
	python3 -m compileall -q app/services app/core scripts
	pytest -c pytest.ini tests/unit/test_jwt_rotation_dependency_security.py -q --no-cov --tb=short

.PHONY: runtime-blockers-followup-repair runtime-blockers-followup-check backend-implementation-781-830-full-check

runtime-blockers-followup-repair:
	PYTHONPATH=. python3 scripts/repair_runtime_blockers_after_followup_audit.py

runtime-blockers-followup-check:
	PYTHONPATH=. python3 scripts/check_runtime_blockers_after_followup_audit.py

backend-implementation-781-830-full-check: runtime-blockers-followup-repair runtime-blockers-followup-check
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/modules app/services scripts
	pytest -c pytest.ini tests/unit/test_runtime_blockers_after_followup_audit.py -q --no-cov --tb=short

.PHONY: runtime-integration-proof-report runtime-integration-proof-check popia-lifecycle-integration-test diagnostics-db-integrity-proof-test backend-implementation-831-870-full-check

runtime-integration-proof-report:
	PYTHONPATH=. python3 scripts/generate_runtime_integration_proof_reports.py

runtime-integration-proof-check:
	PYTHONPATH=. python3 scripts/check_runtime_integration_proof.py

popia-lifecycle-integration-test:
	pytest -c pytest.ini tests/integration/test_popia_lifecycle_runtime_contract.py -q --no-cov --tb=short

diagnostics-db-integrity-proof-test:
	pytest -c pytest.ini tests/integration/test_diagnostics_db_integrity_proof.py -q --no-cov --tb=short

backend-implementation-831-870-full-check: runtime-integration-proof-report runtime-integration-proof-check popia-lifecycle-integration-test diagnostics-db-integrity-proof-test
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/modules app/services scripts tests
	pytest -c pytest.ini tests/unit/test_runtime_integration_proof_contracts.py -q --no-cov --tb=short

.PHONY: auth-forward-refs-repair auth-forward-refs-check backend-implementation-831-870R-forward-ref-check

auth-forward-refs-repair:
	PYTHONPATH=. python3 scripts/repair_auth_forward_refs.py

auth-forward-refs-check:
	PYTHONPATH=. python3 scripts/check_auth_forward_refs.py

backend-implementation-831-870R-forward-ref-check: auth-forward-refs-repair auth-forward-refs-check
	python3 -m compileall -q app/api_v2_routers/auth.py scripts/repair_auth_forward_refs.py scripts/check_auth_forward_refs.py
	pytest -c pytest.ini tests/unit/test_auth_forward_ref_import_contract.py -q --no-cov --tb=short

.PHONY: auth-service-extraction-repair auth-service-extraction-check auth-service-extraction-report backend-implementation-871-910-full-check

auth-service-extraction-repair:
	PYTHONPATH=. python3 scripts/repair_auth_service_extraction.py

auth-service-extraction-check:
	PYTHONPATH=. python3 scripts/check_auth_service_extraction.py

auth-service-extraction-report:
	PYTHONPATH=. python3 scripts/generate_auth_service_extraction_report.py

backend-implementation-871-910-full-check: auth-service-extraction-repair auth-service-extraction-check auth-service-extraction-report
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services scripts tests/unit/test_auth_service_extraction_contracts.py
	pytest -c pytest.ini tests/unit/test_auth_service_extraction_contracts.py -q --no-cov --tb=short

.PHONY: auth-lifecycle-method-extraction-repair auth-lifecycle-method-extraction-check auth-lifecycle-extraction-report auth-lifecycle-method-tests auth-lifecycle-route-registration-tests backend-implementation-911-950-full-check

auth-lifecycle-method-extraction-repair:
	PYTHONPATH=. python3 scripts/repair_auth_lifecycle_method_extraction.py

auth-lifecycle-method-extraction-check:
	PYTHONPATH=. python3 scripts/check_auth_lifecycle_method_extraction.py

auth-lifecycle-extraction-report:
	PYTHONPATH=. python3 scripts/generate_auth_lifecycle_extraction_report.py

auth-lifecycle-method-tests:
	pytest -c pytest.ini tests/unit/test_auth_lifecycle_service_methods.py -q --no-cov --tb=short

auth-lifecycle-route-registration-tests:
	pytest -c pytest.ini tests/integration/test_auth_lifecycle_route_registration.py -q --no-cov --tb=short

backend-implementation-911-950-full-check: auth-lifecycle-method-extraction-repair auth-lifecycle-method-extraction-check auth-lifecycle-extraction-report auth-lifecycle-method-tests auth-lifecycle-route-registration-tests
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services scripts tests
	python3 -m ruff check app/api_v2_routers/auth.py app/services/auth_application_service.py app/api_v2_deps/auth_service.py --select F821,F401,F811,E402

.PHONY: auth-service-ownership-migrate auth-service-ownership-check auth-service-ownership-report auth-service-ownership-tests auth-lifecycle-http-non-500-tests backend-implementation-951-990-full-check

auth-service-ownership-migrate:
	PYTHONPATH=. python3 scripts/migrate_auth_lifecycle_helpers_to_service.py

auth-service-ownership-check:
	PYTHONPATH=. python3 scripts/check_auth_service_ownership.py

auth-service-ownership-report:
	PYTHONPATH=. python3 scripts/generate_auth_service_ownership_report.py

auth-service-ownership-tests:
	pytest -c pytest.ini tests/unit/test_auth_service_ownership_contracts.py -q --no-cov --tb=short

auth-lifecycle-http-non-500-tests:
	pytest -c pytest.ini tests/integration/test_auth_lifecycle_http_non_500.py -q --no-cov --tb=short

backend-implementation-951-990-full-check: auth-service-ownership-migrate auth-service-ownership-check auth-service-ownership-report auth-service-ownership-tests auth-lifecycle-http-non-500-tests
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services scripts tests
	python3 -m ruff check app/api_v2_routers/auth.py app/services/auth_application_service.py app/services/auth_lifecycle_impl.py app/api_v2_deps/auth_service.py --select F821,F401,F811,E402

.PHONY: auth-http-success-scope-report auth-http-success-scope-test auth-http-success-scope-check auth-http-success-scope-contracts backend-implementation-991-1030-full-check

auth-http-success-scope-report:
	PYTHONPATH=. python3 scripts/generate_auth_http_success_scope_report.py

auth-http-success-scope-test:
	pytest -c pytest.ini tests/integration/test_auth_lifecycle_http_success_scope.py -q --no-cov --tb=short

auth-http-success-scope-check:
	PYTHONPATH=. python3 scripts/check_auth_http_success_scope.py

auth-http-success-scope-contracts:
	pytest -c pytest.ini tests/unit/test_auth_http_success_scope_contracts.py -q --no-cov --tb=short

backend-implementation-991-1030-full-check: auth-http-success-scope-report auth-http-success-scope-check auth-http-success-scope-contracts
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers app/services scripts tests
	python3 -m ruff check app/api_v2_routers/auth.py app/services/auth_application_service.py app/services/auth_lifecycle_impl.py app/api_v2_deps/auth_service.py tests/integration/test_auth_lifecycle_http_success_scope.py --select F821,F401,F811,E402

.PHONY: auth-db-lifecycle-proof-report auth-db-lifecycle-proof-test auth-db-lifecycle-proof-check auth-db-lifecycle-proof-contracts backend-implementation-1031-1070-full-check

auth-db-lifecycle-proof-report:
	PYTHONPATH=. python3 scripts/generate_auth_db_lifecycle_proof_report.py

auth-db-lifecycle-proof-test:
	pytest -c pytest.ini tests/integration/test_auth_transactional_db_lifecycle_proof.py -q --no-cov --tb=short

auth-db-lifecycle-proof-check:
	PYTHONPATH=. python3 scripts/check_auth_db_lifecycle_proof.py

auth-db-lifecycle-proof-contracts:
	pytest -c pytest.ini tests/unit/test_auth_db_lifecycle_proof_contracts.py -q --no-cov --tb=short

backend-implementation-1031-1070-full-check: auth-db-lifecycle-proof-report auth-db-lifecycle-proof-check auth-db-lifecycle-proof-contracts
	python3 -m compileall -q app/services scripts tests
	python3 -m ruff check app/services/auth_db_lifecycle_proof.py scripts/generate_auth_db_lifecycle_proof_report.py scripts/check_auth_db_lifecycle_proof.py tests/integration/test_auth_transactional_db_lifecycle_proof.py tests/unit/test_auth_db_lifecycle_proof_contracts.py --select F821,F401,F811,E402

.PHONY: jwt-production-guard-repair jwt-production-guard-test jwt-production-guard-check backend-implementation-1071-1110-full-check

jwt-production-guard-repair:
	PYTHONPATH=. python3 scripts/repair_jwt_production_guard.py

jwt-production-guard-test:
	pytest -c pytest.ini tests/unit/test_jwt_keyring_production_guard.py -q --no-cov --tb=short

jwt-production-guard-check:
	PYTHONPATH=. python3 scripts/check_jwt_production_guard.py

backend-implementation-1071-1110-full-check: jwt-production-guard-repair jwt-production-guard-check
	python3 -m compileall -q app/services app/core scripts tests
	python3 -m ruff check app/services/jwt_keyring.py scripts/repair_jwt_production_guard.py scripts/check_jwt_production_guard.py tests/unit/test_jwt_keyring_production_guard.py --select F821,F401,F811,E402

.PHONY: arq-dependency-worker-repair arq-worker-import-test arq-worker-import-check backend-implementation-1111-1150-full-check

arq-dependency-worker-repair:
	PYTHONPATH=. python3 scripts/repair_arq_dependency_worker_import.py

arq-worker-import-test:
	pytest -c pytest.ini tests/unit/test_arq_worker_import_contract.py -q --no-cov --tb=short

arq-worker-import-check:
	PYTHONPATH=. python3 scripts/check_arq_worker_import.py

backend-implementation-1111-1150-full-check: arq-dependency-worker-repair arq-worker-import-check
	python3 -m compileall -q app/services app/modules scripts tests
	python3 -m ruff check app/services/arq_import_compat.py app/services/job_dependency_factory.py app/modules/jobs.py scripts/repair_arq_dependency_worker_import.py scripts/check_arq_worker_import.py tests/unit/test_arq_worker_import_contract.py --select F821,F401,F811,E402

.PHONY: popia-lifecycle-response-contract-test popia-lifecycle-response-contract-check backend-implementation-1151-1190-full-check

popia-lifecycle-response-contract-test:
	pytest -c pytest.ini tests/integration/test_popia_lifecycle_response_contract.py tests/unit/test_popia_lifecycle_response_contracts.py -q --no-cov --tb=short

popia-lifecycle-response-contract-check:
	PYTHONPATH=. python3 scripts/check_popia_lifecycle_response_contract.py

backend-implementation-1151-1190-full-check: popia-lifecycle-response-contract-check
	python3 -m compileall -q app/services app/api_v2_routers scripts tests
	python3 -m ruff check app/services/popia_consent_lifecycle_adapter.py app/api_v2_routers/popia.py scripts/check_popia_lifecycle_response_contract.py tests/integration/test_popia_lifecycle_response_contract.py tests/unit/test_popia_lifecycle_response_contracts.py --select F821,F401,F811,E402

.PHONY: evidence-status-registry-check evidence-status-registry-test pytest-skip-inventory backend-implementation-1191-1230-full-check

evidence-status-registry-check:
	PYTHONPATH=. python3 scripts/check_evidence_status_registry.py

evidence-status-registry-test:
	pytest -c pytest.ini tests/unit/test_evidence_status_registry.py -q --no-cov --tb=short

pytest-skip-inventory:
	PYTHONPATH=. python3 scripts/record_pytest_skip_inventory.py --write-evidence

backend-implementation-1191-1230-full-check: evidence-status-registry-check evidence-status-registry-test
	python3 -m compileall -q scripts tests
	python3 -m ruff check scripts/evidence_registry.py scripts/check_evidence_status_registry.py scripts/record_pytest_skip_inventory.py tests/unit/test_evidence_status_registry.py --select F821,F401,F811,E402

.PHONY: diagnostics-session-binding-repair diagnostics-session-binding-test diagnostics-session-binding-check backend-implementation-1231-1270-full-check

diagnostics-session-binding-repair:
	PYTHONPATH=. python3 scripts/patch_diagnostics_session_binding.py

diagnostics-session-binding-test:
	pytest -c pytest.ini tests/unit/test_diagnostic_route_integrity.py tests/integration/test_diagnostics_session_binding_routes.py -q --no-cov --tb=short

diagnostics-session-binding-check:
	PYTHONPATH=. python3 scripts/check_diagnostics_session_binding.py

backend-implementation-1231-1270-full-check: diagnostics-session-binding-repair diagnostics-session-binding-check diagnostics-session-binding-test
	python3 -m compileall -q app/services app/api_v2_routers scripts tests
	python3 -m ruff check app/services/diagnostic_route_integrity.py app/services/diagnostic_session_integrity.py app/api_v2_routers/diagnostics.py scripts/patch_diagnostics_session_binding.py scripts/check_diagnostics_session_binding.py tests/unit/test_diagnostic_route_integrity.py tests/integration/test_diagnostics_session_binding_routes.py --select F821,F401,F811,E402

.PHONY: auth-repository-fixture-repair auth-repository-fixture-proof-test auth-repository-fixture-proof-check backend-implementation-1271-1310-full-check

auth-repository-fixture-repair:
	PYTHONPATH=. python3 scripts/repair_auth_repository_fixture_proof.py

auth-repository-fixture-proof-test:
	pytest -c pytest.ini tests/integration/test_auth_repository_fixture_proof.py tests/unit/test_auth_repository_fixture_proof_contracts.py -q --no-cov --tb=short

auth-repository-fixture-proof-check:
	PYTHONPATH=. python3 scripts/check_auth_repository_fixture_proof.py

backend-implementation-1271-1310-full-check: auth-repository-fixture-repair auth-repository-fixture-proof-check
	python3 -m compileall -q app/services scripts tests
	python3 -m ruff check app/services/auth_application_service.py app/services/auth_runtime_boundary.py scripts/repair_auth_repository_fixture_proof.py scripts/check_auth_repository_fixture_proof.py tests/integration/test_auth_repository_fixture_proof.py tests/unit/test_auth_repository_fixture_proof_contracts.py --select F821,F401,F811,E402

.PHONY: lesson-authorization-hardening-repair lesson-authorization-hardening-test lesson-authorization-hardening-check backend-implementation-1311-1350-full-check

lesson-authorization-hardening-repair:
	PYTHONPATH=. python3 scripts/patch_lesson_authorization_hardening.py

lesson-authorization-hardening-test:
	pytest -c pytest.ini tests/unit/test_lesson_authorization_hardening.py tests/integration/test_lesson_authorization_negative_contract.py -q --no-cov --tb=short

lesson-authorization-hardening-check:
	PYTHONPATH=. python3 scripts/check_lesson_authorization_hardening.py

backend-implementation-1311-1350-full-check: lesson-authorization-hardening-repair lesson-authorization-hardening-check lesson-authorization-hardening-test
	python3 -m compileall -q app/services app/api_v2_routers scripts tests
	python3 -m ruff check app/services/lesson_authorization.py app/api_v2_routers/lessons.py scripts/patch_lesson_authorization_hardening.py scripts/check_lesson_authorization_hardening.py tests/unit/test_lesson_authorization_hardening.py tests/integration/test_lesson_authorization_negative_contract.py --select F821,F401,F811,E402

.PHONY: diagnostics-dynamic-repository-boundary-repair diagnostics-dynamic-repository-boundary-test diagnostics-dynamic-repository-boundary-check backend-implementation-1351-1390R-full-check

diagnostics-dynamic-repository-boundary-repair:
	PYTHONPATH=. python3 scripts/patch_diagnostics_dynamic_repository_boundary.py

diagnostics-dynamic-repository-boundary-test:
	pytest -c pytest.ini tests/unit/test_diagnostics_dynamic_repository_boundary.py -q --no-cov --tb=short

diagnostics-dynamic-repository-boundary-check:
	PYTHONPATH=. python3 scripts/check_diagnostics_dynamic_repository_boundary.py

backend-implementation-1351-1390R-full-check: diagnostics-dynamic-repository-boundary-repair diagnostics-dynamic-repository-boundary-check diagnostics-dynamic-repository-boundary-test
	python3 -m compileall -q app/api_v2_deps app/api_v2_routers scripts tests
	python3 -m ruff check app/api_v2_deps/diagnostic_repositories.py app/api_v2_routers/diagnostics.py scripts/patch_diagnostics_dynamic_repository_boundary.py scripts/check_diagnostics_dynamic_repository_boundary.py tests/unit/test_diagnostics_dynamic_repository_boundary.py --select F821,F401,F811,E402

.PHONY: transaction-boundary-inventory transaction-boundary-guardrail-check transaction-boundary-guardrail-test backend-implementation-1391-1430-full-check

transaction-boundary-inventory:
	PYTHONPATH=. python3 scripts/transaction_boundary_inventory.py

transaction-boundary-guardrail-check:
	PYTHONPATH=. python3 scripts/check_transaction_boundary_guardrails.py

transaction-boundary-guardrail-test:
	pytest -c pytest.ini tests/unit/test_transaction_boundary_guardrails.py -q --no-cov --tb=short

backend-implementation-1391-1430-full-check: transaction-boundary-inventory transaction-boundary-guardrail-check transaction-boundary-guardrail-test
	python3 -m compileall -q scripts tests
	python3 -m ruff check scripts/transaction_boundary_inventory.py scripts/check_transaction_boundary_guardrails.py tests/unit/test_transaction_boundary_guardrails.py --select F821,F401,F811,E402

.PHONY: popia-transaction-rollback-proof-test popia-transaction-rollback-proof-check backend-implementation-1431-1470-full-check

popia-transaction-rollback-proof-test:
	pytest -c pytest.ini tests/integration/test_popia_transaction_rollback_proof.py tests/unit/test_popia_transactional_lifecycle_contracts.py -q --no-cov --tb=short

popia-transaction-rollback-proof-check:
	PYTHONPATH=. python3 scripts/check_popia_transaction_rollback_proof.py

backend-implementation-1431-1470-full-check: popia-transaction-rollback-proof-check popia-transaction-rollback-proof-test
	python3 -m compileall -q app/services scripts tests
	python3 -m ruff check app/services/popia_transactional_lifecycle.py scripts/check_popia_transaction_rollback_proof.py tests/integration/test_popia_transaction_rollback_proof.py tests/unit/test_popia_transactional_lifecycle_contracts.py --select F821,F401,F811,E402

.PHONY: auth-transaction-rollback-proof-test auth-transaction-rollback-proof-check backend-implementation-1471-1510-full-check

auth-transaction-rollback-proof-test:
	pytest -c pytest.ini tests/integration/test_auth_transaction_rollback_proof.py tests/unit/test_auth_transactional_registration_contracts.py -q --no-cov --tb=short

auth-transaction-rollback-proof-check:
	PYTHONPATH=. python3 scripts/check_auth_transaction_rollback_proof.py

backend-implementation-1471-1510-full-check: auth-transaction-rollback-proof-test auth-transaction-rollback-proof-check
	python3 -m compileall -q app/services scripts tests
	python3 -m ruff check app/services/auth_transactional_registration.py scripts/check_auth_transaction_rollback_proof.py tests/integration/test_auth_transaction_rollback_proof.py tests/unit/test_auth_transactional_registration_contracts.py --select F821,F401,F811,E402

.PHONY: diagnostics-transaction-rollback-proof-test diagnostics-transaction-rollback-proof-check backend-implementation-1511-1550-full-check

diagnostics-transaction-rollback-proof-test:
	pytest -c pytest.ini tests/integration/test_diagnostics_transaction_rollback_proof.py tests/unit/test_diagnostic_transactional_response_contracts.py -q --no-cov --tb=short

diagnostics-transaction-rollback-proof-check:
	PYTHONPATH=. python3 scripts/check_diagnostics_transaction_rollback_proof.py

backend-implementation-1511-1550-full-check: diagnostics-transaction-rollback-proof-test diagnostics-transaction-rollback-proof-check
	python3 -m compileall -q app/services scripts tests
	python3 -m ruff check app/services/diagnostic_transactional_response.py scripts/check_diagnostics_transaction_rollback_proof.py tests/integration/test_diagnostics_transaction_rollback_proof.py tests/unit/test_diagnostic_transactional_response_contracts.py --select F821,F401,F811,E402

.PHONY: lesson-gamification-transaction-rollback-proof-test lesson-gamification-transaction-rollback-proof-check backend-implementation-1551-1590-full-check

lesson-gamification-transaction-rollback-proof-test:
	pytest -c pytest.ini tests/integration/test_lesson_gamification_transaction_rollback_proof.py tests/unit/test_lesson_transactional_completion_contracts.py -q --no-cov --tb=short

lesson-gamification-transaction-rollback-proof-check:
	PYTHONPATH=. python3 scripts/check_lesson_gamification_transaction_rollback_proof.py

backend-implementation-1551-1590-full-check: lesson-gamification-transaction-rollback-proof-test lesson-gamification-transaction-rollback-proof-check
	python3 -m compileall -q app/services scripts tests
	python3 -m ruff check app/services/lesson_transactional_completion.py scripts/check_lesson_gamification_transaction_rollback_proof.py tests/integration/test_lesson_gamification_transaction_rollback_proof.py tests/unit/test_lesson_transactional_completion_contracts.py --select F821,F401,F811,E402

.PHONY: transaction-rollback-rollup-report transaction-rollback-rollup-check transaction-rollback-rollup-test backend-implementation-1591-1630-full-check

transaction-rollback-rollup-report:
	PYTHONPATH=. python3 -c "from scripts.transaction_rollback_rollup import write_rollup; r = write_rollup(); print(r.status)"

transaction-rollback-rollup-check:
	PYTHONPATH=. python3 scripts/check_transaction_rollback_rollup.py

transaction-rollback-rollup-test:
	pytest -c pytest.ini tests/unit/test_transaction_rollback_rollup.py -q --no-cov --tb=short

backend-implementation-1591-1630-full-check: transaction-rollback-rollup-report transaction-rollback-rollup-check transaction-rollback-rollup-test
	python3 -m compileall -q scripts tests
	python3 -m ruff check scripts/transaction_rollback_rollup.py scripts/check_transaction_rollback_rollup.py tests/unit/test_transaction_rollback_rollup.py --select F821,F401,F811,E402

.PHONY: proof-no-skips-check diagnostics-scoring-snapshot-repair diagnostics-scoring-snapshot-test diagnostics-scoring-snapshot-check evidence-registry-commit-provenance-check backend-implementation-1631-1670-full-check

proof-no-skips-check:
	PYTHONPATH=. python3 scripts/check_popia_lifecycle_response_contract.py
	PYTHONPATH=. python3 scripts/check_diagnostics_session_binding.py

diagnostics-scoring-snapshot-repair:
	PYTHONPATH=. python3 scripts/patch_diagnostics_scoring_snapshot.py

diagnostics-scoring-snapshot-test:
	pytest -c pytest.ini tests/unit/test_diagnostics_scoring_snapshot.py tests/unit/test_proof_pytest_no_skips.py -q --no-cov --tb=short

diagnostics-scoring-snapshot-check:
	PYTHONPATH=. python3 scripts/check_diagnostics_scoring_snapshot.py

evidence-registry-commit-provenance-check:
	PYTHONPATH=. python3 scripts/check_evidence_registry_commit_provenance.py

backend-implementation-1631-1670-full-check: proof-no-skips-check diagnostics-scoring-snapshot-repair diagnostics-scoring-snapshot-test diagnostics-scoring-snapshot-check evidence-registry-commit-provenance-check
	python3 -m compileall -q app/services app/modules/diagnostics scripts tests
	python3 -m ruff check app/services/diagnostic_scoring_snapshot.py app/modules/diagnostics/diagnostic_session_service.py scripts/proof_pytest.py scripts/patch_diagnostics_scoring_snapshot.py scripts/check_diagnostics_scoring_snapshot.py scripts/check_popia_lifecycle_response_contract.py scripts/check_diagnostics_session_binding.py scripts/evidence_registry.py scripts/stamp_evidence_registry_commit.py scripts/check_evidence_registry_commit_provenance.py tests/unit/test_diagnostics_scoring_snapshot.py tests/unit/test_proof_pytest_no_skips.py tests/unit/test_evidence_registry_commit_provenance.py tests/integration/test_popia_lifecycle_response_contract.py tests/integration/test_diagnostics_session_binding_routes.py --select F821,F401,F811,E402

.PHONY: ci-authority-registry-patch ci-authority-status ci-authority-local-check ci-authority-release-check ci-authority-test backend-implementation-1671-1710-full-check

ci-authority-registry-patch:
	PYTHONPATH=. python3 scripts/patch_ci_authority_registry.py

ci-authority-status:
	PYTHONPATH=. python3 -c "from scripts.ci_authority import write_status; s = write_status(); print(s.ci_status)"

ci-authority-local-check: ci-authority-registry-patch
	PYTHONPATH=. python3 scripts/check_ci_authority.py

ci-authority-release-check:
	PYTHONPATH=. python3 scripts/check_ci_authority.py --release

ci-authority-test:
	pytest -c pytest.ini tests/unit/test_ci_authority.py -q --no-cov --tb=short

backend-implementation-1671-1710-full-check: ci-authority-status ci-authority-local-check ci-authority-test
	python3 -m compileall -q scripts tests
	python3 -m ruff check scripts/ci_authority.py scripts/patch_ci_authority_registry.py scripts/check_ci_authority.py tests/unit/test_ci_authority.py --select F821,F401,F811,E402

.PHONY: docs-inventory docs-inventory-check docs-intelligence-check docs-intelligence-test backend-implementation-1711-1750-full-check

docs-inventory:
	PYTHONPATH=. python3 scripts/docs_inventory.py --write

docs-inventory-check:
	PYTHONPATH=. python3 scripts/docs_inventory.py --check

docs-intelligence-check:
	PYTHONPATH=. python3 scripts/check_docs_intelligence.py

docs-intelligence-test:
	pytest -c pytest.ini tests/unit/test_docs_intelligence.py -q --no-cov --tb=short

backend-implementation-1711-1750-full-check: docs-inventory docs-inventory-check docs-intelligence-check docs-intelligence-test
	python3 -m compileall -q scripts tests
	python3 -m ruff check scripts/docs_inventory.py scripts/check_docs_intelligence.py tests/unit/test_docs_intelligence.py --select F821,F401,F811,E402

