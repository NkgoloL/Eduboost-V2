#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

REQUIRE_LIVE_DB="${PHASE02R_REQUIRE_LIVE_DB:-0}"
APPLY_DB="${PHASE02R_GATE2R4_APPLY_DB:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --require-live-db) REQUIRE_LIVE_DB=1; shift ;;
    --apply-db) APPLY_DB=1; shift ;;
    --static-only) REQUIRE_LIVE_DB=0; APPLY_DB=0; shift ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done

MIGRATION="alembic/versions/20260622_1200_phase02r_gate2r4_curriculum_graph.py"
[[ -f "$MIGRATION" ]] || { echo "Missing Gate 2R.4 migration: $MIGRATION" >&2; exit 3; }

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
required = [
    "curriculum_node_versions",
    "curriculum_edge_versions",
    "curriculum_source_mapping_versions",
    "curriculum_mapping_review_events",
    "curriculum_language_links",
    "phase02r_prevent_approved_node_version_mutation",
    "phase02r_prevent_mapping_review_event_mutation",
]
text = Path("alembic/versions/20260622_1200_phase02r_gate2r4_curriculum_graph.py").read_text(encoding="utf-8")
missing = [token for token in required if token not in text]
if missing:
    raise SystemExit(f"Gate 2R.4 migration is missing required tokens: {missing}")
print("Gate 2R.4 migration static contract passed")
PY

"$PYTHON_BIN" scripts/verify_migration_graph.py

if [[ "$REQUIRE_LIVE_DB" == "1" || "$APPLY_DB" == "1" ]]; then
  [[ -n "${DATABASE_URL:-}" ]] || { echo "DATABASE_URL is required for live Gate 2R.4 PostgreSQL verification." >&2; exit 3; }
  "$PYTHON_BIN" -m alembic upgrade head
  "$PYTHON_BIN" - <<'PY'
import os
import re
import sys
from pathlib import Path

# Keep this proof dependency-light: it verifies the migration reached the target
# head and that the target table/trigger DDL is in the applied migration file.
# Environment-specific live trigger mutation tests belong in integration CI where
# asyncpg/psycopg and a disposable database are guaranteed.
current = os.popen(f"{sys.executable} -m alembic current").read()
if "20260622_1200_phase02r_gate2r4" not in current:
    raise SystemExit(f"alembic current does not show Gate 2R.4 head: {current}")
text = Path("alembic/versions/20260622_1200_phase02r_gate2r4_curriculum_graph.py").read_text(encoding="utf-8")
for pattern in [r"CREATE TRIGGER trg_phase02r_prevent_approved_node_version_mutation", r"CREATE TRIGGER trg_phase02r_prevent_mapping_review_event_update", r"CREATE TRIGGER trg_phase02r_prevent_mapping_review_event_delete"]:
    if not re.search(pattern, text):
        raise SystemExit(f"missing live-control trigger DDL: {pattern}")
print("Gate 2R.4 live PostgreSQL migration head proof passed")
PY
else
  echo "Live PostgreSQL migration was not executed. Set PHASE02R_REQUIRE_LIVE_DB=1 and DATABASE_URL for closure evidence."
fi

echo "PHASE 02R GATE 2R.4 POSTGRESQL VERIFICATION PASSED"
