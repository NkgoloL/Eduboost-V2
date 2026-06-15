#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required" >&2; exit 2; }

printf '== Phase 6 fast verification ==\n'
"$PYTHON_BIN" --version
"$PYTHON_BIN" - <<'PY'
import sys
assert sys.version_info >= (3, 11), sys.version
PY

"$PYTHON_BIN" -m compileall -q \
  app/models/ai_operations.py \
  app/domain/ai_operations_schemas.py \
  app/services/ai_operations.py \
  app/api_v2_routers/ai_operations.py \
  app/jobs/ai_operations_job.py \
  tests/phase06

if "$PYTHON_BIN" -m ruff --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m ruff check \
    app/models/ai_operations.py \
    app/domain/ai_operations_schemas.py \
    app/services/ai_operations.py \
    app/api_v2_routers/ai_operations.py \
    app/jobs/ai_operations_job.py \
    tests/phase06 \
    --select E9,F63,F7,F82,F821
fi

"$PYTHON_BIN" -m pytest -q \
  tests/phase06/test_phase6_unit.py \
  tests/phase06/test_phase6_registration.py \
  --no-cov -W error::RuntimeWarning

"$PYTHON_BIN" - <<'PY'
from app.api_v2 import ROUTER_REGISTRY, app
from app.modules.jobs import WorkerSettings
names = {name for name, _ in ROUTER_REGISTRY}
assert "ai_operations" in names, names
paths = {r.path for r in app.routes}
required = {
    "/api/v2/admin/ai-operations/providers/health",
    "/api/v2/admin/ai-operations/usage",
    "/api/v2/admin/ai-operations/reservations",
}
assert required <= paths, required - paths
functions = {getattr(fn, "__name__", "") for fn in WorkerSettings.functions}
assert "expire_ai_usage_reservations" in functions
print(f"Phase 6 router/job registration OK: {len(required)} key paths")
PY

MIGRATION_OUTPUT="$("$PYTHON_BIN" scripts/verify_migration_graph.py)"
echo "$MIGRATION_OUTPUT"

"$PYTHON_BIN" scripts/validate_schema_integrity.py

if [[ -f scripts/generate_openapi.py ]]; then
  "$PYTHON_BIN" scripts/generate_openapi.py --check
fi

# Static production guards.
grep -q 'DeterministicContentGenerationProvider is forbidden in production' app/services/content_generation/provider_factory.py
grep -q 'AI_USAGE_RESERVATION_TTL_SECONDS' app/core/config.py
grep -q 'ai_usage_tokens_total' app/core/metrics.py

for script in \
  scripts/verify_phase1.sh \
  scripts/verify_phase2.sh \
  scripts/verify_phase3.sh \
  scripts/verify_phase4.sh \
  scripts/verify_phase5.sh; do
  [[ -f "$script" ]] || { echo "Missing prerequisite verifier: $script" >&2; exit 3; }
  bash "$script"
done

[[ -f docs/roadmap/execution/atlas/phase_06_execution_plan.md ]]
[[ -d docs/release-evidence/atlas/phase-06/raw ]]

echo 'PHASE 6 FAST VERIFICATION PASSED'
