#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"Python 3.11+ required; found {sys.version}")
print(f"python={sys.executable}")
print(f"version={sys.version.split()[0]}")
PY

echo "== compile =="
"$PYTHON_BIN" -m compileall -q \
  app/models/curriculum_expansion.py \
  app/domain/curriculum_expansion_schemas.py \
  app/services/curriculum_expansion.py \
  app/api_v2_routers/curriculum_expansion.py \
  app/jobs/curriculum_expansion_job.py \
  scripts/check_phase7_registry.py \
  scripts/export_phase7_training_dataset.py \
  scripts/phase7_training_readiness.py

echo "== release-blocking ruff =="
if "$PYTHON_BIN" -m ruff --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m ruff check \
    app/models/curriculum_expansion.py \
    app/domain/curriculum_expansion_schemas.py \
    app/services/curriculum_expansion.py \
    app/api_v2_routers/curriculum_expansion.py \
    app/jobs/curriculum_expansion_job.py \
    scripts/check_phase7_registry.py \
    scripts/export_phase7_training_dataset.py \
    scripts/phase7_training_readiness.py \
    tests/phase07 \
    --select E9,F63,F7,F82,F821
fi

echo "== Phase 7 focused tests =="
"$PYTHON_BIN" -W error::RuntimeWarning -m pytest -q \
  tests/phase07/test_phase7_unit.py \
  tests/phase07/test_phase7_registration.py \
  --no-cov

echo "== registry =="
PYTHONPATH=. "$PYTHON_BIN" scripts/check_phase7_registry.py --json

echo "== router and ARQ registration =="
PYTHONPATH=. "$PYTHON_BIN" - <<'PY'
from app.api_v2 import ROUTER_REGISTRY
from app.jobs.curriculum_expansion_job import capture_weekly_curriculum_coverage
from app.modules.jobs import WorkerSettings
registered = dict(ROUTER_REGISTRY)
assert "curriculum_expansion" in registered
paths = sorted(route.path for route in registered["curriculum_expansion"].routes)
assert "/admin/curriculum-expansion/training-manifests" in paths
assert capture_weekly_curriculum_coverage in WorkerSettings.functions
assert any(
    getattr(job, "coroutine", None) is capture_weekly_curriculum_coverage
    or getattr(job, "name", "") == "capture_weekly_curriculum_coverage"
    for job in WorkerSettings.cron_jobs
)
print(f"routes={len(paths)}")
for path in paths:
    print(path)
print("weekly_snapshot_job=registered")
PY

echo "== deterministic training-readiness dry run =="
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/manifest.json" <<'JSON'
{
  "dataset_version": "phase7-synthetic-v1",
  "status": "approved",
  "artifact_count": 1,
  "dataset_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
JSON
printf '%s\n' '{"instruction":"Teach whole numbers","output":"Use place-value blocks."}' > "$TMP/dataset.jsonl"
"$PYTHON_BIN" scripts/phase7_training_readiness.py \
  --manifest "$TMP/manifest.json" \
  --dataset "$TMP/dataset.jsonl" \
  --dry-run

echo "== migration graph =="
MIGRATION_OUTPUT="$("$PYTHON_BIN" scripts/verify_migration_graph.py)"
echo "$MIGRATION_OUTPUT"
grep -q 'head=20260615_2100_p17_reconcile' <<<"$MIGRATION_OUTPUT"
test -f alembic/versions/20260615_1800_p7_curriculum.py

echo "== schema integrity =="
"$PYTHON_BIN" scripts/validate_schema_integrity.py

if [[ -f scripts/generate_openapi.py ]]; then
  echo "== OpenAPI drift =="
  "$PYTHON_BIN" scripts/generate_openapi.py --check
fi

if "$PYTHON_BIN" -m importlinter --version >/dev/null 2>&1; then
  echo "== import boundaries =="
  "$PYTHON_BIN" -m importlinter --config .importlinter
elif command -v lint-imports >/dev/null 2>&1; then
  echo "== import boundaries =="
  lint-imports
fi

echo "== Atlas governance paths =="
for required in \
  docs/roadmap/execution/atlas/phase_06_execution_plan.md \
  docs/roadmap/execution/atlas/phase_06_implementation_report.md \
  docs/release-evidence/atlas/phase-06/phase_06_evidence_index.md \
  docs/release-evidence/atlas/phase-06/phase_06_audit_report.md \
  docs/roadmap/execution/atlas/phase_07_execution_plan.md; do
  [[ -e "$required" ]] || { echo "Missing $required" >&2; exit 3; }
done

if grep -Eq 'docs/(roadmap/execution/phase_6_|release/phase_6_)' docs/roadmap/PHASE_STATUS_REGISTER.md; then
  echo "Legacy non-Atlas Phase 6 links remain in status register." >&2
  exit 4
fi

echo "== prior-phase fast regressions =="
for phase in 1 2 3 4 5 6; do
  script="scripts/verify_phase${phase}.sh"
  [[ -f "$script" ]] || { echo "Missing $script" >&2; exit 5; }
  bash "$script"
done

echo "PHASE 7 FAST VERIFICATION PASSED"
