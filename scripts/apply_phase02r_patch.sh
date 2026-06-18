#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE=""
APPLY_DATABASE="${PHASE02R_APPLY_DATABASE:-0}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate) GATE="${2:-}"; shift 2 ;;
    --apply-database) APPLY_DATABASE=1; shift ;;
    --check-only) APPLY_DATABASE=0; shift ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done

if [[ "$GATE" == "2R.0" ]]; then
  echo "Gate 2R.0 is read-only discovery; patch application is prohibited." >&2
  exit 3
fi
[[ "$GATE" == "2R.1" ]] || {
  echo "Only Gate 2R.1 implementation application is currently supported." >&2
  exit 2
}

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" scripts/phase02r_gate_control.py --expected-authorised-gate 2R.1

required_files=(
  app/models/curriculum_authority.py
  app/services/curriculum/rights_policy.py
  alembic/versions/20260616_1200_phase02r_authority_controls.py
  data/curriculum/registries/grade4_mathematics_caps_source_completeness.json
  scripts/validate_phase02r_authority_schema.py
    scripts/verify_phase02r_gate2r1.py
  scripts/curriculum/validate_source_completeness_register.py
  scripts/verify_phase02r_postgres.sh
  tests/phase02r/test_phase02r_postgres_integration.py
  tests/unit/phase02r/test_authority_schema.py
  tests/unit/phase02r/test_rights_policy.py
  tests/unit/phase02r/test_source_completeness_register.py
  tests/unit/phase02r/test_gate_control.py
)
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || { echo "Missing Gate 2R.1 implementation file: $file" >&2; exit 3; }
done

if [[ "$APPLY_DATABASE" == "1" ]]; then
  "$PYTHON_BIN" -m alembic upgrade head
  echo "PHASE 02R GATE 2R.1 DATABASE MIGRATION APPLIED"
else
  echo "PHASE 02R GATE 2R.1 IMPLEMENTATION MANIFEST VALIDATED"
  echo "Database migration not executed; use --apply-database in the governed target environment."
fi
