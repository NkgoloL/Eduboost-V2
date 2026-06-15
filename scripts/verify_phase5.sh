#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required" >&2; exit 2; }

"$PYTHON_BIN" - <<'PY'
import sys
assert sys.version_info.major == 3 and sys.version_info.minor >= 11, sys.version
print(f"Python: {sys.version.split()[0]}")
PY

export APP_ENV=test ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}"
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://eduboost:eduboost@127.0.0.1:5432/eduboost_test}"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic
export LLM_PROVIDER=deterministic

printf '\n[1/8] Compile Phase 5 code\n'
"$PYTHON_BIN" -m compileall -q \
  app/models/tutor.py app/domain/tutor_schemas.py app/services/tutor_safety.py \
  app/services/learner_tutor.py app/api_v2_routers/tutor.py tests/phase05

printf '\n[2/8] Release-blocking Ruff rules\n'
if "$PYTHON_BIN" -m ruff --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m ruff check \
    app/models/tutor.py app/domain/tutor_schemas.py app/services/tutor_safety.py \
    app/services/learner_tutor.py app/api_v2_routers/tutor.py tests/phase05 \
    --select E9,F63,F7,F82,F821
else
  echo "ruff unavailable in the selected venv; install dev dependencies before closure" >&2
  exit 3
fi

printf '\n[3/8] Phase 5 focused backend tests\n'
"$PYTHON_BIN" -m pytest -q \
  tests/phase05/test_phase5_unit.py \
  tests/phase05/test_phase5_registration.py \
  -W error::RuntimeWarning

printf '\n[4/8] Router, context, and migration contracts\n'
"$PYTHON_BIN" - <<'PY'
from app.api_v2 import ROUTER_REGISTRY, app
names=[name for name,_ in ROUTER_REGISTRY]
assert names.count('tutor') == 1, names
paths={route.path for route in app.routes}
required={
 '/api/v2/tutor/sessions',
 '/api/v2/tutor/sessions/{session_id}',
 '/api/v2/tutor/sessions/{session_id}/messages',
 '/api/v2/tutor/sessions/{session_id}/messages/stream',
 '/api/v2/tutor/sessions/{session_id}/cancel',
}
assert required <= paths, required - paths
print('Tutor router registration OK:', len(required), 'canonical paths')
PY
"$PYTHON_BIN" scripts/verify_migration_graph.py | tee /tmp/phase5-migration-graph.txt
grep -q 'head=20260615_1200_p5_tutor' /tmp/phase5-migration-graph.txt

printf '\n[5/8] Privacy and fail-safe static contracts\n'
grep -q 'prepare_tutor_input(question)' app/services/learner_tutor.py
grep -q 'validate_tutor_output(result.text' app/services/learner_tutor.py
grep -q 'request.is_disconnected' app/api_v2_routers/tutor.py
grep -q 'Never expose provider or infrastructure exception details' app/api_v2_routers/tutor.py
! grep -R -nE 'raw_question|raw_prompt|unredacted_content' app/models/tutor.py app/services/learner_tutor.py

printf '\n[6/8] Frontend type and component tests\n'
if command -v pnpm >/dev/null 2>&1; then
  PNPM=(pnpm)
elif command -v corepack >/dev/null 2>&1; then
  PNPM=(corepack pnpm)
else
  echo "pnpm/corepack is required for Phase 5 frontend verification" >&2
  exit 4
fi
"${PNPM[@]}" --dir app/frontend run type-check
"${PNPM[@]}" --dir app/frontend exec vitest run src/components/learner/__tests__/AiTutorChat.test.tsx

printf '\n[7/8] Architecture, schema, and prior-phase regressions\n'
if [[ -x .venv/bin/lint-imports ]]; then .venv/bin/lint-imports; elif command -v lint-imports >/dev/null; then lint-imports; fi
"$PYTHON_BIN" scripts/validate_schema_integrity.py
"$PYTHON_BIN" scripts/generate_openapi.py --check
for script in scripts/verify_phase1.sh scripts/verify_phase2.sh scripts/verify_phase3.sh scripts/verify_phase4.sh; do
  bash "$script"
done

printf '\n[8/8] Atlas governance paths\n'
test -f docs/roadmap/execution/atlas/phase_05_execution_plan.md
grep -q 'PHASE_05_START_APPROVED=true' docs/roadmap/execution/atlas/phase_05_execution_plan.md

echo 'PHASE 5 FAST VERIFICATION PASSED'
