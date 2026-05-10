SHELL := /bin/bash
PYTHON ?= python3

.PHONY: help dev test lint typecheck migrate docs clean migration-check schema-integrity migration-smoke openapi openapi-check validate-items coverage-gate coverage-matrix seed-items generate-items e2e-diagnostic perf-test tag-rc phase5-gates help-item-bank

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

validate-items:
	$(PYTHON) scripts/validate_item_bank.py --path data/caps/grade4_maths_item_bank.json --fail-on-any-error

coverage-gate:
	$(PYTHON) -m pytest tests/ci/test_item_bank_coverage.py -v --tb=short

coverage-matrix:
	$(PYTHON) scripts/generate_coverage_matrix.py --output docs/caps/grade4_maths_coverage_matrix.md --db-url "$(DATABASE_URL)"

seed-items:
	$(PYTHON) scripts/seed_item_bank.py --path data/caps/grade4_maths_item_bank.json --db-url "$(DATABASE_URL)"

generate-items:
	$(PYTHON) scripts/generate_items.py --caps-ref "$(CAPS_REF)" --n-items "$(N)" --difficulty-band "$(BAND)"

e2e-diagnostic:
	npx playwright test tests/e2e/test_diagnostic_flow.spec.ts --reporter=list

perf-test:
	$(PYTHON) -m pytest tests/ci/test_item_bank_ci_jobs.py -v --tb=short -m performance -k "p99"

tag-rc:
	bash scripts/tag_release.sh $(if $(VERSION),--version $(VERSION),) $(if $(DRY_RUN),--dry-run,)

phase5-gates: validate-items coverage-gate e2e-diagnostic perf-test coverage-matrix
	@echo "All Phase 5 gates passed. Ready to run: make tag-rc"

help-item-bank:
	@echo "Item Bank targets:"
	@echo "  make validate-items"
	@echo "  make coverage-gate"
	@echo "  make coverage-matrix"
	@echo "  make seed-items"
	@echo "  make generate-items CAPS_REF=4.M.1.1 N=60 BAND=moderate"
	@echo "  make e2e-diagnostic"
	@echo "  make perf-test"
	@echo "  make tag-rc VERSION=0.7.0-rc1"
