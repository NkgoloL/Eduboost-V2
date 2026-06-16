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

[[ "$GATE" == "2R.0" || "$GATE" == "2R.1" ]] || { echo "Only Gate 2R.0 and Gate 2R.1 verification are supported." >&2; exit 2; }
if [[ "$GATE" == "2R.0" ]]; then
  [[ "$MODE" == "discovery" ]] || { echo "Gate 2R.0 supports --mode discovery only." >&2; exit 2; }
else
  [[ -z "$MODE" || "$MODE" == "implementation" ]] || { echo "Gate 2R.1 supports no mode or --mode implementation only." >&2; exit 2; }
fi

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

if [[ "$GATE" == "2R.0" ]]; then
  echo "== Gate 2R.0 preflight =="
  bash scripts/preflight_phase02r.sh --gate 2R.0 --mode discovery

  echo "== Source manifest and inventory sample =="
  "$PYTHON_BIN" scripts/curriculum/validate_source_manifest.py --json
  "$PYTHON_BIN" scripts/curriculum/source_inventory.py --json

  echo "== Non-production extraction sample =="
  "$PYTHON_BIN" scripts/curriculum/extract_caps_source_sample.py --json

  echo "== Phase 1-7 reconciliation fast gate =="
  bash scripts/verify_phases_01_07_reconciliation.sh

  echo "PHASE 02R GATE 2R.0 DISCOVERY VERIFICATION PASSED"
else
  echo "== Gate 2R.1 preflight =="
  bash scripts/preflight_phase02r.sh --gate 2R.1

  echo "== Gate 2R.1 patch-application authorisation =="
  bash scripts/apply_phase02r_patch.sh --gate 2R.1

  echo "== Gate 2R.1 baseline controls =="
  "$PYTHON_BIN" scripts/validate_phase_identifier_compatibility.py --strict 02R phase-02r phase_02r
  "$PYTHON_BIN" scripts/validate_phase_control_sets.py
  "$PYTHON_BIN" scripts/verify_migration_graph.py
  "$PYTHON_BIN" scripts/validate_schema_integrity.py

  echo "PHASE 02R GATE 2R.1 VERIFICATION PASSED"
fi
