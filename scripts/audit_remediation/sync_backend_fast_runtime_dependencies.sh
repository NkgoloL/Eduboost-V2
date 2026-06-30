#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PY="$ROOT/.venv/bin/python"
PIP_FLAGS=(--disable-pip-version-check)

if [[ ! -f "$ROOT/requirements/dev.txt" ]]; then
  echo "ERROR: requirements/dev.txt not found" >&2
  exit 1
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "Creating .venv using ${PYTHON_BIN}" >&2
  "$PYTHON_BIN" -m venv "$ROOT/.venv"
fi

"$VENV_PY" -m pip install "${PIP_FLAGS[@]}" --upgrade pip setuptools wheel
"$VENV_PY" -m pip install "${PIP_FLAGS[@]}" -r "$ROOT/requirements/dev.txt"

# Keep explicit installs for packages observed in the failed authority gate and
# already declared in the project dependency files. This makes the script robust
# when the local requirements lock is partially stale.
"$VENV_PY" -m pip install "${PIP_FLAGS[@]}" \
  'pytest-xdist==3.6.1' \
  'pytest-cov' \
  'pypdf==5.4.0' \
  'arq==0.28.0' \
  'mcp[cli]>=1.0.0'

# Prove the exact import used by tools/etl/etl_mcp_server_v2.py, not only `import mcp`.
"$VENV_PY" - <<'PY'
from mcp.server.fastmcp import FastMCP
print(FastMCP.__name__)
PY

cd "$ROOT"
"$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py --json
