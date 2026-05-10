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
