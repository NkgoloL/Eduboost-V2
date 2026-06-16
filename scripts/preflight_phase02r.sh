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

"$PYTHON_BIN" - <<'PY'
import json
import sys
from pathlib import Path

control_path = Path("docs/roadmap/execution/atlas/phase_02r_start_gate_control.json")
try:
    control = json.loads(control_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    print(f"Missing start-gate control file: {control_path}", file=sys.stderr)
    raise SystemExit(3)

errors = []
if control.get("phase") != "02R":
    errors.append("phase must be 02R")
if control.get("start_approved") is not False:
    errors.append("start_approved must remain false for Gate 2R.0 discovery")
if control.get("approval_commit_sha") is not None:
    errors.append("approval_commit_sha must be null until the dedicated approval commit")
if errors:
    for error in errors:
        print(f"Gate 2R.0 control failure: {error}", file=sys.stderr)
    raise SystemExit(3)
PY

"$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py 02R phase-02r phase_02r
"$PYTHON_BIN" scripts/verify_phase0_or_equivalent_baseline.py

echo "PHASE 02R GATE 2R.0 PREFLIGHT PASSED"
