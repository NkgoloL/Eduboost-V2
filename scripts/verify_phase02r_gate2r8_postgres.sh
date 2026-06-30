#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

echo "PHASE 02R GATE 2R.8 POSTGRESQL READINESS"
echo "live_database_executed=${PHASE02R_REQUIRE_LIVE_DB:-no}"
echo "schema_change_required=no"
echo "legacy_migration_executed=no"
echo "production_activation_performed=no"

if [[ "${PHASE02R_REQUIRE_LIVE_DB:-}" == "1" ]]; then
  [[ -n "${DATABASE_URL:-}" ]] || { echo "DATABASE_URL is required when PHASE02R_REQUIRE_LIVE_DB=1" >&2; exit 3; }
  "$PYTHON_BIN" scripts/verify_migration_graph.py
  echo "live_database_contract=verified_migration_graph_only_no_gate2r8_schema_change"
else
  "$PYTHON_BIN" scripts/verify_migration_graph.py >/dev/null
  echo "static_postgres_readiness=passed"
  echo "Set PHASE02R_REQUIRE_LIVE_DB=1 and DATABASE_URL for live closure evidence."
fi
