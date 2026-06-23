#!/usr/bin/env bash
set -euo pipefail

MODE="--check-only"
if [[ $# -gt 0 ]]; then
  MODE="$1"
fi

if [[ "$MODE" != "--check-only" && "$MODE" != "--regenerate" ]]; then
  echo "Usage: $0 [--check-only|--regenerate]" >&2
  exit 2
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -f scripts/generate_openapi.py ]]; then
  echo "missing scripts/generate_openapi.py" >&2
  exit 1
fi

if [[ ! -f scripts/audit_remediation/verify_openapi_route_contract.py ]]; then
  echo "missing scripts/audit_remediation/verify_openapi_route_contract.py" >&2
  exit 1
fi

if [[ -f scripts/audit_remediation/verify_baseline_reset.py ]]; then
  "$PYTHON_BIN" scripts/audit_remediation/verify_baseline_reset.py --json >/tmp/eduboost_audit_baseline_reset.json
fi

if [[ "$MODE" == "--regenerate" ]]; then
  "$PYTHON_BIN" scripts/generate_openapi.py
fi

"$PYTHON_BIN" scripts/generate_openapi.py --check
"$PYTHON_BIN" scripts/audit_remediation/verify_openapi_route_contract.py --json

if [[ -f scripts/audit_remediation/verify_popia_route_contract.py ]]; then
  "$PYTHON_BIN" scripts/audit_remediation/verify_popia_route_contract.py --json
fi

printf 'OPENAPI ROUTE CONTRACT %s PASSED\n' "$MODE"
