#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
EVIDENCE_DIR="docs/release-evidence/technical-audit/baseline-reset"
RAW_DIR="$EVIDENCE_DIR/raw"
mkdir -p "$RAW_DIR"

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'UNKNOWN')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'UNKNOWN')"

run_capture() {
  local output="$1"
  shift
  set +e
  "$@" > "$output" 2>&1
  local status=$?
  set -e
  printf '\nexit_status=%s\n' "$status" >> "$output"
  return "$status"
}

run_capture "$RAW_DIR/baseline_reset.json" "$PYTHON_BIN" scripts/audit_remediation/verify_baseline_reset.py --json
run_capture "$RAW_DIR/popia_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_popia_route_contract.py --json
run_capture "$RAW_DIR/frontend_env_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_frontend_env_contract.py --json
run_capture "$RAW_DIR/dependency_scan_workflow.json" "$PYTHON_BIN" scripts/audit_remediation/verify_dependency_scan_workflow.py --json
run_capture "$RAW_DIR/unit_tests.txt" "$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_technical_audit_baseline_contracts.py
run_capture "$RAW_DIR/compileall.txt" "$PYTHON_BIN" -m compileall -q scripts/audit_remediation

(
  cd "$RAW_DIR"
  sha256sum * > SHA256SUMS.txt
)

INDEX="$EVIDENCE_DIR/evidence_index.md"
cat > "$INDEX" <<EOF
# Technical Audit Remediation Baseline Reset Evidence

Branch: $BRANCH
Source commit: $SOURCE_COMMIT
Status: Candidate verification passed — human approval pending
Phase 02R: closed
Technical-audit stream: baseline reset evidence collected

## Raw artifacts

- raw/baseline_reset.json
- raw/popia_route_contract.json
- raw/frontend_env_contract.json
- raw/dependency_scan_workflow.json
- raw/unit_tests.txt
- raw/compileall.txt
- raw/SHA256SUMS.txt

## Scope

This evidence supports the technical-audit remediation baseline reset only. It does not close the full technical-audit remediation stream and does not establish product release readiness.
EOF

sha256sum "$INDEX" > "$EVIDENCE_DIR/evidence_index.sha256"
printf 'Evidence collected under %s\n' "$EVIDENCE_DIR"
cat "$EVIDENCE_DIR/evidence_index.sha256"
