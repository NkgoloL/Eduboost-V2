#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE=""
MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate)
      GATE="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

[[ "$GATE" == "2R.0" ]] || { echo "Only Gate 2R.0 preflight is available before approval." >&2; exit 2; }
[[ "$MODE" == "discovery" ]] || { echo "Gate 2R.0 supports --mode discovery only." >&2; exit 2; }

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

grep -q 'PHASE_02R_START_APPROVED=false' docs/roadmap/execution/atlas/phase_02r_execution_plan.md || {
  echo "Gate 2R.0 preflight requires PHASE_02R_START_APPROVED=false." >&2
  exit 3
}

"$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py 02R phase-02r phase_02r
"$PYTHON_BIN" scripts/verify_phase0_or_equivalent_baseline.py

echo "PHASE 02R GATE 2R.0 PREFLIGHT PASSED"
