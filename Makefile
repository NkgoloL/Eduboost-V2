SHELL := /bin/bash

.PHONY: help dev test lint typecheck migrate

help:
	@echo "Makefile targets: dev, test, lint, typecheck, migrate"

dev:
	@echo "Starting development server (uvicorn app.api_v2:app)..."
	python -m uvicorn app.api_v2:app --reload --port 8000

test:
	@echo "Running tests..."
	pytest -q

lint:
	@echo "Running linter (ruff if available, fall back to flake8)..."
	if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		flake8 . || true; \
	fi

typecheck:
	@echo "Running mypy type checks..."
	mypy . || true

migrate:
	@echo "Applying Alembic migrations (upgrade head)..."
	alembic upgrade head
# EduBoost V2 Makefile

.PHONY: help dev test lint typecheck migrate docs clean

help:
	@echo "Available commands:"
	@echo "  dev        - Start development servers (API, Frontend, Postgres, Redis)"
	@echo "  test       - Run backend tests"
	@echo "  lint       - Run linters (ruff, black)"
	@echo "  typecheck  - Run type checker (mypy)"
	@echo "  migrate    - Run database migrations"
	@echo "  docs       - Build and serve documentation"
	@echo "  clean      - Remove temporary files"

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
