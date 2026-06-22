#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

MIGRATION="alembic/versions/20260618_1200_phase02r_grounding_controls.py"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

[[ -f "$MIGRATION" ]] || { echo "missing migration: $MIGRATION" >&2; exit 1; }

required=(
  "curriculum_corpus_versions"
  "curriculum_corpus_memberships"
  "curriculum_corpus_activation_events"
  "curriculum_corpus_active_bindings"
  "curriculum_corpus_outbox_events"
  "curriculum_retrieval_evaluation_runs"
  "curriculum_retrieval_evaluation_cases"
  "prevent_phase02r_grounding_mutation"
  "binding_epoch"
  "manifest_sha256"
)
for needle in "${required[@]}"; do
  grep -q "$needle" "$MIGRATION" || { echo "migration static check missing $needle" >&2; exit 1; }
done

"$PYTHON_BIN" scripts/verify_migration_graph.py >/tmp/phase02r_gate2r5_migration_graph.txt
"$PYTHON_BIN" -m compileall -q app/models/curriculum_grounding.py app/services/curriculum/corpus.py

cat <<EOF
PHASE 02R GATE 2R.5 POSTGRES READINESS CHECK PASSED
migration=$MIGRATION
mode=static
live_database_executed=no
reason=Gate 2R.5 package does not apply migrations automatically; run with controlled DB evidence process for closure.
EOF

if [[ "${PHASE02R_REQUIRE_LIVE_DB:-0}" == "1" ]]; then
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "PHASE02R_REQUIRE_LIVE_DB=1 but DATABASE_URL is not set" >&2
    exit 3
  fi
  if command -v alembic >/dev/null 2>&1; then
    alembic heads
    echo "live_database_note=DATABASE_URL was provided; alembic heads succeeded. Upgrade is intentionally not run by this verifier."
  else
    echo "PHASE02R_REQUIRE_LIVE_DB=1 but alembic is unavailable on PATH" >&2
    exit 3
  fi
fi
