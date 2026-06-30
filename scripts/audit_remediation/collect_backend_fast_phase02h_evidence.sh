#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="docs/release-evidence/technical-audit/backend-fast-phase02h/$STAMP"
RAW="$OUT/raw"
mkdir -p "$RAW"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
{
  "$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_phase02h.py --json > "$RAW/phase02h_verification.json"
  "$PYTHON_BIN" -m compileall -q app scripts > "$RAW/compileall.txt" 2>&1
  "$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_backend_fast_phase02h.py --no-cov > "$RAW/focused_tests.txt" 2>&1
} || {
  cat > "$OUT/evidence_index.md" <<EOF
# Backend Fast Phase 02H Evidence

Branch: $BRANCH
Source commit: $SOURCE_COMMIT
Status: Phase 02H verification failed — remediation pending

This is not backend-fast candidate evidence.
EOF
  exit 1
}
SHA_FILE="$OUT/SHA256SUMS.txt"
(cd "$OUT" && find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt)
cat > "$OUT/evidence_index.md" <<EOF
# Backend Fast Phase 02H Evidence

Branch: $BRANCH
Source commit: $SOURCE_COMMIT
Status: Phase 02H verification passed — backend-fast retry pending

## Boundary

This evidence proves the focused Phase 02H remediation contracts only. It does not create passing backend-fast gate evidence.

Backend-fast authority remains:

\`\`\`bash
bash scripts/audit_remediation/collect_backend_fast_evidence.sh
\`\`\`

## Raw evidence

- raw/phase02h_verification.json
- raw/compileall.txt
- raw/focused_tests.txt
- SHA256SUMS.txt
EOF
sha256sum "$OUT/evidence_index.md" > "$OUT/evidence_index.sha256"
echo "Wrote $OUT"
