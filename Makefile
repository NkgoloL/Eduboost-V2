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

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
