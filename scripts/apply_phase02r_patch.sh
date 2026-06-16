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

if [[ "$GATE" == "2R.0" ]]; then
  echo "Gate 2R.0 is read-only discovery; apply_phase02r_patch.sh is prohibited." >&2
  exit 3
fi

echo "Phase 02R implementation patches are blocked until Gate 2R.0 approval sets PHASE_02R_START_APPROVED=true." >&2
exit 3
