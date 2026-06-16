#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  else
    fail "Python 3 is required."
  fi
fi

printf 'Using Python: %s\n' "$PYTHON_BIN"
"$PYTHON_BIN" --version

printf '\n[1/5] Verify production fallback policy\n'
grep -q "except (OperationalError, SQLAlchemyTimeoutError, ConnectionError, TimeoutError)" \
  app/services/semantic_retrieval/service.py
grep -q "vector_temporarily_unavailable" \
  app/services/semantic_retrieval/service.py
grep -q "except Exception:" \
  app/services/semantic_retrieval/service.py

printf '\n[2/5] Verify updated test contract\n'
grep -q "test_vector_query_transient_failure_uses_fulltext_only_when_policy_allows" \
  tests/phase02/test_service.py
grep -q "test_vector_query_generic_runtime_error_fails_closed" \
  tests/phase02/test_service.py
! grep -q "vector_query_failed:RuntimeError" tests/phase02/test_service.py

printf '\n[3/5] Run focused Phase 2 service tests\n'
"$PYTHON_BIN" -m pytest -q tests/phase02/test_service.py

printf '\n[4/5] Run Phase 2 fast verification\n'
bash scripts/verify_phase2.sh

printf '\n[5/5] Re-run reconciliation PostgreSQL verification\n'
bash scripts/verify_phases_01_07_reconciliation_postgres.sh

printf '\nPASS: Phase 2 retrieval fallback hotfix verified.\n'
