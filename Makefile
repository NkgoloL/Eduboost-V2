SHELL := /bin/bash
PYTHON ?= python3

.PHONY: help dev test lint typecheck migrate docs clean migration-check schema-integrity migration-smoke openapi openapi-check route-inventory route-inventory-check runtime-check pr002r-check phase2-authz-check

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
	@echo "  pr002r-check   - Verify PR-002R evidence bundle"
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

pr002r-check:
	$(PYTHON) scripts/check_pr002r_evidence.py

migration-check: schema-integrity
	@echo "Running migration graph and schema integrity checks"
	$(PYTHON) scripts/verify_migration_graph.py

schema-integrity:
	@echo "Validating ORM schema integrity"
	$(PYTHON) scripts/validate_schema_integrity.py

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

release-evidence-artifacts-check:
	$(PYTHON) scripts/check_release_evidence_artifacts.py

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

cluster-e-closure-check:
	$(PYTHON) scripts/check_cluster_e_closure.py

database-resilience-env-matrix-check:
	$(PYTHON) scripts/check_database_resilience_env_matrix.py

production-restore-approval-check:
	$(PYTHON) scripts/check_production_restore_approval.py

caps-alignment-contract-check:
	$(PYTHON) scripts/check_caps_alignment_contract.py

ai-safety-boundary-check:
	$(PYTHON) scripts/check_ai_safety_boundary_contract.py

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

ai-refusal-fixture-check:
	$(PYTHON) scripts/check_ai_refusal_fixtures.py

ai-prompt-secret-leakage-check:
	$(PYTHON) scripts/check_ai_prompt_secret_leakage.py

ai-fixture-coverage-check:
	$(PYTHON) scripts/check_ai_fixture_coverage_matrix.py

frontend-route-inventory:
	$(PYTHON) scripts/generate_frontend_route_inventory.py

frontend-route-inventory-check:
	$(PYTHON) scripts/check_frontend_route_inventory.py

learner-vertical-journey-contract-check:
	$(PYTHON) scripts/check_learner_vertical_journey_contract.py

cluster-g-frontend-check:
	$(PYTHON) scripts/check_cluster_g_frontend_evidence.py

parent-vertical-journey-contract-check:
	$(PYTHON) scripts/check_parent_vertical_journey_contract.py

frontend-auth-consent-denial-check:
	$(PYTHON) scripts/check_frontend_auth_consent_denial_contract.py

frontend-api-client-inventory:
	$(PYTHON) scripts/generate_frontend_api_client_inventory.py

frontend-api-client-inventory-check:
	$(PYTHON) scripts/check_frontend_api_client_inventory.py

frontend-journey-fixture-check:
	$(PYTHON) scripts/check_frontend_journey_fixtures.py

frontend-playwright-scaffold-check:
	$(PYTHON) scripts/check_frontend_playwright_scaffold.py

frontend-e2e:
	npx playwright test

frontend-playwright-specs-check:
	$(PYTHON) scripts/check_frontend_playwright_specs.py

frontend-accessibility-contract-check:
	$(PYTHON) scripts/check_frontend_accessibility_contract.py

frontend-accessibility-static-check:
	$(PYTHON) scripts/check_frontend_accessibility_static.py

frontend-runtime-inventory:
	$(PYTHON) scripts/generate_frontend_runtime_inventory.py

frontend-runtime-inventory-check:
	$(PYTHON) scripts/check_frontend_runtime_inventory.py

frontend-mock-api-fixture-check:
	$(PYTHON) scripts/check_frontend_mock_api_fixtures.py

frontend-playwright-mock-helper-check:
	$(PYTHON) scripts/check_frontend_playwright_mock_helpers.py

frontend-playwright-mocked-specs-check:
	$(PYTHON) scripts/check_frontend_playwright_mocked_specs.py

frontend-e2e-env-contract-check:
	$(PYTHON) scripts/check_frontend_e2e_environment_contract.py

frontend-e2e-mocked:
	PLAYWRIGHT_MOCK_API=1 npx playwright test tests/e2e/learner-mocked-api-journey.spec.ts tests/e2e/parent-mocked-api-journey.spec.ts

frontend-e2e-smoke:
	npx playwright test tests/e2e/learner-vertical-journey.spec.ts tests/e2e/parent-vertical-journey.spec.ts

frontend-e2e-runtime-command-check:
	$(PYTHON) scripts/check_frontend_e2e_runtime_commands.py

frontend-build-test-lint-contract-check:
	$(PYTHON) scripts/check_frontend_build_test_lint_contract.py

frontend-e2e-opt-in-workflow-check:
	$(PYTHON) scripts/check_frontend_e2e_opt_in_workflow.py

cluster-g-closure-check:
	$(PYTHON) scripts/check_cluster_g_closure.py

beta-release-readiness-contract-check:
	$(PYTHON) scripts/check_beta_release_readiness_contract.py

staging-smoke-evidence-manifest:
	$(PYTHON) scripts/generate_staging_smoke_evidence_manifest.py

staging-smoke-evidence-manifest-check:
	$(PYTHON) scripts/check_staging_smoke_evidence_manifest.py

cluster-h-release-readiness-check:
	$(PYTHON) scripts/check_cluster_h_release_readiness.py

beta-signoff-manifest:
	$(PYTHON) scripts/generate_beta_signoff_manifest.py

beta-signoff-manifest-check:
	$(PYTHON) scripts/check_beta_signoff_manifest.py

beta-rollback-runbook-check:
	$(PYTHON) scripts/check_beta_rollback_runbook.py

post-deploy-staging-smoke-checklist-check:
	$(PYTHON) scripts/check_post_deploy_staging_smoke_checklist.py
