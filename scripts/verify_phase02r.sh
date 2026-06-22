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
  *) echo "Gate $GATE verification is not supported." >&2; exit 2 ;;
esac

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

if [[ "$GATE" == "2R.0" ]]; then
  [[ "$MODE" == "discovery" ]] || { echo "Gate 2R.0 supports --mode discovery only." >&2; exit 2; }
  bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery
  "$PYTHON_BIN" scripts/curriculum/validate_source_manifest.py --json
  "$PYTHON_BIN" scripts/curriculum/source_inventory.py --json
  "$PYTHON_BIN" scripts/curriculum/extract_caps_source_sample.py --json
  bash scripts/verify_phases_01_07_reconciliation.sh
  echo "PHASE 02R GATE 2R.0 DISCOVERY VERIFICATION PASSED"
  exit 0
fi

MODE="${MODE:-implementation}"
[[ "$MODE" == "implementation" || "$MODE" == "closure" ]] || {
  echo "Gates 2R.1-2R.8 support --mode implementation or --mode closure." >&2
  exit 2
}

if [[ "$GATE" == "2R.1" ]]; then
  "$PYTHON_BIN" scripts/verify_phase02r_gate2r1.py --mode "$MODE"
  if [[ "$MODE" == "closure" ]]; then
    bash scripts/verify_phase02r_postgres.sh
    echo "PHASE 02R GATE 2R.1 CANDIDATE CLOSURE VERIFICATION PASSED"
  else
    echo "PHASE 02R GATE 2R.1 IMPLEMENTATION VERIFICATION PASSED"
  fi
  exit 0
fi


if [[ "$GATE" == "2R.4" ]]; then
  "$PYTHON_BIN" scripts/verify_phase02r_gate2r4.py --mode "$MODE"
  exit 0
fi

"$PYTHON_BIN" scripts/verify_phase02r_gate2r2_to_2r8.py --gate "$GATE" --mode "$MODE"
if [[ "$MODE" == "closure" ]]; then
  echo "PHASE 02R GATE $GATE CLOSURE REMAINS BLOCKED UNTIL LIVE EVIDENCE AND APPROVALS EXIST"
else
  echo "PHASE 02R GATE $GATE IMPLEMENTATION VERIFICATION PASSED"
fi
