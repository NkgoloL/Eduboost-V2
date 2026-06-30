#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE=""
MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate) GATE="${2:-}"; shift 2 ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done

case "$GATE" in
  2R.0|2R.1|2R.2|2R.3|2R.4|2R.5|2R.6|2R.7|2R.8) ;;
  *) echo "Gate $GATE preflight is not supported." >&2; exit 2 ;;
esac

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" scripts/phase02r_gate_control.py --expected-authorised-gate "$GATE"
"$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py 02R phase-02r phase_02r

if [[ "$GATE" == "2R.0" ]]; then
  [[ "$MODE" == "discovery" ]] || { echo "Gate 2R.0 supports --mode discovery only." >&2; exit 2; }
  "$PYTHON_BIN" scripts/verify_phase0_or_equivalent_baseline.py
  echo "PHASE 02R GATE 2R.0 PREFLIGHT PASSED"
  exit 0
fi

[[ -z "$MODE" || "$MODE" == "implementation" || "$MODE" == "closure" ]] || {
  echo "Gates 2R.1-2R.8 support --mode implementation or --mode closure." >&2
  exit 2
}

"$PYTHON_BIN" scripts/validate_phase_control_sets.py
"$PYTHON_BIN" scripts/verify_migration_graph.py
if [[ "$GATE" == "2R.1" ]]; then
  "$PYTHON_BIN" scripts/curriculum/validate_source_completeness_register.py
else
  "$PYTHON_BIN" scripts/verify_phase02r_gate2r2_to_2r8.py --gate "$GATE" --mode implementation
fi

echo "PHASE 02R GATE $GATE PREFLIGHT PASSED"
