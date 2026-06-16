#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="python3"; fi
RUFF_BIN="${RUFF_BIN:-.venv/bin/ruff}"
if [[ ! -x "$RUFF_BIN" ]]; then RUFF_BIN="ruff"; fi

export APP_ENV=test ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic

printf '\n[1/8] Compile Phase 4 code\n'
"$PYTHON_BIN" -m compileall -q \
  app/domain/irt_quality_schemas.py app/models/irt_quality.py \
  app/services/irt_quality_service.py app/jobs/irt_quality_job.py \
  app/api_v2_routers/irt_quality.py tests/phase04

printf '\n[2/8] Release-blocking Ruff rules\n'
"$RUFF_BIN" check \
  app/domain/irt_quality_schemas.py app/models/irt_quality.py \
  app/services/irt_quality_service.py app/jobs/irt_quality_job.py \
  app/api_v2_routers/irt_quality.py tests/phase04 \
  --select E9,F63,F7,F82,F821

printf '\n[3/8] Phase 4 unit, route, state-machine, and selection tests\n'
"$PYTHON_BIN" -m pytest -q \
  tests/phase04/test_phase4_unit.py \
  tests/phase04/test_phase4_routes_and_selection.py \
  -W error::RuntimeWarning

printf '\n[4/8] Migration graph and schema model integrity\n'
"$PYTHON_BIN" scripts/verify_migration_graph.py
if [[ -f scripts/validate_schema_integrity.py ]]; then
  "$PYTHON_BIN" scripts/validate_schema_integrity.py
fi

printf '\n[5/8] Router and ARQ registration\n'
"$PYTHON_BIN" - <<'PY'
from app.api_v2 import app
from app.modules.jobs import WorkerSettings
from app.jobs.irt_quality_job import run_irt_quality_watchdog
paths={r.path for r in app.routes}
required={
 '/api/v2/admin/irt-quality/runs',
 '/v2/admin/irt-quality/runs',
 '/api/v2/admin/irt-quality/items/{item_id}',
 '/api/v2/admin/irt-quality/items/{item_id}/override',
 '/api/v2/admin/irt-quality/items/{item_id}/override/clear',
}
missing=required-paths
assert not missing, f'missing Phase 4 routes: {sorted(missing)}'
assert run_irt_quality_watchdog in WorkerSettings.functions
assert any(getattr(job, 'coroutine', None) is run_irt_quality_watchdog for job in WorkerSettings.cron_jobs)
print(f'Phase 4 routes OK: {len([p for p in paths if "irt-quality" in p])}')
print('IRT watchdog registered as durable function and nightly cron')
PY

printf '\n[6/8] Fail-closed serving and rewrite-review contracts\n'
"$PYTHON_BIN" - <<'PY'
from pathlib import Path
service=Path('app/services/irt_quality_service.py').read_text()
selection=Path('app/modules/diagnostics/item_bank_service.py').read_text()
assert 'random.shuffle' not in service
assert 'ContentArtifactStatus.PENDING_REVIEW' in service
assert 'IRTQualityState.REWRITE_REVIEW: "retired"' in service
assert '_irt_item_is_learner_eligible' in selection
assert 'state in {"uncalibrated", "healthy", "monitor"}' in selection
for state in ('quarantined','retired','review_required','rewrite_review'):
    assert f'state in {state!r}' not in selection
print('No automatic answer-option mutation; rewrites return to Phase 3 review')
PY

printf '\n[7/8] Phase 1-3 fast regressions\n'
if [[ "${PHASE4_SKIP_PRIOR_FAST:-0}" != "1" ]]; then
  for script in scripts/verify_phase1.sh scripts/verify_phase2.sh scripts/verify_phase3.sh; do
    [[ -x "$script" || -f "$script" ]] && bash "$script"
  done
else
  echo 'Skipped by PHASE4_SKIP_PRIOR_FAST=1'
fi

printf '\n[8/8] Legacy single-review path remains absent\n'
if git grep -n -E 'approve_artifact|test_admin_can_approve_artifact_route|/artifacts/\{artifact_id\}/approve' -- app docs tests audits; then
  echo 'Legacy approval path found' >&2
  exit 1
fi

echo 'PHASE 4 FAST VERIFICATION PASSED'
