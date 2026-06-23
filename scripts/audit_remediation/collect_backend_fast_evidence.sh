#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
BACKEND_FAST_COMMAND="${BACKEND_FAST_COMMAND:-make test-fast}"
EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-gate"
RAW_DIR="$EVIDENCE_DIR/raw"
mkdir -p "$RAW_DIR"

run_capture() {
  local output="$1"
  shift
  {
    echo "$ $*"
    "$@"
  } >"$output" 2>&1
}

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
GENERATED_AT="$(date -Iseconds)"

run_capture "$RAW_DIR/phase02r_terminal_gate_control.json" "$PYTHON_BIN" scripts/phase02r_gate_control.py \
  --expected-approved-gate 2R.8 \
  --expected-authorised-gate null \
  --require-approval-roles \
  --require-evidence-index-sha \
  --json
run_capture "$RAW_DIR/baseline_reset_check.json" "$PYTHON_BIN" scripts/audit_remediation/verify_baseline_reset.py --json
run_capture "$RAW_DIR/openapi_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_openapi_route_contract.py --json
run_capture "$RAW_DIR/popia_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_popia_route_contract.py --json
run_capture "$RAW_DIR/frontend_env_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_frontend_env_contract.py --json
run_capture "$RAW_DIR/dependency_scan_workflow.json" "$PYTHON_BIN" scripts/audit_remediation/verify_dependency_scan_workflow.py --json
run_capture "$RAW_DIR/backend_fast_preflight.json" "$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_gate_preflight.py --json
run_capture "$RAW_DIR/compileall.txt" "$PYTHON_BIN" -m compileall -q app scripts

set +e
"$PYTHON_BIN" scripts/audit_remediation/run_backend_fast_gate.py \
  --output-dir "$RAW_DIR" \
  --command "$BACKEND_FAST_COMMAND" \
  --json > "$RAW_DIR/backend_fast_runner_stdout.json" 2>&1
backend_fast_status=$?
set -e

"$PYTHON_BIN" scripts/audit_remediation/classify_backend_fast_failures.py \
  --input "$RAW_DIR/backend_fast_gate.txt" \
  --json > "$RAW_DIR/backend_fast_failure_classification.json"

if [[ "$backend_fast_status" -ne 0 ]]; then
  printf 'Backend fast gate failed with exit code %s. See %s/backend_fast_gate.txt and classification JSON.\n' "$backend_fast_status" "$RAW_DIR" >&2
  exit "$backend_fast_status"
fi

find "$RAW_DIR" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW_DIR/SHA256SUMS.txt"

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# Technical Audit Remediation Evidence — Backend Fast Gate

**Stream:** technical-audit-remediation  
**Slice:** 02-backend-fast-gate  
**Branch:** ${BRANCH}  
**Source commit:** ${SOURCE_COMMIT}  
**Generated at:** ${GENERATED_AT}  
**Status:** Candidate verification passed — human approval pending  
**Authority command:** ${BACKEND_FAST_COMMAND}

## Raw evidence

- raw/phase02r_terminal_gate_control.json
- raw/baseline_reset_check.json
- raw/openapi_route_contract.json
- raw/popia_route_contract.json
- raw/frontend_env_contract.json
- raw/dependency_scan_workflow.json
- raw/backend_fast_preflight.json
- raw/compileall.txt
- raw/backend_fast_gate.txt
- raw/backend_fast_gate_result.json
- raw/backend_fast_runner_stdout.json
- raw/backend_fast_failure_classification.json
- raw/backend_fast_evidence_check.json
- raw/SHA256SUMS.txt

## Scope boundary

This evidence confirms the backend fast gate for the technical-audit remediation stream. It does not claim full product release readiness, frontend closure, E2E closure, live database execution, or runtime knowledge-graph implementation.
EOF

run_capture "$RAW_DIR/backend_fast_evidence_check.json" "$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_evidence.py --json --evidence-dir "$EVIDENCE_DIR"
find "$RAW_DIR" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW_DIR/SHA256SUMS.txt"
sha256sum "$EVIDENCE_DIR/evidence_index.md" > "$EVIDENCE_DIR/evidence_index.sha256"
printf 'Collected backend fast-gate evidence in %s\n' "$EVIDENCE_DIR"
