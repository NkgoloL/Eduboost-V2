# EduBoost V2 Makefile

SHELL := /bin/bash
PYTHON ?= python
PYTEST ?= pytest
COMPOSE ?= docker-compose
FRONTEND_DIR ?= app/frontend
STAGING_URL ?=
STAGING_API_KEY ?=

.PHONY: help dev test lint typecheck e2e migrate migration-check schema-integrity migration-smoke docs openapi openapi-check ops-check env-check staging-smoke release-evidence security release-check smoke clean

help:
	@echo "Available commands:"
	@echo "  dev           - Start development dependencies/services with docker-compose"
	@echo "  test          - Run backend tests"
	@echo "  lint          - Run Python lint/format checks"
	@echo "  typecheck     - Run Python type checks"
	@echo "  e2e           - Run Playwright E2E tests"
	@echo "  migrate       - Apply database migrations"
	@echo "  migration-check - Verify migration graph and ORM integrity without a database"
	@echo "  schema-integrity - Verify ORM schema integrity invariants"
	@echo "  migration-smoke - Upgrade/downgrade/upgrade migration smoke test against DATABASE_URL"
	@echo "  docs          - Build MkDocs documentation"
	@echo "  openapi       - Regenerate docs/openapi.json"
	@echo "  openapi-check - Verify docs/openapi.json is current"
	@echo "  ops-check     - Validate Docker, Compose, k8s, Prometheus, alerts, and runbooks"
	@echo "  env-check     - Validate runtime environment variables"
	@echo "  staging-smoke - Run HTTP smoke checks against STAGING_URL"
	@echo "  release-evidence - Generate a local release evidence manifest"
	@echo "  security      - Run local security checks where tools are installed"
	@echo "  release-check - Run release-oriented validation gates"
	@echo "  smoke         - Run smoke tests or import checks"
	@echo "  clean         - Remove local cache files"

dev:
	$(COMPOSE) up

test:
	$(PYTEST) tests/ -v --tb=short

lint:
	ruff check app/ tests/
	black --check app/ tests/ scripts/

typecheck:
	mypy app/ --ignore-missing-imports --strict-optional

e2e:
	npm ci
	npx playwright install --with-deps chromium
	npx playwright test

migrate:
	alembic upgrade head

migration-check: schema-integrity
	$(PYTHON) scripts/verify_migration_graph.py

schema-integrity:
	$(PYTHON) scripts/validate_schema_integrity.py

migration-smoke:
	./scripts/smoke_test_migrations.sh

docs:
	mkdocs build --strict

openapi:
	$(PYTHON) scripts/generate_openapi.py --output docs/openapi.json

openapi-check:
	$(PYTHON) scripts/generate_openapi.py --output docs/openapi.json --check

ops-check:
	$(PYTHON) scripts/validate_ops_assets.py

env-check:
	$(PYTHON) scripts/validate_runtime_env.py --env $${APP_ENV:-development} --env-file $${ENV_FILE:-.env}

staging-smoke:
	@if [ -z "$(STAGING_URL)" ]; then echo "STAGING_URL is required" >&2; exit 2; fi
	$(PYTHON) scripts/staging_smoke.py --base-url "$(STAGING_URL)" --json-output reports/staging_smoke.json

release-evidence:
	$(PYTHON) scripts/build_release_evidence.py --output-dir reports/release_evidence --version $${APP_VERSION:-snapshot}

security:
	@command -v detect-secrets >/dev/null && detect-secrets scan --baseline .secrets.baseline || echo "detect-secrets not installed; skipping"
	@command -v bandit >/dev/null && bandit -r app/ -ll -ii --exclude app/tests || echo "bandit not installed; skipping"
	@command -v pip-audit >/dev/null && pip-audit -r requirements/base.txt -r requirements/ml.txt || echo "pip-audit not installed; skipping"

release-check: lint typecheck test docs openapi-check migration-check ops-check security smoke release-evidence
	@echo "Release checks completed. Review CI, migrations, frontend, POPIA, and deployment gates before tagging."

smoke:
	$(PYTHON) -c "import importlib; importlib.import_module('app.api_v2')"
	@if [ -d tests/smoke ]; then $(PYTEST) tests/smoke/ -v --tb=short; else echo "No tests/smoke directory found; import smoke completed"; fi

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

frontend-env-check:
	python scripts/validate_frontend_env.py

frontend-typecheck:
	cd app/frontend && npm run type-check

frontend-test:
	cd app/frontend && npm run test

frontend-pr-007-check:
	$(MAKE) frontend-env-check
	$(MAKE) frontend-typecheck
	$(MAKE) frontend-test
