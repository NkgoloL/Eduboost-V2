#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

export APP_ENV=test
export ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}" 
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:postgres@localhost:5432/eduboost_test}"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic
export CONTENT_CONSENSUS_THRESHOLD=3
export CONTENT_REVIEW_POLICY_VERSION=phase3-v1
export CONTENT_REVIEW_RUBRIC_VERSION=1.0

"$PYTHON_BIN" -m compileall -q \
  app/models/content_factory.py \
  app/services/content_review_governance.py \
  app/services/content_artifact_lifecycle.py \
  app/services/content_reviewer_assignment.py \
  app/services/content_generation/providers/llm.py \
  app/api_v2_routers/content_review.py \
  app/domain/content_review_schemas.py \
  tests/phase03

"$PYTHON_BIN" -m pytest -q tests/phase03 --ignore=tests/phase03/test_phase3_postgres_integration.py
"$PYTHON_BIN" -m pytest -q tests/phase01 --ignore=tests/phase01/test_phase1_postgres_integration.py
"$PYTHON_BIN" -m pytest -q tests/phase02 --ignore=tests/phase02/test_phase2_postgres_integration.py
"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" - <<'PY'
from app.api_v2_routers.content_review import router
from app.services.content_review_governance import ReviewGovernancePolicy
paths = {route.path for route in router.routes}
assert "/content-review/artifacts/{artifact_id}/decisions" in paths
assert ReviewGovernancePolicy().quorum_threshold == 3
print(f"Phase 3 route/policy contract OK: {len(paths)} routes")
PY
