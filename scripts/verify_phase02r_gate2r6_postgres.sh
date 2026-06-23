#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" scripts/verify_migration_graph.py >/tmp/phase02r_gate2r6_migration_graph.txt
cat /tmp/phase02r_gate2r6_migration_graph.txt

cat <<'EOF'
PHASE 02R GATE 2R.6 POSTGRES READINESS PASSED
live_database_executed=no
schema_change_required=no
reason=Gate 2R.6 adds service-layer grounded generation and assessment validation controls only; no database migration is applied by this package.
EOF
