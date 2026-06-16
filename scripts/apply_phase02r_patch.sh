#!/usr/bin/env bash
set -euo pipefail

GATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate)
      GATE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

if [[ "$GATE" == "2R.0" ]]; then
  echo "Gate 2R.0 is read-only discovery; apply_phase02r_patch.sh is prohibited." >&2
  exit 3
fi

if [[ "$GATE" != "2R.1" ]]; then
  echo "Only Gate 2R.1 implementation patch application is currently supported." >&2
  exit 2
fi

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

"$PYTHON_BIN" - <<'PY'
import json
import sys
from pathlib import Path

control_path = Path("docs/roadmap/execution/atlas/phase_02r_start_gate_control.json")
control = json.loads(control_path.read_text(encoding="utf-8"))
errors = []
if control.get("phase") != "02R":
    errors.append("phase must be 02R")
if control.get("start_approved") is not True:
    errors.append("start_approved must be true")
if control.get("approved_gate") != "2R.0":
    errors.append("approved_gate must be 2R.0")
if control.get("authorised_next_gate") != "2R.1":
    errors.append("authorised_next_gate must be 2R.1")
if not control.get("parent_evidence_commit_sha"):
    errors.append("parent_evidence_commit_sha is required")
if errors:
    for error in errors:
        print(f"Gate 2R.1 apply control failure: {error}", file=sys.stderr)
    raise SystemExit(3)
PY

echo "PHASE 02R GATE 2R.1 PATCH APPLICATION AUTHORISED"
