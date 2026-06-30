#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

export APP_ENV=test
export ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-test-encryption-key}"
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:postgres@localhost:5432/eduboost_test}"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic

"$PYTHON_BIN" -m compileall -q \
  app/models/retrieval.py \
  app/services/semantic_retrieval \
  app/services/content_generation/source_context.py \
  tests/phase02

"$PYTHON_BIN" -m pytest -q tests/phase02 --ignore=tests/phase02/test_phase2_postgres_integration.py
"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" - <<'PY'
from app.models.retrieval import EMBEDDING_DIMENSIONS
from app.services.semantic_retrieval.embedding import DeterministicEmbeddingProvider
assert EMBEDDING_DIMENSIONS == 1536
assert DeterministicEmbeddingProvider.dimensions == 1536
print("Phase 2 import/dimension contract OK")
PY
