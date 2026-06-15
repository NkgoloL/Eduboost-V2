#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="python3"; fi
RUFF_BIN="${RUFF_BIN:-.venv/bin/ruff}"
if [[ ! -x "$RUFF_BIN" ]]; then RUFF_BIN="ruff"; fi

PHASE1_PYTHON_PATHS=(
  app/services/llm_provider.py
  app/services/prompt_registry.py
  app/services/content_schemas.py
  app/services/content_validator.py
  app/services/safety_filter.py
  app/services/batch_generation.py
  app/services/content_generation/source_context.py
  app/jobs/batch_generation_job.py
  app/api_v2_routers/generation.py
  app/models/content_factory.py
  app/modules/jobs.py
  app/api_v2.py
  alembic/versions/20260614_0900_p1_validation.py
  tests/phase01
)

"$PYTHON_BIN" -m compileall -q "${PHASE1_PYTHON_PATHS[@]}"
"$RUFF_BIN" check "${PHASE1_PYTHON_PATHS[@]}"
"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" -m pytest -q tests/phase01 --disable-warnings

"$PYTHON_BIN" - <<'PY'
from app.api_v2 import ROUTER_REGISTRY, app
from app.modules.jobs import WorkerSettings

assert any(name == "generation" for name, _ in ROUTER_REGISTRY)
assert any(
    getattr(fn, "__name__", "") == "generate_content_batch"
    for fn in WorkerSettings.functions
)
paths = [
    route.path
    for route in app.routes
    if "/admin/generation" in getattr(route, "path", "")
]
assert paths, "generation router is not mounted"
print(f"Phase 1 registration OK: {len(paths)} mounted paths")
PY

if [[ -n "${PHASE1_TEST_DATABASE_URL:-}" ]]; then
  .venv/bin/python -m pytest -q tests/phase01/test_phase1_postgres_integration.py
else
  echo "NOTICE: PHASE1_TEST_DATABASE_URL is unset; PostgreSQL closeout checks remain pending." >&2
fi
