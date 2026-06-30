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
    --check-only|--dry-run) APPLY_DATABASE=0; shift ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done

if [[ "$GATE" == "2R.0" ]]; then
  echo "Gate 2R.0 is read-only discovery; patch application is prohibited." >&2
  exit 3
fi
case "$GATE" in
  2R.1|2R.2|2R.3|2R.4|2R.5|2R.6|2R.7|2R.8) ;;
  *) echo "Gate $GATE implementation application is not supported." >&2; exit 2 ;;
esac

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" scripts/phase02r_gate_control.py --expected-authorised-gate "$GATE"

if [[ "$GATE" == "2R.1" ]]; then
  required_files=(
    app/models/curriculum_authority.py
    app/services/curriculum/rights_policy.py
    alembic/versions/20260616_1200_phase02r_authority_controls.py
    data/curriculum/registries/grade4_mathematics_caps_source_completeness.json
    scripts/validate_phase02r_authority_schema.py
    scripts/verify_phase02r_gate2r1.py
    scripts/curriculum/validate_source_completeness_register.py
    scripts/verify_phase02r_postgres.sh
  )
else
  "$PYTHON_BIN" scripts/verify_phase02r_gate2r2_to_2r8.py --gate "$GATE" --mode implementation
  required_files=(
    app/models/curriculum_grounding.py
    app/services/curriculum/acquisition.py
    app/services/curriculum/extraction.py
    app/services/curriculum/graph.py
    app/services/curriculum/corpus.py
    app/services/curriculum/grounding.py
    app/services/curriculum/claim_validation.py
    app/services/curriculum/answer_verification.py
    app/services/curriculum/tutor_grounding.py
    app/services/curriculum/legacy.py
    app/services/curriculum/evaluation.py
    alembic/versions/20260618_1200_phase02r_grounding_controls.py
  )
fi
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || { echo "Missing Gate $GATE implementation file: $file" >&2; exit 3; }
done

if [[ "$APPLY_DATABASE" == "1" ]]; then
  "$PYTHON_BIN" -m alembic upgrade head
  echo "PHASE 02R GATE $GATE DATABASE MIGRATION APPLIED"
else
  echo "PHASE 02R GATE $GATE IMPLEMENTATION MANIFEST VALIDATED"
  echo "Database migration not executed; use --apply-database in the governed target environment."
fi
