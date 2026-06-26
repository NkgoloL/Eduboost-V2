#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/docs/release-evidence/technical-audit/backend-fast-phase02e/$STAMP"
RAW="$OUT/raw"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p "$RAW"

cd "$ROOT"

set +e
"$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_phase02e.py --json > "$RAW/phase02e_verification.json" 2> "$RAW/phase02e_verification.stderr"
VERIFY_STATUS=$?
"$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02e.py --no-cov > "$RAW/focused_tests.txt" 2>&1
TEST_STATUS=$?
"$PYTHON_BIN" -m compileall -q app/api_v2_routers/ether.py app/services/content_staging_seed_executor.py scripts/curriculum/seed_staging_review_scopes.py scripts/audit_remediation > "$RAW/compileall.txt" 2>&1
COMPILE_STATUS=$?
set -e

{
  echo "# Backend Fast Phase 02E Evidence"
  echo ""
  echo "Generated at: \`${STAMP}\`"
  echo ""
  echo "## Status"
  echo ""
} > "$OUT/evidence_index.md"

if [[ "$VERIFY_STATUS" -eq 0 && "$TEST_STATUS" -eq 0 && "$COMPILE_STATUS" -eq 0 ]]; then
  echo "Status: Phase 02E focused verification passed — backend-fast retry pending" >> "$OUT/evidence_index.md"
else
  echo "Status: Phase 02E focused verification failed — remediation pending" >> "$OUT/evidence_index.md"
fi

GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
{
  echo ""
  echo "## Source"
  echo ""
  echo "- Source commit: \`${GIT_SHA}\`"
  echo "- Branch: \`${GIT_BRANCH}\`"
  echo ""
  echo "## Checks"
  echo ""
  echo "| Check | Exit code |"
  echo "|---|---:|"
  echo "| Phase 02E verifier | ${VERIFY_STATUS} |"
  echo "| Focused tests | ${TEST_STATUS} |"
  echo "| Compileall | ${COMPILE_STATUS} |"
  echo ""
  echo "## Boundary"
  echo ""
  echo "This is focused remediation evidence only. It is not backend-fast candidate evidence. The authority gate remains \`make test-fast\` and must exit 0 before passing backend-fast evidence may be committed."
  echo ""
} >> "$OUT/evidence_index.md"

(
  cd "$OUT"
  find . -type f -not -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

if [[ "$VERIFY_STATUS" -eq 0 && "$TEST_STATUS" -eq 0 && "$COMPILE_STATUS" -eq 0 ]]; then
  exit 0
fi
exit 1
