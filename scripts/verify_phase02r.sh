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

[[ "$GATE" == "2R.0" || "$GATE" == "2R.1" ]] || {
  echo "Only Gate 2R.0 and Gate 2R.1 verification are currently supported." >&2
  exit 2
}
if [[ "$GATE" == "2R.0" ]]; then
  [[ "$MODE" == "discovery" ]] || { echo "Gate 2R.0 supports --mode discovery only." >&2; exit 2; }
else
  MODE="${MODE:-implementation}"
  [[ "$MODE" == "implementation" || "$MODE" == "closure" ]] || {
    echo "Gate 2R.1 supports --mode implementation or --mode closure." >&2
    exit 2
  }
fi

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

if [[ "$GATE" == "2R.0" ]]; then
  bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery
  "$PYTHON_BIN" scripts/curriculum/validate_source_manifest.py --json
  "$PYTHON_BIN" scripts/curriculum/source_inventory.py --json
  "$PYTHON_BIN" scripts/curriculum/extract_caps_source_sample.py --json
  bash scripts/verify_phases_01_07_reconciliation.sh
  echo "PHASE 02R GATE 2R.0 DISCOVERY VERIFICATION PASSED"
  exit 0
fi

# Behavioral and control checks execute in a single Python process to keep
# local and CI behavior deterministic and avoid partially reported runs.
"$PYTHON_BIN" scripts/verify_phase02r_gate2r1.py --mode "$MODE"

if [[ "$MODE" == "closure" ]]; then
  # Database proof is intentionally a separate gate because the static verifier
  # cannot establish PostgreSQL triggers, append-only enforcement, or upgrade
  # behavior. It runs only after the frozen inventory/control checks pass.
  bash scripts/verify_phase02r_postgres.sh
  echo "PHASE 02R GATE 2R.1 CANDIDATE CLOSURE VERIFICATION PASSED"
else
  echo "PHASE 02R GATE 2R.1 IMPLEMENTATION VERIFICATION PASSED"
fi
