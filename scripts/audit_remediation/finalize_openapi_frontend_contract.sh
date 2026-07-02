#!/usr/bin/env bash
set -euo pipefail

MODE="${1:---check-only}"
if [[ "$MODE" != "--check-only" && "$MODE" != "--regenerate" ]]; then
  echo "Usage: $0 [--check-only|--regenerate]" >&2
  exit 2
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${FALLBACK_PYTHON_BIN:-python3}"
fi

if [[ "$MODE" == "--regenerate" ]]; then
  "$PYTHON_BIN" scripts/generate_openapi.py
fi

"$PYTHON_BIN" scripts/generate_openapi.py --check
python3 scripts/audit_remediation/verify_openapi_route_contract.py --json >/tmp/eduboost_openapi_route_contract.json
python3 scripts/audit_remediation/verify_openapi_frontend_contract.py --json >/tmp/eduboost_openapi_frontend_contract.json
python3 scripts/audit_remediation/verify_popia_route_contract.py --json >/tmp/eduboost_popia_route_contract.json

printf 'OPENAPI FRONTEND CONTRACT %s PASSED\n' "$MODE"
