#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/docs/release-evidence/technical-audit/backend-fast-phase02d/$STAMP"
RAW="$OUT/raw"
mkdir -p "$RAW"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"

set +e
"$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_phase02d.py --json > "$RAW/phase02d_verification.json" 2> "$RAW/phase02d_verification.err"
VERIFY_RC=$?
"$PYTHON_BIN" -m compileall -q app/services/content_staging_readiness.py scripts/curriculum/seed_staging_review_scopes.py scripts/audit_remediation scripts/ci/content_factory_schema_contract.py > "$RAW/compileall.txt" 2>&1
COMPILE_RC=$?
"$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02d.py --no-cov > "$RAW/focused_tests.txt" 2>&1
TEST_RC=$?
set -e

sha256sum "$RAW"/* > "$RAW/SHA256SUMS.txt"
VALID=false
if [[ "$VERIFY_RC" == "0" && "$COMPILE_RC" == "0" && "$TEST_RC" == "0" ]]; then
  VALID=true
fi
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
INDEX="$OUT/evidence_index.md"
cat > "$INDEX" <<EOF
# Technical Audit Phase 02D Evidence — Backend Fast Staging and Contract Remediation

- Generated at: $STAMP
- Source commit: $SOURCE_COMMIT
- Status: $(if [[ "$VALID" == "true" ]]; then echo "Phase 02D remediation verification passed — backend-fast retry pending"; else echo "Phase 02D remediation verification failed — remediation pending"; fi)
- Backend-fast authority evidence: not created by this slice
- Authority command remains: \`make test-fast\`
- Runtime KG implementation: not included

## Results

| Check | Exit code |
| --- | ---: |
| phase02d verifier | $VERIFY_RC |
| compileall | $COMPILE_RC |
| focused tests | $TEST_RC |

## Raw artifacts

- raw/phase02d_verification.json
- raw/phase02d_verification.err
- raw/compileall.txt
- raw/focused_tests.txt
- raw/SHA256SUMS.txt
EOF
sha256sum "$INDEX" > "$OUT/evidence_index.sha256"
echo "$INDEX"
if [[ "$VALID" != "true" ]]; then
  exit 1
fi
