#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

GATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate) GATE="${2:-}"; shift 2 ;;
    *) echo "Unsupported argument: $1" >&2; exit 2 ;;
  esac
done
case "$GATE" in
  2R.0|2R.1|2R.2|2R.3|2R.4|2R.5|2R.6|2R.7|2R.8) ;;
  *) echo "Gate $GATE evidence collection is not supported." >&2; exit 2 ;;
esac

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

if [[ "$GATE" == "2R.4" && -x scripts/collect_phase02r_gate2r4_evidence.sh ]]; then
  exec bash scripts/collect_phase02r_gate2r4_evidence.sh
fi
if [[ "$GATE" == "2R.5" && -x scripts/collect_phase02r_gate2r5_evidence.sh ]]; then
  exec bash scripts/collect_phase02r_gate2r5_evidence.sh
fi
if [[ "$GATE" == "2R.6" && -x scripts/collect_phase02r_gate2r6_evidence.sh ]]; then
  exec bash scripts/collect_phase02r_gate2r6_evidence.sh
fi
if [[ "$GATE" == "2R.7" && -x scripts/collect_phase02r_gate2r7_evidence.sh ]]; then
  exec bash scripts/collect_phase02r_gate2r7_evidence.sh
fi
if [[ "$GATE" == "2R.8" && -x scripts/collect_phase02r_gate2r8_evidence.sh ]]; then
  exec bash scripts/collect_phase02r_gate2r8_evidence.sh
fi

if [[ "$GATE" == "2R.0" ]]; then
  EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-2r0"
  REPORT="docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md"
else
  GATE_FILE="${GATE/./}"
  GATE_DIR="${GATE,,}"
  GATE_DIR="${GATE_DIR/.}"
  EVIDENCE_ROOT="docs/release-evidence/atlas/phase-02r/gate-${GATE_DIR}"
  REPORT="docs/roadmap/execution/atlas/phase_02r_gate_${GATE_FILE}_closure_report.md"
fi
mkdir -p "$EVIDENCE_ROOT"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$EVIDENCE_ROOT/collection_failure.md" <<EOF
# Phase 2R Gate $GATE Evidence Collection Failure

**Generated:** $timestamp
**Status:** Failed

No dedicated collector was found for Gate $GATE.
EOF

echo "No dedicated collector found for Gate $GATE" >&2
exit 3
