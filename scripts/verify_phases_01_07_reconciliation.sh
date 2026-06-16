#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"
cd "$ROOT"
MODE="${PHASE_RECONCILIATION_MODE:-closure}"
[[ "$MODE" == "closure" || "$MODE" == "discovery" ]] || { echo "PHASE_RECONCILIATION_MODE must be closure or discovery." >&2; exit 2; }

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

printf '\n[1/10] Python and source-state identity\n'
"$PYTHON_BIN" --version
if command -v git >/dev/null 2>&1 && [[ -d .git ]]; then
  git status --short
  git branch --show-current
  git rev-parse HEAD
fi

printf '\n[2/10] Compile reconciliation modules\n'
"$PYTHON_BIN" -m py_compile \
  app/models/content_factory.py \
  app/models/curriculum_expansion.py \
  app/services/content_answer_key_verification.py \
  app/services/content_review_governance.py \
  app/api_v2_routers/content_review.py \
  app/domain/content_review_schemas.py \
  app/services/semantic_retrieval/service.py \
  app/services/semantic_retrieval/repository.py \
  app/services/semantic_retrieval/indexing.py \
  app/modules/diagnostics/item_bank_service.py \
  app/services/ai_operations.py \
  app/services/curriculum_expansion.py \
  app/api_v2_routers/curriculum_expansion.py \
  scripts/phase2_evaluate_retrieval.py \
  scripts/validate_phase2_evaluation_dataset.py \
  scripts/validate_phase_control_sets.py \
  alembic/versions/20260615_2100_p17_reconcile.py \
  tests/reconciliation/test_phases_1_7_reconciliation.py \
  tests/reconciliation/test_reconciliation_postgres.py

printf '\n[3/10] Release-blocking Ruff rules\n'
if "$PYTHON_BIN" -m ruff --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m ruff check \
    app/models/content_factory.py \
    app/models/curriculum_expansion.py \
    app/services/content_answer_key_verification.py \
    app/services/content_review_governance.py \
    app/api_v2_routers/content_review.py \
    app/domain/content_review_schemas.py \
    app/services/semantic_retrieval/service.py \
    app/services/semantic_retrieval/repository.py \
    app/services/semantic_retrieval/indexing.py \
    app/modules/diagnostics/item_bank_service.py \
    app/services/ai_operations.py \
    app/services/curriculum_expansion.py \
    app/api_v2_routers/curriculum_expansion.py \
    scripts/phase2_evaluate_retrieval.py \
    scripts/validate_phase2_evaluation_dataset.py \
    scripts/validate_phase_control_sets.py \
    tests/reconciliation \
    --select E9,F63,F7,F82,F821
else
  if [[ "$MODE" == "closure" ]]; then
    echo "Ruff is required for closure reconciliation." >&2
    exit 3
  fi
  echo "WARNING: Ruff is not installed; canonical CI must run this gate." >&2
fi

printf '\n[4/10] Focused reconciliation tests\n'
"$PYTHON_BIN" -W error::RuntimeWarning -m pytest -q \
  tests/reconciliation/test_phases_1_7_reconciliation.py \
  --no-cov

printf '\n[5/10] Migration and schema gates\n'
"$PYTHON_BIN" scripts/verify_migration_graph.py
grep -q '20260615_2100_p17_reconcile' <("$PYTHON_BIN" scripts/verify_migration_graph.py)
"$PYTHON_BIN" scripts/validate_schema_integrity.py

printf '\n[6/10] Atlas control-set and evidence integrity\n'
"$PYTHON_BIN" scripts/validate_phase_control_sets.py

printf '\n[7/10] Static safety contracts\n'
! grep -R -n -E 'artifact\.answer_key_verified = True' \
  app/services/content_review_governance.py \
  app/services/content_file_artifact_import.py

grep -q 'actual_usage_exceeded_budget' app/services/ai_operations.py
grep -q 'vector_temporarily_unavailable' app/services/semantic_retrieval/service.py
grep -q 'source_origin' app/services/semantic_retrieval/repository.py
grep -q '_irt_item_is_learner_eligible' app/modules/diagnostics/item_bank_service.py
grep -q 'published_total' app/services/curriculum_expansion.py
grep -q 'PHASE7_POSTGRES_PORT' scripts/verify_phase7_postgres.sh
grep -q 'PHASE4_POSTGRES_PORT' scripts/verify_phase4_postgres.sh

printf '\n[8/10] Phase 2 evaluation claim guard\n'
set +e
"$PYTHON_BIN" scripts/phase2_evaluate_retrieval.py \
  --dataset data/retrieval/phase2_evaluation_set.json \
  --output /tmp/phase2-smoke-result.json >/tmp/phase2-smoke-guard.txt 2>&1
phase2_smoke_rc=$?
set -e
if [[ "$phase2_smoke_rc" -eq 0 ]]; then
  echo "The two-case Phase 2 smoke dataset was incorrectly accepted for closure." >&2
  exit 8
fi
grep -q 'not approved for retrieval closure' /tmp/phase2-smoke-guard.txt
echo "Phase 2 smoke dataset correctly rejected for closure."

printf '\n[9/10] Prior-phase fast regression\n'
if [[ "${RUN_PHASE_REGRESSION:-1}" == "1" ]]; then
  for phase in 1 2 3 4 5 6 7; do
    script="scripts/verify_phase${phase}.sh"
    [[ -f "$script" ]] || { echo "Missing $script" >&2; exit 9; }
    bash "$script"
  done
else
  if [[ "$MODE" == "closure" ]]; then
    echo "RUN_PHASE_REGRESSION=0 is prohibited for closure reconciliation." >&2
    exit 9
  fi
  echo "RUN_PHASE_REGRESSION=0: prior-phase fast gates skipped by operator."
fi

printf '\n[10/10] OpenAPI and import boundaries\n'
if [[ -f scripts/generate_openapi.py ]]; then
  "$PYTHON_BIN" scripts/generate_openapi.py --check
else
  if [[ "$MODE" == "closure" ]]; then
    echo "scripts/generate_openapi.py is required for closure reconciliation." >&2
    exit 10
  fi
fi
if "$PYTHON_BIN" -m importlinter --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m importlinter --config .importlinter
elif command -v lint-imports >/dev/null 2>&1; then
  lint-imports
else
  if [[ "$MODE" == "closure" ]]; then
    echo "import-linter/lint-imports is required for closure reconciliation." >&2
    exit 10
  fi
  echo "WARNING: import-linter unavailable; canonical CI must run this gate." >&2
fi

echo 'PHASES 1-7 RECONCILIATION FAST VERIFICATION PASSED'
