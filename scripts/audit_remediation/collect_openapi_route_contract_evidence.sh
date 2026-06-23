#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
EVIDENCE_DIR="docs/release-evidence/technical-audit/openapi-route-contract"
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

run_capture "$RAW_DIR/baseline_reset_check.json" "$PYTHON_BIN" scripts/audit_remediation/verify_baseline_reset.py --json
run_capture "$RAW_DIR/openapi_regeneration_check.txt" bash scripts/audit_remediation/regenerate_openapi_contract.sh --check-only
run_capture "$RAW_DIR/openapi_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_openapi_route_contract.py --json
run_capture "$RAW_DIR/popia_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_popia_route_contract.py --json
run_capture "$RAW_DIR/frontend_env_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_frontend_env_contract.py --json
run_capture "$RAW_DIR/compileall.txt" "$PYTHON_BIN" -m compileall -q scripts/audit_remediation
run_capture "$RAW_DIR/unit_tests.txt" "$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_openapi_route_contracts.py --no-cov

sha256sum docs/openapi.json > "$RAW_DIR/openapi_sha256.txt"
find "$RAW_DIR" -type f -print0 | sort -z | xargs -0 sha256sum > "$RAW_DIR/SHA256SUMS.txt"

OPENAPI_SHA="$(cut -d' ' -f1 "$RAW_DIR/openapi_sha256.txt")"

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# Technical Audit Remediation Evidence — OpenAPI Route Contract

**Stream:** technical-audit-remediation  
**Slice:** 01-openapi-route-contract  
**Branch:** ${BRANCH}  
**Source commit:** ${SOURCE_COMMIT}  
**Generated at:** ${GENERATED_AT}  
**Status:** Candidate verification passed — human approval pending  
**OpenAPI SHA-256:** ${OPENAPI_SHA}

## Raw evidence

- raw/baseline_reset_check.json
- raw/openapi_regeneration_check.txt
- raw/openapi_route_contract.json
- raw/popia_route_contract.json
- raw/frontend_env_contract.json
- raw/compileall.txt
- raw/unit_tests.txt
- raw/openapi_sha256.txt
- raw/SHA256SUMS.txt

## Scope boundary

This evidence confirms OpenAPI regeneration and route-contract verification for the technical-audit remediation stream. It does not claim product release readiness or full remediation closure.
EOF

printf 'Collected OpenAPI route-contract evidence in %s\n' "$EVIDENCE_DIR"
