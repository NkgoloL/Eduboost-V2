#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="docs/release-evidence/technical-audit/backend-fast-phase02g/${STAMP}"
RAW="${OUT}/raw"
mkdir -p "$RAW"

set +e
"$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_phase02g.py --json > "$RAW/phase02g_verification.json" 2> "$RAW/phase02g_verification.stderr"
VERIFY_RC=$?
"$PYTHON_BIN" -m compileall -q app/services/popia_service.py app/repositories/learner_repository.py scripts/audit_remediation > "$RAW/compileall.txt" 2>&1
COMPILE_RC=$?
"$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02g.py --no-cov > "$RAW/focused_tests.txt" 2>&1
TEST_RC=$?
set -e

STATUS="Phase 02G verification failed — remediation pending"
if [[ "$VERIFY_RC" -eq 0 && "$COMPILE_RC" -eq 0 && "$TEST_RC" -eq 0 ]]; then
  STATUS="Phase 02G verification passed — backend-fast retry pending"
fi

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
cat > "$OUT/evidence_index.md" <<EOF
# Technical Audit Backend Fast Phase 02G Evidence

- Branch: ${BRANCH}
- Source commit: ${SOURCE_COMMIT}
- Status: ${STATUS}
- Scope: POPIA async-session write safety and route/auth contract hardening
- Backend-fast authority: \`make test-fast\` remains required before passing backend-fast evidence may be recorded.
- KG boundary: no runtime knowledge-graph implementation included.

## Raw artifacts

- raw/phase02g_verification.json
- raw/phase02g_verification.stderr
- raw/compileall.txt
- raw/focused_tests.txt
EOF

( cd "$OUT" && find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt )

cat > docs/roadmap/execution/technical_audit_remediation/02g_backend_fast_popia_async_contracts_status.md <<EOF
# TA Phase 02G Status — POPIA Async Route Contracts

- Evidence collected at: ${OUT}
- Status: ${STATUS}
- Backend-fast candidate evidence remains blocked until \`make test-fast\` exits 0.
EOF

if [[ "$VERIFY_RC" -ne 0 || "$COMPILE_RC" -ne 0 || "$TEST_RC" -ne 0 ]]; then
  echo "Phase 02G evidence collection failed; see ${OUT}" >&2
  exit 1
fi

echo "Phase 02G evidence collected at ${OUT}"
