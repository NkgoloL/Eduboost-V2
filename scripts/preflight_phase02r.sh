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

[[ "$GATE" == "2R.0" || "$GATE" == "2R.1" ]] || { echo "Only Gate 2R.0 and Gate 2R.1 preflight are supported." >&2; exit 2; }
if [[ "$GATE" == "2R.0" ]]; then
  [[ "$MODE" == "discovery" ]] || { echo "Gate 2R.0 supports --mode discovery only." >&2; exit 2; }
else
  [[ -z "$MODE" || "$MODE" == "implementation" ]] || { echo "Gate 2R.1 supports no mode or --mode implementation only." >&2; exit 2; }
fi

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" - "$GATE" <<'PY'
import json
import sys
from pathlib import Path

gate = sys.argv[1]
control_path = Path("docs/roadmap/execution/atlas/phase_02r_start_gate_control.json")
try:
    control = json.loads(control_path.read_text(encoding="utf-8"))
except FileNotFoundError:
    print(f"Missing start-gate control file: {control_path}", file=sys.stderr)
    raise SystemExit(3)

errors = []
if control.get("phase") != "02R":
    errors.append("phase must be 02R")
if gate == "2R.0":
    if control.get("start_approved") is not False:
        errors.append("start_approved must remain false for Gate 2R.0 discovery")
    if control.get("approval_commit_sha") is not None:
        errors.append("approval_commit_sha must be null until the dedicated approval commit")
else:
    if control.get("start_approved") is not True:
        errors.append("start_approved must be true before Gate 2R.1")
    if control.get("approved_gate") != "2R.0":
        errors.append("approved_gate must be 2R.0 before Gate 2R.1")
    if control.get("authorised_next_gate") != "2R.1":
        errors.append("authorised_next_gate must be 2R.1")
    if not control.get("approved_at"):
        errors.append("approved_at must be recorded before Gate 2R.1")
    if not control.get("parent_evidence_commit_sha"):
        errors.append("parent_evidence_commit_sha must be recorded before Gate 2R.1")
if errors:
    for error in errors:
        print(f"Gate {gate} control failure: {error}", file=sys.stderr)
    raise SystemExit(3)
PY

"$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py 02R phase-02r phase_02r
if [[ "$GATE" == "2R.0" ]]; then
  "$PYTHON_BIN" scripts/verify_phase0_or_equivalent_baseline.py
  echo "PHASE 02R GATE 2R.0 PREFLIGHT PASSED"
else
  "$PYTHON_BIN" scripts/validate_phase_control_sets.py
  "$PYTHON_BIN" scripts/verify_migration_graph.py
  "$PYTHON_BIN" scripts/validate_schema_integrity.py
  echo "PHASE 02R GATE 2R.1 PREFLIGHT PASSED"
fi
