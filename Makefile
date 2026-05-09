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
